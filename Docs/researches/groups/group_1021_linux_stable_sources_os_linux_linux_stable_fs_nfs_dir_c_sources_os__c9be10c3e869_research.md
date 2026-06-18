# Group Research: group_1021_linux_stable_sources_os_linux_linux_stable_fs_nfs_dir_c_sources_os__c9be10c3e869

Repository root: `/home/sansha/Github/learn_fs`

Scope checked: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`, so all files in this group are within subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/dir.c

## Role

`dir.c` implements the Linux NFS client's directory-facing VFS behavior. It wires `nfs_dir_operations` and `nfs_dir_aops`, provides directory open/release/readdir/llseek/fsync, manages NFS dentry revalidation, implements lookup and create-family directory operations, handles unlink/rename with silly-rename protection, and maintains the per-credential NFS ACCESS result cache.

## Main interfaces

- `nfs_dir_operations`: `.iterate_shared = nfs_readdir`, `.open = nfs_opendir`, `.release = nfs_closedir`, `.llseek = nfs_llseek_dir`, `.fsync = nfs_fsync_dir`.
- `nfs_dir_aops`: uses `.free_folio = nfs_readdir_clear_array` so cached directory-entry name allocations are released when page-cache folios go away.
- Exported directory and lookup helpers include `nfs_lookup`, `nfs_atomic_open`, `nfs_atomic_open_v23`, `nfs_create`, `nfs_mknod`, `nfs_mkdir`, `nfs_rmdir`, `nfs_unlink`, `nfs_symlink`, `nfs_link`, `nfs_rename`, `nfs_permission`, `nfs_access_get_cached`, `nfs_access_add_cache`, `nfs_access_zap_cache`, `nfs_set_verifier`, and `nfs_force_lookup_revalidate`.

## Directory stream cache

The file uses a folio-sized directory-entry cache made of `struct nfs_cache_array` and `struct nfs_cache_array_entry`. Each entry stores the server cookie, fileid, name pointer, name length, and d_type. Name strings are copied with `kmemdup_nul()` and intentionally hidden from kmemleak because they are referenced from page-cache memory that kmemleak does not scan.

`nfs_readdir_descriptor` is the central transient state for `nfs_readdir()`: it tracks the file, `dir_context`, current folio, cookie, last cookie, synthetic position, verifier bytes, change/generation attributes, adaptive `dtsize`, whether READDIRPLUS is active, and end-of-buffer/end-of-directory state.

Cookie-to-folio lookup uses `nfs_readdir_folio_cookie_hash()`. Cookie zero maps to index zero, while nonzero cookies are hashed to 18 bits. This lets the page cache hold long cookie-indexed directory streams without growing an enormous XArray.

## READDIR and READDIRPLUS flow

`nfs_readdir()` revalidates the directory mapping, snapshots the open-directory context under `file->f_lock`, decides whether to use READDIRPLUS, then repeatedly searches or fills page-cache folios until the userspace buffer is full or EOF is reached.

Cache lookup starts in `readdir_search_pagecache()` and `find_and_lock_cache_page()`. If a folio needs data, `nfs_readdir_xdr_to_array()` allocates XDR pages, sends `NFS_PROTO(inode)->readdir()`, decodes entries using the protocol-specific `decode_dirent`, and converts decoded entries into one or more `nfs_cache_array` folios. Cookie verifier changes at the beginning of the stream invalidate later cached pages.

READDIRPLUS is selected by `nfs_use_readdirplus()` based on server capability, force mount option, stream start, and recorded cache-hit/cache-miss behavior. When READDIRPLUS returns filehandles and attributes, `nfs_prime_dcache()` opportunistically validates or instantiates child dentries, rejects illegal names, verifies fsid/fileid/filehandle consistency, refreshes inodes, and sets dentry verifiers.

If a cookie cannot be found in the cache, `uncached_readdir()` asks the server for a temporary anonymous stream starting at that cookie. Those folios are not inserted into the page cache because their contents may not be aligned to the page-cache representation and because the ordinary cache should already cover the directory once the scan stabilizes.

## Dentry verifiers and lookup cache consistency

Dentry freshness is driven by parent directory change attributes stored in `dentry->d_time`. Bit 0 is reserved as a delegation tag. `nfs_set_verifier()` stores a verifier only if it still matches the parent; if the parent or child has a read delegation, it marks the verifier as delegated so lookup revalidation can trust it after directory changes until delegation return/revoke paths clear the tag.

`nfs_check_verifier()` compares the saved dentry verifier against the parent directory change attribute and may revalidate the parent inode first. Negative dentries are handled by `nfs_neg_need_reval()`, with stricter behavior for `lookupcache=noneg` and case-insensitive servers.

`nfs_do_lookup_revalidate()` is the common dentry hit path. It handles negative dentries, bad/stale inodes, rename targets on case-insensitive servers, delegated verifiers, close-to-open validation, LOOKUP_RCU limitations, and fallback wire lookups through `nfs_lookup_revalidate_dentry()`.

For NFSv4, `nfs4_lookup_revalidate()` optimizes regular-file `LOOKUP_OPEN` so later file open code can perform the real OPEN/revalidation, while still falling back to full dentry revalidation for directories, mountpoints, negative dentries, non-regular files, exclusive/revalidation flags, or changed parent directories.

## Lookup, open, create, and namespace mutation

`nfs_lookup()` validates name length, skips ordinary lookup for exclusive create and rename target intents, performs protocol lookup, creates or finds the inode with `nfs_fhget()`, sets the dentry verifier, and uses `d_splice_alias()`.

`nfs_atomic_open()` implements NFSv4 atomic OPEN integration. It validates flags, prepares mode/truncation attributes, handles negative dentry replacement for non-create opens, creates an NFS open context, calls `NFS_PROTO(dir)->open_context()`, marks `FMODE_CREATED` when the server creates the file, and finishes only regular files. Errors such as `-EISDIR`, `-ENOTDIR`, and follow-related `-ELOOP` fall back to lookup/no-open handling.

`nfs_atomic_open_v23()` provides NFSv2/v3 create-plus-open behavior with different truncation handling. It tries `nfs_do_create()` for `O_CREAT`, returns a finished open on success, and otherwise falls back to lookup unless exclusive-create semantics require the error.

Create-like operations (`nfs_create`, `nfs_mknod`, `nfs_mkdir`, `nfs_symlink`) call protocol-specific RPC operations, drop dentries on ambiguous failed create/mknod/symlink paths, and set dentry verifiers on success. `nfs_symlink()` builds a raw folio containing the symlink target, sends it to the server, and opportunistically inserts that folio into the new inode mapping.

`nfs_link()` drops the target dentry, syncs regular-file data first, sends LINK, and instantiates the target dentry on success. `nfs_rmdir()` serializes with the child inode's `rmdir_sem`, clears link count on successful server removal, and updates verifier/negative dentry state for `-ENOENT`.

`nfs_unlink()` chooses silly rename when the dentry has extra users and the inode is not marked preserve-unlinked. Otherwise it blocks lookup revalidation via `d_fsdata = NFS_FSDATA_BLOCKED`, performs `nfs_safe_remove()`, updates verifier/error state, then wakes waiters.

`nfs_rename()` rejects nonzero VFS flags, silly-renames a busy non-directory target if necessary, blocks revalidation for direct target replacement, syncs old regular-file data for unsafe rename cases, executes `nfs_async_rename()` and waits for completion, invalidates old inode attributes on success, moves the dentry locally under VFS locks, and drops target link count when overwriting.

## ACCESS cache and permissions

The file maintains a global LRU and per-inode red-black tree of `nfs_access_entry` objects keyed by fsuid, fsgid, and group list. `nfs_access_get_cached()` first attempts a lockless RCU lookup of the most-recent entry, then falls back to locked RB-tree search. Entries are invalidated when inode access cache state is stale, when user login time is newer than the entry timestamp, or when explicit zap/shrinker paths run.

`nfs_access_add_cache()` copies credential identity and the ACCESS mask into a new entry, inserts or replaces it in the RB tree, links it into per-inode and global LRUs, updates `nfs_access_nr_entries`, and enforces `nfs_access_max_cachesize`.

`nfs_access_cache_scan()` and `nfs_access_cache_count()` are shrinker callbacks registered elsewhere. The scan walks the global inode LRU, evicts one entry per inode visit, and clears the inode LRU flag when the per-inode list becomes empty.

`nfs_permission()` avoids unnecessary ACCESS RPCs for symlinks, NFSv4 atomic-open regular-file opens, and pure directory writes that the server will check during the operation. Otherwise it calls `nfs_do_access()`, which fetches or sends an ACCESS RPC and converts NFS access bits to Linux `MAY_*` bits. Execute checks additionally revalidate mode if needed and call `execute_ok()`.

## Concurrency and failure behavior

Directory-open state is held in `nfs_open_dir_context` and linked on the inode under `i_lock`, with RCU deletion on close. Dentry blocking for unlink/rename uses `wait_var_event()` and release-store wakeups on `d_fsdata`. Directory folio cache entries are locked through the page cache during fill/search. Access-cache updates use inode locks, a global LRU spinlock, RCU freeing, and explicit memory barriers around global accounting/list visibility.

The code treats `-EBADCOOKIE` and `-ENOTSYNC` as signals to invalidate or bypass directory cache state. `-ENOTSUPP` on READDIRPLUS disables server READDIRPLUS capability for this mount. Soft revalidation can accept cached roots after timeout, while stale non-root entries are dropped or marked for revalidation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/direct.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/direct.c

## Role

`direct.c` implements uncached/direct I/O for the NFS client, including `O_DIRECT` reads and writes, swap-file I/O through NFS, asynchronous completion, direct write COMMIT handling, and retry/reschedule paths for pNFS and unstable writes. It avoids populating the Linux page cache for direct I/O and relies on NFS server semantics for EOF and write durability.

## Main state

The central object is `struct nfs_direct_req`, allocated from the `nfs_direct_cachep` slab. It carries the inode, open context, lock context, optional async iocb, byte accounting, error state, pNFS data-server commit info, MDS commit info, completion, work item, and a spinlock. `io_count` tracks outstanding pageio/commit activity; `kref` tracks object lifetime.

`nfs_init_cinfo_from_dreq()` adapts a direct request into the generic NFS commit infrastructure by filling `struct nfs_commit_info` with MDS and data-server commit lists and direct commit completion ops.

## Direct read flow

`nfs_file_direct_read()` handles zero-length I/O, allocates a direct request, takes NFS open and lock contexts, records async completion state when the kiocb is asynchronous, marks user-backed pages dirty-after-read when needed, starts direct I/O serialization with `nfs_start_io_direct()`, and schedules pageio with `nfs_direct_read_schedule_iovec()`.

`nfs_direct_read_schedule_iovec()` pins batches of user pages with `iov_iter_get_pages_alloc2()`, slices them into `nfs_page` requests bounded by server `rsize`, adds them to an NFS read pageio descriptor, and completes the descriptor. Completion is handled by `nfs_direct_read_completion()`, which counts bytes, updates delegated atime, optionally marks user pages dirty, removes each `nfs_page`, and completes the direct request when the last I/O reference drops.

Read byte accounting is defensive: `nfs_direct_count_bytes()` computes the covered byte range from each header and `nfs_direct_handle_truncated()` clamps the overall request on EOF or header error so later completions cannot extend the visible result past a truncation point.

## Direct write and commit flow

`nfs_file_direct_write()` performs generic write checks except for swap I/O, rejects no-byte writes, allocates and initializes a direct request, initializes pNFS data-server commit info, and schedules writes with stable mode `FLUSH_STABLE` for swap or `FLUSH_COND_STABLE` for normal direct writes. Normal direct writes also invalidate overlapping page-cache folios after the RPCs are scheduled and then invalidate fscache state with `FSCACHE_INVAL_DIO_WRITE`.

`nfs_direct_write_schedule_iovec()` pins user pages in server `wsize` chunks, creates `nfs_page` requests, locks them, and adds them to a write pageio descriptor. If the descriptor reports a soft `-EAGAIN`, remaining requests are deferred into commit/retry lists and the direct request flag becomes `NFS_ODIRECT_RESCHED_WRITES`.

`nfs_direct_write_completion()` accounts successful bytes, adjusts local `i_size` for extending writes, updates delegated mtime, and either releases requests or marks them for commit/reschedule. Unstable writes set `NFS_ODIRECT_DO_COMMIT` and preserve the write verifier in each request.

Commit handling uses `nfs_direct_commit_schedule()`, `nfs_direct_commit_complete()`, and `nfs_direct_resched_write()`. Commit verifier mismatches cause writes to be re-marked for retransmission. Commit errors are fatal and truncate the visible byte count to the failed request boundary.

Final direct write completion is deferred through `nfsiod_workqueue` via `nfs_direct_write_complete()` and `nfs_direct_write_schedule_work()`. That work either schedules COMMIT, reschedules writes, or clears outstanding requests, zaps mapping cache state, and completes the request.

## Retry and pNFS integration

The completion ops set `NFS_IOHDR_ODIRECT` on pageio headers. Write completion can request `.reschedule_io`, which marks the header redo bit and moves its pages back to commit/retry lists. `nfs_direct_write_reschedule()` scans commit lists, rejoins page groups, clears pNFS data-server commit verifiers, and retransmits with stable writes.

The direct path shares pNFS commit data structures with buffered writeback through `pnfs_init_ds_commit_info`, `pnfs_recover_commit_reqs`, `pnfs_release_ds_info`, and generic NFS commit scanning.

## Swap support

`nfs_swap_rw()` maps swap read/write requests onto direct read/write with `swap = true`. Swap writes bypass generic write checks and are forced stable. On success the swap address-space operation returns zero rather than byte count, matching swap I/O expectations.

## Lifecycle and error behavior

Synchronous direct I/O waits in `nfs_direct_wait()` unless the request has an async iocb, in which case completion returns `-EIOCBQUEUED` to the submitter and later invokes `ki_complete`. `nfs_direct_complete()` always calls `inode_dio_end()`, completes async iocbs with either byte count or error, signals the completion object, and drops the final direct-request reference.

Pinned pages are released after request construction because `nfs_page` objects hold the needed page references. If no bytes were successfully scheduled, the schedule helper ends DIO, releases the direct request reference it would otherwise consume, and returns the construction error or `-EIO`.

`nfs_init_directcache()` and `nfs_destroy_directcache()` create and destroy the direct-request slab cache, with callers declared in `internal.h` and used from NFS inode module init/exit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/direct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/dns_resolve.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/dns_resolve.c

## Role

`dns_resolve.c` resolves NFS hostnames into socket addresses. It supports two compile-time implementations: a kernel DNS resolver path when `CONFIG_NFS_USE_KERNEL_DNS` is enabled, and a userspace upcall/cache implementation through SUNRPC cache and rpc_pipefs otherwise. NFSv4 namespace referral code calls `nfs_dns_resolve_name()`.

## Kernel DNS implementation

With `CONFIG_NFS_USE_KERNEL_DNS`, `nfs_dns_resolve_name()` calls `dns_query()` with the network namespace and hostname. A positive DNS response string is converted to a `sockaddr` using `rpc_pton()`. DNS failure maps to `-ESRCH`, and the allocated IP string is freed with `kfree()`. All resolver init/destroy functions are inline no-ops in the header for this configuration.

## SUNRPC cache/upcall implementation

Without kernel DNS, each resolver entry is `struct nfs_dns_ent`: a SUNRPC `cache_head`, hostname and length, resolved `sockaddr_storage`, address length, and RCU head. Entries are hashed by hostname using a 16-bucket hash table.

`nfs_dns_resolve_template` describes the cache: allocation, initialization, update, matching, request formatting, parser, display, upcall, and put/free callbacks. Entry freeing is RCU-delayed and releases the hostname string.

`nfs_dns_upcall()` sets `CACHE_PENDING`, first tries `nfs_cache_upcall()`, and otherwise sends an rpc_pipefs cache upcall with timeout. `nfs_dns_request()` writes the requested hostname into the upcall payload.

Userspace replies are parsed by `nfs_dns_parse()`. The expected line contains an IP address, hostname, and TTL. The parser converts the address with `rpc_pton()`, stores negative entries when address conversion yields zero length, computes expiry from `seconds_since_boot() + ttl`, and updates the cache entry.

## Lookup behavior

`nfs_dns_resolve_name()` builds a temporary key from the requested hostname and uses `do_cache_lookup_wait()`. That function allocates a deferred request, calls `cache_check()`, waits for an upcall on `-EAGAIN`, then does a nowait validation pass. A valid positive entry copies the address into the caller's buffer if it fits; too small a buffer returns `-EOVERFLOW`. Negative cache entries become `-ESRCH`.

Nowait validation rejects entries that are not `CACHE_VALID`, expired, older than cache flush time, or negative. Cache references are put through `cache_put()`.

## Namespace and rpc_pipefs lifecycle

`nfs_dns_resolver_cache_init()` creates a per-net cache from the template and registers it with NFS cache infrastructure; destroy unregisters and destroys it. The file registers pernet operations in `nfs_dns_resolver_init()`.

The rpc_pipefs notifier registers or unregisters the cache against a mounted rpc_pipefs superblock on `RPC_PIPEFS_MOUNT` and `RPC_PIPEFS_UMOUNT`. It takes a module reference around notifier work and ignores namespaces where the cache has not been initialized.

## Error handling

Parsing rejects malformed lines, missing newline, empty qwords, zero TTL, allocation failures, and lookup/update failures. Upcall lookup can return `-ENOMEM`, `-ETIMEDOUT`, `-ENOENT`, `-EAGAIN`, `-EOVERFLOW`, or the mapped public `-ESRCH` for unresolved names.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/dns_resolve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/dns_resolve.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/dns_resolve.h

## Role

`dns_resolve.h` declares the NFS DNS resolver interface and the maximum supported hostname length for the userspace-cache parser.

## Contents

- `NFS_DNS_HOSTNAME_MAXLEN` is `128`.
- When `CONFIG_NFS_USE_KERNEL_DNS` is enabled, resolver global/per-net init and destroy functions are static inline no-ops because `dns_resolve.c` directly uses the kernel DNS resolver.
- Otherwise it declares `nfs_dns_resolver_init()`, `nfs_dns_resolver_destroy()`, `nfs_dns_resolver_cache_init()`, and `nfs_dns_resolver_cache_destroy()`.
- It always declares `nfs_dns_resolve_name(struct net *net, char *name, size_t namelen, struct sockaddr_storage *sa, size_t salen)`.

## Integration

The header lets common NFS initialization and net namespace code call resolver setup without caring which DNS backend was compiled. It also exposes the actual resolution function used by NFSv4 namespace/referral handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/dns_resolve.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/export.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/export.c

## Role

`export.c` supplies `export_operations` for re-exporting an NFS mount through Linux exportfs/NFS server mechanisms. It encodes an NFS client inode into a file handle that embeds the server filehandle, and decodes such handles back into dentries.

## File handle format

The encoded handle contains high and low 32-bit portions of the inode's NFS fileid, the inode file type (`S_IFMT`), and an embedded `struct nfs_fh`. `nfs_exp_embedfh()` returns the embedded filehandle area inside the raw `__u32` buffer.

`nfs_encode_fh()` computes the required XDR-quad length from the embedded server filehandle size. If the caller's buffer is too small it updates `*max_len` and returns `FILEID_INVALID`. Otherwise it writes fileid, type, padding, copies the NFS filehandle, updates `*max_len`, and returns the filehandle type equal to the encoded length.

Subtree checking is intentionally disabled because embedding parent filehandles could exceed available filehandle space.

## Decoding and parent lookup

`nfs_fh_to_dentry()` validates handle bounds and type, extracts the embedded filehandle size, builds minimal attributes from encoded fileid and type, and first tries `nfs_ilookup()`. If no inode is cached, it calls the server `getattr` RPC, then creates/fetches the inode via `nfs_fhget()` and returns `d_obtain_alias()`.

`nfs_get_parent()` requires protocol `lookupp` support. It calls LOOKUPP on the child inode, creates/fetches the parent inode with `nfs_fhget()`, and returns an alias dentry.

## Export operation flags

`nfs_export_ops` sets `EXPORT_OP_NOWCC`, `EXPORT_OP_NOSUBTREECHK`, `EXPORT_OP_CLOSE_BEFORE_UNLINK`, `EXPORT_OP_REMOTE_FS`, `EXPORT_OP_NOATOMIC_ATTR`, `EXPORT_OP_FLUSH_ON_CLOSE`, and `EXPORT_OP_NOLOCKS`. These advertise remote filesystem limitations and force conservative behavior around unlink, close, attributes, and locking.

## Failure behavior

Malformed or mismatched handles return `NULL`, which exportfs treats as stale. Allocation failure returns `ERR_PTR(-ENOMEM)`. Failed getattr or LOOKUPP errors propagate as error dentries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/file.c

## Role

`file.c` implements regular-file VFS operations for NFS. It dispatches cached and direct reads/writes, handles mmap page-mkwrite, fsync and commit synchronization, page-cache write begin/end, folio invalidation/reclaim laundering, NFS-backed swap activation, and POSIX/flock locking behavior.

## Main interfaces

- `nfs_file_operations`: llseek, read_iter, write_iter, mmap_prepare, open, flush, release, fsync, lock, flock, splice read/write, flag validation, and `FOP_DONTCACHE`.
- `nfs_file_aops`: read folio, readahead, dirtying, writepages, write_begin/write_end, invalidate/release/migrate/launder, dirty/writeback query, error removal, swap activation/deactivation, and swap direct rw.
- `nfs_file_vm_ops`: filemap fault/map_pages plus `nfs_vm_page_mkwrite`.

## Open, close, seek, and flush

`nfs_check_flags()` rejects the unsupported combination of `O_APPEND | O_DIRECT`. `nfs_file_open()` validates flags, calls `nfs_open()`, and marks the file as capable of direct I/O. `nfs_file_release()` clears the NFS open context and releases fscache state.

`nfs_file_llseek()` revalidates file size before `SEEK_END`, `SEEK_DATA`, or `SEEK_HOLE`, then delegates to `generic_file_llseek()`. Size revalidation is forced for `O_DIRECT` or when size cache validity is marked invalid.

`nfs_file_flush()` writes back all dirty pages for writable files and returns writeback errors sampled from the mapping.

## Cached and direct reads

`nfs_file_read()` sends direct reads to `nfs_file_direct_read()` when `IOCB_DIRECT` is set. Cached reads serialize through `nfs_start_io_read()`, revalidate the mapping, call `generic_file_read_iter()`, update normal-read byte stats, and end read serialization.

`nfs_file_splice_read()` follows the same read serialization and mapping revalidation but uses `filemap_splice_read()`.

`nfs_file_mmap_prepare()` first calls `generic_file_mmap_prepare()`, then installs NFS VM ops and revalidates the mapping. Calling generic mmap setup first preserves nommu error behavior.

## Buffered writes

`nfs_file_write()` checks key timeout, dispatches direct writes to `nfs_file_direct_write()`, rejects writes to active swap files, revalidates size for append or writes beyond current `i_size`, clears invalid mapping state, runs generic write checks and `generic_perform_write()` inside NFS write serialization, then applies mount options `WRITE_EAGER` and `WRITE_WAIT`. It calls `generic_write_sync()` and checks mapping writeback errors, forcing full writeback for quota, file-size, or space errors so errors are surfaced reliably.

`nfs_write_begin()` truncates/zeros the last folio for extending writes, gets the target folio, flushes incompatible state, and may perform read-modify-write if the folio is not uptodate, not already private/dirty, not a full overwrite, and pNFS or file-open mode suggests reading first is better.

`nfs_write_end()` zeroes uninitialized regions when extending or partially writing non-uptodate folios, updates NFS folio dirty/private state through `nfs_update_folio()`, unlocks/drops the folio, accounts written bytes, and flushes if the open context key is near expiry.

## Fsync, commits, and folio lifecycle

`nfs_file_fsync()` loops until writeback, NFS COMMIT, pNFS sync, and redirtied-page accounting stabilize. It samples `redirtied_pages` before each iteration to detect writes that became dirty again during commit.

`nfs_truncate_last_folio()` locks the folio containing a truncation/extension boundary, marks it dirty if it had clean PTEs, zeroes the requested segment if uptodate, and emits a tracepoint.

`nfs_invalidate_folio()` writes back or cancels pending NFS writes depending on whether invalidation is partial or whole-folio, waits on deprecated fscache/private_2 state, and traces invalidation. `nfs_release_folio()` refuses reclaim under restricted GFP or kswapd/kcompactd when private state exists, otherwise tries reclaim writeback and fscache release. `nfs_launder_folio()` waits on private_2 state then writes back the folio.

`nfs_check_dirty_writeback()` tells the VM that unstable folios are effectively under writeback while commits are outstanding, or dirty when private state exists and no commit is running.

## mmap write faults

`nfs_vm_page_mkwrite()` handles shared writable mappings. It starts a pagefault write section, waits for fscache/private storage and NFS invalidation to finish, locks and validates the folio still belongs to the inode mapping, waits for writeback, rejects zero-length folios, flushes incompatible state, and calls `nfs_update_folio()` for the full valid folio length. Failures map to retry or SIGBUS-style VM faults.

## Swap support

`nfs_swap_activate()` verifies the swapfile has no holes by comparing `i_blocks` against `i_size`, activates RPC swap behavior, adds one full-file swap extent, enables protocol-specific swap hooks if present, and sets `SWP_FS_OPS`. Deactivation reverses RPC/protocol swap state.

## File locking

`nfs_lock()` handles POSIX locks. It rejects reclaim, honors local lock mount options, validates protocol lock bounds, and dispatches to getlk, unlock, or setlk helpers. `do_setlk()` flushes mapping data before server locks, then treats successful locking as a cache-coherency point by syncing and invalidating caches unless a delegation is held. `do_unlk()` writes back all data and waits for outstanding lock-context I/O before unlocking, with special handling for process-exit `FL_CLOSE`.

`nfs_flock()` simulates flock locks via POSIX locks on the server unless local flock mode is configured.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/filelayout/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/nfs/filelayout/Makefile

## Role

This Makefile builds the pNFS NFSv4.1 file layout driver module when `CONFIG_PNFS_FILE_LAYOUT` is enabled.

## Build outputs

- Adds `nfs_layout_nfsv41_files.o` to `obj-y`/`obj-m` through `obj-$(CONFIG_PNFS_FILE_LAYOUT)`.
- Links the module from `filelayout.o` and `filelayoutdev.o`.

## Integration

The resulting module registers layout type `LAYOUT_NFSV4_1_FILES` from `filelayout.c` and uses device/address helper code from `filelayoutdev.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/filelayout/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayout.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayout.c

