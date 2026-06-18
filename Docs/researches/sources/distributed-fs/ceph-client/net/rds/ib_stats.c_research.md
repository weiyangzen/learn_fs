# sources/distributed-fs/ceph-client/net/rds/ib_stats.c

## Purpose
`ib_stats.c` defines and exports the per-CPU RDS/IB statistics block and provides the RDS info callback that aggregates IB transport counters for user-space inspection.

## Important APIs, Types, and Functions
The file defines `DEFINE_PER_CPU_SHARED_ALIGNED(struct rds_ib_statistics, rds_ib_stats)`, the string table `rds_ib_stat_names[]`, and `rds_ib_stats_info_copy()`. The names correspond by order to the fields of `struct rds_ib_statistics` in `ib.h`.

## Control Flow
`rds_ib_stats_info_copy()` returns the number of available stats. If the caller-provided capacity is large enough, it iterates over online CPUs, treats each per-CPU statistics struct as a `uint64_t` array, sums every field into a local aggregate, and passes values and names to `rds_stats_info_copy()`.

## State and Persistence
Counters are per-CPU volatile kernel counters reset at module load. They persist while the module remains loaded and are not written to disk. Alignment reduces false sharing on hot paths.

## Dependencies and Integration Points
The file integrates with the generic RDS info mechanism (`rds_info_iterator`) and generic stats formatting (`rds_stats_info_copy()`). Transport hot paths update the counters through `rds_ib_stats_inc()` and `rds_ib_stats_add()` macros declared in `ib.h`.

## Risks
The string table and `struct rds_ib_statistics` must remain in exact order and count alignment. A field added to the struct without a corresponding name silently produces confusing user-visible output. The current name table omits the final cache add/remove fields visible in the struct, so maintainers should verify intended ABI/count behavior before extending it.

## Test Signals
Validate that info queries report the expected element count, that counters increase under send/receive/RDMA workloads, and that table-size changes remain compatible with RDS info consumers.
