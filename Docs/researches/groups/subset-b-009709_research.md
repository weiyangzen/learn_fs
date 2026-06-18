# subset-b-009709 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs.c

## Purpose

`recovery_fs.c` implements the legacy filesystem-backed NFSv4 recovery backend for nfs-ganesha. It persists confirmed client IDs, NFSv4 reclaim-complete markers, and revoked delegation file handles in a directory tree under configured recovery root directories so a restarted server can enter grace, rebuild the reclaim allowlist, and reject `DELEG_PREV` reclaims for already revoked delegations.

## Important APIs, types, and functions

- Global storage paths: `v4_recov_dir`, `v4_recov_dir_len`, `v4_old_dir`, and `v4_old_dir_len` are shared with filesystem recovery variants through `recovery_fs.h`.
- `fs_create_recov_dir()` creates the configured recovery root, current directory, old directory, and optional clustered `node%d` subdirectories. It populates the global path buffers and returns negative errno-style failures.
- `fs_add_clid()` creates a persistent directory path for a confirmed client. It calls `fs_create_clid_name()` to build `cid_recov_tag`, then splits long names into `NAME_MAX` path segments.
- `fs_reclaim_complete()` records an OP_RECLAIM_COMPLETE marker by creating a `reclaim_complete` file under the final client directory.
- `fs_rm_clid()` and recursive helper `fs_rm_clid_impl()` remove the client directory hierarchy and embedded files for normal client destruction/expiry.
- `fs_read_recov_clids_takeover()` is the backend read hook. It handles cold restart with no `nfs_grace_start_t`, IP takeover, nodeid takeover, and update-client events.
- `fs_read_recov_clids_impl()` recursively reconstructs split client names, validates their `<IP>-(len:value)` format, calls `add_clid_entry()`, copies revoked file handles, and optionally moves entries into the old directory.
- `fs_clean_old_recov_dir_impl()` recursively deletes old recovery trees after grace.
- `fs_add_revoke_fh()` base64url-encodes an NFS file handle and persists it as a file prefixed by byte `0x01` under the client directory.
- `fs_backend` wires these functions into `struct nfs4_recovery_backend`.

## Control flow

Initialization builds current and old recovery paths from `nfs_param.nfsv4_param.recov_root`, `recov_dir`, and `recov_old_dir`. If `recovery_backend_ipbased` is disabled and clustering is active, it appends `/node%d`; if IP-based recovery is enabled, per-IP directories are formed later with `fs_make_ip_recov_dir_name()`.

When a client becomes persistent, `fs_add_clid()` derives a name from the server/client address and opaque client owner value. Printable opaque values without slashes are copied directly; other values are rendered as opaque bytes. The name is wrapped with an explicit length field and split into nested directories so filesystem `NAME_MAX` is not exceeded.

On restart, `fs_read_recov_clids_recover()` first reads the old directory, then reads current and moves/copies entries into old. The recursive read helper treats a directory leaf whose reconstructed name validates as one client entry. It checks for the reclaim marker, adds the client to the in-memory reclaim list, imports revoke files through `add_rfh_entry()`, and deletes current entries when not in takeover mode. During takeover, it reads the failed peer's path but leaves source records in place.

At end of grace, `fs_clean_old_recov_dir()` removes old entries recursively. Client removal performs a recursive postorder traversal, deletes revoke files and reclaim markers at the leaf, and removes directories up the tree.

## State and persistence behavior

The persistent format is directory-oriented. A client is represented by one path whose segment concatenation is the client recovery tag. Revoked delegation handles are regular files below that path whose names begin with `0x01` followed by base64url file-handle text. OP_RECLAIM_COMPLETE is represented by a regular file named `reclaim_complete`.

The backend uses two directories: current records for active clients and old records for the previous boot/grace epoch. Current records are copied/moved into old during recovery so a restart during grace can still recover clients. IP-based mode adds per-server-address recovery directories, while clustered node mode adds node-specific subdirectories.

## Dependencies and integration points

The file depends on SAL/NFS recovery hooks (`add_clid_entry_hook`, `add_rfh_entry_hook`, `nfs_grace_start_t`), client structures (`nfs_client_id_t`, `nfs_client_record_t`), path configuration in `nfs_param`, global cluster node id `g_nodeid`, display helpers, `bsd-base64`, and FSAL file-handle conversion indirectly through revocation consumers. It integrates with the generic NFSv4 recovery layer through `fs_backend_init()` and with delegation revocation through `nfs4_record_revoke()` callers that invoke `.add_revoke_fh`.

## Risks and edge cases

- Several paths depend on `struct dirent.d_type`; filesystems that return `DT_UNKNOWN` may be skipped or logged as unknown.
- The client recovery tag parser uses `atoi()` and manual substring checks; malformed directory trees are ignored but still can accumulate until cleanup.
- Long path handling is defensive, but recursive allocation and `PATH_MAX` assumptions remain central to correctness.
- IP-based removal has a branch that logs an expired v4.1 client path but does not remove it, which looks intentional or unfinished and should be reviewed with IP takeover semantics.
- `fs_add_revoke_fh()` asserts that `cid_recov_tag` is present and the base64 encode succeeds; unexpected call ordering becomes process-fatal in assert-enabled builds.
- Non-atomic directory moves/cleanup mean crash windows are mitigated by current/old directories but not eliminated.