## Role

`filelayout.c` is the pNFS NFSv4.1 file-layout driver. It decodes layout segments, validates device IDs, selects data servers and filehandles for striped I/O, issues read/write/commit RPCs to data servers, handles data-server/session/layout failures, manages pNFS commit buckets, and registers the layoutdriver with the generic pNFS client.

## Layout offsets and striping

`filelayout_get_dserver_offset()` maps logical file offsets to data-server offsets. Sparse striping keeps the original offset. Dense striping removes holes for other data servers by using `filelayout_get_dense_offset()`, which calculates stripe number and offset within a stripe unit after subtracting `pattern_offset`.

`filelayout_pg_test()` extends generic pNFS request coalescing. For unstriped layouts it accepts the generic size. For striped layouts it prevents a pageio segment from crossing stripe-unit boundaries by comparing stripe numbers and limiting returned bytes to the remainder of the current stripe.

## Data-server RPC setup

`filelayout_read_pagelist()` and `filelayout_write_pagelist()` calculate the stripe index `j`, data-server index, connect/prepare the selected data server through `nfs4_fl_prepare_ds()`, find or create an RPC client, select the data-server filehandle, adjust offsets for dense layouts, set `hdr->ds_clp` and commit index, and initiate asynchronous pgio to the data server with filelayout-specific RPC call ops.

