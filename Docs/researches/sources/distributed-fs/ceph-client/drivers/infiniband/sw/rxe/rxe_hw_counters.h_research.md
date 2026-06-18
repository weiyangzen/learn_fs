# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hw_counters.h

## Purpose
`rxe_hw_counters.h` defines RXE counter indexes and declares RDMA hw-stats callbacks.

## Important APIs, types, and functions
`enum rxe_counters` lists all counter slots and terminates with `RXE_NUM_OF_COUNTERS`. Declarations include `rxe_ib_alloc_hw_port_stats()` and `rxe_ib_get_hw_stats()`.

## Control flow
No runtime flow. The enum indexes are used by `rxe_counter_inc()` and by `rxe_hw_counters.c` to expose stats.

## State and persistence
The header does not own state; it defines the index contract for `rxe_dev.stats_counters[]`.

## Dependencies and integration points
It integrates RXE internal counter increments with RDMA core hw stats. Every source file that increments counters depends on stable enum values.

## Risks
The comment says new enum entries must also be added to the descriptor vector. Reordering existing counters changes userspace-visible stat meanings.

## Test signals
Build with `BUILD_BUG_ON` in `rxe_hw_counters.c`, inspect stats names/order, and exercise each counter increment path.
