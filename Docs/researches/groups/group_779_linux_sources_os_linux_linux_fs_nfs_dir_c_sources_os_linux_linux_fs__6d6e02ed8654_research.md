# Group Research: group_779_linux_sources_os_linux_linux_fs_nfs_dir_c_sources_os_linux_linux_fs__6d6e02ed8654

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/dir.c -->
# File Research: sources/os/linux/linux/fs/nfs/dir.c

## Role

`dir.c` is the NFS client’s directory and name-resolution implementation. It supplies directory file operations, dentry operations, VFS inode operations for namespace mutations, readdir caching, lookup revalidation, access permission caching, and NFS-specific unlink/rename behavior.

Major exported surfaces include `nfs_dir_operations`, `nfs_dir_aops`, `nfs_dentry_operations`, `nfs4_dentry_operations`, `nfs_lookup`, `nfs_atomic_open`, `nfs_atomic_open_v23`, `nfs_create`, `nfs_mknod`, `nfs_mkdir`, `nfs_rmdir`, `nfs_unlink`, `nfs_symlink`, `nfs_link`, `nfs_rename`, `nfs_access_get_cached`, `nfs_access_add_cache`, `nfs_may_open`, and `nfs_permission`.

## Directory Reading And Cache Model

The file implements a custom readdir cache stored in folios via `struct nfs_cache_array`. Each array stores directory cookies, inode numbers, names, d_type, a change attribute, EOF/full flags, and an ordered-cookie hint. Names are copied with `nfs_readdir_copy_name()` and released by `nfs_readdir_clear_array()` through `nfs_dir_aops.free_folio`.

`nfs_readdir()` is the central path. It creates a `struct nfs_readdir_descriptor`, revalidates the mapping, chooses READDIRPLUS via `nfs_use_readdirplus()`, searches or fills cached folios, emits entries with `nfs_do_filldir()`, and stores cursor state back in `struct nfs_open_dir_context`.

The cache is indexed by `nfs_readdir_folio_cookie_hash()`, which hashes NFS cookies into page-cache indexes with a bounded 18-bit hash space. Cookie and position handling differs for 32-bit APIs through `nfs_readdir_use_cookie()`, falling back to positional offsets when full cookies cannot be safely represented.

When cached cookie lookup fails, `uncached_readdir()` asks the server starting at the problematic cookie and emits temporary folios without inserting them into the page cache. This handles deleted entries or server cookie loss without corrupting the primary directory cache.

## READDIRPLUS And Dcache Priming

`nfs_readdir_entry_decode()` uses `xdr_decode()` and, for READDIRPLUS, calls `nfs_prime_dcache()` to populate or refresh child dentries from returned filehandles and attributes. `nfs_prime_dcache()` validates names, rejects `.`/`..`, embedded NUL and `/`, compares fsid/fileid/filehandle, refreshes matching inodes, invalidates stale mismatches, and uses `d_alloc_parallel()`/`d_splice_alias()` for concurrent lookup-safe insertion.

The file tracks lookup cache hits and misses per open directory. `nfs_readdir_record_entry_cache_hit()` and `nfs_readdir_record_entry_cache_miss()` feed the heuristic in `nfs_use_readdirplus()`. `nfs_lookup_advise_force_readdirplus()` nudges future readdir calls when ordinary lookup indicates READDIRPLUS may help.

## Dentry Revalidation

The dentry verifier is based on the parent directory change attribute stored in `dentry->d_time`. `nfs_force_lookup_revalidate()` advances the directory cache-change attribute. `nfs_set_verifier()` records a verifier and tags it when a directory or file read delegation allows trusted revalidation.

`nfs_lookup_revalidate()` and `nfs4_lookup_revalidate()` drive dcache validation. They handle negative dentries, RCU pathwalk constraints, close-to-open checks, `LOOKUP_REVAL`, `LOOKUP_OPEN`, atomic-open shortcuts, delegated dentries, case-insensitive server behavior, and stale inode detection. Full validation goes through `NFS_PROTO(dir)->lookup()` and compares returned filehandles with the cached inode.