Read and write prepare callbacks check for bad open contexts, reset to MDS if the deviceid is invalid/unavailable, set up NFSv4.1 sequence state, and install read/write stateids. Call-done callbacks let the generic MDS ops process normal completions, but if the header has been marked redo and the task succeeded they only complete the sequence.

## Error handling and fallback to MDS

`filelayout_async_handle_error()` categorizes data-server RPC failures:

- Session errors schedule session recovery.
- `DELAY` and `GRACE` delay and retry.
- Layout invalidation errors destroy the layout, wake the slot table waitqueue, and force reset to MDS.
- Connection and transport errors mark the deviceid unavailable, mark the layout for return/failure, wake waiters, and reset to MDS.
- Retryable cases clear task status and return `-EAGAIN`.

`filelayout_reset_read()` and `filelayout_reset_write()` set `NFS_IOHDR_REDO` once and call generic resend-to-MDS helpers. This is the primary safety path when data-server I/O cannot proceed.

## Layout commit and write verifiers

`filelayout_set_layoutcommit()` requests a LAYOUTCOMMIT when writes are not committed through the MDS and not already `NFS_FILE_SYNC`. For `NFS_DATA_SYNC`, it records the end offset immediately; unstable writes defer precise end-offset handling until commit.

`filelayout_write_done_cb()` handles write completion, sets layoutcommit when appropriate, clears fattr validity so DS attributes do not update the MDS inode incorrectly, and updates writeback inode state on success.

