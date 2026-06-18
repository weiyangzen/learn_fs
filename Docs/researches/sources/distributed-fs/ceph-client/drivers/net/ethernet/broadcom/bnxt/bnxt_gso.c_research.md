# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_gso.c

## Purpose

`bnxt_gso.c` implements software UDP L4 GSO/USO fallback for BNXT hardware that lacks native UDP segmentation offload. It converts one large UDP GSO SKB into multiple hardware TX packets by building per-segment inline headers, mapping payload chunks through the kernel TSO helper, emitting normal BNXT TX descriptors, and preserving a single SKB ownership model until the final segment completes.

## Important APIs and functions

- `bnxt_sw_gso_lhint()` maps a segment's total length to BNXT TX length-hint flags.
- `bnxt_sw_udp_gso_xmit()` is the exported transmit path used by the main BNXT TX code when `NETIF_F_GSO_UDP_L4` is requested but `BNXT_FLAG_UDP_GSO_CAP` is absent.
- It uses kernel TSO helpers: `tso_start()`, `tso_build_hdr()`, `tso_dma_map_init()`, `tso_dma_map_count()`, `tso_dma_map_next()`, and `tso_dma_map_completion_save()`.
- It uses BNXT TX helpers/macros from the main data path: `bnxt_tx_avail()`, `bnxt_inline_avail()`, `bnxt_xmit_get_cfa_action()`, `bnxt_init_ext_bd()`, `SET_TX_OPAQUE()`, `TX_BD_CNT()`, `NEXT_TX()`, `RING_TX()`, `TX_RING()`, `TX_IDX()`, and `bnxt_db_write()`.

## Control flow

The function starts by deriving header length, MSS, total UDP payload, and segment count. It drops malformed cases where only one segment would be produced. Before touching descriptors, it computes an upper bound of required BDs as `3 * num_segs + nr_frags + 1`, checks TX descriptor availability, and separately checks inline-header slot availability because per-segment headers live in `txr->tx_inline_buf`.

After initializing a TSO DMA map, it prepares VLAN/CFA metadata and checksum offload flags. For each segment, it selects an inline header slot, builds the segment header, clears stale UDP and IPv4 checksum fields because hardware will recompute them, syncs the inline header DMA range, calculates payload BD count, emits a long TX BD and extension BD, then walks payload mappings to emit one payload BD per chunk. The last payload BD for each segment gets `TX_BD_FLAGS_PACKET_END`.

Payload DMA unmapping is deliberately deferred to the last BD touching each mapped region. The code tracks `last_unmap_buf`, `last_unmap_addr`, and `last_unmap_len`, assigning the actual DMA unmap metadata only once it knows a later BD has superseded the same region. The last segment's first software BD is marked `BNXT_SW_GSO_LAST` and stores TSO completion state; earlier segment starts are marked `BNXT_SW_GSO_MID`.

At the end it advances `tx_inline_prod`, accounts the full original SKB length to the queue, publishes `tx_prod`, executes a write memory barrier, rings the TX doorbell, and may stop the netdev queue if descriptor space is low. On drop/error paths it frees the original SKB and increments TX dropped stats.

## State and persistence behavior

- Advances `txr->tx_prod` and `txr->tx_inline_prod` for normal TX ring and inline header ring consumption.
- Populates `txr->tx_buf_ring` entries with SKB ownership, fragment counts, software-GSO state, DMA unmap metadata, and completion state.
- Writes hardware TX descriptors into `txr->tx_desc_ring`.
- Uses queue accounting through `netdev_tx_sent_queue()` and queue stop helpers.
- No durable persistence exists; all state is in TX rings, DMA mappings, and SKB ownership until completions clean them.

## Dependencies and integration points

- Linux networking SKB, UDP/IP/IPv6, queue stop, and TSO segmentation helper APIs.
- PCI DMA APIs for header sync and payload mapping state.
- BNXT TX completion logic must understand `is_sw_gso`, `BNXT_SW_GSO_MID`, `BNXT_SW_GSO_LAST`, and saved TSO completion state.
- `bnxt_gso.h` supplies descriptor and inline-slot sizing assumptions used by ringparam validation and queue availability checks.

## Risks and edge cases

- Descriptor upper-bound math and cleanup assumptions must stay aligned with the main TX completion path; otherwise software USO can overwrite descriptors or leak mappings.
- Inline header ring availability is separate from TX BD availability. Missing this check would corrupt headers still referenced by in-flight DMA.
- The original SKB is referenced by every segment-start BD but must be freed exactly once, on the final software-GSO completion.
- DMA unmap metadata is assigned to the last BD touching a region; regressions in `tso_dma_map_next()` usage can double-unmap or leak payload mappings.
- IPv6 has no header checksum field to clear, while IPv4 does. The UDP checksum is always cleared before hardware offload.
- `num_segs` is bounded indirectly by `gso_max_segs` from `bnxt_gso.h`; if that cap changes, descriptor and inline buffer sizing must change with it.

## Test signals

- UDP GSO transmit on hardware without native USO for IPv4 and IPv6.
- Boundary cases at 2 segments, `BNXT_SW_USO_MAX_SEGS`, maximum SKB frags, VLAN-tagged SKBs, CFA action metadata, and short/large length hints.
- DMA mapping fault injection in `tso_dma_map_init()` and payload iteration.
- Queue stop/wake behavior when descriptor availability or inline slots are exhausted.
- TX completion tests that verify SKB free once, DMA unmap balance, and `tx_inline_cons` advancement.
