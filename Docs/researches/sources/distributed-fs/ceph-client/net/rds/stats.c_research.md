# sources/distributed-fs/ceph-client/net/rds/stats.c

## Purpose
Exports global RDS runtime counters through the RDS info interface and provides the shared formatting helper used by transport-specific statistics.

## Important APIs, Types, and Functions
Defines and exports per-CPU `struct rds_statistics rds_stats`. `rds_stats_info_copy()` formats counter names and values as `struct rds_info_counter` records. `rds_stats_init()` registers `RDS_INFO_COUNTERS`, and `rds_stats_exit()` deregisters it. The local `rds_stats_info()` callback sums per-CPU counters and appends transport-specific stats through `rds_trans_stats_info_copy()`.

## Control Flow
When an RDS info request asks for counters, `rds_stats_info()` converts byte length to entry capacity, sums all online CPU counter slots into a local aggregate, copies named global counters if the caller supplied enough room, then delegates remaining capacity to transports. The result lengths report a fixed record size and a total count that includes transport counters even when the caller had insufficient buffer space.

## State and Persistence
State is per-CPU, cacheline-aligned, volatile counter memory. It persists only for the lifetime of the module or built-in subsystem and is reset by boot or module reload.

## Dependencies and Integration
Depends on the RDS info registry, per-CPU counter macros, online CPU iteration, and transport registration. The counter names must stay in field order with `struct rds_statistics` for the cast-and-sum logic to remain correct.

## Risks and Test Signals
Risks include counter-name drift from structure layout, buffer-size under-reporting, and CPU hotplug snapshot races inherent in unlocked per-CPU summation. Test signals are correct `RDS_INFO_COUNTERS` sizing, stable counter names, nonzero increments from send/receive paths, and appended TCP transport counters when `rds_tcp` is registered.