`filelayout_commit_done_cb()` handles data-server commit completion. Reset-to-MDS prepares writes for resend; retryable errors restart the call; success records layoutcommit up to the commit low-watermark.

## Layout decode and validation

`filelayout_decode_layout()` decodes the layout body from layoutget pages with an XDR stream and scratch folio. It reads deviceid, utility flags, dense/sparse type, commit-through-MDS bit, stripe unit, first stripe index, pattern offset, number of filehandles, and each filehandle. It bounds `num_fh` against the larger of supported stripe and multipath limits and rejects oversized NFS filehandles.

`filelayout_check_layout()` rejects impossible segment parameters such as `pattern_offset` after the layout range start or zero stripe unit. `filelayout_check_deviceid()` resolves the referenced deviceid, rejects unavailable/invalid deviceids, validates first stripe index and number-of-filehandle rules for dense versus sparse layouts, and atomically installs the data-server address pointer.

## Pageio and layout acquisition

`fl_pnfs_update_layout()` wraps `pnfs_update_layout()`, treating nonfatal server errors as MDS fallback and checking the deviceid before accepting the segment. Bad deviceids mark the layout for return/failure and drop the segment.

`filelayout_pg_init_read()` and `filelayout_pg_init_write()` check current layout suitability, obtain read or read/write layout segments, and reset the pageio descriptor to MDS operations when no pNFS segment is available.

