# Group Research: group_937_linux_stable_sources_os_linux_linux_stable_fs_afs_dir_search_c_sourc_418f1c7712be

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dir_search.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/dir_search.c

## Summary
Implements lookup of names inside locally cached AFS directory data. It hashes names into AFS directory hash buckets, locates directory blocks in the vnode's folio queue, walks hash chains, and returns the matching file identifier plus directory data version.

## Main Responsibilities
- Computes AFS directory name hash buckets with `afs_dir_hash_name()`.
- Initializes and resets `struct afs_dir_iter` for a lookup.
- Maps a requested AFS directory block from `dvnode->directory`.
- Walks one directory bucket chain and detects corrupt chains.
- Coordinates directory reread/retry behavior around stale or invalid directory contents.

## Key APIs
- `afs_dir_hash_name()`.
- `afs_dir_init_iter()`.
- `afs_dir_find_block()`.
- `afs_dir_search_bucket()`.
- `afs_dir_search()`.

## Important Behavior
`afs_dir_find_block()` reuses the iterator's current folio queue position when possible, but rewinds to the start if the requested block is before the current position. If a block cannot be found or mapped consistently, it invalidates the directory with `afs_invalidate_dir()`.

`afs_dir_search_bucket()` starts from the directory metadata block's hash table, validates reserved slot boundaries, compares the inline directory entry name including NUL termination, and returns the raw directory entry index on success. It decrements `loop_check` on each chain step to detect loops.

`afs_dir_search()` calls `afs_read_dir()` and retries up to three times on `-ESTALE`, unless the directory vnode is already marked deleted. It records the raw inode version as the directory version after a successful read.

## State and Synchronization
`afs_read_dir()` is expected to acquire `dvnode->validate_lock`; this file releases that read lock after bucket search. Directory validity is tracked through `AFS_VNODE_DIR_VALID` and explicit invalidation reasons.

## Risks
Directory corruption or stale folio queue state is treated as `-ESTALE` and invalidates the cached directory. The code relies on AFS directory layout constants and careful slot arithmetic; incorrect reserved-slot handling would misinterpret metadata as entries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dir_search.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dir_silly.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/dir_silly.c

## Summary
Implements AFS silly rename handling for unlinking open files. Because AFS servers are stateless with respect to open file references, the client renames an open-but-unlinked file to a hidden `.__afsNNNN` name and removes it later when the dentry/inode is finally released.

## Main Responsibilities
- Performs server-side rename to a generated silly name.
- Marks dentries with `DCACHE_NFSFS_RENAMED`.
- Locally edits cached directory contents after successful silly rename/unlink.
- Removes silly-renamed files during `dentry_iput`.
- Handles lookup races while transferring silly-delete state to aliases.

## Key APIs
- `afs_sillyrename()`.
- `afs_silly_iput()`.
- Internal operations: `afs_do_silly_rename()` and `afs_do_silly_unlink()`.

## Important Behavior
Silly names use the `.__afs` prefix, which the comment notes is understood by the AFS salvager. The generated name is found with `lookup_noperm()` and must be negative before use.

On rename success, the target vnode gets `AFS_VNODE_SILLY_DELETED`, and `d_move()` moves the original dentry to the silly dentry. On `-ERESTARTSYS`, both dentries are dropped so a later lookup will revalidate unknown server state.

`afs_silly_iput()` uses `d_alloc_parallel()` to avoid racing lookup. If another lookup already instantiated an alias, it transfers `DCACHE_NFSFS_RENAMED` to that alias instead of performing unlink itself.

## State and Synchronization
Directory updates use `dvnode->validate_lock` and only apply local edits when the cached directory is valid and the returned data version matches the expected delta. `dvnode->rmdir_lock` protects silly-unlink against directory removal races. Lock state is forced to `AFS_VNODE_LOCK_DELETED` before final silly unlink to suppress lock-release complaints.

