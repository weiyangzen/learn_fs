# Research Group subset-b-005602

This grouped report covers AFS client directory, inode, file, locking, operation, probing, and FS RPC client code under `sources/distributed-fs/ceph-client/fs/afs/`. Each section is source-path aligned for reconciliation into the corresponding per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dir.c -->
## sources/distributed-fs/ceph-client/fs/afs/dir.c

Purpose: `dir.c` is the main VFS-facing directory implementation for the AFS client. It wires directory file, inode, address-space, and dentry operations, and implements lookup, readdir, dentry revalidation, create, mkdir, rmdir, unlink, link, symlink, rename, and single-blob cache writeback for directory and symlink data.

Important APIs and functions: exported operation tables are `afs_dir_file_operations`, `afs_dir_inode_operations`, `afs_dir_aops`, and `afs_fs_dentry_operations`. Key read paths are `afs_dir_open()`, `afs_read_single()`, `afs_read_dir()`, `afs_dir_iterate()`, `afs_readdir()`, `afs_do_lookup_one()`, and `afs_do_lookup()`. Mutation entry points are `afs_create()`, `afs_mkdir()`, `afs_rmdir()`, `afs_unlink()`, `afs_link()`, `afs_symlink()`, and `afs_rename()`. Operation callbacks such as `afs_create_success()`, `afs_unlink_success()`, `afs_rename_success()`, and their `edit_dir` counterparts bridge server results to inode state and local cached directory edits.

Control flow: directory reads call `afs_read_dir()`, which uses `validate_lock` as read/write coordination. Valid cached data returns under a read lock; invalid or unread data upgrades to write locking, invalidates the cache if needed, downloads the directory in one synchronous netfs read, verifies AFS directory blocks, marks `AFS_VNODE_DIR_VALID` and `AFS_VNODE_DIR_READ`, then downgrades back to a read lock for iteration. Lookup validates the parent, supports `@sys` substitution, searches the directory hash through `afs_dir_search()`, optionally prefetches nearby statuses through InlineBulkStatus, and instantiates or splices the resulting inode. Mutations allocate `struct afs_operation`, set vnode parameters and expected data-version deltas, execute the AFS/YFS RPC through `fs_operation.c`, commit returned statuses, and opportunistically edit cached directory data if the server data version advanced exactly as expected.

State and persistence: dentry `d_fsdata` stores the parent directory data version observed at lookup time. Directory contents live in `vnode->directory` folio queues and are persisted to fscache with `afs_single_writepages()` when valid. Inode and vnode flags including `AFS_VNODE_DIR_VALID`, `AFS_VNODE_DIR_READ`, `AFS_VNODE_DELETED`, `AFS_VNODE_NEW_CONTENT`, and sillyrename dentry flags control cache reuse and VFS lifetime behavior. Create-like operations update dentry versions and instantiate new inodes; unlink and rmdir can mark victim vnodes deleted; rename can adjust child `..` data versions for moved directories.

Dependencies and integration points: this file depends on directory search/edit helpers from `dir_search.c` and `dir_edit.c`, silly rename from `dir_silly.c`, inode creation/status functions from `inode.c`, RPC stubs in `fsclient.c` and YFS equivalents, callback validation, fscache/netfs APIs, Linux dcache locking, and trace/stat helpers. It is a central integration point between VFS operations and the AFS fileserver operation layer.

Risks: directory cache correctness depends on data-version comparisons matching server semantics; any missed invalidation can produce stale dentries. Rename contains complex dcache races around `d_drop()`, `d_rehash()`, `d_move()`, `d_exchange()`, busy target silly-rename, and `d_fsdata` updates. `afs_read_dir()` retry behavior must avoid endless `-ESTALE` loops. Local directory edits are deliberately skipped or invalidated when conflicts are detected, so tests should verify both optimistic edit and fallback reload paths.

Test signals: exercise readdir on valid, invalid, too-small, too-large, and malformed directory blobs; positive/negative lookup with data-version changes; `@sys` substitution; create/mkdir/symlink/link local edit insertion; unlink/rmdir/sillyrename removal; rename replace, noreplace, exchange, cross-directory moves, and busy-target replacement; dentry revalidation under RCU and non-RCU paths; fscache writeback for valid directory and symlink blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dir_edit.c -->
## sources/distributed-fs/ceph-client/fs/afs/dir_edit.c