`filelayout_pg_read_ops` and `filelayout_pg_write_ops` plug these init/test functions into generic pNFS pageio read/write execution and cleanup.

## Commit bucket management

The layout maintains `struct pnfs_ds_commit_info` inside `struct nfs4_filelayout`. `filelayout_setup_ds_info()` allocates a commit array sized to either the number of data servers for sparse layouts or stripe count for dense layouts. `filelayout_mark_request_commit()` sends commit-through-MDS writes to the MDS list, otherwise calculates the correct commit bucket from the page offset and layout type. `filelayout_initiate_commit()` maps commit bucket index back to data-server index, selects the correct filehandle, and starts a data-server COMMIT RPC.

`filelayout_commit_ops` delegates scanning, recovery, and clearing to generic pNFS helpers while supplying filelayout-specific setup, release, request marking, and commit initiation.

## Module registration

`filelayout_type` registers layout id `LAYOUT_NFSV4_1_FILES`, name `LAYOUT_NFSV4_1_FILES`, `PNFS_LAYOUTGET_ON_OPEN`, one-page-ish max layoutget response, layout header/segment allocators, pageio ops, data-server info lookup, pagelist read/write, deviceid alloc/free, and generic sync. Module init/exit register and unregister the layout driver, and the module alias is `nfs-layouttype4-1`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayout.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayout.h

