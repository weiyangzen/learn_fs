# subset-b-005635 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mds_client.c -->
# sources/distributed-fs/ceph-client/fs/ceph/mds_client.c

## Purpose
`mds_client.c` is the main CephFS metadata-server client implementation in the kernel client. It owns MDS session lifetime, request registration and dispatch, MDS reply parsing, request forwarding/replay, cap renewal and release batching, MDS reconnect after failover, map handling, lease and quota message dispatch, mount/unmount synchronization, and authenticated messenger integration. It is the coordination point between VFS metadata operations and the Ceph MDS cluster.

## Important APIs, types, and functions
The file implements public entry points declared in `mds_client.h`: `ceph_mdsc_init`, `ceph_mdsc_destroy`, `ceph_mdsc_create_request`, `ceph_mdsc_submit_request`, `ceph_mdsc_wait_request`, `ceph_mdsc_do_request`, `ceph_mdsc_sync`, `ceph_mdsc_pre_umount`, `ceph_mdsc_close_sessions`, `ceph_mdsc_force_umount`, `ceph_mdsc_handle_mdsmap`, `ceph_mdsc_handle_fsmap`, `ceph_mdsc_build_path`, `ceph_trim_caps`, `ceph_mds_check_access`, `ceph_get_deleg_ino`, and `ceph_restore_deleg_ino`.

Key internal subsystems are reply parsing (`parse_reply_info_*`, `destroy_reply_info`), session management (`register_session`, `__open_session`, `handle_session`, `check_session_state`, `inc_session_sequence`), request dispatch (`__register_request`, `__choose_mds`, `create_request_message`, `__do_request`, `handle_reply`, `handle_forward`), cap release/reclaim (`ceph_send_cap_releases`, `__ceph_queue_cap_release`, `ceph_cap_reclaim_work`, `ceph_cap_unlink_work`), reconnect (`send_mds_reconnect`, `reconnect_caps_cb`, `encode_snap_realms`, `replay_unsafe_requests`), and connection callbacks (`mds_con_ops`).

## Control flow
Metadata operations allocate a `ceph_mds_request` with `ceph_mdsc_create_request`, attach inode/dentry/path arguments, and submit through `ceph_mdsc_submit_request` or `ceph_mdsc_do_request`. Submission pins relevant caps, registers the request in `mdsc->request_tree`, assigns a monotonically increasing `r_tid`, and calls `__do_request`. `__do_request` handles mount state, map availability, request timeout, MDS selection, session registration/opening, feature checks, session wait queues, and actual send.

MDS selection first honors forward hints, then uses dentry hashes, directory frags, auth caps, any available caps, or finally a random active MDS from the MDS map. Sending serializes a `CEPH_MSG_CLIENT_REQUEST` with an MDS request header version selected from peer/session features, encoded paths, cap/dentry release records, caller credentials, gid list, fscrypt alternate names, fscrypt file/auth data, idmapped-mount owner fields when supported, payload pagelists for xattrs, and replay flags when unsafe operations are resent.

Replies arrive through `mds_dispatch` and `handle_reply`. Unsafe replies mark the request unsafe and keep it registered until a later safe reply; safe replies unregister the request and complete safe waiters. Normal replies are parsed, target inodes are resolved or instantiated, snap traces are applied under `snap_rwsem`, and `ceph_fill_trace` plus optional `ceph_readdir_prepopulate` update the local inode/dentry cache. Forward messages update `r_num_fwd`, reset attempts, switch `r_resend_mds`, and resubmit unless the request was aborted or forwarding counts overflow.

Session control messages update session state, feature bits, cap auth rules, blocklist status, TTLs, cap renewal state, force-readonly flags, and waiting request queues. MDS map updates decode a new map, swap it under `mdsc->mutex`, run `check_new_map`, wake map waiters, and schedule delayed maintenance. Map transitions can close dead sessions, reconnect restarted sessions, open export-target sessions, kick stalled requests, and wake caps after recovery.

