# Group Research: group_397_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_nfsclient_nfs_clport_c_145be133f647

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clport.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clport.c

## Summary
FreeBSD-specific NFS client port layer. It ties generic newnfs client logic to FreeBSD vnode, mount, credential, pager, module, syscall, sysctl, Capsicum, and kernel-thread facilities.

## Main Responsibilities
- Creates and finds `nfsnode`/vnode instances by NFS file handle.
- Maintains NFS client attribute cache contents and pager size synchronization.
- Builds NFSv4 client IDs, open-owner names, and lock-owner names.
- Parses weak-cache-consistency and post-op attributes from NFS replies.
- Loads mount `statfs` and FSINFO-derived transfer-size limits.
- Maps NFSv4 protocol errors to local `errno` values.
- Implements client-side `nfssvc()` operations for callback sockets, callback nfsd workers, mount-option dumping, and forced dismount.
- Initializes and pins the `nfscl` kernel module.

## Key APIs
- `nfscl_nget()`, `nfscl_ngetreopen()`.
- `nfscl_loadattrcache()`, `ncl_copy_vattr()`, `ncl_pager_setsize()`.
- `nfscl_uuidcheck()`, `nfscl_fillclid()`, `nfscl_filllockowner()`, `nfscl_getparent()`.
- `nfscl_wcc_data()`, `nfscl_postop_attr()`, `nfscl_request()`.
- `nfscl_loadsbinfo()`, `nfscl_loadfsinfo()`.
- `newnfs_copyincred()`, `nfscl_checksattr()`, `nfscl_maperr()`, `nfscl_procdoesntexist()`.
- Internal syscall/module hooks: `nfssvc_nfscl()`, `nfscl_modevent()`.

## Important Behavior
`nfscl_nget()` uses `vfs_hash_get()`/`vfs_hash_insert()` keyed by an FNV hash of the file handle. It handles fake-root file handles, duplicate vnode races, doomed vnode checks, initial vnode construction, `VV_ROOT`, vnode operation switching for FIFOs, NFSv4.0 parent-fh/name side data, and loser vnode cleanup.

`nfscl_ngetreopen()` is a cache-only lookup variant used during reopen/recovery. It avoids blocking on vnode locks where possible because the caller holds exclusive client state.

`nfscl_loadattrcache()` rejects attribute updates where the server-reported fileid changes unexpectedly, rate-limits warnings, updates cached attributes, handles write-attribute partial refreshes, computes synthetic NFSv4 per-server-filesystem `va_fsid` values, reconciles local dirty size with server size, and invalidates stale attrs when mtime moves backwards.

`nfssvc_nfscl()` supports adding a callback socket with Capsicum socket rights, running callback service threads, copying formatted mount options to userland, and marking NFS mounts for forced dismount while canceling in-flight RPCs.

## State and Integration
Uses FreeBSD vnode/vfs hash tables, UMA zones, mount flags, NFS mount state, `nfsnode` locks, pager object size state, DTrace NFS probes, sysctls under `vfs.nfs`, and module dependencies on `nfscommon`, `krpc`, `nfssvc`, `xdr`, and `acl_nfs4`.

## Risks
VNode lifecycle is delicate: hash lookup/insert races, doomed vnode handling, `insmntque()` failure cleanup, lock state, and NFSv4 parent-name side data must stay consistent. Attribute-cache correctness depends on fileid stability, mtime ordering, local dirty-size rules, and pager size updates. Forced dismount and callback setup cross mount-list, data-server mirror, socket, and RPC cancellation state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clstate.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clstate.c

## Summary
Implements FreeBSD NFSv4 client state management: client IDs, sessions, open owners, opens, byte-range locks, delegations, callback handling, recovery, renewals, and pNFS layouts/device information.

## Main Responsibilities
- Creates and references per-mount `nfsclclient` state and performs SetClientID/CreateSession setup.
- Tracks NFSv4 open owners and open stateids, including pid-based and single-open-owner modes.
- Tracks lock owners and normalized non-overlapping byte-range lock lists.
- Supports read/write delegations, local opens/locks under delegations, delegation recall, and delegation return.
- Runs the renew thread for lease renewal, recovery, cleanup of exited process owners, delegation recall, layout recall, stale layout return, and data-server renewals.
- Handles NFSv4 callback compound operations such as CB_GETATTR, CB_RECALL, CB_SEQUENCE, CB_LAYOUTRECALL, CB_RECALL_SLOT, and CB_RECALL_ANY.
- Manages pNFS file/flexfile layouts, layout recalls, layout returns, layout commits, device-info references, and data-server error shutdown.

## Key APIs
- Client/open state: `nfscl_getcl()`, `nfscl_findcl()`, `nfscl_clientrelease()`, `nfscl_open()`, `nfscl_getstateid()`, `nfscl_getclose()`, `nfscl_doclose()`.
- Lock state: `nfscl_getbytelock()`, `nfscl_relbytelock()`, `nfscl_releasealllocks()`, `nfscl_checkwritelocked()`, `nfscl_lockrelease()`, `nfscl_lockt()`.
- Delegations: `nfscl_deleg()`, `nfscl_delegreturnvp()`, `nfscl_trydelegreturn()`, `nfscl_mustflush()`, `nfscl_nodeleg()`, `nfscl_removedeleg()`, `nfscl_renamedeleg()`, `nfscl_startdelegrecall()`.
- Recovery/renewal: `nfscl_renewthread()`, `nfscl_initiate_recovery()`, `nfscl_hasexpired()`, `nfscl_umount()`.
- Callback path: `nfscl_docb()`.
- pNFS: `nfscl_layout()`, `nfscl_getlayout()`, `nfscl_rellayout()`, `nfscl_adddevinfo()`, `nfscl_getdevinfo()`, `nfscl_reldevinfo()`, `nfscl_freelayout()`, `nfscl_layoutcommit()`, `nfscl_dserr()`, `nfscl_cancelreqs()`.

