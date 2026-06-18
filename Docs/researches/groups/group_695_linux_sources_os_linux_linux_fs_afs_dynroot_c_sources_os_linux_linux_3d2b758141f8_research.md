# Group Research: Linux AFS client subset A group 695

This grouped report covers the requested AFS files under `sources/os/linux/linux/fs/afs/`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/dynroot.c -->
# File Research: sources/os/linux/linux/fs/afs/dynroot.c

## Purpose
Implements the AFS dynamic root directory, where the root exposes known AFS cells as synthetic automount directories and exposes `@cell` / `.@cell` symlinks for the workstation cell.

## Main Responsibilities
- Creates pseudo inodes for dynroot, autocell mount directories, and `@cell` symlinks via `iget5_locked()`.
- Resolves dynroot path lookups to cells with `afs_lookup_cell()`, using dotted names as read/write volume selectors.
- Provides dynroot dentry operations, including automount dispatch through `afs_d_automount()`.
- Implements `readdir` for dynroot by walking `net->cells_dyn_ino` and emitting both undotted and dotted cell entries.

## Key Functions and Data
- `afs_dynroot_iget_root()` creates the synthetic root inode with `afs_dynroot_inode_operations` and `afs_dynroot_file_operations`.
- `afs_dynroot_lookup()` handles `@cell`, `.@cell`, and general cell-name lookup.
- `afs_dynroot_lookup_cell()` creates pseudo automount directories backed by looked-up cells.
- `afs_atcell_get_link()` resolves `@cell` and `.@cell` symlink targets from `net->ws_cell`.
- `afs_dynroot_readdir_cells()` emits active cells under the dynamic root.

## Important Details
- Pseudo inode numbers reserve `1` for root, `2`/`3` for `@cell`/`.@cell`, and then cell entries from `cell->dynroot_ino`.
- Dotted cell names use `cell->name - 1`, relying on cell names being allocated with a leading dot slot.
- `afs_dynroot_delete_dentry()` keeps only `@cell` symlink dentries around; synthetic cell dirs are dropped when unused.
- Dynamic root directories and autocell directories are read-only, no-atime pseudo directories.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/dynroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/file.c -->
# File Research: sources/os/linux/linux/fs/afs/file.c

## Purpose
Provides VFS file operations, address-space operations, netfs integration, mmap tracking, file open/release handling, and data fetch operation glue for regular AFS files.

## Main Responsibilities
- Registers regular-file operations in `afs_file_operations`, including reads, netfs writes, mmap, splice, fsync, and locking.
- Manages per-open authentication keys and per-vnode writeback key caching.
- Bridges netfs read requests to AFS/YFS `FetchData` operations.
- Tracks mmapped vnodes so callback invalidation can affect active mappings.
- Maintains inode size and cache coherency for fetched and written data.

## Key Functions and Data
- `afs_open()` requests a key, validates the vnode, caches a writeback key for write opens, and uses the fscache cookie.
- `afs_release()` fsyncs write opens, unuses fscache, drops keys, and prunes writeback keys.
- `afs_issue_read()` allocates an `afs_operation`, attaches the vnode and subrequest, and dispatches sync or async fetches.
- `afs_fetch_data_async_rx()` and `afs_read_receive()` process asynchronous RxRPC read progress and retry server rotation.
- `afs_req_ops` supplies netfs callbacks for request init/free, reads, writes, writeback, cache invalidation, and size updates.
- `afs_vm_ops` tracks mmap opens/closes and validates callbacks before `map_pages`.

## Important Details
- Direct I/O reads are routed to `netfs_unbuffered_read_iter()`, while buffered reads validate the vnode then call `filemap_read()`.
- `afs_set_i_size()` updates size under callback and inode locks, avoiding tearing on 32-bit systems and updating fscache metadata.
- Open mmaps are linked through `volume->open_mmaps` when `cb_nr_mmap` transitions from zero.
- Write begin rejects writes to vnodes marked `AFS_VNODE_DELETED`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/flock.c -->
# File Research: sources/os/linux/linux/fs/afs/flock.c

## Purpose
Implements AFS file locking for POSIX locks and BSD `flock()` by combining VFS local lock records with AFS server-side whole-file locks.