`block_revalidate()` and `unblock_revalidate()` use `dentry->d_fsdata == NFS_FSDATA_BLOCKED` to pause lookup/open races during unlink or overwrite rename.

## Namespace Operations

`nfs_lookup()` performs ordinary lookup unless skipped for exclusive create or rename target. It allocates fhandle/fattr, performs protocol lookup, handles negative dentries including case-insensitive verifier handling, creates/obtains an inode via `nfs_fhget()`, and splices aliases.

`nfs_atomic_open()` handles NFSv4-style open-context based atomic open, including create/truncate attributes, O_DIRECTORY fallback, regular-file enforcement, and `FMODE_CAN_ODIRECT`. `nfs_atomic_open_v23()` implements the NFSv2/v3 create-plus-lookup/open path.

Creation helpers include `nfs_do_create()`, `nfs_create()`, `nfs_mknod()`, `nfs_mkdir()`, and `nfs_instantiate()`. Failed creates and mknods drop dentries because a server-side success may have been hidden by reply-path errors.

Removal and rename logic is NFS-specific:
- `nfs_rmdir()` serializes positive directory removal with `rmdir_sem` and clears link count on success.
- `nfs_unlink()` performs sillyrename when the dentry has active references, otherwise blocks revalidation and calls `nfs_safe_remove()`.
- `nfs_safe_remove()` invalidates link state and calls protocol `remove`.
- `nfs_rename()` handles busy overwrite targets with sillyrename, blocks target revalidation when needed, may sync regular files for unsafe cross-directory renames, waits for async RPC completion, invalidates old inode attributes, moves dentries locally, and drops replaced target link state.

`nfs_symlink()` allocates a folio containing the link body, sends the SYMLINK RPC, then opportunistically inserts the folio into the new inode mapping. `nfs_link()` syncs regular files before hardlink RPC and installs the target dentry on success.

## Access Permission Cache

The file maintains a global LRU and per-inode rb-tree of `struct nfs_access_entry` keyed by fsuid, fsgid, and supplementary groups. `nfs_access_get_cached()` first tries an RCU fast path for the most recent entry, then a locked rb-tree lookup. Entries are invalidated on `NFS_INO_INVALID_ACCESS` and also checked against login time to avoid reusing credentials across changed login sessions.

`nfs_access_add_cache()` copies credential identity and returned access mask, inserts/replaces in the rb-tree, updates LRU/accounting, and enforces `nfs_access_max_cachesize`. The shrinker hooks `nfs_access_cache_scan()` and `nfs_access_cache_count()` reclaim entries under memory pressure.

`nfs_permission()` maps VFS permission checks onto NFS ACCESS RPCs when available. It avoids unnecessary checks for symlinks, directory write-only operations, and atomic-open regular-file opens. It falls back to inode revalidation plus `generic_permission()` if ACCESS is unsupported.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/direct.c -->
# File Research: sources/os/linux/linux/fs/nfs/direct.c

## Role

`direct.c` implements uncached NFS I/O for `O_DIRECT` and NFS swap I/O. It bypasses the page cache for application buffers while preserving NFS semantics around short I/O, unstable writes, commits, pNFS data-server commits, lock contexts, and async completion.

Primary entry points are `nfs_file_direct_read()`, `nfs_file_direct_write()`, `nfs_swap_rw()`, `nfs_init_directcache()`, and `nfs_destroy_directcache()`.

## Direct Request Lifecycle

Each operation uses `struct nfs_direct_req`, allocated from `nfs_direct_cachep` by `nfs_direct_req_alloc()`. The request tracks inode, open context, lock context, I/O start, max byte count, completed count, first error, async `kiocb`, commit info, work item, spinlock, completion, and internal refcounts.

`get_dreq()` and `put_dreq()` count outstanding pageio/commit work. Final completion flows through `nfs_direct_complete()`, which calls `inode_dio_end()`, completes async `kiocb` if present, signals synchronous waiters, and drops the final kref.

