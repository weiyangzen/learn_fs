# sources/distributed-fs/ceph-client/fs/ceph/subvolume_metrics.h

## Purpose
`subvolume_metrics.h` declares the CephFS per-subvolume metrics interface and the tracker/snapshot data structures used by IO paths, MDS metric reporting, and debugfs.

## Important APIs, Types, And Functions
It defines `struct ceph_subvol_metric_snapshot` with per-subvolume read/write counters and latency sums, and `struct ceph_subvolume_metrics_tracker` with lock, rb-tree, enable flag, and debug/cumulative atomics. It declares init, destroy, enable, record, snapshot, free, dump, record-IO, and slab-cache lifecycle functions plus inline `ceph_subvolume_metrics_enabled()`.

## Control Flow
The header itself has only the inline enabled check via `READ_ONCE()`. Callers initialize a tracker, enable collection when supported, record IO events, periodically snapshot/free arrays, and destroy the tracker during MDS client teardown.

## State, Persistence, And Dependencies
All state is in the tracker embedded elsewhere, not global to the header. It depends on Linux types, rb-tree, spinlock, ktime, atomics, `seq_file`, and forward declarations for Ceph MDS/inode types.

## Integration Points
The tracker is embedded in `struct ceph_mds_client` and used by data IO instrumentation, metric scheduling, and debugfs dumps. Cache lifecycle hooks are called from Ceph module initialization and exit.

## Risks
Callers must respect the lock ownership encoded by the implementation and must not inspect rb-tree internals without the lock. `enabled` is readable locklessly, so implementation paths must recheck it under lock before mutating state.

## Test Signals
Compile coverage across configurations, sparse/lockdep checks, and integration tests that enable/disable metrics and verify snapshot contents are enough to validate the public contract.