## Test signals

Useful tests should cover restart with current-only records, restart with old records, crash during grace, long client owner strings split across several `NAME_MAX` components, malformed recovery directories, reclaim-complete marker presence/absence, revoke file import and deletion, IP-based recovery naming, clustered node directories, and end-grace cleanup. Integration tests should verify `add_clid_entry()` receives the expected `reclaim_complete` boolean and revoked handle strings.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs.h -->
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs.h

## Purpose

`recovery_fs.h` exposes the reusable pieces of the filesystem recovery backend needed by newer filesystem variants. It is intentionally small: it exports current recovery path state and helper operations from `recovery_fs.c`.

## Important APIs, types, and functions

- `extern char v4_recov_dir[PATH_MAX]` and `extern unsigned int v4_recov_dir_len` expose the active recovery directory buffer and length.
- `fs_add_clid()`, `fs_rm_clid()`, and `fs_add_revoke_fh()` allow another backend to reuse legacy client directory creation/removal and revoked-handle persistence.
- `fs_clean_old_recov_dir_impl()` exposes recursive cleanup for arbitrary recovery directory roots.

## Control flow

There is no control flow in the header beyond include guarding. Its main effect is coupling `recovery_fs_ng.c` to `recovery_fs.c`: fs-ng implements a new directory-lifetime strategy but reuses the legacy record layout and per-client operations.

## State and persistence behavior

The header surfaces `v4_recov_dir` and `v4_recov_dir_len`, so callers must ensure those globals refer to the desired active directory before invoking shared helpers. For fs-ng, this means the global current directory points at the newly created temp directory rather than the stable symlink target.

## Dependencies and integration points

The declarations depend on `PATH_MAX`, `nfs_client_id_t`, and `nfs_fh4` being visible through including translation units. It integrates the old and new filesystem recovery backends by sharing the on-disk client-record format.

## Risks and edge cases

The global path exports make ordering important: if a backend calls `fs_add_clid()` before initializing `v4_recov_dir` correctly, records go to the wrong location. The header also exposes implementation details rather than an opaque context, which limits parallel use of multiple filesystem recovery instances.

## Test signals

Build coverage should ensure both `recovery_fs.c` and `recovery_fs_ng.c` can include the header in their expected include order. Runtime testing should verify fs-ng writes client directories under its temp active directory via these legacy helpers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs_ng.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs_ng.c

## Purpose

`recovery_fs_ng.c` implements a newer filesystem recovery backend that keeps the legacy per-client directory record format but changes how recovery epochs are managed. Instead of maintaining separate current and old directories directly, it creates a fresh temp directory for this boot and swaps a stable host/node symlink to the new directory at end of grace.

## Important APIs, types, and functions

- `v4_recov_link` is the stable symlink path, usually `<recov_root>/<recov_dir>/<hostname>` or `node%d`.
- `legacy_fs_db_migrate()` detects an old backend directory at the link path, renames it to a temp sibling, and replaces it with a symlink so fs-ng can recover legacy state.
- `fs_ng_create_recov_dir()` creates root/base directories, derives host or node id, creates a fresh `mkdtemp()` active directory, updates `v4_recov_dir`, and runs migration.
- `fs_ng_read_recov_clids_impl()` recursively reads the symlink target directory and reconstructs legacy client tags.
- `fs_ng_read_recov_clids()` is the backend read hook. Normal local recovery is implemented; takeover code is currently compiled out behind `#ifndef FIXME` early return.
- `fs_ng_swap_recov_dir()` atomically installs a temporary symlink pointing at the new active directory and removes the old real directory after the rename.
- `fs_ng_backend` reuses `fs_add_clid()`, `fs_rm_clid()`, and `fs_add_revoke_fh()` from the legacy filesystem backend.

## Control flow

Initialization creates `<root>/<recov_dir>`, chooses a stable identity from `g_nodeid` or `gethostname()`, builds `v4_recov_link`, and creates `v4_recov_dir` as `<link>.XXXXXX` via `mkdtemp()`. The legacy migration step runs after the new temp directory exists so an old directory at the stable link path can be renamed and linked without losing recoverable state.

During normal restart, `fs_ng_read_recov_clids_recover()` reads `v4_recov_link`, not the fresh active directory, because the link points to the previous epoch's durable records. It reconstructs client names with the same `<IP>-(len:value)` validation used by the legacy backend and adds each valid leaf with `reclaim_complete=true`.

At end of grace, `fs_ng_swap_recov_dir()` captures the old realpath, creates `<link>.tmp` pointing to `basename(v4_recov_dir)`, renames the temporary symlink over `v4_recov_link`, and then recursively deletes the old target directory.

## State and persistence behavior

The stable durable state is a symlink whose target is a generation directory. Active records for the current process are written to the fresh temp directory through reused `fs_add_clid()` helpers. The symlink is not updated until grace ends, so crashes during grace leave the previous generation visible for the next process.

Revoked handle and client directory formats remain identical to `recovery_fs.c`, but this reader does not import revoke handle files despite accepting an `add_rfh_entry` hook; it currently only adds client entries.

## Dependencies and integration points

