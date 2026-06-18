# sources/distributed-fs/ceph-client/drivers/md/dm-ps-service-time.c

## Purpose
Implements the `service-time` multipath path selector. It estimates service time as current in-flight byte load plus incoming request size divided by a user-configured relative throughput value, then selects the path with the lowest estimate.

## Important APIs, Types, And Functions
`struct selector` holds valid and failed path lists protected by a spinlock. `struct path_info` contains the `dm_path`, repeat count, relative throughput, and atomic in-flight byte count. Key functions are `st_add_path()`, `st_compare_load()`, `st_select_path()`, `st_start_io()`, `st_end_io()`, and `st_status()`. The selector table accepts optional per-path `repeat_count` and `relative_throughput` in the range 0 to 100.

## Control Flow
Selection scans valid paths and compares each candidate with the current best. If throughputs match, it chooses lower in-flight bytes; if load is equal or one path has throughput zero, it chooses higher throughput; otherwise it avoids division by comparing cross-multiplied service-time estimates and shifts down very large values to avoid overflow. The selected path is moved to the tail for tie fairness. `start_io` adds `nr_bytes` to `in_flight_size`, and `end_io` subtracts it.

## State And Persistence
All state is volatile and rebuilt on table load. The selector maintains a byte-weighted current load per path but no historical latency and no persistent state. A relative throughput of zero keeps a path from being selected while positive-throughput alternatives are available.

## Dependencies And Integration Points
It integrates with DM multipath path-selector hooks and relies on the multipath core to pass request byte size to select/start/end callbacks. Status exposes current in-flight bytes and relative throughput for monitoring and table reconstruction.

## Risks
The in-flight byte counter is an `atomic_t`, so very large or many concurrent requests can overflow on platforms where `int` is narrower than `size_t`. Incorrect start/end balancing permanently skews load. The throughput value is manually configured and can misrepresent actual path performance. Overflow mitigation in comparison preserves heuristic behavior but reduces precision at extreme loads.

## Test Signals
Test asymmetric throughput choices, zero-throughput paths, equal-load tie rotation, fail/reinstate, and high in-flight byte values near overflow thresholds. Status should show in-flight bytes changing with outstanding bios and table output should preserve configured throughput.
