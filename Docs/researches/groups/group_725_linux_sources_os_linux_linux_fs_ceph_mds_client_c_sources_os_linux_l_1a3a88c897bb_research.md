# Group Research: group_725_linux_sources_os_linux_linux_fs_ceph_mds_client_c_sources_os_linux_l_1a3a88c897bb

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`. This grouped report covers the requested CephFS MDS client, MDS map, metrics, and quota files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/mds_client.c -->
# File Research: sources/os/linux/linux/fs/ceph/mds_client.c

Implements the CephFS kernel client’s Metadata Server client: MDS sessions, metadata requests, replies, reconnect/replay, leases, caps renewal/release, MDS map handling, and messenger connection callbacks.

Key behavior:
- Parses MDS replies for inode traces, directory fragments, leases, readdir entries, file locks, create delegated inode numbers, vxattr values, snap blobs, quotas, pool namespaces, fscrypt metadata, subvolume IDs, and versioned encodings.
- Maintains per-MDS sessions with states from new/opening/open/hung/restarting/reconnecting/closing/closed/rejected.
- Registers sessions lazily, opens them with client metadata, supported CephFS feature bits, metric specs, and oldest client TID.
- Chooses target MDS ranks using resend hints, directory frag hashes, auth caps, replica distribution, laggy-state filtering, or random active MDS fallback.
- Tracks in-flight MDS requests in an rb-tree keyed by TID, assigns credentials/idmap context, reserves caps, and links unsafe directory operations for fsync/safe-reply tracking.
- Builds wire requests with path encoding, snap path bases, fscrypt alternate names, cap/dentry release records, gid lists, fscrypt auth/file fields, replay flags, retry/forward counters, async flags, and idmapped owner UID/GID fields when supported.
- Handles synchronous request submission/wait as well as aborts on timeout, signal, shutdown, fenced I/O, unavailable maps, unsupported MDS features, or rejected sessions.
- Handles unsafe and safe replies separately: unsafe replies fill caches and complete the caller, while safe replies unregister the request and complete safe waiters.
- Processes reply traces through `ceph_fill_trace()` and readdir results through `ceph_readdir_prepopulate()`, with snap trace updates serialized by `snap_rwsem`.
- Handles request forwarding by updating resend MDS and forward sequence, while detecting overflow/multihop loops.
- Sends periodic cap renewal, keepalive, cap release, flushmsg ack, and mdlog flush messages.
- Batches cap releases into `CEPH_MSG_CLIENT_CAPRELEASE` messages with an OSD epoch barrier.
- Trims caps on MDS recall by dropping unused caps or pruning aliases/dentries under memory pressure.
- Replays unsafe requests and old requests during MDS reconnect, and sends reconnect payloads containing caps, paths, locks, snaprealm information, and snap-follow sequence data.
- Supports delegated inode numbers on 64-bit builds via an xarray, while 32-bit builds ignore delegated ranges.
- Reacts to MDS map changes by closing removed sessions, reconnecting restarted sessions, kicking requests when ranks become active, opening export target sessions, and handling laggy ranks.
- Handles session control messages, including open, renewcaps, close, stale, recall-state, flushmsg, force-readonly, reject, blocklist detection, MDS auth caps, metrics enablement, and subvolume metrics enablement.
- Handles dentry lease revoke/renew messages and sends lease revoke acknowledgements.
- Handles FS map selection for named CephFS mounts and MDS map decoding/swapping.
- Provides mount sync, pre-umount, force-umount, close-session, and destroy paths that flush dirty caps, wait for unsafe metadata operations, clean quota realm inodes, and tear down sessions.
- Implements local MDS auth-cap access checks by matching current credentials, fs name, mount path, auth path, readable/writeable bits, and root-squash policy.
- Provides messenger connection operations for dispatch, allocation, peer reset, session refcounting, auth handshake, authorizer invalidation, message signing, and signature verification.

Important interactions:
- Central coordinator for `caps.c`, `dir.c`, `inode.c`, `snap.c`, `quota.c`, `metric.c`, `mdsmap.c`, `crypto.c`, and the Ceph messenger/auth layers.
- Uses `struct ceph_mds_client`, `struct ceph_mds_session`, and `struct ceph_mds_request` from `mds_client.h`.
- Uses `ceph_mdsmap_decode()` and map helper state from `mdsmap.c`.
- Updates metadata latency through `ceph_update_metadata_metrics()` and binds metric collection sessions when MDS supports metric collection.
- Dispatches quota messages to `ceph_handle_quota()`.
- Relies on careful lock ordering among `session->s_mutex`, `mdsc->mutex`, `snap_rwsem`, inode cap locks, cap dirty locks, and dentry locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/mds_client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/mds_client.h -->
# File Research: sources/os/linux/linux/fs/ceph/mds_client.h

Defines the CephFS MDS client’s public internal contract: feature bits, reply parse structures, session state, request state, quota helpers, path info, and MDS client-global state.

Key behavior:
- Defines CephFS feature IDs supported by the kernel client, including reply encoding, lazy cap wanted, multi reconnect, delegated inode numbers, metric collection, alternate names, vxattr op, 32-bit retry/forward counters, owner uid/gid, MDS auth caps, and subvolume metrics.
- Documents core lock ordering used by the MDS client and cap/snap paths.
- Defines MDS auth-cap match structures for uid/gid/path/fs-name/root-squash matching and readable/writeable permissions.
- Defines parsed reply structures for inode data, directory entries, xattrs, file locks, readdir extras, create inode results, and snap blobs.
- Defines `CEPH_CAPS_PER_RELEASE`, accounting for cap release message header and trailing OSD epoch barrier.
- Defines MDS session states and `struct ceph_mds_session`, including connection, auth handshake, cap lists, cap release work, dirty/flushing cap lists, renewal state, waiting/unsafe requests, and delegated inode xarray.
- Defines MDS selection modes: any, random, or authoritative.
- Defines `struct ceph_mds_request`, including request target objects, paths, parent/old dentry information, flags, request args, fscrypt fields, credentials/idmap, drop/release caps, wire messages, reply parse state, completions, unsafe tracking, retry/forward state, delegated ino, and cap reservation.
- Defines `struct ceph_mds_client`, the global MDS client state: map, sessions, request tree, snap realms, quota realm cache, cap pools, delayed work, metrics, subvolume metrics, pool permissions, auth caps, and nodename.
- Provides prototypes for request lifecycle, session iteration, cap release/reclaim work, sync/umount paths, mdsmap/fsmap handling, leases, delegated inode handling, access checks, and path building/freeing.
- Provides inline request ref helpers, async-create wait helper, and `ceph_mdsc_free_path_info()`.

Important interactions:
- Included by most CephFS source files that touch metadata operations, sessions, caps, quotas, metrics, or MDS maps.
- Bridges `mds_client.c` with `mdsmap.h`, `metric.h`, `subvolume_metrics.h`, and `super.h`.
- The structs here are the shared memory layout for MDS reply parsing and request construction.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/mds_client.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/mdsmap.c -->
# File Research: sources/os/linux/linux/fs/ceph/mdsmap.c

Implements decoding, selection, destruction, and availability checks for CephFS MDS maps.

Key behavior:
- `ceph_mdsmap_get_random_mds()` chooses a random ready MDS rank, preferring non-laggy ranks and falling back to laggy ready ranks if needed.
- Decodes only map fields the kernel client needs, while safely skipping or dropping many compatibility, metadata, failure, standby, balancer, and feature fields.
- Handles versioned MDS map and MDS info encodings, including address-vector decoding for newer info versions.
- Extracts epoch, client epoch, last failure, root, session timeout, session autoclose, max file size, max MDS, active rank count, data pools, CAS pool, fs name, damaged state, laggy count, and max xattr size.
- Computes `possible_max_rank` from active rank count, max MDS, and later the `in` set.
- Populates per-rank `ceph_mds_info` entries for valid ranks with positive state, global ID, address, laggy flag, and export target list.
- Validates decoded fs name against the mount namespace option for newer maps; older maps use `CEPH_OLD_FS_NAME`.
- Treats damaged maps, disabled maps, fully laggy active sets, or no active ranks as unavailable.
- Frees all export target arrays, data pool arrays, fs name, and the map itself in `ceph_mdsmap_destroy()`.

Important interactions:
- Used by `mds_client.c` when processing `CEPH_MSG_MDS_MAP`.
- Supplies MDS state, laggy-state, address, random-rank, and cluster-availability data for request routing and session recovery.
- Depends on Ceph messenger address decoding and mount namespace matching from Ceph common/super code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/mdsmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/mdsmap.h -->
# File Research: sources/os/linux/linux/fs/ceph/mdsmap.h

Declares the reduced CephFS MDS map representation used by the kernel client.

Key behavior:
- Defines `struct ceph_mds_info` with global ID, entity address, state, export target count/list, and laggy flag.
- Defines `struct ceph_mdsmap` with epochs, root, session timeouts, max file/xattr sizes, max/active/possible ranks, per-rank info, data pools, CAS pool, enabled/damaged/laggy state, and fs name.
- Provides inline helpers:
  - `ceph_mdsmap_get_addr()` returns a rank address or NULL if out of range.
  - `ceph_mdsmap_get_state()` returns rank state or `CEPH_MDS_STATE_DNE` if out of range.
  - `ceph_mdsmap_is_laggy()` checks rank laggy state.
- Declares random MDS selection, decoding, destruction, and cluster-availability helpers.

Important interactions:
- Shared by `mds_client.c` and `mdsmap.c`.
- Keeps the kernel-side map intentionally smaller than the full on-wire MDS map by storing only client-relevant fields.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/mdsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/metric.c -->
# File Research: sources/os/linux/linux/fs/ceph/metric.c

Implements CephFS client metric collection, encoding, delayed sending, and latency/stat aggregation.

Key behavior:
- Encodes subvolume metric snapshots in a versioned on-wire format compatible with the MDS/FUSE client expectation, with operation counts clamped to u32 and byte/latency counters preserved as u64.
- Sends `CEPH_MSG_CLIENT_METRICS` only to active MDS sessions that advertise metric collection support.
- Includes metrics for cap hits/misses/total caps, read latency, write latency, metadata latency, dentry lease hits/misses, opened files, pinned icaps, opened inodes, read I/O sizes, and write I/O sizes.
- Optionally includes subvolume metrics when the local tracker is enabled and the target session supports `CEPHFS_FEATURE_SUBVOLUME_METRICS`.
- Saves the last sent subvolume metric snapshot and send counters under `subvol_metrics_last_mutex`.
- Finds an eligible MDS session for metric sending, skipping sessions without metric support and skipping non-subvolume-capable sessions when subvolume metrics are enabled.
- Delayed metric work exits during MDS client stopping, respects the global `disable_send_metrics` module parameter, warns if no eligible session exists, and reschedules once per second.
- Initializes percpu counters, atomic counters, per-metric locks, min/max/average/stdev accumulator fields, and delayed work.
- Destroys delayed work and all percpu counters, and drops the held metric session reference.
- Updates metric aggregates for successful operations and selected negative results (`-ENOENT`, `-ETIMEDOUT`) using running mean and squared-sum variance accumulation.

Important interactions:
- Bound to an MDS session by `mds_client.c` when session open features include metric collection.
- Uses `struct ceph_client_metric` and wire structs from `metric.h`.
- Reads total caps, dentry/inode counters, and operation latency data maintained by other CephFS paths.
- Integrates subvolume metrics through `subvolume_metrics` tracker helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/metric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/metric.h -->
# File Research: sources/os/linux/linux/fs/ceph/metric.h

Defines CephFS client metric IDs, on-wire metric records, aggregate counters, and update helpers.

Key behavior:
- Declares `disable_send_metrics`.
- Enumerates client metric types for caps, read/write/metadata latency, dentry leases, opened files/inodes, pinned caps, I/O sizes, average/stdev variants, and subvolume metrics.
- Defines `CEPHFS_METRIC_SPEC_CLIENT_SUPPORTED`, ordered so the maximum metric bit remains last.
- Defines packed wire structures for each metric item and the metric message head.
- Defines `ceph_subvolume_metric_entry_wire`, the MDS-facing subvolume I/O metric format, plus an older internal tracking struct.
- Defines aggregate metric categories: read, write, metadata, copyfrom, and max.
- Defines `struct ceph_metric` with total count, size sum/min/max, latency sum/avg/squared-sum/min/max, and a spinlock.
- Defines `struct ceph_client_metric` with dentries, caps, operation metrics, opened file/inode counters, selected MDS session, and delayed work.
- Provides `metric_schedule_delayed()`, which schedules one-second delayed work unless metrics sending is disabled.
- Provides inline cap hit/miss increment helpers.
- Provides inline read/write/metadata/copyfrom metric update wrappers around `ceph_update_metrics()`.

Important interactions:
- Used by `metric.c` for encoding/sending and by other CephFS I/O/metadata paths for accounting.
- Embedded in `struct ceph_mds_client` from `mds_client.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/metric.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/quota.c -->
# File Research: sources/os/linux/linux/fs/ceph/quota.c

