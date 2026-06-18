# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_tsn.h

## Purpose
`igc_tsn.h` declares the public TSN/FPE interface for the IGC driver and provides inline helpers for MAC merge packet recognition and SMD-V TX descriptor inspection.

## Important APIs, Types, and Functions
It defines `IGC_RX_MIN_FRAG_SIZE`, `SMD_FRAME_SIZE`, `enum igc_txd_popts_type` with `SMD_V` and `SMD_R`, and declares the static key `igc_fpe_enabled`. Public declarations cover FPE initialization, preempt queue tracking, supported fragment size selection, TSN offload apply/reset, launchtime offset adjustment, and taprio activation query. Inline helpers are `igc_fpe_is_pmac_enabled()`, `igc_fpe_handle_mpacket()`, and `igc_fpe_transmitted_smd_v()`.

## Control Flow
The header has simple inline control flow. `igc_fpe_is_pmac_enabled()` requires both the static key and adapter PMAC state. `igc_fpe_handle_mpacket()` extracts SMD type from RX descriptor status, accepts only verify/response SMD frames, validates a zero-filled 60-byte mpacket, reports the matching ethtool MAC merge event, and consumes the frame. `igc_fpe_transmitted_smd_v()` reads TX descriptor popts to detect transmitted verification frames.

## State and Persistence Behavior
No state is stored in the header. It reads adapter FPE state, RX descriptor status, and TX descriptor fields. Runtime FPE/TSN state is maintained in `igc_tsn.c` and adapter/ring structures.

## Dependencies and Integration Points
The header depends on packet scheduler types, ethtool MAC merge events, IGC descriptor bit definitions, `mem_is_zero()`, field extraction helpers, and adapter/ring structures supplied by the including driver headers. It is consumed by RX/TX paths that need to identify MAC merge mpackets.

## Risks and Edge Cases
The mpacket helper assumes SMD-V/SMD-R frames are exactly 60 zero bytes; malformed frames with valid SMD status are still consumed after the SMD type check even if no ethtool event is emitted. Static-key gating in `igc_fpe_is_pmac_enabled()` must match the global feature enable lifecycle. The include guard closing comment names `_IGC_BASE_H_`, which is cosmetic but misleading.

## Test Signals
Compile TSN/FPE users, inject RX descriptors for SMD-V, SMD-R, and non-SMD packets, verify ethtool MAC merge events, confirm malformed SMD frames are consumed as coded, and test TX descriptor detection for SMD-V versus SMD-R.
