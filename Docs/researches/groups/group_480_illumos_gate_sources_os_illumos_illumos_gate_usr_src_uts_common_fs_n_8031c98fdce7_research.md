# Group Research: group_480_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_8031c98fdce7

Scope: `Docs/research_subset_a.md`

Files researched:
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_state.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_stub_vnops.c`

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_state.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_state.c

## Purpose

`nfs4_state.c` implements the illumos NFSv4 server state engine: client IDs, open owners, lock owners, open stateids, lock stateids, file state, delegation state, lease expiry, stable storage recovery, distributed stable storage path handling, and export teardown cleanup. The file is the stateful protocol core beneath the NFSv4 server operations, with the explicit lock hierarchy documented near the top: `client > openowner > state > lo_state > lockowner > file`, and with database hash bucket locks above the object locks they protect.

## Main Responsibilities

- Maintains protocol sentinel stateids: all-zero, all-one, current-stateid, and invalid-stateid, plus helpers to save/resolve NFSv4.1 current stateid in a compound request.
- Provides a general `rfs4_state_wait_t` single-active waiter primitive used by state owners to serialize replay-sensitive operations.
- Deep-copies and frees cached `OPEN` and `LOCK` replies, including denied lock owner buffers and delegation ACL strings.
- Initializes and tears down global kmem caches for each state object class and per-zone NFSv4 state databases/tables.
- Reads, writes, moves, removes, and validates stable-storage client records under the default and distributed stable storage directories.
- Creates and searches state database entries through multiple indices: NFS client identity, server clientid, client IP, open owner, lock owner, lock owner pid, vnode/file, stateid, owner+file, file, delegation client+file, and delegation stateid.
- Enforces NFSv4 lease expiry, stateid generation/sequence validation, cluster node ID embedding, grace-period reclaim eligibility, and state cleanup during client close, file remove, and unexport.

## Key Data and Tables

- Global `kmem_cache_t *` caches: `rfs4_client_mem_cache`, `rfs4_clntIP_mem_cache`, `rfs4_openown_mem_cache`, `rfs4_openstID_mem_cache`, `rfs4_lockstID_mem_cache`, `rfs4_lockown_mem_cache`, `rfs4_file_mem_cache`, `rfs4_delegstID_mem_cache`, `rfs4_session_mem_cache`.
- Per-zone tables created in `rfs4_state_zone_init()`:
  `rfs4_client_tab`, `rfs4_clntip_tab`, `rfs4_openowner_tab`, `rfs4_state_tab`, `rfs4_lo_state_tab`, `rfs4_lockowner_tab`, `rfs4_file_tab`, `rfs4_deleg_state_tab`, plus NFSv4.1 extended state via `rfs4x_state_init_locked()`.
- Clientids/stateids encode server start time and database IDs. In clustered boots, the low-level ID fields embed `clconf_get_nodeid()` and reject foreign node IDs through `foreign_clientid()` / `foreign_stateid()`.
- Stable storage entries store `NFS4_SS_VERSION`, client verifier, and client owner byte string; record leaf names are derived from client address plus server-generated clientid.

## Stable Storage and Recovery Flow

The stable-storage code supports NFSv4 reclaim after restart and HA-style distributed stable storage.

- `rfs4_dss_setpaths()` unpacks an nvlist provided by `nfssys()` and records the active DSS paths, preserving a previous set as old paths across warm starts.
- `rfs4_state_zone_init()` creates a new server instance with either the default path or default plus DSS paths, then initializes the state database and calls `rfs4_ss_init()`.
- `rfs4_ss_init()` reads default stable storage by calling `rfs4_dss_readstate()`, then enables future stable-storage writes.
- `rfs4_dss_readstate()` reads oldstate in place and reads state while moving entries into oldstate. This builds the current server instance's reclaim list.
- `rfs4_ss_getstate()` validates state files by type, readability, size, version, and encoded client-id length; malformed/empty files may be removed.
- `rfs4_ss_chkclid()` searches oldstate from the current server instance backward through active grace instances and marks `rc_can_reclaim` when a client owner matches. Expired instances have oldstate cleared.
- `rfs4_ss_clid()` writes a client stable-storage record after SETCLIENTID/confirmation activity, and `rfs4_ss_clid_write()` writes to all paths of all active instances until client grouping is improved.
- Client expiry/removal marks `rc_ss_remove`; `rfs4_client_destroy()` removes the stable-storage leaf from every DSS path when needed.

## State Object Lifecycle

Clients are created by `rfs4_client_create()`, which allocates a server clientid, copies the client-provided owner and address, initializes callback state, open-owner/session lists, credentials, lock-manager sysid state, server-instance association, and NFSv4.1 contrived sequence state. Lookup is by client owner (`rfs4_findclient()`) or server clientid (`rfs4_findclient_by_id()`), with special handling for replacing old unconfirmed clients.

Open owners are keyed by `{clientid, owner bytes}`. `rfs4_openowner_create()` looks up the parent client, copies the owner, initializes the cached reply, sequence id, waiter, and per-owner state list, and links the owner into the client. `rfs4_update_open_sequence()` and `rfs4_update_open_resp()` maintain replay state for the owner.

Lock owners are similarly keyed by `{clientid, owner bytes}` and also indexed by generated `pid`. `rfs4_lockowner_create()` holds the parent client and assigns `rl_pid` from the database entry ID. Lock-owner destruction frees owner bytes and releases the client.

File entries are keyed by vnode and may also be cached in vnode-specific data under `nfs4_srv_vkey`. `rfs4_file_create()` holds the vnode, copies the filehandle, initializes delegation info, share counters, recall condition variable, and per-file rwlock. Lookup can use the table or the vnode VSD fast path; `rfs4_findfile_withlock()` also returns with the file rwlock held and retries if the vnode disappeared.

Open state entries are keyed by stateid and also indexed by openowner+file and file. Creation holds the file and open owner, generates an OPENID stateid, initializes the lostate list, and links into the open owner. Destruction removes from the owner, destroys lock-state list, releases share locks if still open, and drops file/owner references.

Lock state entries connect a lock owner to an open state. Creation derives a LOCKID stateid from the open state, adds the lock owner pid, initializes sequence/reply/wait state, and links into the open state's `rs_lostatelist`. Destruction removes kernel locks via local `cleanlocks()` or cluster-aware `lm_remove_file_locks`, frees cached reply, and releases lock owner and open state.

Delegation state entries are keyed by client+file and by delegation stateid. Creation holds the file and client, creates a DELEGID stateid, records grant time, and starts as `OPEN_DELEGATE_NONE`. Expiry deliberately preserves revoked delegations as live protocol objects awaiting `FREE_STATEID`; destruction returns the delegation, adjusts revoked counts, and releases references.

## Stateid Validation and Access Control

The file centralizes stateid error mapping and sequence checks:

- `rfs4_check_clientid()` maps stale/expired clientids using server start time and cluster node ID.
- `what_stateid_error()` maps absent stateids to `STALE_STATEID`, `BAD_STATEID`, or `EXPIRED`, with delegation-specific revoked/removed behavior.
- `rfs4_get_state()`, `rfs4_get_state_nolock()`, `rfs4_get_lo_state()`, `rfs4_get_deleg_state()`, and `rfs4_get_all_state()` retrieve referenced state while rejecting foreign cluster stateids and expired leases.
- `rfs4_check_stateid_seqid()` and `rfs4_check_lo_stateid_seqid()` return internal classification values for bad, old, replay, expired, unconfirmed, closed, and OK stateids.
- `check_state_seqid()` implements NFSv4.1 session semantics where a seqid of zero is accepted.
- `rfs4_check_stateid()` is the main read/write path validator. It handles zero/one special stateids, delegation recalls and `NFS4ERR_DELAY`, grace-period rejection, stateid/filehandle matching, open-owner confirmation, closed state, access mode checks, delegation write tracking, lease refresh, and caller context filling for nbmand checks.
- `rfs4_state_has_access()` enforces OPEN share access for reads/writes and checks file deny-read counters when the current state did not grant read access.

## Cleanup Paths

- `rfs4_client_close()` invalidates a client, removes all open state and NFSv4.1 sessions, then releases the client reference.
- `rfs4_free_opens()` closes each state for an open owner and optionally invalidates the state/open owner.
- `rfs4_close_all_state()` invalidates a file entry, closes every open state referring to it, clears vnode VSD, and releases the vnode; this is used when remove-like operations must force state teardown after delegations are handled.
- `rfs4_clean_state_exi()` is called during unexport and walks lock-state, open-state, delegation-state, and file tables for filehandles under the export. It closes/invalidate matching state and clears vnode/delegation hooks. The comments explicitly note this may run from global-zone unexport code against non-global-zone structures, so it uses the passed `nfs_export_t`/`nfs4_srv_t` rather than zone-specific lookup.

## Dependencies and Integration Points

- Depends on the generic `rfs4_database`/`rfs4_table`/`rfs4_index`/`rfs4_dbe_*` state database layer.
- Integrates with NFSv4 protocol state from `nfs4.h`, `nfs4_state.h`, NFS export data, vnode/VOP primitives, lock manager APIs, DTrace probes, cluster node configuration, CPR callbacks, and NFSv4.1 session helpers (`rfs4x_*`, `rfs4_has_session()`).
- Stable storage uses kernel vnode file I/O (`vn_open`, `VOP_READ`, `VOP_WRITE`, `VOP_READDIR`, `vn_rename`, `vn_remove`) and nvlist unpacking for DSS path configuration.
- Delegation cleanup interacts with FEM monitors (`deleg_rdops`, `deleg_wrops`) and vnode open downgrade paths.

## Concurrency and Locking Notes

The implementation relies on strict reference-before-lock behavior. Most public lookup functions return held database entries that must be released through the matching `rfs4_*_rele()` routine, and some variants also return with file rwlocks held. Stable storage server-instance traversal uses `servinst_lock` and per-instance `oldstate_lock`; client lookup replacement uses `rfs4_findclient_lock` to hide an old client while searching. Vnode VSD access is guarded by `v_vsd_lock`, while file-level state operations use `rf_file_rwlock` to serialize teardown and lookup.

## Risks and Edge Cases

- Stable-storage code intentionally ignores many I/O failures and may remove malformed files; correctness depends on conservative validation and robust DSS path configuration.
- `rfs4_ss_has_client()` appears intended to prevent double-counting clients in oldstate. The body continues on byte-equal client IDs and returns true on byte-different IDs after equal length, which is surprising and worth reviewing against historical fixes.
- Many hash functions are simple shift/add or pointer-address hashes; correctness is maintained by compare functions, but distribution may matter under high state counts.
- `rfs4_state_zone_fini()` warns that consumers may still be active while database tables are destroyed; teardown ordering is a known sensitivity.
- Cluster encoding assumes table IDs leave enough high bits for node IDs and asserts this rather than handling overflow dynamically.
- Several paths hold locks across `KM_SLEEP` allocations because structure sizes come from locked objects. The comments acknowledge this as difficult to avoid.

## Testing and Verification Signals

Useful tests would exercise SETCLIENTID/CONFIRM replay, server restart reclaim from stable storage, DSS path failover, lease expiry and clear-locks forced expiry, open/lock replay reply caching, special zero/one/current stateids, NFSv4.1 session seqid-zero behavior, delegation revocation plus `FREE_STATEID`, file remove/unexport cleanup, and clustered foreign clientid/stateid rejection.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_state.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_stub_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_stub_vnops.c

## Purpose

`nfs4_stub_vnops.c` implements NFSv4 client-side vnode operations for trigger stub vnodes used by ephemeral mounts, especially NFSv4 mirror mounts and referrals. A stub vnode represents a directory that should be covered by a new NFSv4 mount when accessed. The file detects trigger operations, constructs mount arguments from parent NFS mount state plus mirror/referral-specific location data, performs the kernel mount, records the mount in an ephemeral tree, and later unmounts idle ephemeral mounts through a per-zone harvester.

## Vnode Operation Surface

The file defines `nfs4_trigger_vnodeops_template`, installed as `nfs4_trigger_vnodeops`, for stub vnodes.

Triggering operations include `open`, `getattr` when `ATTR_TRIGGER` is present, `setattr`, `access`, `lookup`, `create`, `remove`, `link`, `rename`, `mkdir`, `rmdir`, `symlink`, and `readlink`. Most call `nfs4_trigger_mount()` and then reissue the requested VOP on the root vnode of the covering filesystem.

Some operations deliberately do not trigger:

- `getattr` without `ATTR_TRIGGER` returns real NFSv4 attributes for mirror-mount stubs, and fabricated directory attributes for referral stubs through `nfs4_fake_attrs()`.
- `lookup("..")` is special. Mirror mounts call regular `nfs4_lookup()` on the stub, while referrals return the parent vnode via `vtodv()`.
- `inactive`, `rwlock`, `rwunlock`, `fid`, `realvp`, `getsecattr`, and `pathconf` use regular NFSv4 vnodeops because they should not mount.
- `frlock`, `dispose`, and `shrlock` are mapped to `fs_error`.

`nfs4_trigger_rename()` also blocks cross-filesystem semantics early: if source and target directories are different stubs, it returns `EXDEV` without triggering either mount.

## Mount Trigger Flow

`nfs4_trigger_mount()` is the central path.

1. It first calls `nfs4_trigger_mounted_already()` under vnode vfs locks. If another thread already mounted over the stub, it returns the covering root vnode and refreshes the ephemeral reference time.
2. It obtains per-zone trigger globals from `nfs4_ephemeral_key`.
3. It creates or joins the parent mount's `nfs4_ephemeral_tree_t`. Creation links the tree into the zone forest, marks it building, holds the parent `mntinfo4_t` and VFS, and locks the tree. Joining holds the tree and refuses to proceed when tree processing/teardown is underway.
4. It marks the tree mounting, builds mount arguments via `nfs4_trigger_domount_args_create()`, temporarily grants zone privileges to duplicated caller credentials, and calls `nfs4_trigger_domount()`.
5. It clears mounting/building status and releases tree references/locks according to whether this thread created the tree.

The returned vnode is held for the caller. Trigger vnodeops release it after reissuing the real VOP, except `open`, which replaces the caller's stub vnode reference with the new root vnode and delegates to `VOP_OPEN()`.

## Mount Argument Construction

`nfs4_trigger_domount_args_create()` builds a `domount_args_t` containing:

- `ephemeral_servinfo_t` for the server actually used by the mount.
- A comma-separated host list for NFS read-only failover.
- A linked list of `struct nfs_args`, one per responsive server.

It pings the current server first, then iterates all parent `servinfo4_t` entries. Nonresponsive servers are omitted from the failover list. If all servers are down, it sleeps and retries until one responds, unless interrupted. This avoids known mount-path hangs when an unavailable server is passed into the mount code.

`nfs4_trigger_nargs_create()` copies generic mount behavior from the parent `mntinfo4_t` and `servinfo4_t`: soft/hard, interruptible, caching timers, rsize/wsize, timeout/retransmit, local lock/direct I/O/nocto/grpid/public options, security data, and NFSv4 argument extension B. It adjusts referrals to use security negotiation with an AUTH_SYS starting point and to prefer RDMA negotiation (`TRYRDMA` not `DORDMA`). Mirror mounts preserve parent security negotiation policy.

`nfs4_trigger_domount()` constructs the effective mount point from the parent VFS mountpoint plus the stub path, strips zone root prefixes for non-global zones, builds the `hostlist:path` spec, creates an option string, and calls `domount()` with `MS_SYSSPACE | MS_DATA | MS_OPTIONSTR`. On `EBUSY`, it retries once and checks whether another thread won the race by mounting over the stub.

## Mirror Mount Handling

`nfs4_trigger_esi_create_mirrormount()` builds ephemeral server info by deep-copying the selected parent `servinfo4_t`: hostname, address, knetconfig, optional AUTH_DH sync address and netname, and a composed remote path. The remote path combines the parent server path with the stub's path from `fn_path()`, taking care not to produce malformed paths when the parent path is `/`. The copied data is intentionally independent because the new ephemeral mount may outlive or be unmounted separately from the parent structures.

## Referral Handling

Referral support uses several stages:

- `nfs4_fetch_locations()` sends an NFSv4 compound `CPUTFH`, `CLOOKUP`, `GETATTR` requesting `FATTR4_FSID`, `FATTR4_FS_LOCATIONS`, and `FATTR4_MOUNTED_ON_FILEID`. It validates the result and returns `nfs4_ga_res_t` plus the XDR compound result for later cleanup.
- `find_referral_stubvp()` uses `mounted_on_fileid` and the parent directory filehandle to construct a synthetic shared filehandle, creates or finds an NFSv4 vnode with `makenfs4node()`, marks it as a directory, and returns a referral stub vnode.
- `nfs4_setup_referral()` marks that vnode's rnode as a referral stub and enters it in the DNLC.
- `nfs4_process_referral()` fetches fs_locations, detects migration by checking whether the fsid already exists in the rnode cache, resolves candidate servers through `nfs4_callmapid()`, and selects the first server responding to an NFSv4 NULL ping.
- `nfs4_trigger_esi_create_referral()` fetches the parent directory/name, calls `nfs4_process_referral()`, then builds `ephemeral_servinfo_t` from the selected fs_location rootpath and resolved network data.

The mapid upcall in `nfs4_callmapid()` uses the zone's nfsmapid door with XDR-encoded `NFSMAPID_SRV_NETINFO`, handles missing daemon cases, and decodes `struct nfs_fsl_info`.

## Ephemeral Mount Tree Model

Each zone owns `nfs4_trigger_globals_t`, containing a forest lock, current mount timeout, a harvester-started flag, and a list of `nfs4_ephemeral_tree_t` roots. Each tree tracks:

- Tree-wide locks and reference count.
- Status bits for building, mounting, processing, unmounting, derooting, invalid, and harvester-locked states.
- The non-ephemeral enclosing parent `mntinfo4_t`.
- A root list of `nfs4_ephemeral_t` nodes.

Each ephemeral mount node tracks its `mntinfo4_t`, reference time, timeout copy, child pointer, peer pointer, prior pointer, and traversal/error state.

`nfs4_record_ephemeral_mount()` is called from `nfs4_mount()` after an ephemeral mount succeeds. It starts the harvester if needed, attaches the new `mntinfo4_t` to the parent tree, allocates an ephemeral node, holds the mount and VFS, records the timeout and reference time, and links the node as a child, peer, or tree root depending on whether the parent is itself ephemeral.

## Unmount and Harvesting

Manual and automatic unmounting share the same tree data structures.

- `nfs4_ephemeral_umount()` is called from NFSv4 unmount handling. It detects whether the current mount is an ephemeral node or the enclosing tree root, coordinates with active harvester or recursive unmount work, marks tree status, and either unmounts children of a node or deroots the entire tree.
- `nfs4_ephemeral_unmount_engine()` avoids recursive C stack traversal by iteratively walking to child/peer leaves, setting `MI4_EPHEMERAL_RECURSED`, calling `umount2_engine()`, and stitching tree links after successful unmounts.
- `nfs4_ephemeral_umount_activate()` finalizes node removal after the ordinary unmount path proves the mount is not busy. It unlinks the node, releases tree/mount/VFS references, frees the node, and unlocks the tree.
- `nfs4_ephemeral_harvest_forest()` scans every tree in a zone. It can force-unmount during zone destruction, or time-check nodes against `ne_mount_to` during normal harvests. It walks child/peer relationships without C recursion, records child/peer errors so parents are not removed incorrectly, and frees invalid trees whose refcount reaches zero.
- `nfs4_ephemeral_harvester()` is a per-zone zthread that wakes every `nfs4_trigger_thread_timer` seconds, exits when the zone shuts down, and harvests idle ephemeral mounts only when the forest is non-empty.
- Zone key callbacks allocate per-zone globals, gracefully harvest on zone shutdown, force harvest on zone destroy, and free locks/globals.

The public initialization/teardown entry points are `nfs4_ephemeral_init()` and `nfs4_ephemeral_fini()`. `nfs4_ephemeral_set_mount_to()` updates the per-zone timeout used by future ephemeral mounts.

## Mount Options and Server Ping Helpers

`nfs4_trigger_create_mntopts()` walks the NFSv4 mount option prototype list and appends currently set options from the parent VFS to a comma-separated string, also explicitly handling `xattr`/`noxattr` because those are not in the v4 option prototype list. `nfs4_trigger_add_mntopt()` bounds the string at `MAX_MNTOPT_STR` and returns `EOVERFLOW` if it would exceed the fixed buffer.

`nfs4_ping_server_common()` creates a temporary RPC client for `NFS_PROGRAM` version 4 and sends an `RFS_NULL` call with a two-second timeout and one retry. `nfs4_trigger_ping_server()` wraps it for `servinfo4_t`.

## Dependencies and Integration Points

- VFS/vnode interfaces: vnodeops registration, `domount()`, `VFS_ROOT`, `vn_mountedvfs`, `vn_vfsrlock_wait`, `umount2_engine`, VFS mount options, and vnode references.
- NFSv4 client internals: `mntinfo4_t`, `servinfo4_t`, `rnode4_t`, shared filehandles, recovery locks, security negotiation data, `nfs4_mount()`, `nfs4_lookup()`, `makenfs4node()`, `sfh4_put()`, and rnode cache lookup by fsid.
- RPC and idmap infrastructure: TLI RPC client creation, nfsmapid door upcalls, XDR encode/decode, `struct nfs_fsl_info`.
- Zone infrastructure: zone-specific data keys, zone shutdown detection, zthreads, non-global-zone mountpoint path handling.
- DTrace probes instrument referral fetch/upcall/debug and ephemeral tree derooting.

## Concurrency and Locking Notes

The file uses several layers of synchronization: parent `mi_lock`, tree `net_tree_lock`, tree `net_cnt_lock`, zone forest lock, server info rwlocks, recovery locks, and vnode VFS locks. The mount path avoids duplicate mounts by first checking the covering VFS, then serializing tree creation/building/mounting. The unmount path carefully distinguishes manual unmount, recursive unmount, harvester work, and derooting so that tree invalidation and node finalization happen in the right phase.

## Risks and Edge Cases

- `nfs4_trigger_domount_args_create()` can retry forever when no server responds unless interrupted; this is intended to avoid mounting with an all-dead failover list, but it can stall a caller on persistent outage.
- Referral mount creation depends on the nfsmapid daemon. Missing daemon or malformed XDR responses cause referral setup failure.
- Several routines allocate while holding server or mount locks to deep-copy mutable structures; this avoids stale data but can sleep under locks.
- The ephemeral tree logic is complex and status-bit driven. Bugs in refcount/status transitions could produce busy mounts, leaked tree nodes, or failed automatic cleanup.
- The fixed mount option buffer requires careful option length accounting; overflow is handled by failing mount option creation.
- Referral rootpath construction rejects paths exceeding `MAXPATHLEN`, but the error path must free several partially populated nested allocations.

## Testing and Verification Signals

Useful tests include mirror mount trigger through each vnodeop, lookup of `..` for mirror and referral stubs, concurrent triggers racing on the same stub, failover host-list filtering with one or more unavailable servers, referral resolution via nfsmapid, migration-vs-referral fsid detection, non-global-zone mountpoint path construction, option propagation including xattr/noxattr, harvester timeout unmount, manual unmount of child and enclosing parent trees, forced zone-destroy cleanup, and `EBUSY`/race behavior in `domount()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_stub_vnops.c -->