## State and persistence behavior
All state is runtime kernel memory. `ceph_mds_client` persists for the mount and contains the current MDS map, session array, request RB tree, wait lists, snap realm state, cap flush/release/reclaim queues, dentry lease lists, quota realm cache, pool permissions, MDS cap auth rules, metrics, and subvolume metrics. `ceph_mds_session` persists per MDS rank while the client needs it and tracks state, sequence, connection, auth handshake, feature bits, cap TTL/generation, cap lists, unsafe requests, waiting requests, and delegated inode xarray.

Requests persist until completion or forced teardown; unsafe mutating requests persist past the first reply until safe commit acknowledgement, allowing fsync/sync/umount to wait for metadata durability. Reconnect serializes held caps, wanted/issued cap bits, path bases, file locks, snap follow information, and snap realm versions back to the recovering MDS. There is no local on-disk persistence; durability is delegated to MDS safe replies, mdlog flushes, OSD barriers in cap release messages, and server-side journal semantics.

## Dependencies and integration points
This file sits between VFS-facing CephFS code and lower Ceph infrastructure. It calls inode, dentry, dir, snap, cap, xattr, lock, crypto/fscrypt, quota, subvolume metrics, pool permission, and superblock helpers. It depends on Ceph messenger connections, auth handshakes, monitor map subscriptions, decode/encode helpers, pagelists, tracepoints, workqueues, completions, xarrays, rbtrees, percpu/atomic metrics, and Linux VFS locking. MDS messages handled here include MDS maps, FS maps, session control, replies, forwards, caps, snaps, leases, and quotas.

## Risks and test signals
Important risks are lock-order regressions across `session->s_mutex`, `mdsc->mutex`, `snap_rwsem`, inode cap locks, and dentry locks; request lifetime races between reply, abort, forward, safe reply, and unregister; replay correctness for unsafe rename/create/unlink operations; stale path construction during concurrent rename; MDS feature negotiation mismatches; cap release loss on reconnect; delegated inode reuse; idmapped mount behavior against old MDSs; fscrypt name encoding and no-key readdir paths; and shutdown races with delayed work and messenger callbacks.

Useful test signals include basic metadata operations across single and multi-MDS clusters, MDS failover during unsafe writes/renames, request forwarding due to directory migration, async create/unlink conflict handling, mount with no initial MDS map, clean recover after blocklist, session reject/close/stale/force-ro messages, cap recall and trim pressure, fsync and umount waiting for safe replies, encrypted directory readdir/create, idmapped mount new-inode ops with and without `CEPHFS_FEATURE_HAS_OWNER_UIDGID`, quota and lease message dispatch, and malformed reply/map decode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mds_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mds_client.h -->
# sources/distributed-fs/ceph-client/fs/ceph/mds_client.h

## Purpose
`mds_client.h` defines the public interface and central runtime data structures for the CephFS MDS client. It is included by most CephFS client subsystems that need to create MDS requests, inspect sessions, queue cap releases, handle MDS maps, enforce MDS cap auth rules, wait for async creates, or share MDS-managed metadata state.

## Important APIs, types, and functions
The header defines CephFS feature bits in `enum ceph_feature_type` and the supported feature vector `CEPHFS_FEATURES_CLIENT_SUPPORTED`. These feature bits gate reply encoding, lazy cap wanted behavior, multi reconnect, delegated inodes, metric collection, alternate names, session-state notification, getvxattr, 32-bit retry/forward counters, owner uid/gid support, MDS auth caps checks, and subvolume metrics.

Core wire-parsed reply containers are `ceph_mds_reply_info_in`, `ceph_mds_reply_dir_entry`, `ceph_mds_reply_xattr`, and `ceph_mds_reply_info_parsed`. They hold pointers into MDS reply messages plus allocated fscrypt blobs and readdir buffers. `ceph_mds_session` captures per-rank session state, including connection/auth state, cap generation/TTL, cap lists, dirty/flushing cap lists, wait and unsafe request lists, delegated inode xarray, and refcounting. `ceph_mds_request` captures one in-flight metadata operation, including VFS objects, explicit paths, operation args, flags, credentials, idmap, request/reply messages, reply parse state, timing, unsafe tracking, forwarding/retry state, and cap reservations.