## Role

`filelayout.h` defines the pNFS file-layout driver's private data structures, layout type constants, accessor helpers, and cross-file function declarations shared by `filelayout.c` and `filelayoutdev.c`.

## Constants and layout types

- `NFS4_PNFS_MAX_STRIPE_CNT` is `4096`, the supported maximum number of stripe indices.
- `NFS4_PNFS_MAX_MULTI_CNT` is `256`, chosen because stripe indices are stored as `u8`.
- `enum stripetype4` defines `STRIPE_SPARSE = 1` and `STRIPE_DENSE = 2`.

## Data structures

`struct nfs4_file_layout_dsaddr` embeds the generic `nfs4_deviceid_node`, stores stripe count, an array of `u8` stripe indices, the number of data-server multipath entries, and a flexible array of `struct nfs4_pnfs_ds *`.

`struct nfs4_filelayout_segment` embeds `struct pnfs_layout_segment` and stores stripe type, commit-through-MDS flag, stripe unit, first stripe index, pattern offset, deviceid, resolved data-server address, number of filehandles, and the decoded filehandle array.

`struct nfs4_filelayout` embeds the generic layout header and stores filelayout pNFS data-server commit info.

## Helper API

Inline helpers convert generic pNFS headers/segments to filelayout types: `FILELAYOUT_FROM_HDR()`, `FILELAYOUT_LSEG()`, and `FILELAYOUT_DEVID_NODE()`. `filelayout_test_devid_invalid()` checks the generic `NFS_DEVICEID_INVALID` flag.