The backend depends on `recovery_fs.h` for shared globals and record helpers, POSIX `mkdtemp`, `symlink`, `rename`, `realpath`, and `basename`, and the generic recovery backend table. It integrates with existing filesystem record generation while changing the epoch switch primitive to symlink replacement.

## Risks and edge cases

- Takeover support is effectively disabled by an unconditional `return` in the `gsp` path. Cluster/failover operators need a different backend or completed implementation.
- `legacy_fs_db_migrate()` is explicitly non-atomic; a crash between rename and symlink creation can strand old records.
- `fs_ng_read_recov_clids_impl()` ignores revoke files and always marks clients reclaim-complete, which differs from legacy marker semantics.
- Symlink cleanup depends on `realpath(v4_recov_link)` before replacement. If the link is missing or invalid, old generation cleanup is skipped.
- Reused legacy helpers depend on `v4_recov_dir` pointing to the temp generation, so initialization order is critical.

## Test signals

Test symlink swap atomicity, restart before end grace, restart after end grace, migration from a legacy directory, missing/broken symlink behavior, host and node naming, long client path reconstruction, and the disabled takeover path. Tests should confirm that new client records are written to the temp directory and become visible only after `end_grace`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs_ng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados.h -->
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados.h

## Purpose

`recovery_rados.h` is the shared interface for Ceph RADOS-backed NFSv4 recovery backends. It defines common limits, configuration structures, global RADOS handles/object names, callback argument shapes, key/value helpers, and backend functions used by the kv, ng, and clustered variants.

## Important APIs, types, and functions

- `RADOS_KEY_MAX_LEN` is 21 bytes for a decimal `uint64_t` clientid plus NUL.
- `RADOS_VAL_MAX_LEN` is `PATH_MAX`, used for the client-name plus revoked-handle string.
- `rados_recov_io_ctx`, `rados_recov_oid`, and `rados_recov_old_oid` are shared RADOS IO and object-name state.
- `struct rados_kv_parameter` holds `ceph_conf`, `userid`, `pool`, `namespace`, `grace_oid`, and optional `nodeid`.
- `struct pop_args` bundles `add_clid_entry`, `add_rfh_entry`, and flags describing old/takeover traversal.
- `rados_kv_create_key()` formats `clientid->cid_clientid` into the decimal key.
- The header declares shared KV operations, node-id setup, value creation, traversal callbacks, revoked-handle update, and `takeover_reclaim_reset()`.

## Control flow

The header establishes a common key/value contract: backends derive a RADOS object name, use decimal client IDs as omap keys, and store client identity plus revoked file handles as values. Traversal functions call a backend-specific `pop_clid_entry_t` to repopulate the recovery list.

## State and persistence behavior

Persistent RADOS state is omap data in one or more RADOS objects. Non-clustered kv uses current and old object names; ng uses one object and a grace-period write operation; clustered recovery names objects by grace epoch and node/IP identity. `gsh_refstr` object-name pointers are shared with RCU protection in implementations.

## Dependencies and integration points

This header depends on librados types, `gsh_refstr`, NFS client structures, and recovery hooks from SAL. It is included by all RADOS recovery backend implementations and provides the public entry points that clustered code uses to call lower-level kv helpers.

## Risks and edge cases

The header exposes mutable global state, so backend mixing requires careful one-backend-at-a-time assumptions. `rados_kv_create_key()` asserts the buffer size exactly, making misuse fail fast. Value-size constraints are implicit and callers must avoid appending revoked handles past `PATH_MAX`.

## Test signals

Compile tests should cover all RADOS backend combinations. Unit-level tests can validate key formatting at `UINT64_MAX`, node-id string selection, value limits, and traversal callback argument behavior. Integration tests should check each backend's object naming aligns with the declarations here.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_cluster.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_cluster.c

## Purpose

`recovery_rados_cluster.c` implements the clustered RADOS recovery backend. It coordinates cluster-wide NFSv4 grace epochs through the rados-grace object, creates epoch-scoped recovery omap objects, handles node/IP takeover, and can start local grace when another cluster member triggers a new global grace period.

## Important APIs, types, and functions

- Static state: `takeover`, `object_takeover`, `object_takeover_old`, `object_ipbased`, `rados_watch_cookie`, `addr_int`, and global epoch values `cur` and `rec`.
- `rados_cluster_init()` sets node id, configures optional IP-based identity, connects to RADOS, verifies grace membership, and installs a watch on the grace object.
- `rados_grace_watchcb()` acknowledges RADOS notifications and wakes grace waiters/reaper.
- `rados_cluster_read_clids()` joins grace, creates the current epoch recovery object, chooses the old/takeover object, and traverses reclaim clients with `rados_ng_pop_clid_entry()`.
- `rados_cluster_add_clid()` and `rados_cluster_rm_clid()` write/remove clients in the current epoch object or per-client IP-based object.
- `rados_cluster_end_grace()` turns off enforcing in rados-grace and removes the old/takeover recovery object.
- `rados_cluster_maybe_start_grace()` detects remote grace epochs, snapshots current confirmed clients into a new object, and calls `nfs_start_grace()`.
- `rados_cluster_try_lift_grace()`, `rados_cluster_set_enforcing()`, `rados_cluster_grace_enforcing()`, and `rados_cluster_is_member()` wrap rados-grace state transitions/checks.
- `rados_cluster_backend` exposes the full clustered backend hook table.