## Risks
The hidden-name generator is a static counter and retries until it finds a negative dentry. If rename result is interrupted, the client deliberately drops cached dentries because server state is unknown. The final unlink uses `dvnode->silly_key`; stale or missing key state would affect cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dir_silly.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dynroot.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/dynroot.c

## Summary
Implements the dynamic AFS root directory. It exposes configured/known cells as pseudo directories, provides `@cell` and `.@cell` symlinks to the workstation cell, and creates automount-capable pseudo-inodes for cell traversal.

## Main Responsibilities
- Creates pseudo directory inodes for dynamic root and autocell entries.
- Looks up cell names, including dotted names for read/write volume preference.
- Provides `@cell` and `.@cell` symlink handling.
- Emits dynamic root directory entries from the cell database.
- Supplies dentry operations for dynamic root automount behavior and cache deletion policy.

## Key APIs
- `afs_dynroot_iget_root()`.
- `afs_dynroot_inode_operations`.
- `afs_dynroot_dentry_operations`.
- Internal helpers: `afs_dynroot_lookup_cell()`, `afs_lookup_atcell()`, `afs_dynroot_readdir()`.

## Important Behavior
Dynamic root lookup rejects creation and overlong names. `@cell` maps to inode 2 and `.@cell` to inode 3. Ordinary cell entries are looked up through `afs_lookup_cell()` and represented by pseudo directories whose inode numbers derive from `cell->dynroot_ino * 2 + dotted`.

`afs_atcell_get_link()` returns the current workstation cell name. For dotted symlinks it returns `cell->name - 1`, relying on the cell name allocation being NUL/dot padded for dotted display.

`afs_dynroot_readdir()` emits dot entries, optional `@cell` symlinks when a workstation cell exists, then iterates `net->cells_dyn_ino`, emitting both undotted and dotted directory names for each live cell.

## State and Synchronization
Cell enumeration and workstation-cell access use `net->cells_lock` and RCU accessors. Dynamic cell dentries keep a cell usage reference in `d_fsdata`, released by `afs_dynroot_d_release()`. Non-symlink cell autodirs are allowed to be deleted from dcache when unused.

## Risks
Pseudo inode numbers are bounded by `AFS_MAX_DYNROOT_CELL_INO`. The dotted-cell behavior depends on name storage layout outside this file. Dynamic root visibility follows in-memory cell state and can skip removing/dead cells during readdir.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dynroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/file.c

## Summary
Provides regular file operations and netfs integration for AFS. It handles open/release keys, read dispatch, writeback key caching, mmap callback tracking, file size updates, and the `netfs_request_ops` used by buffered and direct I/O paths.

## Main Responsibilities
- Defines AFS file, inode, address-space, and VM operation tables.
- Requests authentication keys on open and validates vnodes before access.
- Caches writeback keys per vnode for later writeback.
- Dispatches synchronous and asynchronous FS/YFS fetch-data operations.
- Wires AFS into netfs read/write helpers.
- Tracks mmap users so callback breaks can invalidate mapped files.

## Key APIs
- `afs_open()`, `afs_release()`.
- `afs_cache_wb_key()`, `afs_put_wb_key()`.
- `afs_fetch_data_operation`.
- `afs_fetch_data_async_rx()`, `afs_fetch_data_immediate_cancel()`.
- `afs_set_i_size()`.
- `afs_req_ops`.

## Important Behavior
Open attaches an `struct afs_file` containing the selected key to `file->private_data`, validates the vnode, and caches a writeback key for writable opens. Release fsyncs writable files, unuses the fscache cookie with updated auxiliary data, drops key references, and prunes stale writeback keys.

`afs_issue_read()` allocates an operation and either executes synchronously or sets `AFS_OPERATION_ASYNC` for readahead/iocb reads. Async receive processing drains rxrpc attention, reports progress to netfs, retries server selection on failure, and terminates the netfs subrequest when done.