Purpose: `dir_edit.c` performs optimistic local modifications to cached AFS directory blobs after successful server mutations. It avoids full directory refetches when server data-version changes are exactly understood.

Important APIs and functions: public helpers are `afs_edit_dir_add()`, `afs_edit_dir_remove()`, `afs_edit_dir_update()`, and `afs_mkdir_init_dir()`. Internal helpers manage the AFS directory format: `afs_find_contig_bits()`, `afs_set_contig_bits()`, `afs_clear_contig_bits()`, `afs_dir_get_block()`, `afs_dir_scan_block()`, and `afs_edit_init_block()`.

Control flow: additions verify directory size alignment, map or allocate the necessary folio-backed block, calculate the slot count from name length, choose a block using metadata allocation counters where available, initialize new blocks, fill an `afs_xdr_dirent`, update the bitmap, allocation counter, and hash-chain head, increment the inode version, and mark the inode dirty. Removals initialize a directory iterator, search the hash bucket for the target, clear the entry's slots, update allocation counters, splice the removed entry out of the hash chain using `iter.prev_entry`, mark the inode dirty, and set the inode version to the server data version. Updates scan blocks for a name and rewrite the vnode/unique fields, used mainly for `..` updates during directory rename/exchange. `afs_mkdir_init_dir()` initializes a new directory block with `.` and `..`.

State and persistence: edits operate on `vnode->directory`, `vnode->directory_size`, inode size, raw inode version, and the dirty state consumed by single-blob writeback. They rely on callers holding `validate_lock` and having checked `AFS_VNODE_DIR_VALID` plus expected data version. On structural uncertainty, they call `afs_invalidate_dir()` rather than risk preserving corrupted cached data.

Dependencies and integration points: callers are mostly mutation `edit_dir` callbacks in `dir.c` and `dir_silly.c`. The code depends on AFS directory XDR layout constants, folio queues, netfs allocation helpers, hash search from `dir_search.c`, endian conversion, and fscache writeback through the inode dirty flag.

Risks: hash-chain maintenance is critical; `afs_edit_dir_add()` still carries a note about `hash_next` maintenance but does insert at the bucket head. Bugs in slot accounting, allocation counters, or block initialization can corrupt all later lookup/readdir behavior. The optimistic nature means any stale callback or unexpected data-version jump must lead to invalidation. Boundary cases include maximum directory blocks, multi-slot long names, block-zero reserved slots, and name extension slots.

Test signals: add/remove/update names of varying lengths including multi-slot entries; remove head and non-head hash-chain entries; add into existing space and newly allocated blocks; create first directory contents; force invalid size and too-many-blocks paths; verify dirty marking and inode version changes; simulate callback break while edit is in progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dir_edit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dir_search.c -->
## sources/distributed-fs/ceph-client/fs/afs/dir_search.c

Purpose: `dir_search.c` searches the AFS directory hash table for a single name and returns the file identifier plus the directory data version observed during the search.

Important APIs and functions: `afs_dir_hash_name()` implements the AFS directory hash bucket algorithm. `afs_dir_init_iter()` prepares an `afs_dir_iter` with slot count, bucket, and loop budget. `afs_dir_find_block()` maps a specific directory block out of the vnode folio queue. `afs_dir_search_bucket()` walks one hash chain. `afs_dir_search()` wraps cache loading, retry, data-version capture, and bucket search.

Control flow: `afs_dir_search()` initializes the iterator, repeatedly calls `afs_read_dir()` to get validated directory contents under `validate_lock`, records `inode_peek_iversion_raw()`, and calls `afs_dir_search_bucket()`. The bucket search maps block zero for the hash table, then follows entry indexes through `hash_next`, validating reserved slots and using `loop_check` to detect chains that loop. If it finds a matching NUL-terminated name with enough slots in the current block, it decodes vnode and unique into the output FID.

