# sources/distributed-fs/lizardfs/src/common/disk_info.cc

Purpose: implements accumulation of disk I/O statistics.

Important APIs/types/functions: `HddStatistics::add(const HddStatistics&)` sums byte, time, and operation counters and preserves maxima for read/write/fsync latency.

Control flow: simple field-wise addition, followed by max comparisons for `usecreadmax`, `usecwritemax`, and `usecfsyncmax`.

State and persistence: mutates the receiving `HddStatistics` object; serialized representation is defined in `disk_info.h`.

Dependencies and integration: depends on `common/disk_info.h`. Used by disk reporting to aggregate minute/hour/day or multi-disk statistics.

Risks: arithmetic can overflow silently on long-running or aggregated counters. No locking is provided for non-atomic `HddStatistics`.

Test signals: no direct tests in this subset.