`afs_init_request()` attaches a key to read requests, sets read/write sizing, and enables the write stream for regular-file write origins. Request cleanup drops both the request key and writeback key.

## State and Synchronization
`afs_set_i_size()` updates inode size and block count under `vnode->cb_lock` and `inode->i_lock` to avoid tearing and callback races. Mmap users are counted in `cb_nr_mmap` and linked into `volume->open_mmaps` under `open_mmaps_lock`.

## Risks
Read retry and async call lifetime are subtle: `call->op`, `op->call`, rxrpc refs, and netfs subrequest completion must be balanced exactly. Mmap callback tracking has a special zero-count path protected by callback locking and work flushing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/flock.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/flock.c

## Summary
Implements POSIX and BSD-style file locking for AFS using whole-file server locks plus local VFS lock arbitration. It supports several partial-lock emulation modes because AFS3 server locks are whole-file and cannot be upgraded or downgraded.

## Main Responsibilities
- Acquires, extends, and releases AFS/YFS server locks.
- Queues pending local lock requests and grants compatible local locks.
- Periodically renews server locks before timeout.
- Handles lock contention by waiting for callback breaks or polling.
- Integrates AFS lock state into VFS `lock` and `flock` operations.
- Cleans up vnode lock queues when VFS lock records are copied or released.

## Key APIs
- `afs_lock()`.
- `afs_flock()`.
- `afs_lock_work()`.
- `afs_lock_may_be_available()`.
- `afs_lock_op_done()`.

## Important Behavior
The lock state machine moves among `NONE`, `SETTING`, `GRANTED`, `EXTENDING`, `WAITING_FOR_CB`, `NEED_UNLOCK`, `UNLOCKING`, and `DELETED`. Successful lock RPCs record `locked_at` and schedule renewal at roughly half the AFS lock wait interval.

Partial-file locks may remain local in OpenAFS-compatible mode, always use a server lock in strict mode, or force an exclusive server lock in write mode. After a server lock is obtained, VFS locking still decides local access among processes on the same client.

If the server reports contention, blocking callers wait on the file lock waitqueue. Because servers may not notify on lock expiry, the client schedules periodic retry work.

## State and Synchronization
`vnode->lock` protects pending/granted lock lists, lock key, lock type, and lock state. Server unlock can be deferred to the `afs_lock_manager` workqueue so signal-interruptible contexts do not interrupt rxrpc release. VFS lock-copy/release callbacks keep AFS vnode queues aligned with copied kernel lock records.

## Risks
The implementation must reconcile three views of locking: server whole-file lock state, local VFS byte-range state, and AFS callback notifications. Interruptions after dispatching a lock RPC can leave ambiguous server state until timeout or cleanup. Starvation is possible because local compatible locks can be granted while other clients wait.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/flock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/fs_operation.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/fs_operation.c

## Summary
Provides the common operation wrapper for fileserver-directed AFS operations. It allocates operation state, serializes vnode I/O, prepares vnode parameters, drives server/address rotation through RPC issue callbacks, applies success/failure hooks, and releases all operation-owned resources.

## Main Responsibilities
- Allocates and initializes `struct afs_operation`.
- Implements a custom per-vnode I/O serialization lock.
- Locks one or two vnodes for operations in stable pointer order.
- Captures pre-operation vnode status, data version, and callback break state.
- Waits for fileserver selection and RPC completion.
- Runs operation-specific success, abort, failure, and directory-edit hooks.
- Tears down operation references and updates preferred address hints.

## Key APIs
- `afs_alloc_operation()`.
- `afs_begin_vnode_operation()`.
- `afs_wait_for_operation()`.
- `afs_end_vnode_operation()`.
- `afs_put_operation()`.
- `afs_do_sync_operation()`.

## Important Behavior
`afs_alloc_operation()` pins the key and volume, snapshots volume callback and volsync state, assigns a debug id, and starts with cumulative error `-EDESTADDRREQ`.

