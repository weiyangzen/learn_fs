# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-stats.c

## Purpose
Implements server-side RDMA statistics reset and formatting for sysfs.

## Important APIs, Types, And Functions
`rtrs_srv_reset_rdma_stats()` zeros each CPU's `struct rtrs_srv_stats_rdma_stats` when userspace writes an enabling value through the sysfs macro-generated attribute. `rtrs_srv_stats_rdma_to_str()` folds per-CPU read/write counters and byte totals into a single line.

## Control Flow
The server hot path updates per-CPU counters through `rtrs_srv_update_rdma_stats()` from `rtrs-srv.h`. Sysfs show calls aggregate all possible CPUs without locking individual counters, trading exact snapshots for low overhead. Store calls only accept the reset-enabled path; disabling returns `-EINVAL`.

## State And Persistence
Stats live in per-CPU kernel memory under each `rtrs_srv_stats`. They are resettable and not persisted across path teardown or module unload.

## Dependencies And Integration Points
Depends on `rtrs-srv.h`, Linux per-CPU iteration, and `sysfs_emit()`. Exposed through `rtrs-srv-sysfs.c` via `STAT_ATTR(struct rtrs_srv_stats, rdma, ...)`.

## Risks
Aggregation can race with live updates, so values are observational rather than transactionally consistent. Counter growth uses `u64`, but very long-lived high-throughput sessions can still wrap eventually.

## Test Signals
Validate sysfs `stats/rdma` output format, counter increments for server READ and WRITE events, reset behavior with `echo 1`, rejection of invalid reset values, CPU hotplug-adjacent possible-CPU iteration, and teardown after stats kobject release.
