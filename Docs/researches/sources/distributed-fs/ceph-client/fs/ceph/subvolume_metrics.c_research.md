# sources/distributed-fs/ceph-client/fs/ceph/subvolume_metrics.c

## Purpose
`subvolume_metrics.c` tracks per-subvolume CephFS read/write operation counts, byte counts, and aggregate latency, then exposes snapshots for metric transmission or debugfs dumping.

## Important APIs, Types, And Functions
The private rb-tree node is `struct ceph_subvol_metric_rb_entry`. Public APIs include `ceph_subvolume_metrics_init()`, `destroy()`, `enable()`, `record()`, `snapshot()`, `free_snapshot()`, `dump()`, `record_io()`, and cache init/destroy helpers. The slab cache is `ceph_subvol_metric_entry_cachep`.

## Control Flow
Record paths first reject disabled trackers, unknown subvolume IDs, zero bytes, or zero latency. On a miss, allocation happens outside the spinlock and insertion is retried to handle races. Snapshot first counts active entries, allocates an output array, copies active metrics under lock, and optionally consumes entries by zeroing/removing them. Debug dump formats live rb-tree entries directly.

## State, Persistence, And Dependencies
State lives in `struct ceph_subvolume_metrics_tracker`: a cached rb-tree, entry count, enabled flag, spinlock, and atomic debug counters. It is volatile and reset when disabled or destroyed. Dependencies include rb-tree APIs, slab allocation, `ktime`, `seq_file`, and Ceph inode subvolume IDs.

## Integration Points
`record_io()` is called from data IO paths with a `ceph_mds_client` and `ceph_inode_info`; snapshots are consumed by MDS metric reporting, and dump output appears in debugfs through CephFS debug plumbing. Cache init/destroy is wired through Ceph module cache setup.

## Risks
Potential risks include high-cardinality subvolume IDs growing the rb-tree, allocation failure dropping metrics, snapshot count races causing partial results, and lock hold time during debug `seq_printf()`. Metrics are best-effort and should not affect IO correctness.

## Test Signals
Test disabled/enabled transitions, concurrent records for the same/new IDs, consume and non-consume snapshots, zero/unknown filtering, allocation-failure paths, debugfs formatting, and cache teardown after active entries are cleared.