The I/O lock is implemented with `AFS_VNODE_IO_LOCK`, a waiters list, task wakeups, and release/acquire memory barriers. This is used instead of a normal mutex because operations may unlock from a different thread context.

`afs_wait_for_operation()` repeatedly asks `afs_select_fileserver()` for a viable server/address, issues the AFS or YFS RPC, waits for call completion, records call error/abort/responded state, then invokes operation callbacks based on cumulative result.

## State and Synchronization
Operations may hold `AFS_OPERATION_LOCK_0` and `AFS_OPERATION_LOCK_1`. Modification operations set `AFS_VNODE_MODIFYING` during preparation and clear it in `afs_put_operation()`. More-than-two vnode operations store additional vnode params in `op->more_files`.

## Risks
The custom I/O lock is easy to misuse: waiter removal, signal interruption, and lock transfer must remain paired. Operation cleanup owns many heterogeneous references: calls, server state arrays, server lists, volumes, keys, inodes, and optional operation payloads.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/fs_operation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/fs_probe.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/fs_probe.c

## Summary
Implements fileserver endpoint probing. It periodically sends `FS.GetCapabilities` to each known fileserver address, records responsive endpoints, detects YFS/AFS capability differences, updates RTT/preferred address state, and feeds the server rotation logic.

## Main Responsibilities
- Manages reference-counted `struct afs_endpoint_state` probe snapshots.
- Schedules fast and slow probe polling.
- Dispatches probes across all fileserver addresses by address preference.
- Processes probe results, errors, capabilities, RTT, and service upgrade.
- Provides wait helpers for operations needing responsive endpoints.
- Cleans up probe timers during namespace teardown.

## Key APIs
- `afs_fs_probe_fileserver()`.
- `afs_fileserver_probe_result()`.
- `afs_wait_for_fs_probes()`.
- `afs_probe_fileserver()`.
- `afs_fs_probe_dispatcher()`.
- `afs_wait_for_one_fs_probe()`.
- `afs_fs_probe_cleanup()`.

## Important Behavior
Responsive servers are moved to the slow probe list and nonresponsive servers to the fast list. Fast polling is 30 seconds; slow polling is 5 minutes.

Probe results distinguish local failures, unreachable/network failures, responded aborts, and successful replies. A YFS response sets `AFS_SERVER_FL_IS_YFS`; AFS capability word 0 controls `AFS_SERVER_FL_HAS_FS64`.

The best RTT endpoint becomes both `server->rtt` and `alist->preferred`. Responsive and failed endpoint sets are captured in `endpoint_state` so concurrent operation rotation is not disrupted by later probe rounds.

## State and Synchronization
`server->fs_lock` protects installation of new endpoint state. `server->probe_lock` protects probe-result aggregation. `net->fs_lock` protects fast/slow probe queues. Endpoint states are refcounted and freed by RCU.

## Risks
`afs_fs_probe_fileserver()` installs a new endpoint state before probes complete, so consumers must handle superseded states. Timer/work accounting uses `servers_outstanding`; missed decrements would affect namespace teardown waits.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/fs_probe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/fsclient.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/fsclient.c

## Summary
Implements AFS fileserver RPC client stubs. It encodes requests, decodes XDR replies, defines call types, and bridges high-level `afs_operation` requests to rxrpc calls for status, data I/O, namespace mutation, attributes, locks, capabilities, bulk status, and ACLs.

## Main Responsibilities
- Decodes common AFS XDR records: FIDs, fetch status, callbacks, volsync, and volume status.
- Encodes store-status attributes and request payloads.
- Implements `FS.FetchStatus`, `FS.FetchData`, and `FS.FetchData64`.
- Implements create, mkdir, remove, link, symlink, rename, store data, and setattr RPCs.
- Implements volume status, lock, callback give-up, capability probe, inline bulk status, fetch ACL, and store ACL RPCs.
- Defines `struct afs_call_type` instances for each RPC family.

