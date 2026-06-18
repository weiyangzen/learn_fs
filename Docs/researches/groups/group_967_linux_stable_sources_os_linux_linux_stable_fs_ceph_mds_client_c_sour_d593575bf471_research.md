# Group Research: group_967_linux_stable_sources_os_linux_linux_stable_fs_ceph_mds_client_c_sour_d593575bf471

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux-stable`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/mds_client.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/mds_client.c

## Purpose

`mds_client.c` is the CephFS kernel client's central Metadata Server control plane. It manages MDS sessions, request routing, request encoding/replay, reply parsing, capability renewal/release/reconnect, dentry leases, MDS map updates, fsmap handling, metric-session binding, MDS auth-cap checks, and mount sync/teardown behavior.

## Major Responsibilities

- Parses MDS replies, including versioned inode payloads, directory fragments, leases, readdir entries, create inode delegation, file-lock replies, vxattrs, snap blobs, fscrypt auth/file fields, alternate names, quotas, birth times, change attributes, and subvolume IDs.
- Tracks in-flight metadata requests in `mdsc->request_tree`, assigns tids, manages completion and safe-completion state, aborts timed-out or interrupted requests, and invalidates directory completeness/leases after aborted write namespace operations.
- Chooses an MDS using explicit resend hints, directory fragment authority/replicas, inode caps, or random active MDS fallback.
- Opens, closes, unregisters, reconnects, and periodically renews MDS sessions.
- Encodes session-open metadata including hostname, kernel version, entity id, mount root, supported CephFS feature bits, supported metric spec, flags, and `oldest_client_tid`.
- Builds metadata request messages with path encodings, cap/dentry releases, uid/gid and idmapped-mount handling, fscrypt auth/file data, fscrypt long-name alternate names, retry/forward counters, and optional pagelist payloads.
- Handles unsafe/safe reply sequencing. Unsafe replies populate client cache and mark requests unsafe; safe replies unregister requests and wake umount waiters.
- Handles request forwarding by resetting session state and resending to the forwarded MDS while guarding against retry/forward counter overflow.
- Reconnects after MDS restart by replaying unsafe requests, sending cap reconnect records, encoding file locks and snap realm state, supporting multi-message reconnect when needed.
- Maintains dentry leases by handling revoke/renew messages and sending lease messages back to MDS.
- Handles fsmap and mdsmap messages, updates subscriptions, swaps maps, checks rank state transitions, kicks waiting requests, closes stale sessions, opens export target sessions, and sends reconnects for recovering ranks.
- Provides `ceph_mdsc_sync`, pre-umount flushing, session close, forced unmount, initialization, destruction, and messenger connection callbacks.

## Key Data and Control Flow

- `parse_reply_info*()` decodes on-wire reply fragments into `struct ceph_mds_reply_info_parsed`; memory owned by parsed fscrypt fields and readdir buffers is released in `destroy_reply_info()`.
- `ceph_mdsc_create_request()` creates request objects; `ceph_mdsc_submit_request()` pins relevant caps, registers the request, and calls `__do_request()`.
- `__do_request()` performs mount-state checks, waits for initial maps when needed, chooses an MDS, opens/registers sessions, enforces feature requirements, queues requests behind unopened sessions, or sends them.
- `create_request_message()` is the main request serializer. It handles parent path construction, old-dentry path construction, release encoding, idmapped owner/caller ids, request head version compatibility, and fscrypt fields.
- `handle_reply()` validates session/tid, detects duplicate safe/unsafe replies, parses the reply, creates/gets target inodes, applies snap traces, fills inode/dentry cache, prepopulates readdir, stores reply state, completes waiters, and updates metadata metrics.
- `check_new_map()` compares old/new MDS maps and drives close/reconnect/kick behavior for changed, laggy, stopped, active, or export-target ranks.
- `send_mds_reconnect()` composes reconnect state by replaying requests, flushing caps, walking session caps, encoding snap realms, and sending `CEPH_MSG_CLIENT_RECONNECT`.

## Important Interactions

- Depends on `mds_client.h` for client/session/request data structures.
- Depends on `mdsmap.c/h` for rank state, addresses, laggy checks, map decode, and random MDS selection.
- Calls into caps, inode, dir, snap, super, crypto/fscrypt, messenger, monitor, and metric subsystems.
- Integrates with `quota.c` through `ceph_handle_quota()` dispatch and quotarealm cleanup during pre-umount.
- Integrates with `metric.c` by binding metric collection to sessions that advertise `CEPHFS_FEATURE_METRIC_COLLECT`.

## Concurrency and Lifetime Notes

- `mdsc->mutex` protects sessions, request tree, waiting lists, map swaps, and many high-level client transitions.
- `session->s_mutex` serializes session control processing and reconnect/close/cap-renew operations.
- `session->s_cap_lock`, inode `i_ceph_lock`, `cap_dirty_lock`, `cap_delay_lock`, `snap_rwsem`, dentry locks, and RCU are used for cap/session/inode/dentry/snap coordination.
- Request lifetime uses `kref`; session lifetime uses `refcount_t`.
- Safe teardown flushes messenger work before freeing structures that may still be referenced by dispatch/reply handlers.
- Reconnect code explicitly marks `s_cap_reconnect` so cap removal does not queue stale cap releases while reconnect state is being composed.

## Edge Cases and Compatibility

- Supports legacy and versioned reply/request encodings.
- Handles old MDSes that lack 32-bit retry/forward fields, owner uid/gid support, metric collection, subvolume metrics, or newer session operations.
- Guards retry and forward counter overflow with `-EMULTIHOP`.
- Handles async unlink conflict waits to avoid create/open races with delayed async unlink.
- Handles async create forwarding by moving auth caps between sessions when necessary.
- Has special fscrypt handling for long encrypted names and no-key readdir cases.
- Detects blocklisted sessions from metadata or flags and can trigger clean recovery.
- During sync, flushes dirty caps, cap releases, mdlog, unsafe write requests, and cap flush completions.

## Research Notes

This file is the operational hub for CephFS metadata correctness. The riskiest areas are request message serialization, replay semantics, lock ordering across `mdsc->mutex` and `session->s_mutex`, reconnect pagination, and cache filling after replies. Any changes here need tests or reasoning around MDS feature compatibility, interrupted requests, unsafe/safe reply ordering, and session-map transitions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/mds_client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/mds_client.h -->
# File Research: sources/os/linux/linux-stable/fs/ceph/mds_client.h

## Purpose

`mds_client.h` defines the CephFS MDS client interface, feature negotiation constants, reply parse containers, session state, request state, quota realm tracking, snap/pool/cap client state, and public functions used by the rest of the CephFS kernel client.

## Major Definitions

- `enum ceph_feature_type` lists CephFS session feature bits such as reply encoding, lazy cap wanted, multi reconnect, delegated inode numbers, metric collection, alternate names, vxattr op support, 32-bit retry/forward counters, owner uid/gid, MDS auth-cap checks, and subvolume metrics.
- `CEPHFS_FEATURES_CLIENT_SUPPORTED` defines the client-advertised feature set.
- `struct ceph_mds_cap_match` and `struct ceph_mds_cap_auth` model path/fs/uid/gid/root-squash based MDS auth-cap rules.
- `struct ceph_mds_reply_info_in`, `struct ceph_mds_reply_dir_entry`, and `struct ceph_mds_reply_info_parsed` hold decoded MDS reply data, mostly as pointers into message buffers plus separately allocated fscrypt fields.
- `CEPH_CAPS_PER_RELEASE` calculates cap release batching capacity per page-sized message.
- MDS session states define lifecycle from `NEW` through `OPEN`, `HUNG`, `RESTARTING`, `RECONNECTING`, `CLOSING`, `CLOSED`, and `REJECTED`.
- `struct ceph_mds_session` stores per-rank connection, auth, caps, waiting/unsafe request lists, delegated inode xarray, sequence/feature/ttl state, and cap release work.
- `struct ceph_mds_request` stores request identity, operands, dentries/inodes/paths, cap releases, request/reply messages, parsed reply info, completions, retry/forward state, fscrypt fields, idmap, credentials, and unsafe tracking.
- `struct ceph_mds_client` stores global MDS client state: current mdsmap, sessions, request tree, snap realms, caps, delayed work, dentry leases, metrics, subvolume metrics, snapid map, pool permissions, quotarealm inode cache, auth caps, and shutdown state.
- `struct ceph_path_info` groups path string, length, base vino, and allocation ownership for path builders.

## Exported API Surface

- Session management: lookup/get/put session, session state name, iterate sessions, open export target session.
- Client lifecycle: `ceph_mdsc_init`, `ceph_mdsc_destroy`, close sessions, force umount, pre-umount, sync.
- Request lifecycle: create, submit, wait, do request, release request, invalidate aborted directory request.
- Cap/session helpers: queue cap release, flush session releases, trim caps, reclaim caps, queue unlink work, iterate session caps.
- Lease and path helpers: build paths, free path info, drop dentry lease, send lease message.
- Map handlers: handle MDS map and FS map.
- Quota/async helpers: wait on async create, wait on conflict unlink, delegated inode get/restore.
- Auth access: `ceph_mds_check_access`.

## Concurrency Notes

The header documents key lock ordering expectations: `session->s_mutex` above `mdsc->mutex`, `mdsc->snap_rwsem`, and inode `i_ceph_lock`, with lower locks for snap flush and cap delay. The structs mirror this by separating mutex-protected request/session topology from spinlock-protected cap, dentry lease, snap, and counter lists.

## Research Notes

This header is the contract for the MDS client subsystem. Its structs are large because request/session state spans VFS objects, Ceph wire protocol compatibility, cap lifetime, snap realms, fscrypt, idmapped mounts, and delayed asynchronous work. Changes to field ownership or lock protection here would have broad impact across MDS request handling, caps, quota, metrics, and unmount/reconnect paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/mds_client.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/mdsmap.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/mdsmap.c

## Purpose

`mdsmap.c` decodes CephFS MDS maps and provides helper logic for selecting usable MDS ranks, destroying decoded map state, and determining whether the MDS cluster is available to serve metadata requests.

## Major Responsibilities

- Selects a random ready MDS rank with `ceph_mdsmap_get_random_mds()`, preferring non-laggy ranks first and then retrying while ignoring laggy status if no non-laggy rank is available.
- Provides decode-and-drop macros/helpers for unsupported or unneeded wire fields.
- Decodes versioned MDS map payloads into `struct ceph_mdsmap`.
- Tracks rank state, address, global id, laggy status, export targets, data pools, CAS pool, filesystem name, enabled/damaged state, laggy count, and max xattr size.
- Validates decoded filesystem name against the mount namespace.
- Handles older encodings by assigning `CEPH_OLD_FS_NAME` and disabling newer fs-enabled semantics.
- Frees all dynamic map allocations.
- Reports cluster availability based on enabled state, damaged state, laggy-active count, and at least one active rank.

## Decode Flow

- Reads mdsmap version/compat/length and core fields: epoch, client epoch, last failure, root, session timeout, autoclose, max file size, max mds, and active MDS count.
- Computes `possible_max_rank` from active and configured maximum ranks, then allocates rank info.
- Decodes active MDS info records, including global id, rank, state, address or address vector, laggy timestamp, and export targets.
- Decodes data pools and CAS pool.
- Skips many map sections the kernel client does not need directly: compat sets, metadata pool, timestamps, tableserver, inc/up/failed/stopped sets, snap policy booleans, balancer fields, standby counts, required client features, and rank masks.
- Updates `possible_max_rank` from the `in` rank set and counts laggy ranks.
- Decodes filesystem enabled/name state, damaged set, and max xattr size when present.

## Error Handling

- Allocation failure returns `ERR_PTR(-ENOMEM)`.
- Corrupt or invalid map content prints a hex dump, destroys partial state, and returns an error pointer.
- Some trailing extension decode failures fall through `bad_ext`, set the cursor to `end`, and still return the partially decoded usable map, reflecting forward-compatible skip behavior for optional extension fields.

## Research Notes

This file intentionally decodes only the MDS map fields needed by the kernel client. It is tightly coupled to request routing and session recovery in `mds_client.c`; rank state, laggy status, export targets, session timeout/autoclose, max file size, fs name, and max xattr size directly influence client behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/mdsmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/mdsmap.h -->
# File Research: sources/os/linux/linux-stable/fs/ceph/mdsmap.h

## Purpose

`mdsmap.h` defines the in-memory MDS map structures and helper functions used by the CephFS MDS client.

## Major Definitions

- `struct ceph_mds_info` stores per-rank global id, network address, state, laggy flag, export target count, and export target rank array.
- `struct ceph_mdsmap` stores map epochs, root rank, session timeout/autoclose values, maximum file size, maximum xattr size, max/active rank counts, possible rank range, rank info array, data pools, CAS pool, enabled/damaged state, laggy count, and filesystem name.
- `ceph_mdsmap_get_addr()` returns the rank address or `NULL` if rank is out of range.
- `ceph_mdsmap_get_state()` returns `CEPH_MDS_STATE_DNE` for out-of-range ranks and asserts against negative ranks.
- `ceph_mdsmap_is_laggy()` returns laggy status only for valid ranks.

## Exported API

- `ceph_mdsmap_get_random_mds()`
- `ceph_mdsmap_decode()`
- `ceph_mdsmap_destroy()`
- `ceph_mdsmap_is_cluster_available()`

## Research Notes

This is a compact data contract for `mdsmap.c` and `mds_client.c`. Its fields are only the subset of the full Ceph MDS map that the kernel client needs for routing, recovery, feature limits, and mount availability decisions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/mdsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/metric.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/metric.c

## Purpose

`metric.c` collects and periodically sends CephFS client metrics to an MDS session that supports metric collection. It serializes cap, lease, inode/file, latency, I/O size, metadata, and optional subvolume metrics into `CEPH_MSG_CLIENT_METRICS` messages.

## Major Responsibilities

- Computes encoded lengths for subvolume metrics and serializes subvolume metric snapshots in the MDS-compatible wire format.
- Converts kernel `ktime_t` values to Ceph wire `ceph_timespec`.
- Builds metrics messages containing:
  - cap hit/miss/total counts,
  - read latency,
  - write latency,
  - metadata latency,
  - dentry lease hit/miss/total counts,
  - opened files,
  - pinned icaps,
  - opened inodes,
  - read I/O operation and byte totals,
  - write I/O operation and byte totals,
  - optional subvolume metrics.
- Sends metrics only when the selected MDS rank is active.
- Snapshots subvolume metrics only when both local tracking is enabled and the session advertises `CEPHFS_FEATURE_SUBVOLUME_METRICS`.
- Maintains `mdsc->subvol_metrics_last`, sent counters, and nonzero send counters after successful subvolume metric transmission.
- Finds a suitable metric session by scanning open client sessions that support `CEPHFS_FEATURE_METRIC_COLLECT`.
- Runs delayed metric work once per second unless sending is disabled or the client is stopping.
- Initializes/destroys percpu counters, atomics, metric accumulators, session refs, and delayed work.
- Updates metric totals, min/max, average, and variance-like square sum in `ceph_update_metrics()`.

## Important Behavior

- The worker avoids sending metrics to sessions lacking support because older MDSes may close the socket on unknown metric messages.
- If subvolume metrics are enabled, the worker skips sessions that do not support the subvolume metric feature rather than sending a partially unsupported payload.
- `disable_send_metrics` prevents scheduling and causes the worker to emit a one-time informational message.
- `ceph_update_metrics()` ignores most negative return codes, but counts `-ENOENT` and `-ETIMEDOUT` along with successful operations.

## Concurrency and Lifetime Notes

- Metric counters use atomics, percpu counters, and per-metric spinlocks.
- The delayed worker holds and releases session references through `mdsc->metric.session`.
- Subvolume last-sent snapshot state is protected by `subvol_metrics_last_mutex`.
- Destroy cancels delayed work before tearing down counters and dropping the stored session reference.

## Research Notes

This file is a telemetry adjunct to the MDS client rather than a correctness path for metadata operations. Its compatibility gates are important: metric sending is session-feature negotiated, and subvolume metrics have an additional feature gate.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/metric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/metric.h -->
# File Research: sources/os/linux/linux-stable/fs/ceph/metric.h

## Purpose

`metric.h` defines CephFS client metric types, supported metric bitsets, on-wire metric structures, internal metric counters, and inline update helpers.

## Major Definitions

- `enum ceph_metric_type` enumerates supported metric payload types, including cap info, read/write/metadata latency, dentry lease stats, opened files/inodes, pinned icaps, read/write I/O sizes, average/stdev metric identifiers, and subvolume metrics.
- `CEPHFS_METRIC_SPEC_CLIENT_SUPPORTED` lists metric types advertised during session open.
- `struct ceph_metric_header` is the common packed header for most metric records.
- Packed wire records define cap, latency, lease, opened file, pinned icap, opened inode, and read/write I/O size payloads.
- `struct ceph_subvolume_metric_entry_wire` defines the MDS-compatible subvolume metrics wire layout with 32-bit clamped operation counts and 64-bit byte/latency fields.
- `struct ceph_metric` stores internal totals, size min/max/sum, latency min/max/sum/average/square sum, protected by a spinlock.
- `struct ceph_client_metric` stores global dentry, cap, file, inode, and operation metrics plus the metric session and delayed work.

## Inline Helpers

- `metric_schedule_delayed()` schedules per-second metric work unless metrics sending is disabled.
- `ceph_update_cap_hit()` and `ceph_update_cap_mis()` update cap counters.
- `ceph_update_read_metrics()`, `ceph_update_write_metrics()`, `ceph_update_metadata_metrics()`, and `ceph_update_copyfrom_metrics()` dispatch to `ceph_update_metrics()` with the correct internal metric bucket.

## Research Notes

This header defines the metric wire contract used by `metric.c` and the feature-advertised metric spec encoded by `mds_client.c`. Any wire layout change must remain consistent with the MDS side, especially `ceph_subvolume_metric_entry_wire`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/metric.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/quota.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/quota.c

## Purpose

`quota.c` implements CephFS quota handling in the kernel client. It receives quota updates from MDS, tracks hidden quota realm inodes, checks file and byte quota limits through snap realm ancestry, compares quota realms for rename/link decisions, and adjusts statfs output for mounted roots constrained by quota.

## Major Responsibilities

- Maintains `mdsc->quotarealms_count` with `ceph_adjust_quota_realms_count()`.
- Quickly decides whether quota checks may be needed with `ceph_has_realms_with_quotas()`.
- Handles `CEPH_MSG_CLIENT_QUOTA` messages by finding the target inode and updating recursive bytes/files/subdirs plus max byte/file quota fields.
- Maintains an rb-tree of `struct ceph_quotarealm_inode` for quota realm inodes that are outside the visible mountpoint.
- Looks up hidden quota realm inodes and caches failures for 60 seconds to avoid repeated useless requests.
- Cleans hidden quotarealm inode cache during pre-umount.
- Walks snap realm ancestry to find the nearest realm with relevant quota, optionally dropping and reacquiring `snap_rwsem` to look up hidden realm inodes.
- Compares whether two inodes belong to the same quota realm.
- Checks max-files and max-bytes quota exceedance.
- Checks whether max-bytes quota is approaching, using a threshold of writes consuming more than 1/16 of remaining quota space.
- Updates `statfs` block counts when the mounted root is under a max-bytes quota.

## Key Algorithms

- `get_quota_realm()` starts from an inode's snap realm, walks parents, obtains each realm inode, checks `__ceph_has_quota()`, and returns the first matching realm or the root realm.
- `check_quota_exceeded()` walks the same realm hierarchy and tests each realm's recursive usage against `i_max_files` or `i_max_bytes`.
- `ceph_quota_is_same_realm()` needs two realm lookups under a consistent snap view. If the second lookup has to drop `snap_rwsem`, it returns `-EAGAIN` and restarts.
- `ceph_quota_update_statfs()` converts quota bytes and recursive bytes into reported block/free counts, with special handling for quotas smaller than the normal Ceph block size and smaller than 4 KiB.

## Concurrency and Lifetime Notes

- Uses `mdsc->snap_rwsem` to protect snap realm traversal.
- Temporarily drops `snap_rwsem` around hidden inode lookup when needed, then restarts traversal to avoid stale realm state.
- Uses `realm->inodes_with_caps_lock` to safely access realm inode pointers.
- Uses inode `i_ceph_lock` while reading or updating quota and recursive usage fields.
- Hidden quotarealm inode cache is protected by `quotarealms_inodes_mutex`, with per-entry mutexes for lookup/update serialization.

## Edge Cases

- Snapshotted inodes are treated as not quota-checkable for enforcement paths.
- If `i_snap_realm` is temporarily `NULL` after caps are released, quota checks treat it as no quota found or not exceeded.
- Reserved MDS stray inodes are exempt from quota realm detection.
- If the mount root is not the real CephFS root, the client conservatively assumes quota realms may exist even if the local count is zero.
- Quota usage can exceed quota; statfs reports zero free blocks in that case.

## Research Notes

This file bridges MDS-maintained recursive quota accounting with local VFS decisions. The delicate part is realm traversal under `snap_rwsem` while sometimes needing to perform inode lookups that require dropping that lock.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/quota.c -->