State and persistence: the iterator carries current folio queue position, mapped block pointer, previous entry, bucket, required slot count, and loop budget. It does not persist state beyond the search, but it can invalidate the directory cache through `afs_invalidate_dir()` on stale block mapping or chain corruption.

Dependencies and integration points: this module depends on `afs_read_dir()` from `dir.c`, directory format constants and XDR structures, folio queue mapping, inode i_version, and validation flags on `afs_vnode`. `dir.c` uses it for normal lookup and `dir_edit.c` uses the bucket walk to remove entries while preserving hash-chain linkage.

Risks: search correctness depends on the local directory blob being fully validated and NUL-terminated by the read path. Broken hash chains, reserved-slot references, or stale folio queues must invalidate the directory to force a server refetch. Hash bucket computation must remain protocol-compatible. The retry limit in `afs_dir_search()` should catch repeated invalidation without spinning indefinitely.

Test signals: hash known names to expected buckets; search missing names; find entries in head and later chain positions; detect chain loops; reject reserved slots and out-of-range block references; retry after `-ESTALE`; ensure the read lock from `afs_read_dir()` is released after searches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dir_search.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dir_silly.c -->
## sources/distributed-fs/ceph-client/fs/afs/dir_silly.c

Purpose: `dir_silly.c` implements AFS silly rename, mirroring NFS behavior for unlinking an open file on a stateless server. It renames the busy file to a hidden `.__afsXXXX` name in the same directory and removes it later when the final dentry/inode reference is dropped.

Important APIs and functions: public entry points are `afs_sillyrename()` and `afs_silly_iput()`. Internal operation helpers are `afs_do_silly_rename()`, `afs_silly_rename_success()`, `afs_silly_rename_edit_dir()`, `afs_do_silly_unlink()`, `afs_silly_unlink_success()`, and `afs_silly_unlink_edit_dir()`.

Control flow: `afs_sillyrename()` rejects already silly-renamed dentries, searches for an unused hidden name with a static counter and `lookup_noperm()`, holds the victim inode, then issues an AFS/YFS rename operation. On success it marks the vnode `AFS_VNODE_SILLY_DELETED`, sets the dentry flag `DCACHE_NFSFS_RENAMED`, and moves the dentry to the hidden name. On uncertain interruption it drops both dentries to force lookup. Later, `afs_silly_iput()` runs from dentry iput, handles a possible alias race through `d_alloc_parallel()`, marks lock state deleted to quiet lock release, and calls `afs_do_silly_unlink()` to remove the hidden server-side file.

State and persistence: the parent directory remembers `silly_key` for the deferred unlink. The old dentry carries `DCACHE_NFSFS_RENAMED`; the victim vnode carries `AFS_VNODE_SILLY_DELETED` and may transition its lock state to `AFS_VNODE_LOCK_DELETED`. Directory cache edits remove the old name and add the hidden name after rename, then remove the hidden name after unlink, but only when the directory is still valid and data-version deltas match.

Dependencies and integration points: `dir.c` invokes silly rename from unlink and rename target replacement when a file is busy. The code depends on the normal operation layer, `afs_fs_rename()`, `afs_fs_remove_file()`, YFS counterparts, directory edit helpers, dcache aliasing, rmdir locks, vnode status commit, and flock state tracing.

Risks: failure or interruption can leave hidden server-side files that must be cleaned later or rediscovered by lookup. The static counter is simple and collision-handled through lookup, but not globally unique. Alias transfer in `afs_silly_iput()` is subtle. Lock-state changes around deletion must not strand waiters. Directory cache edits must not run after unrelated changes.

Test signals: unlink open files; repeat silly rename attempts; hidden-name collision loops; interrupted rename returning `-ERESTARTSYS`; last close cleanup; alias race in `afs_silly_iput()`; conflict path that fetches victim status after unlink; verify parent `silly_key` lifetime and directory cache edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dir_silly.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dynroot.c -->
## sources/distributed-fs/ceph-client/fs/afs/dynroot.c