`ceph_mds_client` is the mount-level controller. It holds the active MDS map, sessions, request tree, wait queues, stopping state, dirty folio counters, quota realm cache, snap realm trees/lists, cap delay/flush/reclaim state, cap reservation pool, dentry leases, global metrics, subvolume metrics send tracking, snapid and pool permission caches, MDS cap auth rules, and nodename metadata.

Public functions cover lifecycle (`ceph_mdsc_init`, `ceph_mdsc_destroy`, `ceph_mdsc_close_sessions`, `ceph_mdsc_force_umount`), request handling (`ceph_mdsc_create_request`, `ceph_mdsc_submit_request`, `ceph_mdsc_wait_request`, `ceph_mdsc_do_request`, `ceph_mdsc_release_request`), cap handling (`ceph_flush_session_cap_releases`, `__ceph_queue_cap_release`, `ceph_trim_caps`, `ceph_iterate_session_caps`), path and lease helpers, MDS map handlers, export-target session opening, access checks, and delegated inode helpers.

## Control flow
The header documents the primary lock layering: `session->s_mutex`, then `mdsc->mutex`, then `mdsc->snap_rwsem`, then inode cap locks and snap/cap delay locks. Callers allocate and populate `ceph_mds_request`, submit it to the MDS client, wait or receive callbacks, then drop the kref through `ceph_mdsc_put_request`. Session references use `ceph_get_mds_session` and `ceph_put_mds_session`. Request flags record important lifecycle transitions such as aborted, got unsafe, got safe, got result, parent locked, async, and fscrypt file marshalling.

## State and persistence behavior
The structures describe in-memory state only. Session and request state is persistent for the lifetime of the mount or operation, not across remounts or reboot. The MDS client uses RB trees and lists for deterministic runtime lookup and ordering: request TIDs, quota realm inodes, snap realms, snapid maps, pool permissions, cap queues, unsafe operations, and dentry leases. Durability-related fields such as unsafe request lists, safe completions, cap flush TIDs, and oldest client TID reflect protocol persistence on the MDS side rather than local storage.

## Dependencies and integration points
The header depends on Linux kernel synchronization, krefs/refcounts, rbtree/list/xarray users via included structures, Ceph messenger/auth/types, `mdsmap.h`, `metric.h`, `subvolume_metrics.h`, and `super.h`. It is the shared contract for implementation files such as `mds_client.c`, `caps.c`, `inode.c`, `dir.c`, `file.c`, `quota.c`, `metric.c`, `snap.c`, and debugfs support.

## Risks and test signals
Risks include ABI drift between feature vectors and session-open encoding, misuse of request flags, incorrect kref/session ref pairing, lock-order violations by call sites, stale comments relative to actual lock behavior, and memory ownership mistakes for path buffers, fscrypt blobs, pagelists, credentials, idmaps, dentries, and inodes. Test signals include build coverage across `CONFIG_DEBUG_FS` and fscrypt options, sparse/lockdep runs, request allocation/free fault injection, MDS feature negotiation, multi-MDS session array growth, and lifecycle tests for async requests, cap release queues, quota realm cleanup, and mount shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mds_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mdsmap.c -->
# sources/distributed-fs/ceph-client/fs/ceph/mdsmap.c

## Purpose
`mdsmap.c` decodes CephFS MDS map messages into the kernel client's compact `ceph_mdsmap` representation. It also provides helper behavior for choosing an available MDS, destroying decoded maps, and determining whether the metadata cluster is usable for mounting and request routing.

## Important APIs, types, and functions
The main exported functions are `ceph_mdsmap_get_random_mds`, `ceph_mdsmap_decode`, `ceph_mdsmap_destroy`, and `ceph_mdsmap_is_cluster_available`. Internal helpers include `__mdsmap_get_random_mds`, `__decode_and_drop_compat_set`, and macros that skip unused scalar, set, and map encodings while still validating bounds.

