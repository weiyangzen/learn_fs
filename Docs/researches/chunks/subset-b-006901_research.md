# sources/distributed-fs/ceph/src/client/Client.cc lines 1-8769

## Scope and Purpose

This chunk covers the front half of CephFS `Client.cc`, from includes through the beginning of `Client::_do_setattr`. It implements the core user-space CephFS client control plane: client lifecycle, metadata cache population, MDS request/reply routing, MDS session management, capability and lease handling, snapshot realm tracking, mount/unmount, permission checks, path lookup, and the first part of POSIX-style namespace and inode operations.

The code is the bridge between public libcephfs/FUSE-facing operations and distributed Ceph services. Metadata mutations and lookup state are coordinated with MDS daemons through `MetaRequest` and `MClient*` messages. File data caching and writeback are coordinated with `Objecter`, `ObjectCacher`, `ObjecterWriteback`, and `Filer`. Most mutable client structures are protected by `client_lock`, with lifecycle admission controlled by `initialize_state` and `mount_state` `RWRef_t` state machines.

## Important APIs, Types, and Helpers

- `Client` owns the CephFS mount session, including `Messenger`, `MonClient`, `Objecter`, `ObjectCacher`, `Filer`, `MDSMap`, `FSMap`, inode/dentry caches, open file tables, MDS sessions, cap state, snap realms, timers, finishers, and admin socket commands.
- `Client::CommandHook` exposes admin socket commands: `mds_requests`, `mds_sessions`, `dump_cache`, `kick_stale_sessions`, `status`, and subvolume metrics dumping. It takes `client_lock` before calling dump or control helpers.
- `Inode`, `Dentry`, `Dir`, `Fh`, `MetaSession`, `MetaRequest`, `Cap`, `CapSnap`, and `SnapRealm` form the main local metadata model. `inode_map` indexes inodes by `vinodeno_t`; dentries are cached under `Dir`; `lru` tracks trim candidates.
- Faked inode helpers `_reset_faked_inos`, `_assign_faked_ino`, `_assign_faked_root`, `_release_faked_ino`, `_map_faked_ino`, and `map_faked_ino` maintain a local 32-bit-compatible inode namespace when the platform or config requires it.
- Request helpers `make_request`, `choose_target_mds`, `build_client_request`, `send_request`, `verify_reply_trace`, `unregister_request`, and `put_request` implement blocking metadata RPC execution, request replay, forwarding, trace ingestion, and cleanup.
- Cache mutation helpers `add_update_inode`, `insert_dentry_inode`, `insert_readdir_results`, `insert_trace`, `link`, `unlink`, `trim_cache`, `trim_dentry`, and `_try_to_trim_inode` keep local inode/dentry state aligned with MDS replies and revocations.
- Capability helpers `add_update_cap`, `remove_cap`, `check_caps`, `send_cap`, `get_caps`, `put_cap_ref`, `mark_caps_flushing`, `flush_caps_sync`, `wait_sync_caps`, `handle_caps`, and specialized `handle_cap_*` functions implement CephFS client cap protocol.
- Snapshot helpers `get_snap_realm`, `put_snap_realm`, `adjust_realm_parent`, `update_snap_trace`, `handle_snap`, `queue_cap_snap`, `flush_snaps`, and `handle_cap_flushsnap_ack` maintain snapshot contexts and flush per-snapshot dirty metadata.
- Mount and control-plane helpers `authenticate`, `fetch_fsmap`, `resolve_mds`, `mds_command`, `subscribe_mdsmap`, `mount`, `_unmount`, `_close_sessions`, `abort_conn`, and `unmount` coordinate monitor auth/subscriptions, MDS command routing, and lifecycle teardown.
- POSIX-facing helpers in this chunk include `walk`, `path_walk`, `_lookup`, `_do_lookup`, `do_link`, `unlinkat`, `do_rename`, `do_mkdirat`, `mkdirs`, `mknod`, `do_symlinkat`, `readlinkat`, `_getattr`, `_getvxattr`, and the start of `_do_setattr`.

## Control Flow

Initialization starts in `Client::Client`, which reads config, sets supported feature bits, initializes faked inode state, creates `MDSMap`, constructs `ObjecterWriteback`, and configures `ObjectCacher` with `client_flush_set_callback`. `init()` moves `initialize_state` to initializing, calls `_pre_init()` to start timer/objecter finishers/object cache/filer/fscrypt, registers the dispatcher, then `_finish_init()` creates perf counters and admin socket commands.