## Important Behavior
Open owners normally map to POSIX process identity; NFSv4.1/4.2 mounts with the single-open-owner option can use one all-zero open owner and shared owner locking for concurrent opens. Opens are delayed for server-side CLOSE until vnode inactive/close processing because mmap and inherited descriptors make a syscall close hard to map to one exact NFS open.

Lock owners map to POSIX/flock identities. `nfscl_updatelock()` maintains ordered, merged, non-overlapping local byte-range lock ranges and handles unlock splits. Delegations allow local opens and locks when safe; recall migrates local delegation opens/locks to server state and flushes dirty data for write delegations.

Recovery serializes on the client sleep lock, reestablishes client/session state, marks queued requests `R_DONTRECOVER`, reclaims opens, locks, and delegations where possible, expires unrecoverable state, and issues `RECLAIM_COMPLETE` for NFSv4.1+. The renew thread also performs periodic lease renewals, callback-path-down total recalls, exited-process cleanup, stale delegation/layout trimming, layout returns, layout commits, and DS session renewals.

`nfscl_docb()` builds callback replies and validates callback sequencing for NFSv4.1+. It can return delegation attributes, mark delegations for recall, process layout recalls by file/fsid/all, reduce callback slot counts, adjust delegation/layout high-water marks, and cache callback replies by session slot.

## State and Synchronization
Global state is protected by `NFSCLSTATEMUTEX`; client structures also use `nfsv4_lock` reference/exclusive-lock fields. State is arranged in client lists, open-owner lists, file-handle hash tables, delegation hash/LRU lists, lock-owner lists, layout hash/LRU lists, recall lists, and device-info lists. Many paths intentionally allocate before taking mutexes to avoid sleeping while list state is locked.

## pNFS Details
Layouts are stored by MDS file handle and split into read/RW file-layout lists. Layout recalls are ordered by recall type and wrapped seqid comparison. Layout returns can carry data-server error/device information. Device info objects are reference-counted by live users and layout references; unused entries are freed by the renew thread. Flexfile layouts can suppress layoutcommit via server flags.

## Risks
This is high-risk concurrency code: client recovery, unmount, forced dismount, callback threads, renew thread, vnode reclaim, close, delegation recall, and pNFS I/O can all interact. Correctness depends on strict lock/refcount discipline, careful avoidance of sleeping under the wrong mutex, stateid seqid handling, list/hash consistency, and cleanup of defunct owners. Error handling can intentionally discard unrecoverable lock/delegation/layout state, so callers must tolerate lost state after server expiry or failed reclaim.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clstate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clsubs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clsubs.c

## Summary
Small NFS client support module for initialization, attribute-cache lookup, directory-cookie tracking, vnode exclusive-access helpers, and write-verifier cleanup.

## Main Responsibilities
- Initializes async I/O daemon state and the NFS node hash table.
- Rejects client unload, matching the unsupported unload policy in the module layer.
- Provides directory cookie-map locking and cookie lookup/allocation.
- Provides an extra per-node exclusive lock helper for shared-vnode-lock callers.
- Serves cached attributes when valid and synchronizes vnode pager size on cache hits.
- Invalidates directory cookie state after directory changes.
- Clears `B_NEEDCOMMIT` dirty buffers when the server write verifier changes.

## Key APIs
- `ncl_init()`, `ncl_uninit()`.
- `ncl_dircookie_lock()`, `ncl_dircookie_unlock()`, `ncl_getcookie()`, `ncl_invaldir()`.
- `ncl_excl_start()`, `ncl_excl_finish()`.
- `ncl_getattrcache()`.
- `ncl_clearcommit()`.

## Important Behavior
`ncl_getattrcache()` computes adaptive attribute-cache timeout from mount `acregmin/acregmax/acdirmin/acdirmax` values and file modification age. It treats valid delegations as allowing cached attrs, counts cache hits/misses, reconciles cached regular-file size with local dirty state, may call `ncl_pager_setsize()`, overlays local atime/mtime changes, and fires DTrace cache hit/miss probes.

`ncl_getcookie()` maps logical directory offsets to NFS cookies in chained `nfsdmap` blocks. It refuses offsets above 50 GiB to avoid truncating the calculated cookie index and can allocate cookie-map blocks when `add` is set.

`ncl_clearcommit()` walks all vnodes on a mount and clears `B_NEEDCOMMIT` and `B_CLUSTEROK` on dirty buffers that need recommit after a write verifier change.

## State and Synchronization
Uses `ncl_iod_mutex` for async daemon state, per-node `n_mtx` plus `NDIRCOOKIELK` for directory cookie maps, per-node `n_excl` for exclusive operation serialization, vnode/bufobj locks for dirty-buffer scanning, and global `nfsstatsv1` counters.

## Risks
Attribute-cache validity depends on delegation status, mount timeout tuning, local dirty-size handling, and correct pager-size updates outside node locks. Directory cookie maps assume stable offset-to-cookie mapping until invalidated. `ncl_clearcommit()` walks all mount vnodes and mutates dirty-buffer flags only when buffers are not locked, so verifier recovery depends on later writeback behavior for buffers it cannot touch.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clsubs.c -->