## Control flow

Initialization calls shared `set_nodeid()`, optionally converts `g_node_vip` to an integer `ip_%d` identity, connects to RADOS, verifies this node is in the grace table, and starts watching `rados_kv_param.grace_oid`. Watch callbacks do not process records directly; they wake existing NFS grace/reaper mechanisms.

On recovery read, the backend optionally configures takeover target names from `nfs_grace_start_t`. It then calls `rados_grace_join()` to enter or join a grace period and receives current and recovery epochs. It creates a new current object named `rec-%16.16lx:<identity>` for `cur`, clears its omap, and sets `rados_recov_oid`. It then traverses the previous epoch object for `rec`, either for this node/IP or the takeover identity, and populates in-memory recovery clients.

When the local server observes that a remote grace period is already active, `rados_cluster_maybe_start_grace()` creates a new current object and snapshots all currently confirmed clients into it. This allows the local server to participate in the new grace without losing active clients.

End grace disables enforcing for this node and deletes the old recovery object. Shutdown starts/join grace to protect clean shutdown windows, unwatches the grace object, shuts down RADOS, and frees node state.

## State and persistence behavior

Recovery client records live in RADOS omap objects whose names include the grace epoch and identity. The clustered grace object tracks membership and epochs separately through the rados-grace library. IP-based recovery can use object names based on an integer form of the VIP or per-client server address hash, while normal mode uses hostname or `node%d`.

The backend uses RCU-protected `gsh_refstr` object names because add/remove operations may run concurrently with epoch switches. Values are the shared RADOS KV format parsed by `rados_ng_pop_clid_entry()`.

## Dependencies and integration points

The file depends on librados, `rados_grace.h`, shared RADOS KV helpers, global client hash `ht_confirmed_client_id`, NFS grace APIs (`nfs_start_grace`, `nfs_notify_grace_waiters`, `reaper_wake`), and optional FSAL reclaim hook `nfs_recovery_fsal_reclaim_client()` for Ceph nodeid takeover. It integrates with SAL through `struct nfs4_recovery_backend`.

## Risks and edge cases

- `rados_set_client_cb()` has a fixed 1024-entry cap and logs rather than resizing, so large client populations can be incompletely snapshotted during remote grace.
- IPv6 conversion uses the lower 32 bits of the address for integer identity; collisions are possible.
- IP-based object naming differs between init/takeover (`ip_%d`) and per-client add/remove (`rec-epoch:ip_<hash>`), so tests must verify intended semantics.
- Error handling often logs and continues, which can leave grace joined but object creation/traversal incomplete.
- Shutdown intentionally joins grace; failures there are logged but cannot guarantee external MDS/session protection.
- RCU pointer exchange and reference handling are central; missed refs could lead to stale object-name use during epoch transitions.

## Test signals

Cluster tests should cover join/lift grace, grace enforcement on/off, notification watch callbacks, local restart recovery, nodeid takeover, IP takeover, remote grace start with confirmed clients, object cleanup after grace, membership loss, and >1024 clients. Fault injection should cover RADOS connection failures, object create/remove failures, rados-grace API failures, and concurrent add/remove during epoch changes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_cluster.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_kv.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_kv.c

## Purpose

`recovery_rados_kv.c` implements the base RADOS key/value recovery backend and shared utility layer used by other RADOS backends. It persists each NFSv4 client as a RADOS omap key/value entry, supports current/old object recovery, appends revoked delegation handles into values, parses RADOS-specific config, and manages the librados connection.

## Important APIs, types, and functions

- Globals: `clnt`, `rados_recov_io_ctx`, `rados_recov_oid`, `rados_recov_old_oid`, `node_id`, `nodeid`, and `rados_kv_param`.
- Config: `rados_kv_params` and `rados_kv_param_blk` define `RADOS_KV` block parsing.
- `rados_kv_create_val()` builds the persistent client value `<client_addr>-(len:client-string)`.
- `rados_kv_put()`, `rados_kv_get()`, `rados_kv_del()`, and `rados_kv_traverse()` perform omap mutation, lookup, deletion, and paged traversal.
- `rados_kv_connect()` creates/configures/connects a librados client, creates the pool if needed, creates an ioctx, and sets namespace.
- `set_nodeid()` chooses `nodeid` from `g_nodeid`, config `nodeid`, or hostname, prepending `node` for numeric ids.
- `rados_kv_init()` creates current `<nodeid>_recov` and old `<nodeid>_old` objects and installs refcounted object names.
- `rados_kv_add_clid_impl()`/`rados_kv_rm_clid_impl()` implement object-specific add/remove, with public wrappers using current object.
- `rados_kv_pop_clid_entry()` parses values, imports revoked file handles, moves current entries to old during recovery, and deletes processed records when not takeover.
- `rados_kv_read_recov_clids_takeover()` handles normal recovery and IP takeover object traversal.
- `rados_kv_cleanup_old()` clears the old object at end grace.
- `rados_kv_add_revoke_fh()` reads a client value, appends `#<base64url-fh>`, and writes it back.

## Control flow