## Main Responsibilities
- Emulates partial-file locking over the AFS3 whole-file lock model.
- Manages vnode lock state, pending and granted lock queues, lock extension, unlock deferral, and callback-based retry.
- Issues server RPCs for `SetLock`, `ExtendLock`, and `ReleaseLock`.
- Integrates VFS lock copy/release hooks so local lock records stay tied to vnode server-lock state.

## Key Functions and Data
- `afs_lock()` handles POSIX locking commands, including `GETLK`, lock, and unlock.
- `afs_flock()` maps BSD flock semantics onto the same lock engine.
- `afs_do_setlk()` is the core state machine for local/server lock acquisition.
- `afs_lock_work()` extends granted locks, releases deferred locks, and wakes pending lockers.
- `afs_next_locker()` chooses the next pending lock and handles failed lock classes.
- `afs_lock_op_done()` records server lock acquisition time and schedules extension.

## Important Details
- AFS locks expire after about five minutes; extensions are scheduled at half the wait interval.
- Partial lock behavior depends on the mount flock mode: local, OpenAFS-compatible, strict, or write-lock-for-partial.
- Server contention uses callback breaks plus periodic retries because servers do not provide a lock wait queue.
- Permission is checked locally with `afs_check_permit()` because shared local read locks may not contact the server.
- If the vnode is deleted, pending lockers are failed with `-ENOENT` and the vnode lock state becomes `AFS_VNODE_LOCK_DELETED`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/flock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/fs_operation.c -->
# File Research: sources/os/linux/linux/fs/afs/fs_operation.c

## Purpose
Defines the lifecycle for fileserver-directed operations, including operation allocation, vnode I/O serialization, server iteration dispatch, completion handling, and cleanup.

## Main Responsibilities
- Allocates and initializes `struct afs_operation` objects against a volume and key.
- Provides a custom vnode I/O lock that can be handed between tasks without mutex ownership problems.
- Serializes operations on one or two vnodes in stable pointer order.
- Dispatches AFS or YFS RPCs through the operation’s `afs_operation_ops`.
- Applies success/aborted/failed callbacks and then releases all operation-owned references.

## Key Functions and Data
- `afs_alloc_operation()` pins the key and volume, snapshots volume callback/volsync state, and sets the initial error to `-EDESTADDRREQ`.
- `afs_begin_vnode_operation()` takes needed vnode I/O locks and snapshots fid/data-version/callback state.
- `afs_wait_for_operation()` loops through `afs_select_fileserver()`, issues RPCs, waits for calls, records response state, and invokes operation callbacks.
- `afs_end_vnode_operation()` drops I/O locks and dumps address-selection failures for relevant network errors.
- `afs_put_operation()` releases vnode refs, server state, server list, volume, key, and updates preferred address on successful response.
- `afs_do_sync_operation()` wraps begin, wait, and put for synchronous operations.

## Important Details
- Operations with held file locks are marked current-server-only in `afs_prepare_vnode()`.
- Modification operations set `AFS_VNODE_MODIFYING` and clear it in `afs_put_operation()`.
- Two-vnode lock acquisition orders by pointer value to avoid deadlocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/fs_operation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/fs_probe.c -->
# File Research: sources/os/linux/linux/fs/afs/fs_probe.c

## Purpose
Maintains fileserver endpoint probing, capability detection, responsiveness tracking, and periodic probe scheduling.

## Main Responsibilities
- Creates and publishes `afs_endpoint_state` records for each probe generation.
- Sends asynchronous `FS.GetCapabilities` probes to all known fileserver addresses.
- Records responsive and failed endpoints, RTT, YFS upgrade status, and FS64 capability.
- Provides wait helpers for operations that need responsive server endpoints.
- Runs fast/slow periodic probe queues to keep routing and NAT state fresh.

## Key Functions and Data
- `afs_fs_probe_fileserver()` builds a fresh endpoint state, assigns the address list, and probes each address by priority.
- `afs_fileserver_probe_result()` consumes call results and updates endpoint/server flags, RTT, preferred address, and failure masks.
- `afs_wait_for_fs_probes()` waits for one untried responsive endpoint, supersession, completion, or interrupt.
- `afs_wait_for_one_fs_probe()` waits up to two seconds for a specific server probe.
- `afs_fs_probe_dispatcher()` processes fast and slow probe queues and re-arms timers.
- `afs_probe_fileserver()` triggers immediate probing when rotation has exhausted addresses.