Mounting is driven by `mount()`. It enters `CLIENT_MOUNTING`, authenticates and subscribes to the selected MDS map, starts the tick thread, optionally waits for MDS availability, rejects mounts while `CEPH_MDSMAP_REFUSE_CLIENT_SESSION` is set, populates client metadata, then walks from the requested mount root toward the root by repeated `GETATTR` requests. Successful traces build `root`, `root_ancestor`, and parent roots. The mount also opens optional trace output and may initialize Linux dummy fscrypt policy before entering `CLIENT_MOUNTED`.

Metadata operations use `make_request()`. It assigns a client TID, records oldest outstanding TID, stores caller permissions, chooses an MDS by `choose_target_mds()`, opens or waits for a `MetaSession`, checks required MDS feature support, sends the `MClientRequest`, then waits on `request->caller_cond` for a reply, forward, or kick. Forward messages update `resend_mds` and retry counters. Replies are processed by `handle_client_reply()`, which validates the session/TID, calls `insert_trace()`, tracks unsafe requests, wakes the caller once, and unregisters the request after a safe reply.

Trace ingestion decodes MDS reply trace buffers. `insert_trace()` optionally updates snap realms, decodes parent and target inode stats, calls `add_update_inode()`, updates dirfrag distribution, links or unlinks dentries, handles traceless mutation replies, and dispatches readdir/lssnap/snapdiff extras to `insert_readdir_results()`. `verify_reply_trace()` repairs the target inode for create/mutation calls that got traceless replies by looking up the dentry or forcing getattr.

MDS maps and sessions are asynchronous message-driven. `ms_dispatch2()` gates all messages on `CLIENT_INITIALIZED`, dispatches MDS/FS/OSD maps, session messages, request forwards/replies, reclaim replies, snaps, caps, leases, commands, and quotas. `handle_mds_map()` ignores old epochs, decodes the new map outside the client lock, cancels commands targeting missing/laggy MDS daemons, swaps the map, reconnects or closes sessions based on rank state and address/incarnation changes, trims cache for reconnect, and wakes map waiters. `handle_client_session()` moves sessions through open, close, renewcaps, stale, recall, flushmsg, force-ro, and reject behavior.

Reconnect is explicit in `send_reconnect()`: trim reconnect-relevant cache, reset session release and cap sequence state, connect export targets, replay unsafe requests, early-kick flushing caps, then build one or more `MClientReconnect` messages containing current caps, wanted masks, file locks, short paths, and snaprealm metadata. After reconnect it wakes mount waiters and reclaim waiters when needed.

The cap flow is state-machine heavy. Grants and revokes update `Cap::issued`, `implemented`, `wanted`, sequence numbers, max size, inode attributes, and waiters. `check_caps()` computes wanted/used/retain sets, handles lazyio substitution, flushes dirty metadata, releases clean cache, delays cap release unless `CHECK_CAPS_NODELAY`, and sends `MClientCaps` updates. Flush acknowledgements remove `flushing_cap_tids`, clear `flushing_caps`, wake sync waiters, and drop dirty-cap inode refs. Cap imports/exports move auth ownership and flushing-list membership between sessions.

Unmount enters `CLIENT_UNMOUNTING`, waits for readers to drain, optionally aborts sessions and OSD writes, waits for write metadata requests, drops cwd/root/open files/open dirs/low-level pins, releases or purges object cache data, flushes caps when not aborting, trims the metadata cache until both LRU and inode map are empty, closes trace output, stops the tick thread, closes sessions, releases the global snap realm, and finally enters `CLIENT_UNMOUNTED`. Abort and blocklist paths purge data and drop dirty caps rather than flushing.

Path operations use `path_walk()`. It starts from root/cwd/supplied directory, checks mount state, optionally checks lookup permissions, wraps names for charmap normalization/casefolding and fscrypt filename encryption, creates or finds local dentries, calls `_lookup()` for cache or MDS lookup, follows symlinks up to `MAXSYMLINKS`, decrypts encrypted symlink targets when fscrypt is active, and returns a `walk_dentry_result` containing parent dir, dentry name, alternate name, dentry, and target.