Initialization sets node identity, builds current and old object names, connects to Ceph, and creates both objects if absent. Add/remove operations use `rados_kv_create_key()` to map the numeric `cid_clientid` to a decimal key and store the generated value in the current object.

Normal recovery reads old first with `old=true`, then current with `old=false`. Each omap entry is parsed into a client reclaim entry; non-old entries are copied into the old object before deletion from current. This mirrors the legacy filesystem current-to-old recovery epoch behavior.

Takeover builds an object name from `gsp->ipaddr` plus `_recov` and traverses it with `takeover=true`, which imports entries without deleting them. End grace clears old object omap state.

Revoked delegation persistence is value-based: the backend reads the existing value, appends a `#` separator and base64url file handle, and writes the full value back.

## State and persistence behavior

The persistent model is RADOS object omap. Keys are decimal client IDs. Values are NUL-terminated strings containing client identity and optional revoked file-handle fragments separated by `#`. Current and old objects implement crash recovery across grace epochs.

RADOS object-name pointers are `gsh_refstr` values published through RCU. `rados_kv_shutdown()` destroys the ioctx/client and swaps out `rados_recov_oid`, but `rados_recov_old_oid` is not explicitly swapped in shutdown in this file, so lifetime review should include all backend combinations.

## Dependencies and integration points

The file depends on librados, `rados_grace.h` for defaults, `bsd-base64`, config parsing, client manager types, RCU, and generic recovery hooks. Other backends call its config, connection, traversal, node-id, value, and revoked-handle helpers.

## Risks and edge cases

- `rados_kv_get()` copies `val_len_out + 1` into caller storage without a size argument, relying on internal `RADOS_VAL_MAX_LEN` discipline.
- `rados_kv_append_val_rdfh()` uses `strncat()` with remaining buffer calculations but does not explicitly report truncation when too many revoked handles accumulate.
- `rados_kv_pop_clid_entry()` calls `strtok(rfh_names, "#")` even when `rfh_names` can be `NULL`, which is safe for `strtok(NULL, ...)` continuation semantics only if a previous tokenization state is suitable; this deserves scrutiny because it intends to parse an optional second token.
- `set_nodeid()` allocates `nodeid` each call and some error paths do not free it locally.
- Pool creation during connect may be inappropriate for deployments where the pool must be pre-created with specific settings.
- Takeover is limited to IP-derived object naming in this backend.

## Test signals

Tests should cover config parsing, node-id selection, object creation, add/remove/get traversal, old/current recovery movement, takeover traversal, revoked-handle append and import, values at `PATH_MAX`, missing keys, RADOS operation failures, namespaces, and shutdown lifetime. Fuzz tests for value parsing should include no `#`, one revoked handle, multiple handles, empty values, and malformed client strings.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_kv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_ng.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_ng.c

## Purpose

`recovery_rados_ng.c` implements a safer RADOS recovery backend that avoids mutating durable recovery state during grace. It batches all client additions/removals into a pending RADOS write operation while grace is active and commits the clear-plus-updates transaction only when grace ends.

## Important APIs, types, and functions

- Static state: `grace_op` stores the batched write operation and `grace_op_lock` protects it.
- Global flags: `takeover`, `no_cleanup`, and `object_takeover` track takeover mode and cleanup safety.
- `rados_ng_init()` sets node id, creates `<nodeid>_recov`, connects to RADOS, and creates the recovery object.
- `rados_ng_put()` and `rados_ng_del()` either append omap set/remove operations to `grace_op` or perform immediate synchronous writes outside grace.
- `rados_ng_add_clid()` and `rados_ng_rm_clid()` are backend add/remove hooks.
- `rados_ng_pop_clid_entry()` parses the shared value format and imports clients/revoked handles.
- `rados_ng_read_recov_clids_takeover()` reads local or takeover recovery objects.
- `rados_ng_cleanup_old()` creates a `grace_op` with `omap_clear`, commits it to the local/takeover object, releases it, and exits grace mutation batching.
- `rados_ng_backend` exposes the backend hooks and reuses `rados_kv_add_revoke_fh()` and `rados_kv_get_nodeid()`.

## Control flow

Initialization sets a single current recovery object for the node and creates it if needed. On recovery read with no `gsp`, it traverses that object and imports clients. On takeover, it builds either `<ipaddr>_recov` or `node%d_recov`, traverses the selected object, and sets `takeover=true`.

At the grace boundary, `rados_ng_cleanup_old()` allocates `grace_op`, first adding an `omap_clear`. While `grace_op` is non-null, client add/remove calls only append operations to it and return success without RADOS I/O. `rados_ng_cleanup_old()` then operates the write op against the selected recovery object, atomically clearing old records and applying the spooled mutations, releases the op, and sets `grace_op=NULL`. After that, add/remove operations create their own write op and commit synchronously.

## State and persistence behavior

Unlike `rados_kv.c`, this backend has no separate old object. The existing object remains unchanged during grace, preserving crash recovery information. End grace atomically replaces object omap contents through one write op. Values and keys use the shared RADOS KV format.

`grace_op` is process-local state, protected by a mutex. Persistent object names are stored in shared `rados_recov_oid`.

## Dependencies and integration points