The header declares deviceid availability checks, data-server filehandle selection, stripe/data-server index calculations, data-server preparation, deviceid allocation/free/put helpers, and deviceid-node allocation for the layoutdriver.

## Integration

This header is intentionally narrow: policy and I/O logic live in `filelayout.c`, while XDR GETDEVICEINFO decoding, data-server connection, and stripe-index helpers live in `filelayoutdev.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayoutdev.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayoutdev.c

## Role

`filelayoutdev.c` handles GETDEVICEINFO decoding and data-server preparation for the pNFS NFSv4.1 file layout driver. It turns opaque device data into cached data-server address structures, calculates stripe/data-server indices, selects filehandles, and establishes data-server NFSv4.1 client connections.

## Deviceid allocation and decoding

`nfs4_fl_alloc_deviceid_node()` decodes the pNFS file-layout device payload from XDR pages. It reads the stripe count, validates it against `NFS4_PNFS_MAX_STRIPE_CNT`, reads `u32` stripe indices into compact `u8` storage, reads the multipath list count and validates it against `NFS4_PNFS_MAX_MULTI_CNT`, and ensures no stripe index is outside the data-server count.

It then allocates `struct nfs4_file_layout_dsaddr` with a flexible `ds_list[]`, initializes the generic deviceid node, and for each multipath list decodes addresses via `nfs4_decode_mp_ds_addr()`. Valid address lists are converted into cached `struct nfs4_pnfs_ds` objects with `nfs4_pnfs_ds_add()`. Temporary decoded address nodes are drained after each data server.

Errors free the scratch folio, stripe-index array, partially built deviceid, and temporary address list. Successful allocations retain references to each data-server object and return the filelayout device address object.

## Deviceid freeing and references

`nfs4_fl_free_deviceid()` drops each referenced data server with `nfs4_pnfs_ds_put()`, frees stripe indices, and RCU-frees the `dsaddr` through the embedded deviceid node. `nfs4_fl_put_deviceid()` drops the generic deviceid-node reference.

## Stripe and filehandle selection

`nfs4_fl_calc_j_index()` computes the stripe index from `(offset - pattern_offset) / stripe_unit`, adds `first_stripe_index`, and wraps by `stripe_count`. `nfs4_fl_calc_ds_index()` maps stripe index `j` through the decoded compact `stripe_indices` table.

`nfs4_fl_select_ds_fh()` chooses the filehandle for the selected stripe. Sparse layouts with one filehandle always use index zero; sparse layouts with zero filehandles return `NULL` so callers use the MDS OPEN filehandle; sparse layouts with multiple handles use the data-server index; dense layouts use stripe index `j` directly.

## Data-server preparation

`nfs4_fl_prepare_ds()` validates that the selected data server exists, marks the deviceid invalid if not, and connects an unconnected data server with `nfs4_pnfs_ds_connect()`. Connection failure marks the deviceid unavailable. It returns `NULL` if the data server still has no client or if the deviceid is invalid/unavailable.

Connection behavior is controlled by module parameters `dataserver_timeo` and `dataserver_retrans`, defaulting to NFSv4 data-server timeout/retransmit defaults. These parameters tune NFSv4.1 client retry behavior for data-server RPCs.

## Concurrency notes

After checking `ds->ds_clp`, the code uses `smp_rmb()` before deciding whether a connection is visible. Deviceid availability is checked after connection setup so racing invalidation or unavailable marking prevents new pNFS I/O from using the data server.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayoutdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/Makefile

## Role

This Makefile builds the pNFS Flex File layout driver module when `CONFIG_PNFS_FLEXFILE_LAYOUT` is enabled.

## Build outputs

- Adds `nfs_layout_flexfiles.o` through `obj-$(CONFIG_PNFS_FLEXFILE_LAYOUT)`.
- Links the module from `flexfilelayout.o` and `flexfilelayoutdev.o`.

## Integration

The Makefile is parallel in structure to the file-layout driver Makefile, but targets the NFSv4 flexfiles layout implementation in the sibling `flexfilelayout` directory rather than the fixed file layout code researched in this group.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/Makefile -->