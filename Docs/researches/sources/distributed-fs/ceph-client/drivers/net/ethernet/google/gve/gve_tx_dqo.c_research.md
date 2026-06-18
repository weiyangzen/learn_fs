
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_tx_dqo.c

## Purpose

This file implements the DQO transmit datapath for the Google Virtual Ethernet driver. It allocates and tears down DQO TX rings, posts SKB, XDP, and AF_XDP descriptors, manages optional queue-page-list copy buffers, handles descriptor and packet completions, tracks miss/reinjection completions, and integrates TX cleaning with NAPI notification blocks.

## Important APIs, Types, and Functions

- `gve_tx_alloc_rings_dqo()`, `gve_tx_free_rings_dqo()`, `gve_tx_start_ring_dqo()`, and `gve_tx_stop_ring_dqo()` are the lifecycle entry points used by the broader GVE device setup/teardown code.
- `gve_tx_dqo()` is the `ndo_start_xmit`-style SKB transmit entry for DQO rings. It calls `gve_try_tx_skb()`, batches doorbells with `netdev_xmit_more()`, and returns `NETDEV_TX_BUSY` when resource throttling is required.
- `gve_xdp_xmit_dqo()`, `gve_xdp_xmit_one_dqo()`, `gve_xdp_poll_dqo()`, `gve_xdp_tx_flush_dqo()`, and `gve_xsk_tx_poll_dqo()` cover XDP redirect/transmit and AF_XDP TX.
- `gve_clean_tx_done_dqo()` consumes completion descriptors and updates BQL, per-ring statistics, completion tags, and pending-packet state.
- `struct gve_tx_pending_packet_dqo` instances are the completion-tag state objects for SKBs, XDP frames, and XSK descriptors. They carry DMA unmap metadata, SKB/XDP frame pointers, QPL buffer IDs, state, linked-list pointers, and timeout jiffies.
- `gve_tx_fill_pkt_desc_dqo()`, `gve_tx_fill_tso_ctx_desc()`, and `gve_tx_fill_general_ctx_desc()` materialize hardware descriptors in the DQO TX ring.
- `gve_prep_tso()`, `gve_can_send_tso()`, and `gve_features_check_dqo()` enforce hardware descriptor limits for TSO/GSO.

## Control Flow

Ring allocation computes a safe pending-packet count from the completion-queue size, subtracting room for descriptor completions and possible miss/reinjection completions. Each ring gets a pending-packet array, optional XSK reorder queue, DMA-coherent TX and completion rings, queue resources, and, in QPL mode, a queue page list plus a freelist of fixed-size TX copy buffers.

Transmit first estimates data descriptor and buffer requirements. In raw-addressing mode it counts the SKB head and frags after splitting at `GVE_TX_MAX_BUF_SIZE_DQO`; in QPL mode it counts 2 KiB copy buffers. `gve_maybe_stop_tx_dqo()` checks pending-packet objects, ring slots, and QPL buffers, stops the netdev queue on shortage, uses a memory barrier to synchronize with the cleaner, and immediately rechecks to avoid a stop/wake race.

For SKBs, `gve_tx_add_skb_dqo()` allocates a completion tag, records the SKB, emits an optional TSO context descriptor, always emits a general context descriptor, then either maps SKB storage directly or copies packet bytes into QPL buffers. It advances the tail and occasionally requests descriptor report events. `gve_tx_dqo()` rings the doorbell immediately unless xmit-more batching says more packets are coming.

Completion polling walks the completion ring until the generation bit says hardware still owns the descriptor or the NAPI packet budget is reached. Descriptor completions update the cached hardware head. Packet completions free QPL buffers or DMA mappings and release SKBs/XDP frames. Miss completions move packets to a miss list and account BQL completion before waiting for reinjection. Reinjection completions complete those missed packets. Timeout processing drops packets that never receive reinjection and later frees the tag after a deallocation grace period.

AF_XDP TX peeks descriptors from the XSK pool, fills packet descriptors directly against pool DMA addresses, pushes completion tags into a reorder queue, and only reports completions to the XSK pool in original order after packet state becomes `GVE_PACKET_STATE_XSK_COMPLETE`.

## State and Persistence

State is entirely runtime kernel/device state. Ring state includes software head/tail pointers, atomic completion-side freelists for pending packets and QPL buffers, posted/completed descriptor counters, completion generation bit, miss and timed-out linked lists, XSK reorder head/tail, and u64 stats. QPL buffer ownership persists across TX and completion contexts using atomic head/count handoff. DMA mappings persist from descriptor posting until packet completion, timeout cleanup, or ring stop. Hardware state persists in coherent descriptor rings and queue doorbells until the ring is reset or freed.

## Dependencies and Integration Points

The file depends on GVE core structures from `gve.h`, admin queue/page-list helpers, DQO descriptor definitions, the Linux DMA API, BQL, NAPI, XDP, AF_XDP, SKB GSO/checksum helpers, and netdev TX queue APIs. It integrates with notify blocks through `gve_utils.c`, with queue allocation/configuration through GVE adminq code, and with RX-side XSK polling through the XDP TX queue mapping helpers.

## Risks and Edge Cases

The code is resource-accounting heavy. Bugs in pending-packet freelists, QPL buffer counts, or descriptor-count estimation can stop queues permanently or overrun rings. The miss/reinjection model intentionally treats several completion orderings as invalid; those paths are rate-limited errors and can leave packets waiting for timeout. QPL and raw-addressing cleanup differ, so error paths must match allocation mode exactly. `gve_maybe_stop_tx_dqo()` contains two `netif_tx_start_queue()` calls in the recovery branch, which is harmless but suspicious. XSK completion reporting depends on reorder-queue ordering rather than hardware order. TSO eligibility is constrained by per-segment descriptor count; incorrect checks would surface as device-side drops or disabled GSO.

## Test Signals

Useful signals include successful DQO ring allocation/free for raw-addressing and QPL modes, SKB TX under BQL pressure with queue stop/wake, TSO and non-TSO packets with many frags, DMA mapping failure injection, XDP redirect and AF_XDP TX completion ordering, miss/reinjection completion handling, reinjection timeout drops, clean `gve_tx_stop_ring_dqo()` without leaked SKBs or DMA mappings, and counters such as `pkt_done`, `bytes_done`, `dropped_pkt`, `xdp_xmit_errors`, and `xdp_xsk_sent`.