`ceph_mdsmap_decode` fills fields such as map epochs, root rank, session timeout/autoclose, max file size, max xattr size, max MDS count, number of active MDS ranks, possible max rank, per-rank `ceph_mds_info`, data pools, CAS pool, enabled/damaged/laggy status, filesystem name, and export targets.

## Control flow
Map decoding starts by reading the MDS map version and optional length wrapper, then fixed legacy fields. It allocates `m_info` based on the larger of actual active ranks and configured max MDS ranks so transient replacement states can still address higher ranks. For each encoded MDS info item, it decodes global id, rank, incarnation, state, address or address vector, laggy timestamp, and export targets. Only valid positive-state ranks within range are copied into the map.

After active MDS info, the decoder reads data pool ids and skips many server-side fields the kernel client does not need. It still tracks the `in` set to count laggy active ranks and may expand `m_info` to the size of that set. Later encoding versions provide enabled state, filesystem name validation against the mount namespace, damaged ranks, required-client-feature fields to skip, and max xattr size. On success the decode cursor is advanced to the map end; on corruption it logs a hex dump, destroys partial allocations, and returns an error pointer.

Random MDS selection counts ranks with positive state and, on the first pass, excludes laggy ranks. If none are usable, it retries while ignoring laggy status. Cluster availability requires the map to be enabled, not damaged, not entirely laggy, and to contain at least one active rank.

## State and persistence behavior
Decoded maps are heap objects swapped into `mdsc->mdsmap` by `mds_client.c`. They persist until superseded by a newer map or mount teardown, then `ceph_mdsmap_destroy` frees export-target arrays, MDS info, data pools, filesystem name, and the map itself. No map is persisted locally; monitor subscriptions provide fresh maps.

## Dependencies and integration points
This file depends on Ceph decode helpers, messenger address decoding, random number helpers, slab allocation, MDS state string helpers, mount namespace matching, and client logging. It is used by request routing, session opening, metrics sending, cap renewal, reconnect, mount availability checks, and MDS map update handling in `mds_client.c`.

## Risks and test signals
Risks include protocol-version drift, bounds-check mistakes in skipped fields, integer overflow in allocation or skip lengths, accepting invalid ranks or states, filesystem name mismatches causing mount failure, laggy-rank availability edge cases, and export-target decoding errors that would break reconnect during migration/failover. Test signals include decoding old and new map versions, msgr1 and msgr2 address vectors, maps with active ranks above `m_max_mds`, laggy-only maps, damaged maps, disabled filesystems, wrong fs names, empty data-pool lists, export-target reconnect scenarios, and truncated/corrupt map payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mdsmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mdsmap.h -->
# sources/distributed-fs/ceph-client/fs/ceph/mdsmap.h

## Purpose
`mdsmap.h` defines the kernel client's trimmed representation of a CephFS MDS map and exposes small helper APIs used by the MDS client to inspect rank state, addresses, lagginess, data pools, filesystem status, and availability.

## Important APIs, types, and functions
`struct ceph_mds_info` records per-rank runtime data: daemon global id, messenger address, MDS state, export-target count and array, and laggy flag. `struct ceph_mdsmap` records map epochs, root rank, session timers, file and xattr limits, configured and actual active MDS counts, possible max rank, per-rank info, data pool list, CAS pool, enabled/damaged flags, laggy count, and filesystem name.

Inline helpers are `ceph_mdsmap_get_addr`, `ceph_mdsmap_get_state`, and `ceph_mdsmap_is_laggy`. External functions decode and destroy maps, choose a random MDS, and check cluster availability.

## Control flow
The header itself has no executable control flow beyond simple bounds checks. Callers use `ceph_mdsmap_get_state` to convert out-of-range ranks to `CEPH_MDS_STATE_DNE`, and `ceph_mdsmap_get_addr` returns `NULL` when a rank is outside `possible_max_rank`. These helpers keep call sites simpler when sessions outlive map changes or when maps temporarily contain sparse rank states.

