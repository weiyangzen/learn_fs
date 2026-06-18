# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_res.h

## Purpose
`enic_res.h` defines ENIC resource limits, feature access macros, TX/RX descriptor-posting inline helpers, and prototypes for the resource routines implemented in `enic_res.c`.

## Important APIs, types, and functions
- `ENIC_MIN_WQ_DESCS`, `ENIC_MAX_WQ_DESCS_DEFAULT`, `ENIC_MAX_WQ_DESCS`, `ENIC_MIN_RQ_DESCS`, `ENIC_MAX_RQ_DESCS`, and `ENIC_MAX_CQ_DESCS_DEFAULT` bound ring sizing.
- `ENIC_MIN_MTU` and `ENIC_MAX_MTU` bound MTU configuration.
- `ENIC_SETTING(enic, f)` checks `VENETF_*` feature bits in `enic->config.flags`.
- `enic_queue_wq_desc_ex()` is the common encoder/poster for ENIC TX descriptors. It calls `wq_enet_desc_enc()` then `vnic_wq_post()`.
- Wrapper helpers select offload modes: plain checksum (`enic_queue_wq_desc()`), explicit checksum flags (`enic_queue_wq_desc_csum()`), L4 checksum offset (`enic_queue_wq_desc_csum_l4()`), TSO (`enic_queue_wq_desc_tso()`), and continuation descriptors (`enic_queue_wq_desc_cont()`).
- `enic_queue_rq_desc()` encodes an RX descriptor with `rq_enet_desc_enc()` and posts it to the RQ software ring.

## Control flow and state
The inline helpers are on the datapath. TX helpers write hardware descriptor fields first, then update software WQ bookkeeping through `vnic_wq_post()`. RX posting selects descriptor type from `os_buf_index`, encodes DMA address/length, and calls `vnic_rq_post()`, which advances the posted index at its own return rate.

The helpers mutate software queue buffer state and hardware-visible descriptor memory but do not directly ring doorbells except through lower-level queue helpers. The caller owns DMA mapping lifetime and later cleanup.

## Dependencies and integration points
The header binds ENIC code to `wq_enet_desc.h`, `rq_enet_desc.h`, `vnic_wq.h`, `vnic_rq.h`, and the `struct vnic_enet_config` flags from `vnic_enet.h`. It is consumed by ENIC TX/RX paths that need compact descriptor posting.

## Risks and test signals
Descriptor field packing mistakes produce silent packet corruption or stuck queues. The `len`, `mss`, checksum offset, VLAN tag, SOP/EOP, and loopback arguments must fit hardware field widths. Tests should exercise checksum offload, TSO, VLAN insertion, multi-fragment TX, and RX refill under ring wrap.