## Key APIs
- `afs_fs_fetch_status()`.
- `afs_fs_fetch_data()`.
- `afs_fs_create_file()`, `afs_fs_make_dir()`.
- `afs_fs_remove_file()`, `afs_fs_remove_dir()`.
- `afs_fs_link()`, `afs_fs_symlink()`, `afs_fs_rename()`.
- `afs_fs_store_data()`, `afs_fs_setattr()`.
- `afs_fs_get_volume_status()`.
- `afs_fs_set_lock()`, `afs_fs_extend_lock()`, `afs_fs_release_lock()`.
- `afs_fs_give_up_all_callbacks()`.
- `afs_fs_get_capabilities()`.
- `afs_fs_inline_bulk_status()`.
- `afs_fs_fetch_acl()`, `afs_fs_store_acl()`.

## Important Behavior
Fetch-data decoding is phased: it reads the returned length, streams data directly into the netfs subrequest iterator, discards excess if needed, then decodes status/callback/volsync metadata. 64-bit fetch/store variants are selected when `AFS_SERVER_FL_HAS_FS64` is set.

Setattr with size changes uses `FS.StoreData`/`FS.StoreData64` with zero write size so file length can be changed; metadata-only setattr uses `FS.StoreStatus`.

`FS.GetCapabilities` is asynchronous and used by probe code. Its call type reports results through `afs_fileserver_probe_result()` and frees endpoint-state references in its destructor.

`FS.InlineBulkStatus` validates returned status and callback counts against `op->nr_files`; if the server returns invalid operation, the server and volume are marked as maybe lacking inline bulk support.

## State and Synchronization
Each RPC allocates an `afs_call`, fills `call->request`, assigns the primary FID for tracing, and dispatches with `afs_make_op_call()` or `afs_make_call()`. Reply decoding populates `op->file[]`, `op->more_files[]`, `op->volsync`, `op->volstatus`, or ACL pointers.

## Risks
Manual XDR sizing and padding are pervasive. A mismatch between allocated request/reply sizes and encoded fields can corrupt protocol handling. Inline bulk status has known interoperability handling for older OpenAFS status-version behavior and missing support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/fsclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/inode.c

## Summary
Owns AFS inode creation, status application, callback application, cache-cookie acquisition, getattr/setattr, drop, and eviction. It translates fileserver status records into Linux inode state and maintains coherency with AFS data-version and callback semantics.

## Main Responsibilities
- Initializes new inodes from AFS fetch status records.
- Applies status/callback updates to existing vnodes.
- Fetches status and root inode state from fileservers.
- Looks up/inserts inodes by AFS FID.
- Acquires fscache cookies for files, dirs, and symlinks.
- Implements `getattr`, `setattr`, inode drop, and eviction.
- Handles data-version jumps, deleted vnodes, and directory invalidation.

## Key APIs
- `afs_vnode_commit_status()`.
- `afs_fetch_status()`.
- `afs_iget()`.
- `afs_root_iget()`.
- `afs_getattr()`.
- `afs_setattr()`.
- `afs_drop_inode()`.
- `afs_evict_inode()`.

## Important Behavior
`afs_inode_init_from_status()` sets inode mode and operations based on AFS type. Symlinks with mode `0644` are treated as AFS mountpoints and exposed as automount directories.

`afs_apply_status()` rejects vnode type changes, updates owner/group/mode/timestamps/nlink, compares expected data-version deltas, invalidates directories or zaps file data on unexpected jumps, and updates netfs write sizes under inode locking.

`afs_vnode_commit_status()` handles inline error statuses such as `VNOVNODE`, speculative bulk-status results, callback promises, unlink nlink updates, and permit-cache updates.

`afs_setattr()` supports size, mode, uid, gid, mtime/touch-style changes. For truncation that only shortens local unwritten dirty data above remote size, it can avoid a server call and resize local state directly.