## Important Details
- Responding servers move to the slow queue; nonresponding servers move to the fast queue.
- AFS capability word 0 is used to set or clear `AFS_SERVER_FL_HAS_FS64`.
- YFS response upgrades set `AFS_ESTATE_IS_YFS` and `AFS_SERVER_FL_IS_YFS`.
- Old endpoint states are marked `AFS_ESTATE_SUPERSEDED` so waiters can restart against newer probe data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/fs_probe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/fsclient.c -->
# File Research: sources/os/linux/linux/fs/afs/fsclient.c

## Purpose
Implements AFS fileserver RPC client stubs and XDR marshalling/unmarshalling for AFS3 file service operations.

## Main Responsibilities
- Encodes requests and decodes replies for file status, data fetch/store, create/remove/link/symlink/rename, setattr, volume status, locks, callbacks, capabilities, inline bulk status, and ACL operations.
- Defines `afs_call_type` descriptors used by the RxRPC layer and `afs_operation` dispatcher.
- Handles streaming reply state machines for variable-sized or data-bearing replies.
- Selects 32-bit or 64-bit file data RPCs based on server capability.
- Reports protocol errors for malformed status, bad counts, or oversized strings.

## Key Functions and Data
- XDR helpers: `xdr_decode_AFSFid()`, `xdr_decode_AFSFetchStatus()`, `xdr_decode_AFSCallBack()`, `xdr_decode_AFSVolSync()`, `xdr_encode_AFS_StoreStatus()`, and `xdr_decode_AFSFetchVolumeStatus()`.
- Status/data RPCs: `afs_fs_fetch_status()`, `afs_fs_fetch_data()`, `afs_fs_fetch_data64()`.
- Mutation RPCs: `afs_fs_create_file()`, `afs_fs_make_dir()`, `afs_fs_remove_file()`, `afs_fs_remove_dir()`, `afs_fs_link()`, `afs_fs_symlink()`, `afs_fs_rename()`.
- Write/setattr RPCs: `afs_fs_store_data()`, `afs_fs_store_data64()`, `afs_fs_setattr()`, and size-specific StoreData variants.
- Lock RPCs: `afs_fs_set_lock()`, `afs_fs_extend_lock()`, `afs_fs_release_lock()`.
- Probe/capability RPCs: `afs_fs_get_capabilities()` and `afs_deliver_fs_get_capabilities()`.
- Bulk/ACL RPCs: `afs_fs_inline_bulk_status()`, `afs_fs_fetch_acl()`, and `afs_fs_store_acl()`.

## Important Details
- `xdr_decode_AFSFetchStatus()` accepts the OpenAFS `InlineBulkStatus` zero-version error quirk when an inline abort code is present.
- `FS.FetchData` delivery first extracts a returned data length, streams payload into the netfs subrequest iterator, discards excess, then decodes status/callback/volsync.
- `FS.GetVolumeStatus` parses multiple padded strings and bounds them with `AFSNAMEMAX`.
- `FS.GetCapabilities` is asynchronous and reports results through probe callbacks; its destructor drops the endpoint-state reference.
- `FS.InlineBulkStatus` validates returned status and callback counts against `op->nr_files`; unsupported servers set `AFS_SERVER_FL_NO_IBULK`.
- ACL fetch allocates a flexible `afs_acl` payload sized from the server-returned opaque ACL length.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/fsclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/inode.c -->
# File Research: sources/os/linux/linux/fs/afs/inode.c

## Purpose
Manages AFS vnode/inode initialization, status application, callback commitment, inode lookup, root inode creation, attributes, eviction, and setattr.

## Main Responsibilities
- Converts AFS file status records into Linux inode mode, ownership, size, ops, mapping ops, and cache state.
- Applies returned vnode status and callback promises after fileserver operations.
- Detects data-version jumps and invalidates cached directory/file data when needed.
- Creates and looks up inodes by AFS fid.
- Handles getattr, drop-inode policy, eviction cleanup, and setattr operations.

