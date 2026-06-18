# Research: sources/distributed-fs/ceph-client/fs/ceph/debugfs.c

## Purpose

`debugfs.c` exposes runtime CephFS client state through Linux debugfs when `CONFIG_DEBUG_FS` is enabled. It is an observability and tuning file, not part of the data path. It publishes MDS map details, outstanding MDS requests, cap ownership and waiters, MDS sessions, mount status, client metrics, session feature negotiation, and subvolume metric snapshots. It also exposes a writable `writeback_congestion_kb` debugfs attribute backed by the mount option.

When debugfs is disabled, the file compiles to empty `ceph_fs_debugfs_init()` and `ceph_fs_debugfs_cleanup()` stubs, preserving callers without adding runtime artifacts.

## Important APIs, Types, and Functions

- `struct ceph_session_feature_desc` and `ceph_session_feature_table[]` map CephFS session feature bit numbers to stable human-readable names. `metric_features_show()` uses this table to explain which negotiated MDS features are active.
- `mdsmap_show()` prints `ceph_mdsmap` epoch, root, max MDS count, session timeout/autoclose settings, and per-rank address/state.
- `mdsc_show()` walks `mdsc->request_tree` under `mdsc->mutex` and prints each in-flight `ceph_mds_request`, including tid, target session, op name, unsafe status, and inode/dentry/path context.
- `metrics_file_show()`, `metrics_latency_show()`, `metrics_size_show()`, and `metrics_caps_show()` expose counters from `struct ceph_client_metric`, including inode/open-file/cap counts, latency distributions, byte distributions, dentry lease hits/misses, and cap hits/misses.
- `caps_show()` reports global cap reservation status via `ceph_reservation_status()`, iterates per-session inode caps with `ceph_iterate_session_caps()`, and dumps `mdsc->cap_wait_list`.
- `mds_sessions_show()` prints auth global id, mount auth name, and each MDS session state.
- `status_show()` prints the client entity instance, client address/nonce, and blocklist state.
- `subvolume_metrics_show()` snapshots `mdsc->subvol_metrics_last` under `subvol_metrics_last_mutex`, then dumps pending metrics through `ceph_subvolume_metrics_dump()`.
- `metric_features_show()` evaluates whether client metric sending and subvolume metrics are enabled from module state, active metric session state, and negotiated feature bits.
- `congestion_kb_get()` and `congestion_kb_set()` back a debugfs simple attribute that reads/writes `fsc->mount_options->congestion_kb`.
- `ceph_fs_debugfs_init()` creates the debugfs files/directories and stores dentries in `struct ceph_fs_client`; `ceph_fs_debugfs_cleanup()` removes them.

## Control Flow

Initialization starts in `ceph_fs_debugfs_init()`. It creates `writeback_congestion_kb`, a `bdi` symlink, top-level files (`mdsmap`, `mds_sessions`, `mdsc`, `caps`, `status`), a `metrics` directory, and metric files under it (`file`, `latency`, `size`, `caps`, `metric_features`, `subvolumes`). Each read-only debugfs file is wired through `DEFINE_SHOW_ATTRIBUTE`, so opening the file invokes the matching `*_show()` seq_file callback with `fsc` in `s->private`.

Most show paths follow a snapshot pattern: take the narrow lock needed for the state being displayed, copy or read scalar values, drop the lock, and format the result into `seq_file`. `mdsc_show()` holds `mdsc->mutex` while walking the MDS request tree, but temporarily calls path-building helpers for dentries and uses dentry locks when printing names. `caps_show()` avoids holding `mdsc->mutex` while iterating one session's caps by taking a session reference, dropping the MDS client mutex, locking `session->s_mutex`, iterating caps, then reacquiring the MDS client mutex. `subvolume_metrics_show()` explicitly duplicates the last-sent metric array before formatting it so the output path does not hold the snapshot mutex during seq output.

Cleanup is direct and idempotent from the caller perspective: `ceph_fs_debugfs_cleanup()` removes individual files and recursively removes the `metrics` directory. The debugfs API tolerates missing dentries, so partial creation failures during init do not require complicated rollback here.

## State and Persistence Behavior

This file does not persist data to disk or to the Ceph cluster. It exposes volatile kernel-client state:

- MDS map and session state come from `fsc->mdsc`.
- Metrics come from counters, atomics, and spinlock-protected `struct ceph_metric` fields.
- Subvolume metrics come from `mdsc->subvol_metrics_last`, send counters, and pending aggregation state.
- Cap reporting reads live cap structures and cap waiter lists.
- `writeback_congestion_kb` mutates the in-memory mount option and affects writeback congestion behavior for the mounted client.

The output is best-effort diagnostic data. It can race with ongoing MDS transitions, cap changes, request completion, and metrics updates, but the show paths use the same mutexes/spinlocks expected by the owning subsystems to avoid torn list traversal and unsafe dereferences.

## Dependencies and Integration Points

- Linux debugfs and seq_file APIs provide file creation and read formatting.
- Ceph MDS client internals provide request trees, session lookup, cap iteration, cap waiter lists, MDS maps, and metric state.
- Ceph auth and mon client state supply `global_id`, auth mount name, and client entity identity.
- `metric.h` supplies metric counters, latency/size state, and `disable_send_metrics`.
- `subvolume_metrics.h` supplies pending and last-sent subvolume metric dumps.
- `super.h` supplies `struct ceph_fs_client`, mount options, debugfs dentries, and client accessors.

The exported integration surface is only `ceph_fs_debugfs_init()` and `ceph_fs_debugfs_cleanup()`, which are called from mount/client setup and teardown code. The rest of the functions are static show helpers bound to debugfs file operations.

## Risks and Edge Cases

- Debugfs output depends on live mutable state. A reader can see a consistent-enough snapshot but not a transactionally consistent view across MDS map, sessions, caps, and metrics.
- `mdsc_show()` path rendering may fail; it degrades to an empty path string rather than failing the debugfs read.
- `metric_features_show()` reports no active metrics if there is no active `mdsc->metric.session`; this can be a transient state during mount, reconnect, or teardown.
- `subvolume_metrics_show()` can fail to allocate the snapshot copy; it reports no last-sent entries but still prints aggregate send counters and pending metrics.
- The writable congestion attribute accepts any `u64` and casts it to `int`; validation is minimal because this is a debugfs control.
- Feature names must be kept in sync with feature bit definitions in `mds_client.h`; missing names do not break negotiation but reduce diagnosability.

## Test Signals

Useful validation signals include:

- With `CONFIG_DEBUG_FS=y`, mounting CephFS should create the expected files under the client's debugfs directory and remove them cleanly on unmount.
- Reading `mdsmap`, `mdsc`, `caps`, and `mds_sessions` during active metadata operations should not warn, deadlock, or dereference freed sessions/requests.
- `metrics/latency`, `metrics/size`, and `metrics/caps` should reflect read/write/metadata/copy activity after workloads.
- `metrics/metric_features` should change with negotiated session features and `disable_send_metrics`.
- `metrics/subvolumes` should show last-sent and pending subvolume metrics after subvolume I/O when the feature is negotiated.
- Writing and rereading `writeback_congestion_kb` should update `fsc->mount_options->congestion_kb`.
- A debugfs-disabled kernel should still link callers through the empty init/cleanup stubs.
