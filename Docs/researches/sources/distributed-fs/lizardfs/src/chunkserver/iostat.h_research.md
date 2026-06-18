# sources/distributed-fs/lizardfs/src/chunkserver/iostat.h

## Purpose
`iostat.h` provides the chunkserver's disk load estimator. On non-Linux systems it is a no-op. On Linux it samples `/proc/diskstats` for devices backing configured HDD paths and computes a weighted load factor that can be reported to the master.

## Important APIs, Types, and Functions
The public class `IoStat` has `resetPaths(const std::vector<std::string>&)` and `getLoadFactor()`. The Linux implementation maps `dev_t` to `StatEntry { ticks, size }`, where `ticks` is the previous total I/O tick count and `size` is filesystem block count from `statfs`. Constants define diskstats parsing limits and expected field count.

## Control Flow
`resetPaths` clears cached timestamp/load, stats each configured path, obtains filesystem size, and records the path's device. `getLoadFactor` returns cached load if called more than once in the same second, opens `/proc/diskstats`, scans all devices, and for matching devices accumulates `(current_tot_ticks - previous_ticks) * filesystem_size`. It divides by total size, elapsed seconds, and `10` to convert milliseconds of I/O time into a percentage-like factor, clamps to `100`, updates previous ticks and timestamp, and returns the result.

## State and Persistence Behavior
The class is runtime-only and keeps a previous sample per device plus cached load/timestamp. It reads kernel procfs state but does not persist anything. Missing paths, failed `statfs`, empty device maps, and failed `/proc/diskstats` reads produce a zero load factor.

## Dependencies and Integration Points
`hddspacemgr.cc` owns a global `IoStat gIoStat`, calls `resetPaths` after HDD config reload, and exposes `hdd_get_load_factor`. `masterconn.cc` optionally sends changed load factors in `masterconn_send_status` when `ENABLE_LOAD_FACTOR` is configured.

## Risks and Edge Cases
The calculation assumes Linux `/proc/diskstats` field semantics and total tick monotonicity. Device mapper, partitions, bind mounts, or multiple paths on one device can skew weighting. The first sample after reset uses `prev_timestamp_ = 0`, which makes the first computed load mostly a baseline reset rather than an accurate recent window. Integer arithmetic and one-second caching can hide short spikes.

## Test Signals
Unit tests can use a factored parser or fixture text for diskstats, checking matching devices, clamp-to-100, same-second caching, and zero behavior. Integration tests should verify `resetPaths` ignores invalid paths and that enabling load-factor reporting sends status changes without flooding.
