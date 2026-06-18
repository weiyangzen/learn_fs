# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k.h

## Purpose

`cn10k.h` exposes CN10K NIC helper prototypes and an inline DWRR weight helper to the common NIC driver. It is the public header for CN10K LMTST, SQ, refill, and ingress policer operations implemented in `cn10k.c`.

## Important APIs, Types, And Functions

- `mtu_to_dwrr_weight()` computes scheduler DWRR weight as `ceil(mtu / hw.dwrr_mtu)`.
- Prototypes cover `cn10k_refill_pool_ptrs()`, `cn10k_sqe_flush()`, `cn10k_sq_aq_init()`, `cn10k_lmtst_init()`, policer allocation/free/rate/map helpers, and `otx2_init_hw_ops()`.

## Control Flow

The header provides inline arithmetic only. Runtime dispatch happens through `otx2_init_hw_ops()` and `struct dev_hw_ops`, then common code calls the selected functions indirectly for SQ setup, SQE flush, pool refill, aura/pool init, and mailbox interrupts.

## State And Persistence

No state is stored here. The inline helper reads `pfvf->hw.dwrr_mtu`, and the declared functions mutate NIC runtime state and hardware contexts in their implementation files.

## Dependencies And Integration Points

It includes `otx2_common.h`, so it inherits NIC core type definitions and also creates a circular-looking include dependency that is tolerated by include guards. `otx2_common.c`, `cn20k.c`, and feature/offload code use these declarations.

## Risks

- `mtu_to_dwrr_weight()` assumes `hw.dwrr_mtu` is nonzero; `otx2_get_max_mtu()` later normalizes zero to one, so call ordering matters.
- Header inclusion pulls in the large common header; changes can affect many translation units.
- Prototype drift from `cn10k.c` breaks builds across optional configurations.

## Test Signals

Compile coverage across OTX2, CN10K, and CN20K objects, plus runtime checks that DWRR weight changes when AF reports different DWRR MTUs, validate this header.