## Direct Reads

`nfs_file_direct_read()` validates zero length, allocates a direct request, captures open and lock contexts, starts direct I/O exclusion unless this is swap, and schedules reads through `nfs_direct_read_schedule_iovec()`.

`nfs_direct_read_schedule_iovec()` pins user pages with `iov_iter_get_pages_alloc2()`, creates `nfs_page` requests, adds them to an NFS pageio descriptor, releases page references, and completes pageio. If no bytes were scheduled, it returns the initial error.

Read completion uses `nfs_direct_read_completion()`. It updates byte counts through `nfs_direct_count_bytes()`, handles EOF/error truncation, marks user-backed pages dirty when needed, releases requests, updates delegated atime, and completes the direct request when all sub-I/O finishes.

## Direct Writes And Commit Flow

`nfs_file_direct_write()` applies `generic_write_checks()` except for swap, rejects unsupported append semantics through higher-level flag checks, allocates a direct request, captures contexts, initializes pNFS DS commit info, starts direct write exclusion, schedules writes with `nfs_direct_write_schedule_iovec()`, invalidates overlapping page cache after non-swap direct writes, waits or returns queued async status, advances `ki_pos`, and invalidates fscache state.

`nfs_direct_write_schedule_iovec()` pins pages, creates `nfs_page` requests, and adds them to write pageio with stable mode `FLUSH_STABLE` for swap or `FLUSH_COND_STABLE` for ordinary direct writes. Soft `-EAGAIN` conditions defer remaining requests onto commit lists for rescheduling.

`nfs_direct_write_completion()` updates completed byte counts, grows local i_size when needed, records delegated mtime, and either releases stable writes or marks unstable writes for commit. It sets flags such as `NFS_ODIRECT_DO_COMMIT`, `NFS_ODIRECT_RESCHED_WRITES`, or `NFS_ODIRECT_DONE`.

Unstable writes are committed by `nfs_direct_commit_schedule()` and `nfs_direct_commit_complete()`. Commit verifier mismatch causes writes to be rescheduled; commit errors are fatal and truncate the reported byte count. `nfs_direct_write_schedule_work()` runs on `nfsiod_workqueue` to commit, reschedule writes, or clear failed requests and zap the mapping.

## Error And Short-I/O Semantics

`nfs_direct_handle_truncated()` and `nfs_direct_count_bytes()` maintain `max_count`, `count`, and `error` so the final result follows kernel direct-I/O conventions: return completed bytes when any exist, otherwise return the first error.

`nfs_direct_truncate_request()` trims the final reported byte count to the start of a failed request. Redo paths use `NFS_IOHDR_REDO` and avoid double completion accounting.

## Integration Points

The file depends on NFS pageio, pNFS commit handling, lock contexts, fscache invalidation, and inode direct-I/O exclusion helpers. It exports `nfs_dreq_bytes_left()` for pNFS layout code to determine remaining direct-I/O range.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/direct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/dns_resolve.c -->
# File Research: sources/os/linux/linux/fs/nfs/dns_resolve.c

## Role

`dns_resolve.c` resolves NFS hostnames to socket addresses. It has two build-time modes: direct kernel DNS resolver use under `CONFIG_NFS_USE_KERNEL_DNS`, or a SUNRPC cache/upcall resolver path when kernel DNS is not used.

The exported resolver function is `nfs_dns_resolve_name()`.

## Kernel DNS Mode

When `CONFIG_NFS_USE_KERNEL_DNS` is enabled, `nfs_dns_resolve_name()` calls `dns_query()` and converts the returned textual IP address into a `sockaddr` with `rpc_pton()`. Failed DNS lookup maps to `-ESRCH`. The temporary address string is freed after conversion.

## Upcall Cache Mode

Without kernel DNS, the file defines `struct nfs_dns_ent`, a SUNRPC cache entry containing hostname, address, address length, cache header, and RCU free state. Entries are hashed by hostname using a 4-bit hash table.