## State and persistence behavior
The structures are in-memory snapshots of monitor-provided MDS maps. The map object is owned by `ceph_mds_client`; per-rank `export_targets`, `m_info`, `m_data_pg_pools`, and `m_fs_name` are dynamically allocated by the decoder and released by `ceph_mdsmap_destroy`. There is no persistent local storage.

## Dependencies and integration points
The header depends on Ceph type definitions and MDS state constants. It is included by `mds_client.h`, `mdsmap.c`, and components that need MDS rank status. Fields are consumed by request selection, session opening/reconnect, metric send filtering, max file size propagation, quota/statfs behavior indirectly through the MDS client, and mount availability checks.

## Risks and test signals
Risks include callers using addresses without checking for `NULL`, assuming ranks are dense, failing to handle `CEPH_MDS_STATE_DNE`, or missing that `possible_max_rank` can exceed both active and configured counts during failover. Test signals include sparse-rank maps, rank removal, export-target arrays, laggy state transitions, maps with zero `m_max_xattr_size`, and use under lockdep to ensure callers read the map under the intended MDS client synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mdsmap.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/metric.h -->
# sources/distributed-fs/ceph-client/fs/ceph/metric.h

## Purpose
`metric.h` defines CephFS client metric type identifiers, supported metric bitsets, packed wire structures, in-memory aggregation structures, and small update/scheduling helpers used by the rest of the CephFS client.

## Important APIs, types, and functions
`enum ceph_metric_type` enumerates all advertised metric types, including cap info, read/write/metadata latency, dentry leases, opened files/inodes, pinned caps, read/write sizes, average/stdev metric identifiers, and subvolume metrics. `CEPHFS_METRIC_SPEC_CLIENT_SUPPORTED` is the feature vector encoded in session-open messages.

Packed wire records include `ceph_metric_header`, `ceph_metric_cap`, read/write/metadata latency records, `ceph_metric_dlease`, `ceph_opened_files`, `ceph_pinned_icaps`, `ceph_opened_inodes`, `ceph_read_io_size`, `ceph_write_io_size`, and `ceph_subvolume_metric_entry_wire`. `ceph_metric` is the in-memory aggregate for one operation class, and `ceph_client_metric` is the mount-wide metrics container.

Inline helpers include `metric_schedule_delayed`, `ceph_update_cap_hit`, `ceph_update_cap_mis`, and wrappers for read, write, metadata, and copyfrom metric updates. External functions are `ceph_metric_init`, `ceph_metric_destroy`, and `ceph_update_metrics`.

## Control flow
Call sites update lightweight counters directly with inline helpers, while latency/size updates route through `ceph_update_metrics`. Periodic sending is kicked through `metric_schedule_delayed`, which observes the global `disable_send_metrics` flag before queuing delayed work. The supported metric spec is consumed by `mds_client.c` when constructing the session-open message.

## State and persistence behavior
The header declares runtime-only state shapes. `ceph_client_metric` persists for a mount and owns counters, aggregate arrays, a retained MDS session pointer, and delayed work. The packed wire structures are transient message layouts. Nothing in this header implies local persistence across unmount.

## Dependencies and integration points
It depends on Ceph type definitions, percpu counters, and kernel time types. It is included by `mds_client.h` and by code paths that update metrics. The wire comments for `ceph_subvolume_metric_entry_wire` explicitly tie the layout to the MDS-side C++ `AggregatedIOMetrics` structure, making cross-language ABI compatibility important.

## Risks and test signals
Risks include changing enum order or supported bits without server compatibility, packed-structure layout drift, mismatch between advertised metrics and actual sender behavior, misuse of `disable_send_metrics`, and unsynchronized readers of aggregate fields. Test signals include compile-time size/layout checks where available, session-open metric-spec decoding by old and new MDSs, metrics update call coverage for successful and allowed-error operations, and subvolume metric wire compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/metric.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/quota.c -->
# sources/distributed-fs/ceph-client/fs/ceph/quota.c

