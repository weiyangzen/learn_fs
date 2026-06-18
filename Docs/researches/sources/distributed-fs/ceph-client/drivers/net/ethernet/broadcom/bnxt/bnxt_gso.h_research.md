# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_gso.h

## Purpose

`bnxt_gso.h` defines the public interface and sizing rules for BNXT software UDP segmentation offload fallback. It lets the rest of the driver cap advertised UDP GSO, reserve enough TX descriptors, and call the fallback transmit implementation when hardware lacks native UDP GSO.

## Important APIs and macros

- `BNXT_SW_USO_MAX_SEGS` caps software UDP GSO packets at 64 segments for NICs without hardware USO.
- `BNXT_SW_USO_MAX_DESCS` defines the worst-case descriptor budget for one software USO SKB: three descriptors per segment plus payload-fragment boundary overhead.
- `bnxt_inline_avail()` computes remaining inline header slots from `tx_inline_prod - tx_inline_cons`.
- `bnxt_min_tx_desc_cnt()` returns the larger software-USO descriptor minimum when UDP GSO is enabled without hardware capability, otherwise the normal `BNXT_MIN_TX_DESC_CNT`.
- `bnxt_sw_udp_gso_xmit()` is the exported fallback transmit routine.

## Control flow role

This header gates two caller decisions. Feature and ring sizing code uses `bnxt_min_tx_desc_cnt()` to reject rings too small for software USO. The main transmit path calls `bnxt_sw_udp_gso_xmit()` for eligible UDP GSO SKBs when hardware USO is unavailable.

## State and persistence behavior

No standalone state is stored here. The inline helper reads `struct bnxt_tx_ring_info` producer/consumer fields with `READ_ONCE()` on the consumer side because completions may update it asynchronously. The descriptor minimum depends on `bp->flags` and netdev feature bits.

## Dependencies and integration points

- Depends on BNXT TX ring structures and netdev feature flags.
- Tightly coupled to `bnxt_gso.c` descriptor emission and to TX completion handling of software-GSO state.
- Referenced by ethtool ringparam validation so users cannot shrink TX rings below the fallback's worst-case needs.

## Risks and edge cases

- The descriptor formula assumes each segment needs a long BD, extension BD, and payload BDs, with fragment-boundary overhead bounded by `num_segs + nr_frags`. Any descriptor format change must revisit this constant.
- `BNXT_SW_USO_MAX_SEGS` must match inline header ring allocation depth; otherwise availability checks and buffer indexing diverge.
- `bnxt_min_tx_desc_cnt()` only applies the larger minimum when `NETIF_F_GSO_UDP_L4` is enabled and hardware lacks the capability.

## Test signals

- Compile coverage with UDP GSO enabled/disabled and hardware USO capability present/absent.
- Ettool ring-size validation should reject TX rings smaller than `2 * BNXT_SW_USO_MAX_DESCS` when software USO is active, as enforced in `bnxt_ethtool.c`.
- Runtime software USO tests should confirm `bnxt_inline_avail()` backpressure prevents inline buffer overwrite.
