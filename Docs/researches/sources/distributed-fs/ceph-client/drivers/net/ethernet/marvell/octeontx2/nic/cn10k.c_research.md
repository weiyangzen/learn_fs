# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k.c

## Purpose

`cn10k.c` provides CN10K-specific NIC hardware operations for LMTST send/refill paths, SQ context initialization, dynamic LMT line setup, and ingress policer allocation/programming. It also selects between older OTX2 hardware ops and CN10K ops at runtime.

## Important APIs, Types, And Functions

- `otx2_hw_ops` and `cn10k_hw_ops` populate `struct dev_hw_ops` function tables.
- `otx2_init_hw_ops()` selects CN10K ops when `CN10K_LMTST` capability is set.
- `cn10k_lmtst_init()` allocates per-CPU LMT metadata and a dynamic LMT qmem region, then asks AF to configure the LMTST table.
- `cn10k_sq_aq_init()` initializes CN10K NIX SQ contexts through `nix_cn10k_aq_enq`.
- `cn10k_refill_pool_ptrs()` batch-refills NPA auras with up to 16 pointers.
- `cn10k_sqe_flush()` copies an SQE into the per-CPU LMT line and flushes it with `cn10k_lmt_flush()`.
- Ingress policer functions allocate/free leaf profiles, map/unmap RQ policers, calculate mantissa/exponent/rdiv values, and program matchall policer rate/actions.

## Control Flow

Initialization calls `otx2_init_hw_ops()` before queue setup so later common code dispatches through the right ops. If CN10K LMTST is present, `cn10k_lmtst_init()` requests local LMT-region use from AF, allocates qmem sized as `num_online_cpus() * LMT_BURST_SIZE`, and initializes each possible CPU's `otx2_lmt_info` with an address and LMT id.

Transmit flush uses the current CPU's LMT info, copies the prepared SQE into the LMT line, builds the target address with SQ IO address and SQE size, issues a DMA write barrier, flushes, then advances the SQ head. RX refill batches buffer addresses and calls `__cn10k_aura_freeptr()` when the batch reaches 16 or refill completes.

Policer configuration allocates a leaf bandwidth profile through mailbox, calculates token bucket fields from requested burst/rate, writes `nix_cn10k_aq_enq` band-profile fields, then maps the profile to every RQ for matchall policing. Free reverses all RQ mappings and frees the leaf profile.

## State And Persistence

State lives in `pfvf->hw_ops`, `pfvf->hw.lmt_info`, `pfvf->hw.lmt_base`, `pfvf->dync_lmt`, `pfvf->tot_lmt_lines`, and `pfvf->hw.matchall_ipolicer`. Hardware state persists in LMTST table setup, NIX SQ contexts, NPA aura contents, and NIX bandwidth profile/RQ policer mappings.

## Dependencies And Integration Points

The file depends on `otx2_common.h`, `otx2_reg.h`, `otx2_struct.h`, `cn10k_lmt_flush()`, mailbox allocators, qmem allocation, NIX/NPA context definitions, and common queue setup. It is called by PF probe/setup paths and by TC or ethtool code that configures ingress policing.

## Risks

- `alloc_percpu()` result is not checked before use in `cn10k_lmtst_init()`.
- Error after `qmem_alloc()` in LMT setup does not free already allocated percpu/qmem state in this function.
- Batch refill uses `num_ptrs` initialized to 1, leaving index 0 intentionally unused for the hardware helper; this convention is easy to break.
- Rate/burst calculations use integer approximations; low rates and very large bursts need boundary tests.
- Matchall policer setup can partially map RQs if a later map fails.

## Test Signals

CN10K probe with LMTST enabled, TX traffic through LMT flush, RX refill under pressure, per-CPU transmit on many CPUs, ingress policer rate/pps behavior, allocation-failure injection, and common OTX2 fallback when `CN10K_LMTST` is absent are important signals.