## State and Synchronization
Status and callback fields are protected by `vnode->cb_lock`. `validate_lock` blocks new writeback while setattr size changes are coordinated. Eviction waits for netfs I/O, flushes dirty directories/symlinks when needed, truncates pages, frees directory/symlink data, clears writeback state, relinquishes fscache, and drops permits/keys.

## Risks
Data-version handling is central: false expected-delta assumptions cause local invalidation, while missed jumps would leave stale data. `getattr()` reports server remote size for directories because local edited directory data may differ in allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/afs/internal.h

## Summary
Central private header for the Linux AFS client. It defines core structures, flags, state machines, inline helpers, and cross-file function declarations for cells, volumes, servers, vnodes, calls, operations, directory iteration, probing, locking, security, rxrpc, validation, and YFS support.

## Main Contents
- Mount context: `struct afs_fs_context`.
- RxRPC call model: `struct afs_call`, `struct afs_call_type`, call-state enum.
- Address and server discovery: address preferences, `afs_addr_list`, VL server structures, fileserver endpoint state.
- Cell/volume/server lifecycle structures.
- Vnode/inode state: `struct afs_vnode`, callback state, directory cache, locks, writeback keys.
- Operation wrapper: `struct afs_operation`, `struct afs_vnode_param`, `struct afs_operation_ops`.
- Permit cache, symlink cache, error accumulator, VL cursor, server rotation state.
- Declarations for all internal AFS source modules.
- Inline helpers for network namespace lookup, fscache auxiliary data, callbacks, directory invalidation, call extraction, and debug assertions.

## Key Interfaces
Declares APIs for:
- Directory search/edit/silly rename/dynroot/mountpoint handling.
- File operations, netfs request ops, writeback, and mmap invalidation.
- Fileserver RPC stubs, operations, probes, rotation, and server management.
- Inode lifecycle and validation.
- Security key/permit lookup.
- VLDB/VL server probing and volume management.
- YFS enhanced RPC variants and opaque ACL support.

## Important Details
`struct afs_vnode` embeds `struct netfs_inode` and stores AFS FID/status, callback counters, validation locks, directory and symlink caches, writeback keys, file lock queues, and mmap callback tracking.

`struct afs_operation` is the shared execution envelope for fileserver operations. It stores vnode params, dentries, mtime/ctime, operation-specific unions, cumulative errors, current server/address selection, and flags controlling retry, locking, async mode, and directory conflict handling.

`afs_make_op_call()` binds a prepared `afs_call` to the selected endpoint in `op->estate->addresses` and dispatches it through rxrpc. Extraction helpers set the call iterator for temporary fields, fixed buffers, or discard.

## Risks
This header is a dense coupling point: structure layout, flag semantics, and inline lifetime helpers are depended on across the entire AFS client. Many fields are protected by different locks or RCU domains, so consumers must follow the documented owning subsystem conventions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/main.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/main.c

## Summary
Module and per-network-namespace initialization for the AFS client filesystem. It creates workqueues, registers pernet state, initializes cells/proc/rxrpc transport, registers the filesystem, and tears everything down on module exit.

## Main Responsibilities
- Defines module metadata and parameters.
- Selects the initial `@sys` substitution string by architecture.
- Initializes `struct afs_net` for each network namespace.
- Creates global AFS workqueues.
- Registers pernet operations and filesystem type.
- Creates `/proc/fs/afs` symlink to per-net proc state.
- Cleans up workqueues, permits, proc entries, cells, servers, and sockets.

## Key APIs
- Module init: `afs_init()` via `late_initcall`.
- Module exit: `afs_exit()`.
- Pernet callbacks: `afs_net_init()` and `afs_net_exit()`.
- Globals: `afs_wq`, `afs_debug`, `afs_init_sysname`.

## Important Behavior
`afs_net_init()` initializes socket/work state, cell trees, dynamic-root IDR, probe queues, server outstanding count, sysname list, proc entries, cell database, and rxrpc socket in order. Error paths unwind partial initialization and mark the namespace non-live.