Purpose: `dynroot.c` implements the synthetic AFS dynamic root. It presents configured or discovered cells as pseudo directories, exposes `@cell` and `.@cell` symlinks for the workstation cell, and creates automount-ready pseudo inodes.

Important APIs and functions: exported objects are `afs_dynroot_inode_operations`, `afs_dynroot_dentry_operations`, and `afs_dynroot_iget_root()`. Key helpers are `afs_dynroot_lookup()`, `afs_dynroot_lookup_cell()`, `afs_lookup_atcell()`, `afs_atcell_get_link()`, `afs_dynroot_readdir()`, `afs_dynroot_readdir_cells()`, and pseudo-inode iget helpers `afs_iget5_pseudo_test()`/`afs_iget5_pseudo_set()`/`afs_iget_pseudo_dir()`.

Control flow: lookup rejects create and overlong names, handles special `@cell` symlinks, then resolves a cell name through `afs_lookup_cell()` with dynamic-root lookup tracing. Dotted names indicate read-write mounts and use a distinct pseudo inode number. Successful lookup creates a pseudo directory inode with automount flags and stores the cell pointer in `d_fsdata`. Readdir emits `.` and `..`, optionally emits `@cell` and `.@cell`, then walks the `cells_dyn_ino` IDR under `cells_lock`, emitting undotted and dotted entries while skipping removing/dead cells.

State and persistence: dynroot inodes are pseudo, read-only, no-atime, and do not represent fileserver-backed vnodes. Cell references are held through dentry `d_fsdata` and released by `afs_dynroot_d_release()`. `@cell` symlink targets are derived from `net->ws_cell`, with RCU-pathwalk returning direct pointers and non-RCU pathwalk taking a cell reference via delayed call.

Dependencies and integration points: this code depends on the AFS cell registry, DNS resolver-backed lookup path, automount support through `afs_d_automount`, mountpoint inode operations, RCU and cell locks, and the VFS dentry/inode model. It is used by mounts configured for dynamic root rather than ordinary volume root lookup.

Risks: lifetime of `cell->name - 1` for dotted names assumes storage with a leading dot byte. RCU symlink access depends on `ws_cell` staying valid for pathwalk. Dentry deletion intentionally keeps only the special symlinks while allowing cell autodirs to be dropped, so mount cache behavior needs coverage. Pseudo inode numbers must remain within the reserved dynroot range and avoid collisions.

Test signals: lookup ordinary and dotted cells, missing cells, `@cell`, `.@cell`, and overlong names; readdir with and without workstation cell; skip dead/removing cells; automount from pseudo directories; dentry release cell reference balancing; RCU and non-RCU symlink reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/dynroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/file.c -->
## sources/distributed-fs/ceph-client/fs/afs/file.c

Purpose: `file.c` provides regular-file VFS operations and netfs integration for AFS data I/O, open/release key management, fscache usage, mmap tracking, and asynchronous fetch-data completion.

Important APIs and functions: exported tables are `afs_file_operations`, `afs_file_inode_operations`, `afs_file_aops`, `afs_req_ops`, and `afs_fetch_data_operation`. Main functions include `afs_open()`, `afs_release()`, `afs_cache_wb_key()`, `afs_issue_read()`, `afs_fetch_data_async_rx()`, `afs_fetch_data_immediate_cancel()`, `afs_file_read_iter()`, `afs_file_splice_read()`, mmap hooks `afs_file_mmap_prepare()`, `afs_vm_open()`, `afs_vm_close()`, and netfs callbacks `afs_init_request()`, `afs_update_i_size()`, and `afs_netfs_invalidate_cache()`.

Control flow: open obtains an AFS key, allocates `struct afs_file`, validates the vnode, caches a writeback key for writers, sets new-content on truncate, and starts fscache cookie use. Buffered reads validate the vnode under netfs read serialization, then use filemap; direct reads go through netfs unbuffered I/O. Netfs read requests allocate an AFS operation, attach the vnode and subrequest, and either issue an async fileserver read for readahead/iocb paths or a synchronous operation for other reads. Async receive repeatedly delivers rxrpc data, updates netfs subrequest progress, rotates fileservers on failure, and terminates the subrequest on final success/failure.