The cache implementation provides:
- `nfs_dns_ent_alloc()`, `nfs_dns_ent_init()`, `nfs_dns_ent_update()`, and `nfs_dns_ent_put()` for allocation, copy/update, and RCU freeing.
- `nfs_dns_match()` and `nfs_dns_hash()` for cache identity.
- `nfs_dns_request()` and `nfs_dns_upcall()` for userspace resolver upcalls through rpc_pipefs/cache infrastructure.
- `nfs_dns_parse()` for userspace replies containing IP address, hostname, and TTL.
- `nfs_dns_show()` for seq_file cache display.

`nfs_dns_resolve_name()` builds a key from the requested hostname, obtains the network namespace’s `nfs_dns_resolve` cache from `struct nfs_net`, waits for upcall completion through `do_cache_lookup_wait()`, copies the resolved address to caller storage, maps negative cache entries to `-ESRCH`, and returns address length or an error.

## Namespace And Pipefs Lifecycle

`nfs_dns_resolver_cache_init()` creates a per-net cache from `nfs_dns_resolve_template` and registers it with NFS cache infrastructure. `nfs_dns_resolver_cache_destroy()` unregisters and destroys it.

`nfs_dns_resolver_init()` registers per-net operations and an rpc_pipefs notifier. The notifier registers/unregisters the cache for each rpc_pipefs mount/umount event. `nfs_dns_resolver_destroy()` reverses those registrations.

## Error Handling

The upcall path distinguishes missing cache allocation (`-ENOMEM`), pending/expired entries (`-ETIMEDOUT` or `-EAGAIN` internally), negative DNS entries (`-ENOENT` mapped to `-ESRCH`), and caller buffer too small (`-EOVERFLOW`).
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/dns_resolve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/dns_resolve.h -->
# File Research: sources/os/linux/linux/fs/nfs/dns_resolve.h

## Role

`dns_resolve.h` declares the NFS DNS resolver interface and the maximum hostname length used by the userspace-upcall parser.

`NFS_DNS_HOSTNAME_MAXLEN` is `128`.

## Interfaces

The header declares `nfs_dns_resolve_name()` for resolving a hostname in a network namespace into a `sockaddr_storage`.

When `CONFIG_NFS_USE_KERNEL_DNS` is enabled, resolver cache lifecycle functions are inline no-ops because `dns_resolve.c` uses `dns_query()` directly. Otherwise, it declares:
- `nfs_dns_resolver_init()`
- `nfs_dns_resolver_destroy()`
- `nfs_dns_resolver_cache_init(struct net *net)`
- `nfs_dns_resolver_cache_destroy(struct net *net)`

## Integration

This header is included by NFS resolver setup code and by `dns_resolve.c`. It hides the implementation difference between kernel DNS and rpc_pipefs cache/upcall DNS.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/dns_resolve.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/export.c -->
# File Research: sources/os/linux/linux/fs/nfs/export.c

## Role

`export.c` implements `export_operations` for re-exporting an NFS mount through Linux exportfs. It converts NFS inodes to export file handles and reconstructs dentries from those handles.

The exported operations structure is `nfs_export_ops`.

## File Handle Encoding

`nfs_encode_fh()` writes an export file handle containing:
- high 32 bits of the NFS fileid,
- low 32 bits of the fileid,
- inode type bits,
- embedded server NFS filehandle.

It deliberately uses `EXPORT_OP_NOSUBTREECHK`; comments state subtree checking is avoided because embedding parent filehandles may exceed available handle space.

If caller-provided storage is too small, it updates `*max_len` with the required length and returns `FILEID_INVALID`.

## File Handle Decoding

`nfs_fh_to_dentry()` validates handle bounds and type length, extracts the embedded NFS filehandle, builds minimal fattr data from stored fileid/type, and first tries `nfs_ilookup()`. If the inode is not already cached, it performs protocol `getattr()` using the embedded filehandle, then obtains an inode with `nfs_fhget()` and returns `d_obtain_alias()`.