`afs_init()` allocates three workqueues: general AFS work, async call processing, and lock management. It then registers pernet state, filesystem support, and the proc symlink.

## State and Synchronization
`net->live` gates probe scheduling and namespace activity during teardown. `servers_outstanding` starts at 1 and is used with probe/server cleanup waits. `afs_exit()` performs an `rcu_barrier()` after destroying workqueues and cleaning permit caches.

## Risks
Initialization ordering matters: rxrpc socket creation depends on networking being ready, hence `late_initcall`. Error paths must mirror successful setup to avoid leaked workqueues, proc entries, net state, or IDR contents.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/misc.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/misc.c

## Summary
Contains miscellaneous error handling for AFS. It maps AFS, VL, UAE, RXKAD, RXGK, and Kerberos abort codes to Linux errno values, and prioritizes accumulated errors when an operation tries multiple endpoints.

## Main Responsibilities
- Converts remote abort codes into local negative errno values.
- Handles legacy VICE special errors and VL server errors.
- Handles unified AFS error-table codes.
- Handles rxrpc security abort codes for RXKAD and RXGK.
- Chooses which error should be reported from a sequence of failures.

## Key APIs
- `afs_abort_to_error()`.
- `afs_prioritise_error()`.

## Important Behavior
`afs_abort_to_error()` maps volume movement and availability errors to errno values used by higher-level retry logic, for example `VMOVED` to `-ENXIO`, `VBUSY` to `-EBUSY`, and `VNOVOL` to `-ENOMEDIUM`.

`afs_prioritise_error()` treats success as final, preserves higher-priority existing errors, records whether any server responded, and converts `-ECONNABORTED` through `afs_abort_to_error()` while marking the cumulative error as an abort.

## State and Synchronization
The file only mutates caller-owned `struct afs_error`; it has no independent locking or global state.

## Risks
Error priority directly affects server rotation and user-visible errno. Incorrect ordering could hide a meaningful remote abort behind a transient network failure, or conversely suppress retryable connectivity information.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/mntpt.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/mntpt.c

## Summary
Implements AFS mountpoint automount behavior. AFS mountpoints are represented as special symlinks or dynamic-root pseudo directories; this file converts them into submount filesystem contexts and manages expiry of resulting vfsmounts.

## Main Responsibilities
- Defines mountpoint inode and file operation tables.
- Rejects normal lookup/open on mountpoint placeholder directories.
- Parses mount parameters from pseudo-directory names or special symlink contents.
- Creates submounts through `fs_context_for_submount()` and `fc_mount()`.
- Tracks automounted vfsmounts for periodic expiry.
- Cancels the mountpoint expiry timer during shutdown.

## Key APIs
- `afs_d_automount()`.
- `afs_mntpt_inode_operations`.
- `afs_autocell_inode_operations`.
- `afs_mntpt_file_operations`.
- `afs_mntpt_kill_timer()`.

## Important Behavior
For dynamic-root pseudo directories, the dentry name selects the cell; a leading dot forces read/write volume mounting. The target volume is `root.cell`.

For real AFS mountpoint symlinks, the symlink content must end in `.` and is parsed as the submount source. The current source cell is inherited when present. Backup-volume mountpoints cannot cross into another backup volume.

Automounted mounts are placed on `afs_vfsmounts`, marked for expiry after 10 minutes, and the expiry worker reschedules while the list remains nonempty.

## State and Synchronization
The expiry list is a static global `LIST_HEAD`, with delayed work queued on `afs_wq`. Mount context setup may replace `fc->net_ns` with the source superblock's network namespace.

## Risks
Mountpoint parsing is intentionally strict about symlink size and trailing dot. The dynamic-root path depends on pseudo-directory flags from inode setup. Shutdown asserts the vfsmount expiry list is empty before cancelling delayed work.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/mntpt.c -->