State and persistence: per-open state in `struct afs_file` holds the key and optional writeback key. Vnodes maintain a `wb_keys` list, fscache cookies, remote size, mmap count, and open-mmap list membership. Fetch success commits vnode status, counts bytes, and completes netfs subrequests. Release fsyncs writers, unuses fscache cookies with cache auxiliary data, drops keys, and prunes writeback keys.

Dependencies and integration points: this file sits between VFS file operations, Linux netfs helpers, fscache, rxrpc calls from `fsclient.c`, writeback code elsewhere in AFS, callback invalidation, and server rotation. Lock and flock hooks are delegated to `flock.c`.

Risks: key lifetime and writeback-key refcounts must balance across open, request, release, and netfs request free. Async reads must not double-complete subrequests when cancellation races with rxrpc completion. mmap tracking coordinates with callback breaks and must handle the last close while callback work is pending. Cache invalidation must match server data-version jumps.

Test signals: read, readahead, direct/unbuffered read, splice read; open for read/write/truncate; release with fsync failure; async fetch cancellation and retry across fileservers; fscache use/unuse auxiliary updates; mmap open/close and callback invalidation; writeback-key reuse across multiple writable opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/flock.c -->
## sources/distributed-fs/ceph-client/fs/afs/flock.c

Purpose: `flock.c` implements AFS file locking for POSIX locks and BSD flock emulation. Because AFS server locks are whole-file, time-limited, and callback-driven, this file combines local VFS lock records with server lock acquisition, extension, release, retry, and waiter management.

Important APIs and functions: exported entry points are `afs_lock()`, `afs_flock()`, `afs_lock_may_be_available()`, `afs_lock_op_done()`, and `afs_lock_work()`. Server RPC wrappers are `afs_set_lock()`, `afs_extend_lock()`, and `afs_release_lock()`. Core state-machine helpers include `afs_next_locker()`, `afs_grant_locks()`, `afs_defer_unlock()`, `afs_do_setlk_check()`, `afs_do_setlk()`, `afs_do_unlk()`, and `afs_do_getlk()`. File-lock copy/release hooks maintain vnode lock lists.

Control flow: a set-lock request validates vnode status and permissions, maps partial-lock behavior through the configured flock mode, optionally skips server locking for local/OpenAFS-compatible partial locks, queues the lock on `pending_locks`, and either reuses an existing compatible server lock, asks the server for a full-file lock, waits for callback/retry, or returns `-EAGAIN` for nonblocking contention. Once a server lock is held, the VFS lock manager still arbitrates local byte ranges. A delayed work item extends granted locks before timeout, retries waiters when callback break suggests availability, and releases server locks when all local granted locks are gone.

State and persistence: vnode fields `lock_state`, `lock_type`, `lock_key`, `locked_at`, `pending_locks`, `granted_locks`, and delayed `lock_work` are the main state. The server lock is leased and periodically extended; local `file_lock` records carry AFS state and debug IDs. Deleted vnodes move to `AFS_VNODE_LOCK_DELETED` and wake waiters with `-ENOENT`.

Dependencies and integration points: VFS lock APIs, AFS operation layer, FS/YFS lock RPCs in `fsclient.c`, callback break handling, permissions, server status `lock_count`, workqueue `afs_lock_manager`, and tracing. `file.c` registers these hooks in regular-file operations; `dir_silly.c` adjusts lock state during silly-delete cleanup.

Risks: starvation is possible when the client already holds a compatible server lock and grants more local locks. Signal interruption after dispatching a server lock can leave a lease that expires later. Correct key ownership is important when failing waiters by auth/type. Workqueue release failures are tolerated but must not leave local state permanently stuck. Partial locks differ by flock mode and need explicit compatibility testing.