## Key Functions and Data
- `afs_inode_init_from_status()` initializes new inodes from server status and assigns file, dir, symlink, or mountpoint operations.
- `afs_apply_status()` updates existing inodes, handles data-version changes, size changes, directory invalidation, and page-cache sizing.
- `afs_vnode_commit_status()` applies status/callback results or deletion/unlink outcomes under `vnode->cb_lock`.
- `afs_fetch_status()` performs a one-vnode fetch-status operation.
- `afs_iget()` and `afs_root_iget()` create regular and root inodes from fids/status.
- `afs_getattr()` validates stale callback state unless `AT_STATX_DONT_SYNC` is used.
- `afs_evict_inode()` flushes directory/symlink data, waits for netfs I/O, clears fscache/writeback/key/permit state.
- `afs_setattr()` coordinates size and metadata changes through AFS/YFS setattr RPCs and netfs/fscache resizing.

## Important Details
- Symlinks with mode `0644` are treated as AFS mountpoints and exposed as automount directories.
- Directories are marked single-no-upload and assumed locally valid after initialization.
- Data-version mismatch can mark files for data zap or invalidate directory contents.
- `afs_get_inode_cache()` builds an fscache key from vnode id, unique, and extended vnode id fields for YFS-compatible 96-bit vnode IDs.
- Pseudodir inodes use immediate drop semantics in `afs_drop_inode()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/internal.h -->
# File Research: sources/os/linux/linux/fs/afs/internal.h

## Purpose
Central internal header for the Linux AFS client. It defines shared structures, state enums, flags, inline helpers, operation contracts, and cross-file prototypes.

## Main Responsibilities
- Defines mount context, per-network namespace, cell, VL server, fileserver, volume, vnode, call, operation, callback, permit, and address-list data models.
- Declares all major AFS subsystem entry points used across the directory, cell, server, volume, RPC, validation, writeback, lock, proc, and mountpoint code.
- Provides inline helpers for net namespace lookup, vnode/inode conversion, call state transitions, reply extraction setup, callback promise state, dentry data-version updates, and operation error accumulation.
- Defines debugging and assertion macros used throughout the AFS client.

## Key Structures
- `struct afs_net`: per-net namespace state, including cells, server probe queues, proc entries, socket state, sysnames, address preferences, and counters.
- `struct afs_cell`: cell identity, VL server list, root volume, DNS state, alias tracking, proc links, and dynamic-root inode allocation.
- `struct afs_server` / `struct afs_endpoint_state`: fileserver identity, endpoint list, probe state, service/capability flags, and RTT/preferred-address data.
- `struct afs_volume`: live volume state, server list, fscache volume, callback counters, volume type/name, and open mmap list.
- `struct afs_vnode`: inode-private state including fid, status, callback promise, locks, directory/symlink data, writeback keys, permit cache, and netfs inode.
- `struct afs_operation`: high-level fileserver operation wrapper for vnode params, RPC selection, server/address rotation, cumulative errors, and operation-specific unions.
- `struct afs_call`: RxRPC call state, request/reply buffers, iterator state, call type, server/probe refs, error/abort state, and unmarshalling scratch fields.

## Key Contracts
- `struct afs_operation_ops` supplies `issue_afs_rpc`, `issue_yfs_rpc`, `success`, `aborted`, `failed`, `edit_dir`, and `put` hooks.
- `afs_make_op_call()` binds an operation-selected server endpoint to a call and invokes `afs_make_call()`.
- `afs_set_call_complete()` atomically transitions call state to complete, records local/remote errors, traces, and drops deferred refs when needed.
- `afs_op_set_vnode()` marks a vnode parameter as needing the operation I/O lock by default.
- `afs_invalidate_dir()` clears directory-valid state and bumps invalidation stats only on first transition.

## Important Details
- Vnode lock states enumerate the whole server lock lifecycle from no lock through waiting, setting, granted, extending, unlocking, and deleted.
- AFS operation flags track stop/retry, volume errors, current-server-only, uninterruptible operation, held I/O locks, directory conflict, async mode, and opcode downgrade.
- Callback promise expiration uses `AFS_NO_CB_PROMISE == TIME64_MIN`.
- The header includes prototypes for both AFS3 and YFS RPC clients, reflecting the common operation layer.
- Assertion macros are enabled in the visible `#if 1` block, so failed `ASSERT*` checks call `BUG()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/main.c -->
# File Research: sources/os/linux/linux/fs/afs/main.c