The chunk ends inside `_do_setattr()`. The visible portion handles permission and auth-cap checks, local dirtying when exclusive caps permit asynchronous setattr, sync fallback preparation through MDS request args, quota and max-file-size checks, fscrypt auth/file metadata constraints, and Linux fscrypt last-block preparation when truncating encrypted files smaller to an unaligned size. The remainder of setattr is outside this chunk.

## State and Persistence Behavior

Persistent filesystem state is owned by the MDS and OSDs; this client maintains a coherent local cache and sends durable updates through metadata requests, cap flushes, mdlog flushes, and object writes.

- `inode_map`, `root`, `cwd`, `root_parents`, `Dir::dentries`, and the LRU are volatile metadata cache. They are updated from MDS traces and invalidated or trimmed on cap/lease changes, reconnect, unmount, and cache-pressure events.
- Inode attributes are only trusted under appropriate caps. `add_update_inode()` and `handle_cap_grant()` update mode, uid/gid, times, size, layout, xattrs, inline data, quotas, dir stats, change attr, fscrypt metadata, and dirfrag maps according to version and cap ownership rules.
- Dirty metadata lives in inode cap state (`dirty_caps`, `flushing_caps`, `flushing_cap_tids`, `dirty_list`). `mark_caps_flushing()` snapshots dirty bits into a flush TID and `handle_cap_flush_ack()` confirms MDS persistence.
- Dirty file data lives in `ObjectCacher::ObjectSet` per inode. `_flush()`, `_flush_range()`, `flush_set_callback()`, and `_flushed()` coordinate writeback and release `FILE_CACHE`/`FILE_BUFFER` cap refs after commit. Full or blocklisted OSD maps cancel writes and purge object sets to avoid deadlock.
- Unsafe metadata mutations are tracked per session and sometimes per inode (`unsafe_requests`, `unsafe_ops`). A safe reply means the MDS journaled the operation; unmount waits for write requests and can flush mdlog for pending operations.
- Snapshot realms are reference-counted in `snap_realms`. Updating a realm invalidates child contexts; new snaps queue `CapSnap` records so dirty metadata/data are flushed under the old snap context before adopting the new one.
- Faked inode mappings are volatile process-local maps from small `ino_t` values to `vinodeno_t`. They are rebuilt on client construction and cleaned when inodes are released.
- `metadata` is sent to MDS session-open and admin/status output. It includes hostname, pid, entity id, mount root, Ceph version/SHA, and configured overrides.

## Dependencies and Integration Points

- Ceph messaging: `Messenger` dispatches `MClientSession`, `MClientReply`, `MClientCaps`, `MClientLease`, `MClientSnap`, `MClientQuota`, `MClientReconnect`, `MClientMetrics`, maps, and command replies.
- Monitor integration: `MonClient` handles authentication and subscriptions for `mdsmap`, `fsmap`, and `fsmap.user`.
- MDS integration: `MDSMap` and `FSMap` drive target selection, command routing, feature negotiation, reconnect, session state, command cancellation, and MDS availability checks.
- OSD/RADOS integration: `Objecter`, `ObjectCacher`, `ObjecterWriteback`, `Filer`, `OSDMap`, and `Striper` provide file data caching, flushing, full-pool detection, blocklist handling, and epoch barriers.
- Kernel/FUSE/libcephfs integration: callbacks for inode invalidation, dentry invalidation, inode release, remount, interrupt/remount finishers, low-level inode refs, and file descriptor maps connect this cache to external consumers.
- Linux-only fscrypt integration: filename wrapping/unwrapping, symlink decryption, file-size rounding, dummy encryption setup, inode lock/key checks, fscrypt auth/file metadata, and encrypted last-block truncation handling.
- Boost locale is used for UTF-8 validation, normalization, and case folding under directory charmap policy.
- Admin socket and perf counters expose debug state, cache dumps, latency averages/square sums, cap/dentry/open-file metrics, and subvolume metrics.
- POSIX ACL helpers are used when `client_acl_type` enables ACL permission checks.

## Risks and Edge Cases