Test signals: full-file read/write locks, partial locks under local/openafs/write modes, nonblocking contention, callback-triggered retry, lock extension success/failure, unlock while extension in progress, vnode deletion with waiters, VFS rejection after server lock, `GETLK` using local and server lock counts, flock calls with and without `FL_FLOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/flock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/fs_operation.c -->
## sources/distributed-fs/ceph-client/fs/afs/fs_operation.c

Purpose: `fs_operation.c` provides the common lifecycle for fileserver-directed operations. It allocates `struct afs_operation`, serializes vnode I/O operations, selects fileservers through the broader rotation layer, dispatches AFS/YFS RPC callbacks, commits result hooks, and releases all resources.

Important APIs and functions: exported functions are `afs_alloc_operation()`, `afs_begin_vnode_operation()`, `afs_end_vnode_operation()`, `afs_wait_for_operation()`, `afs_put_operation()`, and `afs_do_sync_operation()`. Internal lock helpers are `afs_lock_for_io()`, `afs_lock_for_io_interruptible()`, `afs_unlock_for_io()`, `afs_get_io_locks()`, `afs_drop_io_locks()`, and `afs_prepare_vnode()`.

Control flow: allocation obtains or references a key, pins the volume, captures callback-break and volume-sync snapshots, assigns a debug ID, and initializes the cumulative error. Beginning an operation optionally acquires one or two vnode I/O locks in address order, records each vnode FID, starting data version, callback break, modification flag, and current-lock constraints. `afs_wait_for_operation()` loops over `afs_select_fileserver()`, invokes the operation's AFS or YFS issue function, waits for the call, accumulates call state, then calls success, aborted, or failed hooks. It drops I/O locks before invoking `edit_dir`, so local cache edits happen after server serialization is complete. `afs_put_operation()` runs put hooks, clears modifying flags, releases inodes, endpoint/server/volume/key references, and returns the final error.

State and persistence: operations are transient but record durable vnode transition expectations: `dv_before`, `dv_delta`, callback break snapshots, `AFS_VNODE_MODIFYING`, selected server/address, and pre-operation volume sync. The custom I/O lock uses `AFS_VNODE_IO_LOCK` plus a waiters list because lock acquisition and release can occur across different execution contexts.

Dependencies and integration points: every higher-level vnode operation in `dir.c`, `file.c`, `flock.c`, `inode.c`, ACL/status code, and YFS support uses this abstraction. It depends on server selection, rxrpc call wrappers, key management, volume/server refcounting, vnode flags, and operation-specific callback tables.

Risks: failing to call `afs_begin_vnode_operation()` before waiting would leave FID/status snapshots stale. Two-vnode locking must preserve ordering to avoid deadlocks. Interruptible lock acquisition must correctly hand off or remove waiters on signals. Edit hooks after lock release mean they must take their own validation locks and recheck data versions. Resource release must cover `more_files` and speculative vnode refs.

Test signals: single-vnode and two-vnode operations, signal interruption while waiting for I/O lock, operation with missing AFS/YFS issue function, server rotation after call failure, success/aborted/failed hook dispatch, edit hook ordering, modification flag clearing, address preference update after a responding call, and `more_files` put behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/fs_operation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/fs_probe.c -->
## sources/distributed-fs/ceph-client/fs/afs/fs_probe.c

Purpose: `fs_probe.c` probes AFS fileserver endpoints to discover responsiveness, preferred address, round-trip time, YFS support, and capabilities such as 64-bit file operations. It also schedules periodic fast/slow reprobes.

Important APIs and functions: exported functions include `afs_get_endpoint_state()`, `afs_put_endpoint_state()`, `afs_fileserver_probe_result()`, `afs_fs_probe_fileserver()`, `afs_wait_for_fs_probes()`, `afs_fs_probe_timer()`, `afs_probe_fileserver()`, `afs_fs_probe_dispatcher()`, `afs_wait_for_one_fs_probe()`, and `afs_fs_probe_cleanup()`. Internal helpers manage probe scheduling and completion queues.

Control flow: `afs_fs_probe_fileserver()` allocates a new endpoint state, inherits responsive-set hints from the old state, installs it under the server fs lock, applies address preferences, then sends asynchronous `FS.GetCapabilities` probes to all addresses in priority order. Each completion calls `afs_fileserver_probe_result()`, which records last error, responsive/failed bits, aborts, YFS and FS64 capability flags, RTT, preferred address, and server responding state. When all address probes complete, the server is queued onto either the slow poll list if any endpoint responded or the fast poll list if none did, and a timer is scheduled. The dispatcher drains due fast/slow queues and reschedules itself or the timer.

State and persistence: `struct afs_endpoint_state` is RCU-freed and refcounted. It stores probe sequence, address list, responsive and failed bitsets, error/abort, RTT, flags, and outstanding probe count. Server state stores current endpoint pointer, address version, service ID, RTT, probe queue link, and flags including responding, YFS, and FS64 support. Network state tracks fast/slow probe queues, timer, work item, and outstanding server count.

Dependencies and integration points: probe RPC allocation is in `fsclient.c` (`afs_fs_get_capabilities()`), call completion returns here through call-type `done` hooks, server selection waits on probe states before choosing endpoints, and namespace cleanup stops timers. It depends on rxrpc peer RTT, address preference logic, server and net locks, RCU, timers, and workqueues.

Risks: there is a notable-looking local `old_alist` initialized to NULL and compared to `new_alist` before being assigned, so peer appdata update behavior deserves review against surrounding code. Probe completion races with superseded endpoint states and namespace shutdown must keep refs balanced. Error classification determines whether a server is treated as fast-reprobe unreachable or usable. Address bitsets assume the number of addresses fits in an unsigned long.

Test signals: all addresses responsive, none responsive, mixed failures, YFS response, AFS response with and without FS64, superseded probe while waiters sleep, `afs_wait_for_one_fs_probe()` timeout/signal paths, ENOMEM call allocation path, timer cleanup balancing outstanding counts, and dispatcher fast/slow queue rescheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/fs_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/fsclient.c -->
## sources/distributed-fs/ceph-client/fs/afs/fsclient.c

Purpose: `fsclient.c` is the AFS File Server RPC marshal/unmarshal layer. It defines call types, request encoders, reply delivery state machines, and exported RPC issue functions used by higher-level operations.

Important APIs and functions: exported RPC issuers include `afs_fs_fetch_status()`, `afs_fs_fetch_data()`, `afs_fs_create_file()`, `afs_fs_make_dir()`, `afs_fs_remove_file()`, `afs_fs_remove_dir()`, `afs_fs_link()`, `afs_fs_symlink()`, `afs_fs_rename()`, `afs_fs_store_data()`, `afs_fs_setattr()`, `afs_fs_get_volume_status()`, `afs_fs_set_lock()`, `afs_fs_extend_lock()`, `afs_fs_release_lock()`, `afs_fs_give_up_all_callbacks()`, `afs_fs_get_capabilities()`, `afs_fs_inline_bulk_status()`, `afs_fs_fetch_acl()`, and `afs_fs_store_acl()`. Core decoders include `xdr_decode_AFSFid()`, `xdr_decode_AFSFetchStatus()`, `xdr_decode_AFSCallBack()`, `xdr_decode_AFSVolSync()`, and `xdr_decode_AFSFetchVolumeStatus()`.

Control flow: each issue function allocates an `afs_call`, fills opcode and XDR parameters, attaches FID and tracing metadata, then calls `afs_make_op_call()` or `afs_make_call()`. Delivery functions either use `afs_transfer_reply()` for fixed replies or staged `afs_extract_*()` state machines for variable-length data, volume status strings, capabilities, inline bulk arrays, and ACL payloads. Fetch/store/setattr switch to 64-bit opcodes when the selected server advertises FS64. FetchData can be asynchronous and streams returned bytes into a netfs subrequest before decoding trailing status/callback/volsync.

State and persistence: decoded statuses and callbacks populate `afs_vnode_param.scb` for later commit by inode/operation code. Calls carry operation ID, buffers, temporary words, iterators, service ID, selected peer/server, probe information, write iterator, and async/cancel hooks. Capability probes update endpoint/server state through `fs_probe.c`; lock call types invoke `afs_lock_op_done()` to record lease issue time.

Dependencies and integration points: this file depends on protocol constants in `afs_fs.h`/`xdr_fs.h`, rxrpc call infrastructure, netfs subrequests, operation objects, probe state, lock manager, ACL structures, and YFS fallback decisions handled by callers. It is intentionally low-level and does not itself apply inode state except through decoded operation fields.

Risks: XDR size calculations and padding are error-prone for names, symlink contents, ACL data, and variable strings. `xdr_decode_AFSFetchStatus()` must handle OpenAFS InlineBulkStatus quirks while detecting bad status records. FetchData length handling must avoid overrun/underrun and correctly flag EOF. InlineBulkStatus count mismatches are protocol errors. FS64 selection must be correct for large offsets/sizes.

Test signals: decode valid and malformed status records; FetchData short, exact, long, zero-length, EOF, async cancel; create/mkdir/symlink/link/rename request sizes and padding; StoreData and setattr with and without 64-bit support; GetVolumeStatus long string rejection; lock call done hook; GiveUpAllCallbacks direct call; GetCapabilities probe result paths; InlineBulkStatus per-entry aborts and count mismatch; ACL fetch/store round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/fsclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/inode.c -->
## sources/distributed-fs/ceph-client/fs/afs/inode.c

Purpose: `inode.c` manages AFS inode creation, status application, callback promise application, symlink content handling, root inode setup, getattr/setattr, cache cookies, and inode eviction.

Important APIs and functions: public functions include `afs_init_new_symlink()`, `afs_get_link()`, `afs_readlink()`, `afs_vnode_commit_status()`, `afs_fetch_status()`, `afs_ilookup5_test_by_fid()`, `afs_iget()`, `afs_root_iget()`, `afs_getattr()`, `afs_drop_inode()`, `afs_evict_inode()`, and `afs_setattr()`. Key internals are `afs_inode_init_from_status()`, `afs_apply_status()`, `afs_apply_callback()`, `afs_fetch_status_success()`, `afs_get_inode_cache()`, `afs_setattr_success()`, and `afs_setattr_edit_file()`.

Control flow: new inodes are found or created with `iget5_locked()` keyed by vnode/unique. `afs_inode_init_from_status()` copies server status into vnode/inode fields, selects file/dir/symlink/mountpoint operations, initializes netfs context, size, i_version, callback state, and permits. Existing inodes receive `afs_vnode_commit_status()`, which handles inline errors such as deleted vnodes, speculative bulk-status suppression, normal status/callback application, unlink nlink drops, and permit caching. Symlink reads lazily validate and read the single blob into `vnode->directory`, then return a mapped folio through delayed-call cleanup. Setattr validates supported changes, serializes through `validate_lock`, waits for conflicting writes around truncation, optimizes in-memory-only shrink above remote size, otherwise issues StoreStatus/StoreData and then resizes pagecache/netfs/fscache.

State and persistence: vnode status mirrors fileserver metadata, including data version, type, size, owner, mode, nlink, lock count, access, and callback promise state. Inode i_version tracks data version. `invalid_before`, `AFS_VNODE_ZAP_DATA`, `AFS_VNODE_DIR_VALID`, `AFS_VNODE_DELETED`, and callback locks govern cache invalidation. Symlink content and directory blobs share the folio queue. FSCACHE cookies are keyed by vnode and unique, with auxiliary status data.

Dependencies and integration points: this file connects FS RPC status replies from `fsclient.c`, operation orchestration from `fs_operation.c`, netfs/fscache, VFS inode and symlink operations, directory operations, mountpoint handling, callback breaking, permits, and writeback/pagecache code.

Risks: status application must not regress data versions for speculative bulk status during concurrent modification. Type changes are protocol errors. Directory data-version jumps require directory invalidation while regular files set zap-data. Symlink RCU pathwalk must not sleep and must return `-ECHILD` when validation is needed. Setattr truncate ordering must avoid losing dirty data or leaving cache size inconsistent.

Test signals: instantiate regular files, directories, symlinks, and mountpoint symlinks; fetch status on new and existing inodes; speculative bulk status during modification; deleted vnode abort handling; symlink get_link RCU/non-RCU paths; root inode setup; getattr after silly delete and directory remote-size lie; eviction flushing dirty dir/symlink blobs; setattr mode/uid/gid/mtime/size including local-only shrink and extension.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/inode.c -->