Implements CephFS quota handling, quota realm discovery, quota checks, hidden realm inode lookup, and statfs quota reporting.

Key behavior:
- Maintains `mdsc->quotarealms_count` when inodes gain or lose max-bytes/max-files quota state.
- Quickly decides whether quota checks may be needed based on known quota realm count, whether the mount root is the real CephFS root, and whether the inode is reserved/stray.
- Handles MDS quota messages by finding the target inode and updating recursive bytes/files/subdirs plus max bytes/files under the inode Ceph lock.
- Maintains an rb-tree of `ceph_quotarealm_inode` entries for quota realm inodes not visible from the current mountpoint.
- Looks up hidden quota realm inodes by ino, caches successful inodes, retries getattr when cached inodes exist but lack caps, and throttles failed lookups for 60 seconds.
- Cleans all cached quota realm inode records during MDS client pre-umount.
- Walks an inode’s snaprealm ancestry to find the nearest realm with the requested quota type, returning the root realm if no quota is found before root.
- Temporarily drops and reacquires `snap_rwsem` when hidden realm inode lookup is required; callers can request restart behavior with the `retry` argument.
- Compares whether two inodes belong to the same quota realm, restarting if snap realm lookup had to drop `snap_rwsem`.
- Checks max-files quota for new file creation by walking realm ancestors and testing recursive file/subdir usage plus one.
- Checks max-bytes quota for writes by comparing new file growth against recursive bytes usage.
- Checks max-bytes “approaching” threshold when a write would consume more than 1/16 of remaining quota space, using reported size as the baseline.
- Updates `statfs` output for a mounted root with max-bytes quota, converting quota bytes to block counts, handling quotas smaller than 4 MiB with 4 KiB block sizing, and reporting zero free space when exceeded.

Important interactions:
- Called from `mds_client.c` on `CEPH_MSG_CLIENT_QUOTA`.
- Uses quota helpers and declarations in `super.h`, including `__ceph_has_quota()` and `__ceph_update_quota()`.
- Depends on snaprealm state maintained by `snap.c` and protected by `mdsc->snap_rwsem`.
- Used by create/write/statfs paths to enforce or report CephFS quota limits.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/quota.c -->