Invalid or mismatched handles return `NULL`, which exportfs interprets as stale where appropriate. RPC/getattr failures return `ERR_PTR(ret)`.

## Parent Lookup

`nfs_get_parent()` uses protocol `lookupp` to obtain the parent filehandle and attributes for a dentry’s inode. If the protocol lacks `lookupp`, it returns `-EACCES`. Otherwise it creates the parent inode with `nfs_fhget()` and returns `d_obtain_alias()`.

## Export Flags

`nfs_export_ops.flags` marks NFS export behavior as remote and nonlocal:
`EXPORT_OP_NOWCC`, `EXPORT_OP_NOSUBTREECHK`, `EXPORT_OP_CLOSE_BEFORE_UNLINK`, `EXPORT_OP_REMOTE_FS`, `EXPORT_OP_NOATOMIC_ATTR`, `EXPORT_OP_FLUSH_ON_CLOSE`, and `EXPORT_OP_NOLOCKS`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/file.c -->
# File Research: sources/os/linux/linux/fs/nfs/file.c

## Role

`file.c` is the NFS regular-file VFS bridge. It provides file operations, address-space operations, mmap behavior, cached read/write paths, direct-I/O dispatch, fsync/commit integration, swapfile hooks, and lock/flock handling.

Main exported surfaces include `nfs_file_operations`, `nfs_file_aops`, `nfs_check_flags()`, `nfs_file_release()`, `nfs_file_llseek()`, `nfs_file_read()`, `nfs_file_splice_read()`, `nfs_file_mmap_prepare()`, `nfs_file_fsync()`, `nfs_truncate_last_folio()`, `nfs_file_write()`, `nfs_lock()`, and `nfs_flock()`.

## Open, Release, Seek, Flush

`nfs_check_flags()` rejects `O_APPEND | O_DIRECT`, because NFS direct writes do not provide atomic append semantics.

`nfs_file_open()` updates stats, checks flags, calls `nfs_open()`, and enables `FMODE_CAN_ODIRECT` on success. `nfs_file_release()` clears the open context and releases fscache file state.

`nfs_file_llseek()` revalidates file size for `SEEK_END`, `SEEK_DATA`, and `SEEK_HOLE`, then uses `generic_file_llseek()`.

`nfs_file_flush()` writes back dirty pages for writable files and reports writeback errors sampled from the mapping.

## Cached And Direct Reads

`nfs_file_read()` dispatches `IOCB_DIRECT` to `nfs_file_direct_read()`. Cached reads call `nfs_start_io_read()`, revalidate the mapping, use `generic_file_read_iter()`, update normal read byte stats, and call `nfs_end_io_read()`.

`nfs_file_splice_read()` follows the same revalidation and I/O exclusion pattern around `filemap_splice_read()`.

## Mmap And Folio Operations

`nfs_file_mmap_prepare()` calls `generic_file_mmap_prepare()`, installs `nfs_file_vm_ops`, and revalidates the mapping.

`nfs_vm_page_mkwrite()` handles shared writable mmap faults. It waits for fscache/private state, waits for invalidation, locks the folio, waits for writeback, verifies mapping and page length, flushes incompatible state, and calls `nfs_update_folio()`. Failure maps to `VM_FAULT_SIGBUS`.

`nfs_file_aops` wires NFS read/write helpers into the page cache: `read_folio`, `readahead`, `writepages`, `write_begin`, `write_end`, invalidation, release, migration, laundering, dirty/writeback classification, swap hooks, and direct swap I/O.

## Cached Writes

`nfs_write_begin()` truncates the last folio when extending past EOF, obtains a write folio, flushes incompatible pending state, and may perform read-modify-write if a partial non-uptodate folio should be read first. That decision is controlled by `nfs_want_read_modify_write()` and pNFS layout requirements.

`nfs_write_end()` zeroes uninitialized folio regions when extending, calls `nfs_update_folio()`, unlocks/releases the folio, updates write stats, and flushes all writes if the open context key is expiring.