## Purpose
`quota.c` implements client-side CephFS quota awareness. It receives quota updates from the MDS, tracks whether quota realms exist, locates quota realm inodes even when they are outside the visible mount subtree, checks max-files and max-bytes limits before creates/writes, compares quota realms for rename/link decisions, and adjusts `statfs` output when the mounted root is governed by a byte quota.

## Important APIs, types, and functions
Public functions are `ceph_adjust_quota_realms_count`, `ceph_handle_quota`, `ceph_cleanup_quotarealms_inodes`, `ceph_quota_is_same_realm`, `ceph_quota_is_max_files_exceeded`, `ceph_quota_is_max_bytes_exceeded`, `ceph_quota_is_max_bytes_approaching`, and `ceph_quota_update_statfs`.

Important internal helpers include `ceph_has_realms_with_quotas`, `find_quotarealm_inode`, `lookup_quotarealm_inode`, `get_quota_realm`, and `check_quota_exceeded`. The file uses `struct ceph_quotarealm_inode` nodes stored in `mdsc->quotarealms_inodes` to cache lookup results and recent lookup failures.

## Control flow
Quota update messages enter through `ceph_handle_quota`. The handler validates message length, finds the target inode by vino, and updates recursive byte/file/subdirectory counts plus max byte/file quotas under the inode's Ceph lock. It uses MDS stopping blockers so teardown does not race the message handler.

Quota checks first call `ceph_has_realms_with_quotas` to avoid expensive snaprealm walks when there are no known quotas and the mount root is the real CephFS root. If quotas may exist, `check_quota_exceeded` walks from the inode's snap realm toward the root under `snap_rwsem`, obtains the realm inode either from `realm->inode` or by temporarily dropping the rwsem and performing an MDS lookup, then checks the requested operation against recursive values and max limits. Max-byte "approaching" returns true when a write would consume more than one sixteenth of remaining quota space, allowing writeback/reporting paths to refresh quota state early.

`get_quota_realm` performs a similar snaprealm walk but returns the first realm with a requested quota type, or the root realm. Because hidden realm inode lookup may drop `snap_rwsem`, callers can request retry or receive `-EAGAIN` and restart atomic multi-realm comparisons. `ceph_quota_is_same_realm` uses that behavior to compare two inodes' quota realms safely. `ceph_quota_update_statfs` finds the root quota realm and rewrites block counts/free counts using quota bytes, including special handling for quotas smaller than the normal block size.

## State and persistence behavior
Quota values are cached in `ceph_inode_info` fields such as recursive bytes/files/subdirs and max bytes/files. `mdsc->quotarealms_count` tracks known quota-bearing realms. `mdsc->quotarealms_inodes` caches hidden quota realm inodes and lookup failure timeouts until unmount; cleanup iputs cached inodes and frees nodes. This is runtime cache state only. Authoritative quota state lives on the MDS and is pushed or fetched as needed.

## Dependencies and integration points
The quota code depends on the MDS client, snap realm locking and reference helpers, inode lookup/getattr helpers, Ceph inode quota helpers (`__ceph_update_quota`, `__ceph_has_quota`), VFS inode and statfs APIs, jiffies timeouts, rbtrees, and MDS stopping blockers. It integrates with create/write paths for limit checks, rename/link logic through realm comparison, statfs reporting, and `mds_client.c` dispatch of `CEPH_MSG_CLIENT_QUOTA`.

## Risks and test signals
Risks include deadlocks or races while dropping and reacquiring `snap_rwsem`, stale hidden realm inode lookup failures due to the fixed 60-second timeout, false negatives when `i_snap_realm` is temporarily null after cap loss, quota overshoot from concurrent clients, overflow in `rvalue + delta`, incorrect statfs scaling for very small quotas, and realm comparison restarts that leak snap realm references. Test signals include quota update messages for visible and hidden inodes, creates at and above max-files, extending/truncating writes around max-bytes, approaching-threshold behavior, renames across quota realms, statfs under root quota smaller than 4 MB and 4 KB, missing realm inode lookup with retry, snap realm parent traversal, unmount cleanup of cached realm inodes, and reserved/stray inode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/quota.c -->