The file depends on shared RADOS KV helpers for config/connection/key/value/traversal/revoked-handle behavior, librados write operations, RCU object-name access, and generic recovery backend hooks. It integrates with the same SAL recovery interface as legacy kv but changes the grace commit model.

## Risks and edge cases

- `rados_ng_pop_clid_entry()` uses `strtok(rfh_names, "#")` after `rfh_names = strtok(NULL, "#")`; optional revoked-handle parsing needs null-safety review.
- `no_cleanup` logs and resets but does not return early, so cleanup may still proceed after an object-name setup failure.
- A large grace-period client churn can accumulate a large in-memory RADOS write op.
- `rados_ng_cleanup()` destroys the mutex but does not release a live `grace_op`; lifecycle must ensure end-grace ran or no op exists.
- Reusing `rados_kv_add_revoke_fh()` during grace can perform immediate read-modify-write outside the batched operation, which is a possible semantic mismatch for the safe-by-design model.

## Test signals

Tests should simulate crash before end grace, successful end-grace transaction, add/remove during and after grace, takeover object selection, RADOS write failures, revoked-handle updates during grace, and concurrent add/remove calls. Persistence tests should verify old records remain visible until `end_grace` commits.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_ng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/sal_metrics.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/sal_metrics.c

## Purpose

`sal_metrics.c` registers and updates monitoring metrics for selected SAL client, lock, session, transport, and lease events. It is a thin instrumentation layer around the repository's monitoring API.

## Important APIs, types, and functions

- Metric handles include gauges for confirmed clients and lock counts, counters for lease expiry, client state protection, denied xprt associations, and xprt custom-data status, plus histograms for session connections and sessions per xprt.
- `sal_metrics__init()` registers every metric and must run before update functions.
- Update functions include `sal_metrics__confirmed_clients()`, `sal_metrics__lease_expire()`, `sal_metrics__client_state_protection()`, `sal_metrics__locks_inc()`, `sal_metrics__locks_dec()`, `sal_metrics__session_connections()`, `sal_metrics__xprt_association_denied()`, `sal_metrics__xprt_custom_data_status()`, and `sal_metrics__xprt_sessions()`.
- Label conversion helpers map `xprt_custom_data_status_t` and `state_protect_how4` enums to stable label strings and `LogFatal()` on unsupported values.

## Control flow

Initialization registers groups of metrics: client metrics first, then session connection histogram, denied association counter, xprt status counters, and xprt session histogram. Counter metrics with enum labels are registered once per enum value. Runtime update functions directly call `monitoring__*` primitives with the already stored handles.

## State and persistence behavior

All state is in process-local metric handles and static bucket arrays. The file does not persist data itself; persistence/export is delegated to the monitoring subsystem. Gauges track current values where callers provide increments/decrements or absolute count; counters are monotonic; histograms observe samples.

## Dependencies and integration points

The file depends on `sal_metrics.h`, common utilities for `ARRAY_SIZE`, `nfs_convert.h` for enum definitions, and the monitoring API macros/types. It is called from client/session/xprt/lock lifecycle paths elsewhere in SAL and NFSv4.

## Risks and edge cases

- Update functions assume `sal_metrics__init()` ran and handles are valid.
- Enum conversion helpers fail fatally for out-of-range values, which catches programming errors but can make unexpected input process-fatal.
- `sal_metrics__client_state_protection()` and xprt status updates index arrays directly by enum value; enum count/order changes must update counts and conversion logic together.
- Lock gauges rely on balanced inc/dec calls in other modules.

## Test signals

Tests should validate metric registration names, labels, bucket boundaries, enum label coverage, and update calls. Integration tests can assert lock gauge balance, confirmed-client gauge updates, session/xprt histogram observations, and fatal behavior for invalid enum values in debug/fault-injection builds.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/sal_metrics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_async.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/state_async.c

## Purpose

`state_async.c` manages SAL asynchronous execution for state operations, especially blocked NLM/NFS lock callbacks, lock cancellation, and periodic blocked-lock polling. It wraps fridgethr worker pools so state code can schedule operations outside request threads while preserving the necessary export/op context.

## Important APIs, types, and functions

- Global fridges: `state_async_fridge` handles one-off async work; `state_poll_fridge` is a looper for blocked lock polling.
- `state_async_schedule()` schedules a generic `state_async_queue_t` callback through `state_async_func_caller()`.
- `state_block_schedule()` schedules `process_blocked_lock_upcall()` for a blocked lock.
- `state_block_cancel_schedule()` schedules `state_cancel_blocked()`.
- `test_blocking_lock_eligibility_schedule()` schedules `state_test()` plus optional grant callback and updates last poll time.
- `state_async_init()` creates both fridges and starts `blocked_lock_polling`.
- `state_async_shutdown()` stops both fridges with a 120-second timeout and cancels on timeout.

## Control flow

For blocked lock grant and eligibility callbacks, the worker retrieves the saved export from the lock entry, checks `export_ready()`, obtains an export ref, initializes a root request op context, locks the file state with `STATELOCK_lock()`, and invokes the lock processing function. It then unlocks, decrements the lock entry reference, and releases op context.

Cancellation follows a similar export-context setup and calls `state_cancel_blocked()` without taking the state lock in this wrapper. The generic async scheduler simply invokes the function pointer stored in `state_async_queue_t`.

