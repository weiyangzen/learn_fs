# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_epoch.h

## Purpose
`rgw_dedup_epoch.h` defines the persisted epoch record for dedup scans. The epoch is the concurrency and restart boundary used by cluster coordination to distinguish old token objects from a current scan.

## Important APIs, Types, And Functions
`RGW_DEDUP_ATTR_EPOCH` is the xattr name used on the epoch token object. `dedup_epoch_t` contains a serial number, requested dedup type, timestamp, work shard count, and MD5 shard count.

Inline `encode()` and `decode()` serialize the epoch with Ceph encoding version 1. The dedup type is stored as an `int32_t`, then cast back to `dedup_req_type_t`. `operator<<` prints the epoch time, elapsed time, type, serial, and shard counts.

## Control Flow
The epoch is written by `set_epoch()` or `swap_epoch()` in `rgw_dedup_cluster.cc`. Background setup reads it during `cluster::reset()`, waits for nonzero shard counts when needed, and uses its time to clean old shard token objects.

## State And Persistence Behavior
The epoch is persisted as a single xattr payload in the RGW control pool. The timestamp is not just informational: cleanup compares token object mtime to epoch time and restart gating compares old and new epoch times.

## Dependencies And Integration Points
The type depends on Ceph `utime_t`, `ceph_clock_now()`, `rgw_dedup_utils.h` for `dedup_req_type_t`, and Ceph bufferlist encoding. It is consumed by the cluster coordinator and background setup.

## Risks And Edge Cases
Serial increments and timestamp comparisons are the main correctness signals. Clock skew or future epoch times can suppress restart in `can_start_new_scan()`. Adding fields requires a new encoding version and backward-compatible decode.

## Test Signals
Tests should verify encode/decode round trips for all dedup types and shard-count boundary values, stream output with elapsed time, and restart logic with equal, older, newer, and future epoch timestamps.