`nfs_file_write()` dispatches direct writes to `nfs_file_direct_write()`. Cached writes reject active swapfiles, revalidate file size for append or writes past local EOF, clear invalid mapping state, start write exclusion, run `generic_write_checks()` and `generic_perform_write()`, honor eager/wait mount options, call `generic_write_sync()`, and report writeback errors such as quota, file too large, or no space.

## Fsync And Commit

`nfs_file_fsync()` loops until dirty writeback, NFS commits, pNFS sync, and redirtied-page accounting stabilize. `nfs_file_fsync_commit()` calls `nfs_commit_inode()` and advances writeback error state.

## Swapfile Support

`nfs_swap_activate()` rejects sparse swapfiles by comparing blocks to file size, activates RPC swap behavior, installs a single swap extent, optionally calls protocol `enable_swap()`, and marks `SWP_FS_OPS`. `nfs_swap_deactivate()` reverses RPC/protocol swap state.

## Locking

`nfs_lock()` handles POSIX byte-range locks. It rejects reclaim, optionally validates protocol lock bounds, checks local conflicts first for GETLK, uses server locking unless local locking mount flags apply, flushes writes before unlock/setlk, waits for direct I/O counters on unlock, and treats successful locks as cache-coherency points by syncing/zapping/revalidating mappings unless a delegation protects the file.

`nfs_flock()` implements flock semantics through local or server POSIX-style locks, depending on mount flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/filelayout/Makefile -->
# File Research: sources/os/linux/linux/fs/nfs/filelayout/Makefile

## Role

This Makefile builds the pNFS NFSv4.1 files layout driver module.

## Build Rules

When `CONFIG_PNFS_FILE_LAYOUT` is enabled, it builds `nfs_layout_nfsv41_files.o`.

That object is composed of:
- `filelayout.o`
- `filelayoutdev.o`

## Integration

