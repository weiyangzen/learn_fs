# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_resc.h

## Purpose
This header declares resource-accounting structures and APIs for `bnge`, including firmware resource limits/reservations, requested hardware ring counts, IRQ metadata, and helper constants for RoCE reservation.

## Important APIs, Types, And Functions
Important types are `struct bnge_hw_resc`, `struct bnge_hw_rings`, and `struct bnge_irq`. Public functions include `bnge_reserve_rings`, `bnge_fix_rings_count`, `bnge_alloc_irqs`, `bnge_free_irqs`, default config init/uninit helpers, auxiliary config init, RSS indirection sizing, RSS context count calculation, and `bnge_aux_has_enough_resources`. `bnge_adjust_pow_two` rounds page/block counts for ring sizing.

## Control Flow
The header supports the sequence: query firmware resource caps into `bnge_hw_resc`, compute desired `bnge_hw_rings`, reserve with firmware, allocate IRQ table/vectors, and initialize netdev default resource configuration.

## State And Persistence
`bnge_hw_resc` stores min/max/reserved counts for RSS contexts, completion/TX/RX rings, ring groups, L2 contexts, VNICs, stat contexts, NQs/MSI-X, and flow records. `bnge_irq` persists vector number, handler, request state, affinity mask state, and display name while IRQs are allocated.

## Dependencies And Integration Points
The header includes `bnge_netdev.h` and `bnge_rmem.h`, so it sits above ring data structures and below resource calculation. It is consumed by probe, netdev allocation, open, and HWRM reservation code.

## Risks
The inline rounding helper returns at least two blocks for zero or one input block, which is appropriate for ring/page-table sizing but would be surprising if reused for a different semantic. IRQ naming and affinity state require careful cleanup if request or affinity setup partially fails.

## Test Signals
Build coverage plus runtime checks of resource caps, queue counts, IRQ request/free, RSS table size, and RoCE auxiliary reservation. Low-resource firmware profiles should be included.