## Purpose
Module and per-network-namespace initialization/cleanup for the Linux AFS client.

## Main Responsibilities
- Defines module metadata and parameters: `debug` and `rootcell`.
- Creates global workqueues for general AFS work, asynchronous calls, and lock management.
- Registers per-net namespace state and initializes per-net AFS structures.
- Initializes proc entries, cell database, RxRPC socket, filesystem registration, and `/proc/fs/afs` symlink.
- Tears down all global and per-net resources on namespace exit or module exit.

## Key Functions and Data
- `afs_net_init()` initializes `struct afs_net`, sysname defaults, procfs, cell DB, and RxRPC transport.
- `afs_net_exit()` marks the namespace dead and purges probes, cells, servers, sockets, procfs, sysnames, IDs, and address preferences.
- `afs_init()` allocates workqueues, registers pernet ops, registers the filesystem, and creates the proc symlink.
- `afs_exit()` removes procfs, unregisters filesystem/pernet ops, destroys workqueues, clears permit cache, and waits for RCU.
- `afs_init_sysname` is selected at compile time by architecture.

## Important Details
- Initialization runs as `late_initcall()` because the RxRPC socket requires networking to be available.
- `net->servers_outstanding` starts at `1`, supporting probe/server cleanup wait semantics.
- Error paths unwind in reverse order and mark `net->live = false` before teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/misc.c -->
# File Research: sources/os/linux/linux/fs/afs/misc.c

## Purpose
Provides shared error translation and error-prioritization logic for AFS operations.

## Main Responsibilities
- Maps AFS abort codes, VL server aborts, Unified AFS Error codes, RXKAD/RXGK authentication errors, and generic Rx errors to Linux negative errno values.
- Accumulates and prioritizes errors from multi-server or multi-address operation attempts.

## Key Functions and Data
- `afs_abort_to_error()` converts protocol abort codes to Linux errors.
- `afs_prioritise_error()` updates `struct afs_error` with a preferred cumulative error, response flag, and abort classification.

## Important Details
- Volume and VL errors are mapped to conventional filesystem/network errno values such as `-ENOMEDIUM`, `-ENOSPC`, `-EDQUOT`, `-EBUSY`, and `-ENXIO`.
- Authentication failures map to key errors such as `-EKEYREJECTED`, `-EKEYEXPIRED`, or `-ENOPKG`.
- Prioritization prefers more informative responded/abort errors over transport failures and preserves higher-priority local/network failures according to the fallthrough chain.
- `-ECONNABORTED` is converted through `afs_abort_to_error()` and marks the cumulative error as an abort.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/mntpt.c -->
# File Research: sources/os/linux/linux/fs/afs/mntpt.c

## Purpose
Implements AFS mountpoint and autocell automount handling.

## Main Responsibilities
- Exposes mountpoint inode/file operations that reject direct lookup/open with `-EREMOTE`.
- Parses mountpoint symlink content or pseudo-directory names into a submount `fs_context`.
- Creates automounted AFS submounts and manages their expiry list/timer.
- Handles autocell pseudo directories by mapping the dentry name to `root.cell`.

## Key Functions and Data
- `afs_mntpt_set_params()` fills an AFS submount context from a mountpoint dentry.
- `afs_mntpt_do_automount()` creates an `fs_context` for a submount and mounts it.
- `afs_d_automount()` is the dentry automount hook used by dynroot and mountpoint dentries.
- `afs_mntpt_expiry_timed_out()` marks tracked mounts for expiry and reschedules if needed.
- `afs_mntpt_kill_timer()` cancels the expiry timer during cleanup.

## Important Details
- Pseudo-directory autocell mounts use the dentry name as the cell name and mount `root.cell`.
- Dotted autocell names force read/write volume type.
- Regular AFS mountpoints are encoded as special symlink content ending in `.`.
- Backup-volume mountpoints cannot recursively cross to another backup volume.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/mntpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/proc.c -->
# File Research: sources/os/linux/linux/fs/afs/proc.c

## Purpose
Implements the AFS procfs control and inspection interface for cells, rootcell, address preferences, volume/server status, sysname substitution, and statistics.