The module provides the layout driver registered by `filelayout.c` and the device-ID/data-server helpers in `filelayoutdev.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/filelayout/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/filelayout/filelayout.c -->
# File Research: sources/os/linux/linux/fs/nfs/filelayout/filelayout.c

## Role

`filelayout.c` implements the NFSv4.1 pNFS files layout driver. It registers layout type `LAYOUT_NFSV4_1_FILES`, decodes file layout segments, chooses data servers for read/write/commit I/O, handles data-server errors, maps dense/sparse striping, and manages pNFS commit buckets.

The module registers with `pnfs_register_layoutdriver()` in `nfs4filelayout_init()` and unregisters in `nfs4filelayout_exit()`.

## Layout Segment Geometry

`filelayout_get_dserver_offset()` maps a logical file offset to a data-server offset. Sparse layouts use the original offset. Dense layouts use `filelayout_get_dense_offset()`, which computes stripe number and remainder from `pattern_offset`, `stripe_unit`, and `stripe_count`.

`filelayout_pg_test()` prevents pageio coalescing across stripe boundaries. It delegates generic checks to `pnfs_generic_pg_test()` and then limits request size to the remaining bytes in the current stripe for striped layouts.

## Data-Server Read/Write Paths

`filelayout_read_pagelist()` and `filelayout_write_pagelist()` calculate the stripe index with `nfs4_fl_calc_j_index()`, map it to a DS index with `nfs4_fl_calc_ds_index()`, prepare/connect the DS via `nfs4_fl_prepare_ds()`, create/find a DS RPC client, select the appropriate filehandle with `nfs4_fl_select_ds_fh()`, adjust offsets for dense layouts, and initiate asynchronous NFS read/write RPCs through the data-server client.

`filelayout_read_prepare()` and `filelayout_write_prepare()` validate the open context, reset to MDS if the device is unavailable, set up the NFSv4.1 session sequence, and install read/write stateids. Completion callbacks route errors through `filelayout_async_handle_error()`.

## Error Handling And MDS Fallback

`filelayout_async_handle_error()` centralizes DS error handling:
- Session errors schedule session recovery.
- `NFS4ERR_DELAY`/`GRACE` delay and retry.
- Layout-invalidating errors destroy or return the layout and reset I/O to MDS.
- Connection/device errors mark the device ID unavailable, mark layout for return, set layout failure, wake slot waiters, and reset to MDS.

`filelayout_reset_read()` and `filelayout_reset_write()` set `NFS_IOHDR_REDO` and call generic pNFS resend-to-MDS helpers.

## Layout Decoding And Validation

`filelayout_decode_layout()` decodes layoutget results from XDR pages. It extracts deviceid, utility flags, commit-through-MDS flag, dense/sparse stripe type, stripe unit, first stripe index, pattern offset, filehandle count, and filehandle array. It validates filehandle sizes against `NFS_MAXFHSIZE`.

`filelayout_check_layout()` validates basic segment geometry, including `pattern_offset <= layout range offset` and nonzero stripe unit.

`filelayout_check_deviceid()` obtains the decoded deviceid node, rejects unavailable devices, validates `first_stripe_index`, and checks filehandle count rules for sparse versus dense layouts. It installs the DS address pointer with `cmpxchg()` to avoid races.

`filelayout_alloc_lseg()` allocates and decodes a layout segment. `filelayout_free_lseg()` releases the deviceid, releases per-lseg DS commit info for RW segments, and frees filehandles.

## Layout Acquisition

`fl_pnfs_update_layout()` wraps `pnfs_update_layout()`. Recoverable server errors fall back to MDS by returning `NULL`. After acquiring a segment, it validates the deviceid; invalid device metadata marks the layout for return, marks layout failure, releases the segment, and falls back.

`filelayout_pg_init_read()` and `filelayout_pg_init_write()` initialize pageio descriptors, request READ or RW layouts, and reset to MDS pageio ops when no layout is available.

## Commit Handling

Writes that are not committed through the MDS are bucketed by data server. `filelayout_mark_request_commit()` either adds the request to the MDS commit list or maps the request offset to a DS commit bucket. Sparse and dense layouts use different bucket-to-DS mappings.

`filelayout_initiate_commit()` prepares DS commit RPCs, chooses the DS client and filehandle, installs `filelayout_commit_done_cb()`, and initiates commit. Failure prepares writes for resend and releases commit data.

`filelayout_commit_done_cb()` uses the same async error path; reset-to-MDS prepares writes for resend, retry restarts the RPC, and success sets layoutcommit state.

`filelayout_commit_ops` plugs setup/release, mark/clear, scan/recover, and commit-pagelist behavior into generic pNFS commit infrastructure.

## Layout Driver Registration

`filelayout_type` declares:
- layout id `LAYOUT_NFSV4_1_FILES`,
- `PNFS_LAYOUTGET_ON_OPEN`,
- max layoutget response of 4096 bytes,
- layout header and segment alloc/free hooks,
- read/write pageio ops,
- DS commit info access,
- read/write pagelist functions,
- deviceid alloc/free hooks,
- generic sync callback.

The module alias is `nfs-layouttype4-1`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/filelayout/filelayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/filelayout/filelayout.h -->
# File Research: sources/os/linux/linux/fs/nfs/filelayout/filelayout.h

## Role

`filelayout.h` defines the internal data structures and helper declarations for the NFSv4.1 pNFS files layout driver.

## Constants And Types

The header caps supported geometry at:
- `NFS4_PNFS_MAX_STRIPE_CNT` = 4096 stripe indices,
- `NFS4_PNFS_MAX_MULTI_CNT` = 256 multipath list entries.

It defines `enum stripetype4` with `STRIPE_SPARSE` and `STRIPE_DENSE`.

## Core Structures

`struct nfs4_file_layout_dsaddr` stores decoded GETDEVICEINFO data: generic deviceid node, stripe count, stripe index array, number of data-server entries, and a flexible array of `struct nfs4_pnfs_ds *`.

`struct nfs4_filelayout_segment` extends `struct pnfs_layout_segment` with stripe type, commit-through-MDS flag, stripe unit, first stripe index, pattern offset, deviceid, decoded DS address pointer, filehandle count, and filehandle array.

`struct nfs4_filelayout` extends `struct pnfs_layout_hdr` with pNFS DS commit information.

## Helpers And External Interfaces

Inline helpers convert generic pNFS structures to filelayout-specific containers: `FILELAYOUT_FROM_HDR()`, `FILELAYOUT_LSEG()`, and `FILELAYOUT_DEVID_NODE()`.

The header declares geometry and DS selection helpers implemented in `filelayoutdev.c`, plus deviceid allocation/release helpers used by `filelayout.c`.

`filelayout_test_devid_invalid()` checks the generic invalid bit, while `filelayout_test_devid_unavailable()` also includes transient unavailable state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/filelayout/filelayout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/filelayout/filelayoutdev.c -->
# File Research: sources/os/linux/linux/fs/nfs/filelayout/filelayoutdev.c

## Role

`filelayoutdev.c` decodes pNFS files-layout device information, manages DS address/deviceid objects, computes stripe mappings, selects filehandles, and lazily connects to data servers.

## Deviceid Allocation And Decode

`nfs4_fl_alloc_deviceid_node()` decodes opaque GETDEVICEINFO pages with an XDR stream. It reads:
- stripe count,
- stripe index array,
- multipath list count,
- per-data-server multipath address lists.

It validates `stripe_count <= NFS4_PNFS_MAX_STRIPE_CNT`, `ds_num <= NFS4_PNFS_MAX_MULTI_CNT`, and `max_stripe_index < ds_num`. It stores stripe indices as `u8`, allocates a flexible `nfs4_file_layout_dsaddr`, initializes its generic deviceid node, decodes DS remote addresses, interns/gets `struct nfs4_pnfs_ds` objects with `nfs4_pnfs_ds_add()`, and traces decoded device info.

Failure paths free scratch folio, stripe indices, DS address lists, and partially built deviceid state.

`nfs4_fl_free_deviceid()` drops DS references, frees stripe indices, and RCU-frees the `dsaddr`. `nfs4_fl_put_deviceid()` drops the generic deviceid node reference.

## Stripe Mapping

`nfs4_fl_calc_j_index()` computes the stripe index for a file offset:
`((offset - pattern_offset) / stripe_unit + first_stripe_index) % stripe_count`.

`nfs4_fl_calc_ds_index()` maps that stripe index through the decoded `stripe_indices` array.

`nfs4_fl_select_ds_fh()` chooses the filehandle used for DS I/O. Sparse layouts use the only filehandle if `num_fh == 1`, use the MDS OPEN filehandle if `num_fh == 0`, or select by DS index. Dense layouts select by stripe index.

## Data-Server Preparation

`nfs4_fl_prepare_ds()` returns a connected `struct nfs4_pnfs_ds *` or `NULL`. It validates that a DS exists for the index, marks deviceid invalid if missing, connects to the DS through `nfs4_pnfs_ds_connect()` if needed, marks the device unavailable on connection failure, and rejects unavailable/invalid deviceids.

## Tunables

The module exposes `dataserver_retrans` and `dataserver_timeo` parameters, defaulting to NFSv4 DS retry/timeout constants, and passes them into DS connection setup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/filelayout/filelayoutdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/flexfilelayout/Makefile -->
# File Research: sources/os/linux/linux/fs/nfs/flexfilelayout/Makefile

## Role

This Makefile builds the pNFS flexfiles layout driver module.

## Build Rules

When `CONFIG_PNFS_FLEXFILE_LAYOUT` is enabled, it builds `nfs_layout_flexfiles.o`.

That object is composed of:
- `flexfilelayout.o`
- `flexfilelayoutdev.o`

## Integration

This is only the build declaration for the flexfiles layout driver. The implementation files are outside this work item.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/flexfilelayout/Makefile -->