- Locking is delicate. Many helpers assert `client_lock` held, while async callback finishers assert it is not held and re-enter through callback methods. `make_request()` and dispatcher paths use `adopt_lock` waits, so incorrect lock ownership would deadlock or corrupt state.
- Request lifetime is subtle: `make_request()`, `handle_client_reply()`, `unregister_request()`, and `put_request()` coordinate caller and dispatcher via `dispatch_cond`, refcounts, unsafe lists, and request maps. Double replies, stale replies, and forwards are explicitly guarded.
- Reconnect correctness depends on replaying unsafe requests, preserving old requests for clientreplay, resetting cap sequence numbers, and sending matching reconnect/cap-flush messages. Bugs here risk duplicated or lost metadata operations.
- Cap revocation interacts with object cache flushing. If revoking write/buffer/cache caps while data is dirty, the client must flush or purge correctly. OSD full/blocklist paths deliberately set async errors and purge to avoid holding caps forever.
- `handle_cap_export()`/`handle_cap_import()` move auth caps and flushing lists between sessions. Sequence comparisons and peer cap IDs are critical; mistakes can strand dirty caps or lose auth ownership.
- Dentry cache validity combines leases, session cap TTL/generation, directory shared caps, `I_COMPLETE`, and shared generation counters. Rename in-progress dentries force waits to avoid transient double links.
- Directory completion/order flags are aggressively cleared on link/unlink/readdir changes. Incorrect clearing could cause false ENOENT from local cache or unnecessary MDS lookups.
- Snapshot updates must queue cap snaps before adopting new snap contexts. Missing a dirty inode during `update_snap_trace()` could write data under the wrong snapshot context.
- Fscrypt paths have multiple failure modes: invalid UTF-8 under charmap, missing keys (`-ENOKEY`), symlink decryption failures, encrypted filename alternate-name handling, rounded sizes, and last-block preparation during truncate.
- `_schedule_invalidate_dentry_callback()` assumes `dn->inode` is non-null when checking `dn->inode->ll_ref`; callers must not pass negative dentries to this helper.
- The visible `path_walk()` has a shadowed local `trimmed_path` assignment inside `if (trimmed_path == "")`, so debug logging may keep the empty parameter rather than the computed trimmed path. This is diagnostic but may complicate tracing.
- `_do_setattr()` is partially visible only. The visible part already mixes local dirty-cap updates with sync request fallback; downstream code must preserve the mask/inode_drop invariants established here.

## Test Signals

- Mount lifecycle tests should cover successful root walk, named filesystem subscription, missing filesystem, `require_mds` unavailable/transient behavior, `REFUSE_CLIENT_SESSION`, mount timeout injection, dummy fscrypt policy setup, and clean/abort unmount.
- Metadata request tests should exercise forwards, retry overflow to `-EMULTIHOP`, traceless create/mutation reply repair, unsafe then safe replies, stale reply rejection, request abort on blocklist, and MDS feature-gated operations.
- Cache tests should cover inode update precedence under exclusive/shared caps, xattr and inline-data version updates, empty-directory `I_COMPLETE|I_DIR_ORDERED`, readdir hash-order offsets, snapdiff dual-directory insertion, dentry leases, negative dentries, rename waiters, and trim behavior.
- Cap protocol tests should cover grant, revoke, import/export, stale session generation, delayed release, synchronous cap flush, flush ack ordering, max-size request/renewal, lazyio adjustment, readonly sessions, dirty cap cleanup on session removal, and injected release failure.
- Object cache/error tests should cover flush success/failure, full global and per-pool OSD maps, blocklist transitions, cache purge versus release, epoch barrier propagation, and async error reporting.
- Snapshot tests should cover snaprealm parent changes, split handling, child realm invalidation, new-snap cap-snap queuing, dirty-data flushing before snap context change, and flushsnap acknowledgement cleanup.
- Permission/path tests should cover root DAC override rules, POSIX ACL fallback, sticky-dir deletion, hardlink restrictions, auth caps/root squash matching, charmap normalization/casefolding, fscrypt encrypted names and symlinks, symlink loops, `.`/`..`, snapdir visibility, long names, and path-walk no-target behavior for create.
- Admin and observability tests should verify admin socket command registration/unregistration, JSON dump shape for status/cache/sessions/requests, latency average/square-sum counters, metric message feature filtering, and subvolume metric add/remove behavior.

## Chunk Boundary Notes

This report intentionally covers only lines 1-8769 of `Client.cc`. Later code continues `_do_setattr()` and implements additional POSIX operations, file I/O, xattrs, locks, delegations, reclaim, and low-level APIs. Any whole-file synthesis should merge this with later chunk reports before drawing final conclusions about complete setattr/file-data behavior.