Initialization creates a deferred one-thread async queue and a one-thread looper whose delay comes from `nfs_param.core_param.blocked_lock_poller_interval`.

## State and persistence behavior

The module maintains no persistent state. It holds process-global thread-pool pointers and manipulates references on lock entries and exports. Polling updates `sbd_v4.snbd_last_poll_time` for blocked lock data.

## Dependencies and integration points

It depends on fridgethr, export manager functions, op-context helpers, state lock APIs, lock testing/cancellation helpers, `blocked_lock_polling`, and `nfs_param`. It is initialized/shutdown with SAL state subsystem lifecycle and used by lock conflict paths to notify or poll blocked clients.

## Risks and edge cases

- `state_blocked_lock_cancel()` logs critical and returns without decrementing the lock-entry reference if the export is not ready, which can leak a reference unless upstream prevents this state.
- `state_async_init()` does not tear down `state_async_fridge` if `state_poll_fridge` init or polling submit fails.
- Single-threaded queues serialize all state async work; long callbacks can delay lock notifications.
- Workers rely on saved export pointers remaining valid enough for `export_ready()`/ref acquisition.
- Shutdown returns error if either fridge stop times out or fails; callers must tolerate partial cancellation.

## Test signals

Tests should cover successful scheduling, fridgethr submit failure paths, export-not-ready behavior, reference balance for lock entries, op context setup/release, blocked lock grant after `state_test()`, cancellation, polling interval initialization, and shutdown timeout/cancel paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_deleg.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/state_deleg.c

## Purpose

`state_deleg.c` implements NFSv4 delegation state management in SAL. It decides when delegations can be granted, acquires/releases FSAL leases, tracks delegation heuristics and client/file statistics, handles conflicts and recalls, persists revoked delegation file handles, and tracks revoked stateids until clients free them.

## Important APIs, types, and functions

- Globals: `g_total_num_files_delegated` and `g_max_files_delegatable` enforce a server-wide file delegation limit.
- Revocation state: `revoked_delegations_list` and `revoked_delegations_lock` track revoked delegation stateids for later `NFS4ERR_DELEG_REVOKED` responses and `FREE_STATEID` cleanup.
- `init_new_deleg_state()` initializes `union state_data` for a new delegation.
- `do_lease_op()`, `acquire_lease_lock()`, and `release_lease_lock()` bridge SAL delegation state to FSAL `lease_op2()`.
- `update_delegation_stats()`, `deleg_heuristics_recall()`, `init_deleg_heuristics()`, and `reset_cbgetattr_stats()` maintain file/client counters and CB_GETATTR state.
- `should_we_grant_deleg()` applies configuration, FSAL capability, export permission, callback-channel, reclaim, contention, client-revocation, open-mode, and global-limit checks.
- `deleg_supported()` and `can_we_grant_deleg()` perform additional support and lock/anonymous-operation checks.
- Revoked-state APIs include `has_revoked_delegations_for_client()`, `atomic_remove_revoked_and_clear_flags()`, `mark_sessions_have_revoked_delegations()`, `remove_revoked_stateid()`, and `is_stateid_revoked()`.
- `deleg_revoke()` and `state_deleg_revoke()` perform revocation, FSAL lease release, stable-storage revoke recording, session marking, and state deletion.
- `state_deleg_conflict_impl()`/`state_deleg_conflict()` detect conflicting operations and start async delegation recall.
- `is_write_delegated()` and `handle_deleg_getattr()` support write delegation GETATTR and conflict behavior.

## Control flow

Delegation grant starts with support checks: server config, regular-file object type, FSAL read/write delegation capabilities, export permissions, confirmed owner rules, and reclaim claim types. `should_we_grant_deleg()` then handles callback-channel-down reclaim cases, recent recalls, clients with repeated revokes, write-open contention, and the global files-delegated limit. `can_we_grant_deleg()` separately denies grants when anonymous operations or conflicting NLM locks exist. If a grant proceeds, `acquire_lease_lock()` maps delegation type to `FSAL_DELEG_RD` or `FSAL_DELEG_WR`, calls FSAL `lease_op2()`, updates stats, and clears CB_GETATTR state.

On recall or revoke, `deleg_heuristics_recall()` decrements file/client counters, resets file delegation type when no delegations remain, updates average hold time, and clears CB_GETATTR state. `deleg_revoke()` obtains state owner/export refs, builds an NFSv4 file handle, adds the stateid to the revoked list, releases the FSAL lease, persists the revoked file handle through `nfs4_record_revoke()`, marks v4.1 sessions as having revoked delegations, deletes state, and releases references/context.

Conflict detection scans active delegation states under `STATELOCK`. Write operations conflict unless the current client is the only delegate. Read operations conflict with another client's write delegation. Conflicts start `async_delegrecall()` and return true so callers can delay/deny the operation.

For GETATTR on a write-delegated file, `handle_deleg_getattr()` checks per-file CB_GETATTR state. It returns success for completed callback, delay while in progress or after sending a new callback, and falls back to delegation recall on callback failure or scheduling failure.

## State and persistence behavior