## Main Responsibilities
- Creates per-net `/proc/net/afs` entries and per-cell proc subdirectories.
- Displays known cells, VL servers, fileservers, volumes, address preferences, sysnames, and statistics.
- Accepts writes to add cells, set the root cell, configure `@sys` substitutions, and update address preferences.
- Safely iterates RCU-protected cell/server/volume lists and sysname state.

## Key Functions and Data
- `afs_proc_init()` creates `cells`, `rootcell`, `servers`, `stats`, `sysname`, and `addr_prefs`.
- `afs_proc_cell_setup()` creates per-cell `vlservers` and `volumes` files.
- `afs_proc_cells_write()` supports `add <cellname> <addr-list>` and pins manually added cells against GC.
- `afs_proc_rootcell_write()` initializes the workstation cell if it has not already been set.
- `afs_proc_sysname_write()` replaces the `@sys` substitution list with validated tokens.
- `afs_proc_servers_show()` reports fileserver UUIDs, refs/activity, probe state, endpoint list, RTT, errors, and priorities.
- `afs_proc_stats_show()` reports directory and file read/write counters.

## Important Details
- Cell and server listings use RCU sequence helpers; sysname iteration uses `net->sysnames_lock`.
- `sysname` writes reject recursive `@sys` suffixes, slash-containing names, invalid dot names, overlong names, and more than `AFS_NR_SYSNAME` substitutions.
- `rootcell` writes reject dotted names and names containing `/`, and only succeed before a workstation cell already exists.
- DNS source/status strings are normalized for VL server display.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/protocol_afs.h -->
# File Research: sources/os/linux/linux/fs/afs/protocol_afs.h

## Purpose
Defines small AFS protocol constants related to fileserver capabilities.

## Main Responsibilities
- Sets the maximum capabilities word count for AFS capability replies.
- Defines AFS3 fileserver capability bits in capability word 0.

## Key Constants
- `AFSCAPABILITIESMAX`: maximum number of words in a capability set, `196`.
- `AFS3_VICED_CAPABILITY_ERRORTRANS`: server uses Unified AFS Error translation.
- `AFS3_VICED_CAPABILITY_64BITFILES`: server supports `FetchData64` and `StoreData64`.
- `AFS3_VICED_CAPABILITY_WRITELOCKACL`: server can lock without lock permission.
- `AFS3_VICED_CAPABILITY_SANEACLS`: ACL sanity capability, marked “don’t use”.

## Important Details
- `fs_probe.c` consumes `AFS3_VICED_CAPABILITY_64BITFILES` to set `AFS_SERVER_FL_HAS_FS64`, which drives 64-bit file data RPC selection in `fsclient.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/protocol_afs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/protocol_uae.h -->
# File Research: sources/os/linux/linux/fs/afs/protocol_uae.h

## Purpose
Defines Universal AFS Error (UAE) abort code constants.

## Main Responsibilities
- Provides a contiguous enum of UAE error codes starting at `0x2f6df00`.
- Mirrors many Unix/Linux errno meanings into AFS protocol abort namespace constants.
- Supplies constants consumed by error translation in `misc.c`.

## Key Content
- Basic filesystem/process errors: `UAEPERM`, `UAENOENT`, `UAEIO`, `UAEACCES`, `UAEBUSY`, `UAEEXIST`, `UAENOTDIR`, `UAEISDIR`.
- Filesystem limit/state errors: `UAEFBIG`, `UAENOSPC`, `UAEROFS`, `UAEMLINK`, `UAENAMETOOLONG`, `UAENOTEMPTY`, `UAEOVERFLOW`, `UAEDQUOT`, `UAENOMEDIUM`.
- Network/socket errors: `UAENETUNREACH`, `UAECONNABORTED`, `UAECONNRESET`, `UAETIMEDOUT`, `UAECONNREFUSED`, `UAEHOSTDOWN`, `UAEHOSTUNREACH`.
- Miscellaneous protocol/system errors through `UAEMEDIUMTYPE`.

## Important Details
- `misc.c` maps only selected UAE constants to Linux errno; unmapped abort codes fall back through the default remote I/O path.
- The file is protocol data only and contains no functions or include guards in the visible content.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/protocol_uae.h -->