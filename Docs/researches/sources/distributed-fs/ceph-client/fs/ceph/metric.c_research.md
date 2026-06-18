<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/metric.c -->
# sources/distributed-fs/ceph-client/fs/ceph/metric.c

## Purpose
`metric.c` implements CephFS client metric collection and periodic reporting to an MDS session. It aggregates cap hit/miss counters, dentry lease hit/miss counters, open file/inode counts, read/write/metadata/copyfrom latency and size statistics, and optional subvolume I/O metrics, then serializes them into `CEPH_MSG_CLIENT_METRICS` messages.

## Important APIs, types, and functions
Exported functions are `ceph_metric_init`, `ceph_metric_destroy`, and `ceph_update_metrics`. Important internal helpers are `ceph_mdsc_send_metrics`, `metric_get_session`, `metric_delayed_work`, `ktime_to_ceph_timespec`, subvolume metric length helpers, `ceph_init_subvolume_wire_entry`, `ceph_encode_subvolume_metrics`, and `__update_mean_and_stdev`.

`ceph_mdsc_send_metrics` builds a single metrics message containing cap info, read/write/metadata latency, dentry lease stats, opened files, pinned caps, opened inodes, read/write I/O size totals, and optionally subvolume metric entries. The code tracks the last sent subvolume snapshot and send counters under `mdsc->subvol_metrics_last_mutex`.

## Control flow
Initialization creates percpu counters, resets each `ceph_metric` aggregate, initializes atomic counters, and sets up delayed work. `metric_schedule_delayed` schedules once per second unless metrics are disabled. The delayed worker exits during MDS client stopping, warns once when module-level metric sending is disabled, finds or refreshes a suitable session, sends metrics if possible, and reschedules itself.

Session selection scans registered sessions under `mdsc->mutex`, requiring `check_session_state`, `CEPHFS_FEATURE_METRIC_COLLECT`, and, when subvolume metrics are enabled, `CEPHFS_FEATURE_SUBVOLUME_METRICS`. Sending rechecks that the selected MDS rank is active, optionally snapshots subvolume metrics, allocates a correctly sized Ceph message, fills packed metric records in wire order, appends a special subvolume metric payload without the normal metric header, updates front length/header fields, and sends on the session connection.

Metric updates are called from I/O and metadata paths with start/end timestamps, size, and result code. Negative results other than `-ENOENT` and `-ETIMEDOUT` are ignored. Updates hold the per-metric spinlock, increment total operations, update size sum/min/max, latency sum/min/max, and compute online average and variance accumulator.

## State and persistence behavior
State is runtime-only and lives in `struct ceph_client_metric` inside `ceph_mds_client`: atomics, percpu counters, four `ceph_metric` aggregates, a retained session reference, and delayed work. Subvolume send history is retained in the MDS client for inspection/debugging. Destroy cancels work, destroys counters, and drops the retained session. Metrics are cumulative for the mount lifetime unless the mount is torn down; they are not persisted locally.

## Dependencies and integration points
This file depends on percpu counters, atomics, spinlocks, delayed work, Ceph message allocation/encoding, MDS session feature bits, MDS map state checks, and subvolume metrics tracker APIs. It is integrated with `mds_client.c` session-open feature negotiation and delayed work scheduling, with cap/dentry/inode counters updated elsewhere, and with read/write/metadata paths through inline wrappers in `metric.h`.

## Risks and test signals
Risks include sending to an inactive or feature-incompatible MDS, stale retained session references, delayed work rescheduling during shutdown, inconsistent snapshots because message encoding reads some aggregates without holding their spinlocks, length miscalculation for subvolume payloads, 64-bit to 32-bit subvolume operation clamping, and feature negotiation errors that would disconnect older MDSs. Test signals include metrics disabled/enabled transitions, no eligible session, MDS failover during metrics work, subvolume metrics enabled with mixed-feature MDS sessions, allocation failure, encoded length/front length validation, large counters requiring clamp, and concurrent I/O updating metrics while sends occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/metric.c -->