Most delegation state is in memory on `state_t`, `state_owner_t`, `state_hdl`, `file_deleg_stats`, client counters, and session flags. Persistent behavior occurs only for revoked delegations: `deleg_revoke()` calls `nfs4_record_revoke()`, which uses the selected recovery backend to store the revoked file handle so a post-restart `DELEG_PREV` can be rejected.

The revoked stateid list is process-local and protected by a mutex. It remains until `FREE_STATEID` or explicit removal. For NFSv4.1, session `has_revoked_delegations` flags are set on revoke and cleared when no revoked entries remain.

## Dependencies and integration points

The file depends on FSAL delegation lease support, NFSv4 OPEN/claim semantics, export permissions, callback RPC scheduling (`async_delegrecall`, `async_cbgetattr`), server statistics (`inc_grants`, `dec_grants`), file-handle conversion, recovery revocation recording, state list locking, and op context management. It is used by OPEN, stateid validation, lock/share conflict paths, lease expiry cleanup, and callback handling.

## Risks and edge cases

- `has_revoked_delegations_for_client()` ignores its `clientid` parameter and returns true if any revoked delegation exists globally, so per-client status may be over-reported.
- `atomic_remove_revoked_and_clear_flags()` checks whether the global list is empty, not whether the same client still has revoked delegations, which can keep or clear session flags incorrectly in multi-client scenarios.
- `add_to_revoked_delegations()` uses `malloc()` while `atomic_remove_revoked_and_clear_flags()` uses `gsh_free()` and `remove_revoked_stateid()` uses `free()`, a mixed allocator pattern worth auditing.
- Grant limit accounting increments before the final grant path and relies on recall decrement; failed later paths must avoid leaking the global count.
- Conflict detection uses `state->state_owner` directly while scanning; caller-held locks must protect this relationship.
- CB_GETATTR support is marked TODO and defaults to recall on failure; deployment behavior may be conservative.

## Test signals

Delegation tests should cover read/write grants, mixed read-write opens, export and FSAL capability denial, callback channel down with reclaim claims, recent recall starvation prevention, clients with repeated revokes, global delegation limit accounting, NLM lock conflicts, anonymous operation conflicts, FSAL lease failures, write delegation conflict with same vs different client, CB_GETATTR state transitions, revoke persistence, v4.0 vs v4.1 session flag behavior, `FREE_STATEID` cleanup, and restart `DELEG_PREV` rejection through recovery records.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_deleg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_layout.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/state_layout.c

## Purpose

`state_layout.c` manages pNFS layout state segments in SAL. It adds and removes layout segments, finds existing layout state for a file/client/layout type, and revokes all layouts owned by a client during cleanup such as lease expiry.

## Important APIs, types, and functions

- `state_add_segment()` adds an FSAL-provided `pnfs_segment` and FSAL private data to a `STATE_TYPE_LAYOUT` state.
- `state_delete_segment()` removes and frees one `state_layout_segment_t`.
- `state_lookup_layout_state()` searches a file's state list for a layout state matching owner and layout type and returns it with an incremented ref.
- `revoke_owner_layouts()` iterates a client owner state list and returns every layout with `nfs4_return_one_state()` using `circumstance_revoke`.

## Control flow

Segment add validates that the target state is layout state, allocates a segment object, copies the segment, links it to `state_data.layout.state_segments`, and marks the whole layout state `return_on_close` if any segment requests that behavior. Delete unlinks and frees a segment.

Lookup walks `obj->state_hdl->file.list_of_states` under the caller-held state lock and compares state type, owner, and layout type. On match it increments the state reference and returns success.

Owner revoke loops over the client's state list under `so_mutex`, moves each inspected entry to the tail to avoid spinning on skipped/error entries, skips non-layout states, obtains object/export refs, sets op context to the export, drops `so_mutex`, locks the object state, calls `nfs4_return_one_state()` for the entire file byte range and any I/O mode, then releases refs and restarts because the owner list lock was dropped.

## State and persistence behavior

Layout state is in memory only. Segments are linked under a layout `state_t`; FSAL-specific segment data is stored as an opaque pointer but not freed here. Revocation returns layouts to the client/FSAL path and deletes state through `nfs4_return_one_state()` if successful. No persistent recovery records are written by this file.

## Dependencies and integration points

The file depends on SAL state structures, glist, object state locks, owner refs, export context helpers, pNFS segment definitions, and NFSv4 layoutreturn logic. It is called by NFSv4.1 LAYOUTGET/LAYOUTRETURN and lease/client cleanup paths.

## Risks and edge cases

- `state_delete_segment()` frees only the segment wrapper, not `sls_fsal_data`; ownership must be handled elsewhere.
- `revoke_owner_layouts()` restarts after dropping `so_mutex`; the tail-moving and `first` sentinel reduce but do not eliminate complexity around concurrent list changes.
- Revoke aborts with `LogFatal()` after `STATE_ERR_MAX` failed layout returns, making persistent cleanup failure process-fatal.
- Correct lock ordering between owner mutex, object state lock, and export context is crucial.

## Test signals

Tests should cover segment add/delete, non-layout add rejection, return-on-close propagation, lookup by owner/type, refcounting on lookup, revoke of multiple layouts with intervening non-layout states, stale state/object handling, `nfs4_return_one_state()` deletion success/failure, and concurrency with owner state-list mutation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_layout.c -->
