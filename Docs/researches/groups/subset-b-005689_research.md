# subset-b-005689 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/nfs/dir.c

## Purpose
`dir.c` implements the Linux NFS client directory and path-name side of VFS integration. It provides directory file operations, READDIR/READDIRPLUS caching, dentry revalidation, lookup and atomic-open plumbing, directory mutation operations, silly-rename coordination for active unlinks, rename/link/symlink handling, and the per-credential ACCESS cache used by permission checks.

## Important APIs, types, and functions
The exported surfaces include `nfs_dir_operations`, `nfs_dir_aops`, `nfs_dentry_operations`, `nfs4_dentry_operations`, `nfs_lookup`, `nfs_atomic_open`, `nfs_atomic_open_v23`, `nfs_add_or_obtain`, `nfs_instantiate`, `nfs_create`, `nfs_mknod`, `nfs_mkdir`, `nfs_rmdir`, `nfs_unlink`, `nfs_symlink`, `nfs_link`, `nfs_rename`, `nfs_access_get_cached`, `nfs_access_add_cache`, `nfs_access_set_mask`, `nfs_may_open`, and `nfs_permission`.

`struct nfs_open_dir_context` is allocated per opened directory and tracks directory cookie position, verifier bytes, adaptive directory transfer size, EOF state, and READDIRPLUS cache-hit/miss hints. `struct nfs_cache_array` is stored in page-cache folios and contains decoded directory entries, a starting/last cookie, change attribute, EOF/full flags, and a monotonic-cookie hint. `struct nfs_readdir_descriptor` is the transient state machine for a single `iterate_shared` call.

## Control flow
Directory open allocates an open-dir context, records current inode generation and cookie verifier, and links the context onto the NFS inode open-file list. `nfs_readdir` revalidates the mapping, copies the persistent cursor from the open context, decides whether to request READDIRPLUS from cache-hit/miss heuristics, and then searches/fills folio-backed cache arrays until either the caller buffer is full, EOF is reached, or an error stops iteration.

READDIR cache misses flow through `find_and_lock_cache_page`. It hashes the last cookie to a page-cache index, validates the folio against the directory change attribute and starting cookie, and fills it by issuing `NFS_PROTO(inode)->readdir`. XDR pages are decoded into cache arrays by `nfs_readdir_folio_filler`; READDIRPLUS entries also call `nfs_prime_dcache` to refresh or instantiate matching dentries. Bad cookies or verifier changes invalidate page-cache ranges and rewind the search. When a cookie cannot be found in page cache, `uncached_readdir` reads into anonymous folios and emits entries without installing them into the mapping.

Dentry validation starts with `nfs_lookup_revalidate` or `nfs4_lookup_revalidate`. The common path checks a blocked unlink/rename marker in `d_fsdata`, verifies parent directory change attributes saved in `d_time`, handles delegation-tagged dentries, and either trusts the cached inode or sends a fresh LOOKUP. Negative dentries are revalidated according to lookup-cache mount flags, create/rename intent, case-insensitive server capability, and parent change attributes. Atomic open for NFSv4 uses `open_context`, then `finish_open`; NFSv2/v3 emulate lookup-open with a create fast path.

Mutation operations call protocol methods through `NFS_PROTO(dir)`, then carefully update dcache and inode state. Failed create/mknod drops the dentry because the server may have completed the operation despite a reply error. Remove and rename block dentry revalidation while an unlink or target replacement is in flight, use silly rename when an active target cannot be removed, force writeback before unsafe file rename/link cases, and invalidate or update link count/change attributes after success.

Permission checks first consult a per-inode rb-tree keyed by fsuid, fsgid, and supplementary groups. If no usable cache entry exists, `nfs_do_access` sends ACCESS RPCs, stores the returned NFS access bits, converts them to VFS MAY bits, and applies local execute-bit checks.

## State and persistence behavior
No durable on-disk state is owned here; persistence is remote server state accessed through NFS protocol operations. Runtime state includes directory page-cache folios that store decoded names, per-open readdir cursors, NFS inode cookie verifiers, dentry verifiers in `d_time`, unlink/rename revalidation blocks in `d_fsdata`, access-cache rb-trees and LRUs, and NFS inode cache-validity bits.

Directory cache coherency depends on the parent directory change attribute and cookie verifier. When either changes, folios are reinitialized or invalidated so future `getdents` calls cannot reuse stale cookies. Dentry coherency relies on saved parent verifiers and delegation tags; delegation revocation clears the tag so later pathwalks perform real validation.

## Dependencies and integration points
The file integrates with VFS directory, dentry, inode, permission, and file-locking interfaces; SUNRPC/NFS protocol operation vectors; NFS inode cache invalidation; NFSv4 delegations and atomic OPEN; pNFS-independent writeback through `nfs_sync_inode`; fscache open context setup; idmapped VFS create hooks; Linux shrinker infrastructure for access-cache reclaim; and tracepoints in `nfstrace.h`.

Cross-file contracts include inode construction via `nfs_fhget`, protocol-specific lookup/create/remove/rename/access callbacks, silly-rename helpers, NFS open contexts from the regular file path, and NFSv4 directory delegation helpers.

## Risks
The highest-risk area is cache coherency. Incorrect verifier updates, failure to invalidate directory folios on cookie verifier changes, or trusting negative dentries on case-insensitive servers can produce stale lookups or missing entries. READDIR cookie hashing intentionally admits collisions, so validation by starting cookie and change attribute is essential.

Concurrency risks include races between unlink/rename and open/pathwalk, RCU pathwalk returning `-ECHILD` at the right points, dentry alias invalidation during READDIRPLUS priming, and access-cache rb-tree/LRU updates under inode and global locks. Silly rename paths must not leave `d_fsdata` blocked or leak renamed dentries. Access-cache timestamps also depend on login ancestry and must not grant permissions after a credential transition.

## Test signals
Useful signals include READDIR over changing directories, bad-cookie server replies, verifier changes between page-cache fills, 32-bit getdents position mode, READDIRPLUS fallback on `-ENOTSUPP`, dcache priming with stale aliases, case-insensitive negative lookups, lookup-cache mount flags, NFSv4 delegated pathwalks and delegation revocation, atomic open create/truncate/error cases, unlink of open files, rename over busy targets, cross-directory rename with unstable filehandles, ACCESS cache hits/misses/reclaim, and RCU pathwalk fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/direct.c -->
# sources/distributed-fs/ceph-client/fs/nfs/direct.c

## Purpose
`direct.c` implements uncached NFS I/O for `O_DIRECT` and swapfile paths. It bypasses the page cache for application buffers, builds NFS page requests directly from user or swap iterators, schedules pageio reads/writes, handles asynchronous completion, and drives unstable-write COMMIT or retry behavior for both metadata-server and pNFS data-server commits.

## Important APIs, types, and functions
The main entry points are `nfs_file_direct_read`, `nfs_file_direct_write`, `nfs_swap_rw`, `nfs_init_cinfo_from_dreq`, `nfs_dreq_bytes_left`, `nfs_init_directcache`, and `nfs_destroy_directcache`. Internally, `struct nfs_direct_req` carries the inode, open context, lock context, byte accounting, error state, async kiocb, commit-info structures, refcounts, completion, spinlock, and work item.

Read completion is handled by `nfs_direct_read_completion_ops`; write completion and retry by `nfs_direct_write_completion_ops`; unstable-write commit by `nfs_direct_commit_completion_ops`. Scheduling centers on `nfs_direct_read_schedule_iovec` and `nfs_direct_write_schedule_iovec`.

## Control flow
A direct read allocates an `nfs_direct_req`, captures the NFS open and lock contexts, marks asynchronous requests with the kiocb, optionally starts direct-I/O exclusion, then pins iterator pages in chunks sized by server `rsize`. Each pinned page becomes an `nfs_page` request and is fed into `nfs_pageio_add_request`; completion updates byte counts, marks user-backed read pages dirty when appropriate, releases requests, and completes the direct request when the outstanding I/O count reaches zero.

A direct write performs generic write checks unless it is swap I/O, allocates a direct request, initializes pNFS commit info, starts direct-I/O exclusion, and pins iterator pages in chunks sized by server `wsize`. Requests are submitted through the NFS pageio write path with conditional stability for normal direct I/O and stable writes for swap. After submission, any overlapping page-cache range is invalidated for normal direct writes, then the caller waits or receives async completion.

Completion tracks `count`, `max_count`, and `error` under `dreq->lock`. EOF or header errors truncate the visible result to the first failed byte. Unstable writes are marked for COMMIT; verifier mismatch or soft `-EAGAIN` failures move requests to commit/retry lists and queue `nfsiod_workqueue` work to reschedule writes. Fatal commit errors truncate the result and complete with the first error.

## State and persistence behavior
This file owns runtime state only. Direct data persistence is server-side: normal direct writes use conditional stable writes and may need COMMIT, while swap writes request stable storage. `nfs_direct_file_adjust_size_locked` updates local `i_size` optimistically when a direct write extends the file, clearing invalid-size state after server write success.

The direct request lifetime uses both a kref and an I/O counter. The kref protects allocation lifetime across caller, async completion, and workqueue paths; `io_count` gates final completion after all pageio headers and commit work have drained.

## Dependencies and integration points
`direct.c` depends on NFS pageio, NFS request, commit, lock-context, open-context, pNFS commit-info, fscache invalidation, inode direct-I/O exclusion helpers, generic write sync, task I/O accounting, and `nfsiod_workqueue`. It is called from `file.c` for `IOCB_DIRECT` and from NFS swap address-space operations.

## Risks
Accounting bugs can return too many bytes, fail to rewind the iterator, or hide the first error. Retry and commit paths are sensitive to request reference counts, locked request state, verifier comparison, pNFS data-server commit buckets, and the transition between `NFS_ODIRECT_DO_COMMIT`, `NFS_ODIRECT_RESCHED_WRITES`, and done states. Page pin/release balance is also critical under short reads, allocation failures, and partial scheduling.

## Test signals
Exercise synchronous and asynchronous direct reads/writes, short reads at EOF, server write errors after partial success, unstable writes requiring COMMIT, COMMIT verifier mismatch, pNFS DS commit fallback, iterator rewind after partial direct I/O, page-cache invalidation for overlapping buffered readers, swap read/write paths, signal interruption of synchronous waits, and allocation failure in page pinning or request creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/dns_resolve.c -->
# sources/distributed-fs/ceph-client/fs/nfs/dns_resolve.c

## Purpose
`dns_resolve.c` resolves NFS hostnames to socket addresses for NFSv4 referrals and related client paths. It has two implementations: a simple kernel-DNS path using `dns_query`, and a legacy SUNRPC cache/upcall path that asks user space through rpc_pipefs and caches positive or negative hostname results per network namespace.

## Important APIs, types, and functions
The public API is `nfs_dns_resolve_name`, with lifecycle hooks `nfs_dns_resolver_init`, `nfs_dns_resolver_destroy`, `nfs_dns_resolver_cache_init`, and `nfs_dns_resolver_cache_destroy` when kernel DNS is not enabled.

The cache implementation uses `struct nfs_dns_ent`, embedding `struct cache_head` plus hostname, resolved `sockaddr_storage`, address length, and RCU free state. Cache operations include `nfs_dns_ent_init`, `nfs_dns_ent_update`, `nfs_dns_ent_put`, `nfs_dns_hash`, `nfs_dns_match`, `nfs_dns_request`, `nfs_dns_upcall`, `nfs_dns_parse`, and `nfs_dns_show`.

## Control flow
With `CONFIG_NFS_USE_KERNEL_DNS`, `nfs_dns_resolve_name` directly calls `dns_query`, then parses the returned textual address with `rpc_pton`. Query failures map to `-ESRCH`, and the allocated string is freed.

Without kernel DNS, initialization registers per-net operations and an rpc_pipefs notifier. Each net namespace gets a `cache_detail` cloned from `nfs_dns_resolve_template` and registered with NFS cache infrastructure. A resolve call builds a transient key from the hostname, calls `do_cache_lookup_wait`, and either copies the cached address into the caller buffer or returns `-EOVERFLOW`/`-ESRCH`.

Cache misses trigger `nfs_dns_upcall`, which sets `CACHE_PENDING`, tries the NFS cache upcall helper, and falls back to a SUNRPC cache pipe upcall timeout. User-space replies are parsed by `nfs_dns_parse` as address, hostname, and TTL. Zero-length parsed addresses become negative cache entries; nonzero TTL sets expiry relative to boot time.

## State and persistence behavior
All state is runtime cache state. Entries are keyed by hostname and expire by TTL or cache flush time. Positive entries store a binary socket address; negative entries store only hostname plus the `CACHE_NEGATIVE` flag. Entries are reference-counted by SUNRPC cache code and freed by RCU callback after the final put.

Per-net state lives in `struct nfs_net::nfs_dns_resolve`. rpc_pipefs mount and unmount events register or unregister the cache detail with the pipefs superblock so user-space upcall endpoints are available only while pipefs is mounted.

## Dependencies and integration points
The direct path depends on `linux/dns_resolver.h`, `dns_query`, and SUNRPC address parsers. The upcall path depends on SUNRPC cache APIs, rpc_pipefs notifier APIs, NFS cache helper code, network namespaces, and `nfs4_fs.h`/`netns.h` for NFSv4 client integration.

## Risks
Resolver behavior differs by configuration. Kernel-DNS mode has no local cache lifecycle here, while upcall mode depends on rpc_pipefs availability and user-space responders. Parser risk includes malformed cache lines, TTL zero, hostname length limits, IPv6 scope formatting, negative-cache semantics, and caller buffer overflow. Cache lookup must not return expired, flushed, pending, or negative entries as usable addresses.

## Test signals
Cover kernel-DNS success/failure, IPv4 and IPv6 parsing, caller buffer too small, rpc_pipefs mount/unmount registration, user-space upcall timeout, positive and negative cache replies, TTL expiry, cache flush, malformed parse inputs, per-net namespace create/destroy, and concurrent lookups for the same pending hostname.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/dns_resolve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/dns_resolve.h -->
# sources/distributed-fs/ceph-client/fs/nfs/dns_resolve.h

## Purpose
`dns_resolve.h` declares the NFS DNS resolver interface and hides configuration-dependent resolver lifecycle behavior. It lets callers use `nfs_dns_resolve_name` regardless of whether hostname resolution is implemented by kernel DNS or by the SUNRPC cache/upcall mechanism.

## Important APIs, types, and functions
The header defines `NFS_DNS_HOSTNAME_MAXLEN` as 128 bytes. It declares `nfs_dns_resolve_name(struct net *net, char *name, size_t namelen, struct sockaddr_storage *sa, size_t salen)`.

When `CONFIG_NFS_USE_KERNEL_DNS` is enabled, resolver init/destroy and per-net cache init/destroy are static inline no-ops returning success. Otherwise, those lifecycle functions are declared for the cache implementation in `dns_resolve.c`.

## Control flow
Callers include the header, call global resolver initialization during NFS client/module setup, call per-network-namespace cache setup where needed, and resolve names through `nfs_dns_resolve_name`. The inline no-op branch avoids registering rpc_pipefs cache machinery when kernel DNS is the resolver backend.

## State and persistence behavior
The header has no state. It defines the build-time contract for whether resolver state is external to this subsystem or owned by the SUNRPC cache path in `dns_resolve.c`.

## Dependencies and integration points
The declarations depend on `struct net` and `struct sockaddr_storage` being visible to includers. The header is included by the resolver implementation and by NFS client code that initializes, tears down, or uses hostname resolution.

## Risks
The main risk is configuration skew: callers must not assume cache lifecycle side effects exist in kernel-DNS builds. Hostname length validation is only a constant here; actual parser and caller code must enforce it consistently.

## Test signals
Build both `CONFIG_NFS_USE_KERNEL_DNS=y` and `n`, verify lifecycle calls link and are idempotent in both modes, and test maximum-length hostname handling through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/dns_resolve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/export.c -->
# sources/distributed-fs/ceph-client/fs/nfs/export.c

## Purpose
`export.c` provides exportfs operations for re-exporting an NFS-mounted filesystem. It encodes NFS inode identity into export file handles, reconstructs dentries from those handles, finds parent dentries when supported, and advertises export behavior flags appropriate for a remote filesystem.

## Important APIs, types, and functions
The public object is `nfs_export_ops`. Its callbacks are `nfs_encode_fh`, `nfs_fh_to_dentry`, and `nfs_get_parent`. Helper `nfs_exp_embedfh` locates the embedded NFS server file handle inside the exportfs raw file-handle word array.

Encoded handles contain high and low 32-bit portions of `NFS_FILEID(inode)`, the inode file type, and a serialized `struct nfs_fh`. The file explicitly uses `EXPORT_OP_NOSUBTREECHK`, so parent handles are not embedded.

## Control flow
`nfs_encode_fh` computes the number of 32-bit words needed for the fixed identity words plus the embedded NFS file handle. If the caller buffer is too small it reports the required size and returns `FILEID_INVALID`; otherwise it stores fileid, type, padding, copies the server file handle, and returns the encoded length as the file-handle type.

`nfs_fh_to_dentry` validates bounds and type/length consistency, reconstructs a minimal `nfs_fattr` from encoded fileid and type, tries `nfs_ilookup` with the embedded file handle, and falls back to server `getattr` followed by `nfs_fhget`. The final inode is converted to a disconnected alias dentry with `d_obtain_alias`.

`nfs_get_parent` requires protocol `lookupp` support. It sends LOOKUPP for the child inode, obtains the parent file handle and attributes, then returns a parent alias dentry.

## State and persistence behavior
The encoded export file handle is persistent from exportfs/NFSD's perspective but depends on the remote NFS server file handle remaining valid. The implementation does not persist local state. Reconstructed dentries rely on NFS inode cache lookup or server getattr to refresh attributes.

## Dependencies and integration points
This file integrates with Linux exportfs, NFSD re-export behavior, NFS inode/filehandle helpers, NFS RPC operation vectors, and tracepoints for stale handle diagnostics. Export flags tell upper layers that this is a remote filesystem, subtree checking is unsupported, close-before-unlink and flush-on-close are needed, atomic local attributes and locks should not be assumed, and weak cache consistency data is not supplied.

## Risks
Re-export correctness depends on server file-handle stability. Subtree checking is intentionally disabled because parent file handles may not fit. Bounds validation around embedded `struct nfs_fh` is critical because the input handle comes from an external file-handle decoder. `fh_type` is treated as the encoded word length, so callers with stale or corrupted handles should receive ESTALE-like NULL/ERR behavior.

## Test signals
Test export handle encode/decode with small buffers, maximum NFS file handles, stale handles, cached inode hits, getattr fallback, missing `lookupp`, parent lookup failures, file type mismatch, and re-export unlink/close behavior through NFSD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/file.c -->
# sources/distributed-fs/ceph-client/fs/nfs/file.c

## Purpose
`file.c` implements regular-file VFS operations for the NFS client. It covers open/release, read/write dispatch, direct-I/O handoff, mmap setup and page-mkwrite, fsync and flush, buffered write begin/end, address-space operations, swapfile support, and POSIX/flock locking integration.

## Important APIs, types, and functions
Public exports include `nfs_check_flags`, `nfs_file_release`, `nfs_file_read`, `nfs_file_splice_read`, `nfs_file_mmap_prepare`, `nfs_file_fsync`, `nfs_truncate_last_folio`, `nfs_file_write`, `nfs_lock`, `nfs_flock`, `nfs_file_aops`, and `nfs_file_operations`.

Important internal functions include `nfs_revalidate_file_size`, `nfs_file_flush`, `nfs_file_fsync_commit`, `nfs_write_begin`, `nfs_write_end`, `nfs_invalidate_folio`, `nfs_release_folio`, `nfs_check_dirty_writeback`, `nfs_launder_folio`, `nfs_swap_activate`, `nfs_swap_deactivate`, `nfs_vm_page_mkwrite`, `do_getlk`, `do_unlk`, and `do_setlk`.

## Control flow
Open validates incompatible `O_APPEND|O_DIRECT`, calls `nfs_open`, and marks the file as capable of direct I/O. Reads dispatch to `nfs_file_direct_read` for `IOCB_DIRECT`; otherwise they take NFS read I/O exclusion, revalidate the mapping, use generic file read/splice helpers, and update statistics.

Buffered writes first check key expiry, reject writes to active swapfiles, revalidate size for append or beyond-EOF writes, clear invalid mapping state, take NFS write I/O exclusion, run generic write checks, and call `generic_perform_write`. `nfs_write_begin` truncates/zeros the last folio for extending writes, flushes incompatible pending writes, and may do read-modify-write for partial folio writes depending on pNFS layout requirements and file open mode. `nfs_write_end` zeroes uninitialized folio regions, calls `nfs_update_folio`, and may force writeback when the open context key is expiring.

Fsync loops until no redirtied pages were observed across writeback, commit, and pNFS sync. Flush writes all dirty pages for writable files and reports writeback errors through errseq state. `mmap_prepare` installs NFS vm operations after generic mmap validation and mapping revalidation; `nfs_vm_page_mkwrite` serializes against fscache, invalidation, and writeback before converting a shared mapping write into an NFS dirty folio update.

Locking flushes or syncs pending writes before remote lock transitions. GETLK consults local locks first, then remote locks unless a delegation or local-lock mount option avoids RPC. SETLK/UNLK call protocol locks or local lock helpers and use lock acquisition as a cache-coherency boundary.

## State and persistence behavior
NFS file data persistence is remote. Local runtime state includes page-cache folios, NFS private folio/writeback state, open contexts, writeback error cursors, fscache state, mmap dirtying state, redirtied-page counters, and lock contexts. Fsync/flush force dirty pages and unstable writes through NFS writeback and commit machinery so server-side durability is reflected to the caller.

Swap activation checks that the NFS file has no holes based on `i_blocks` and `i_size`, activates SUNRPC swap mode, installs one synthetic swap extent, and lets protocol code enable or disable swap-specific behavior.

## Dependencies and integration points
The file is the bridge between VFS file operations, Linux address-space operations, NFS read/write/commit paths, direct I/O from `direct.c`, pNFS layout sync and read-whole-page policy, fscache, MM mmap/pagefault code, swap subsystem, file locking, NFS delegations, mount flags, and NFS statistics/tracepoints.

## Risks
Cache coherency is the main risk. Reads must revalidate stale mappings; writes must not collide with incompatible pending NFS private state; locks and mmap writes must act as coherency points. Fsync must loop on redirtied pages or risk returning before unstable writes settle. Direct and buffered I/O interleaving relies on `nfs_start_io_*` exclusion and page-cache invalidation.

Folio paths are sensitive to partial writes, zeroing beyond EOF, fscache private state, writeback cancellation during invalidation, and reclaim contexts that cannot block. Locking paths risk deadlocks or stale data if writeback is not drained before remote lock calls.

## Test signals
Cover buffered and direct reads/writes, append with remote size changes, partial folio writes requiring read-modify-write, pNFS read-whole-page layouts, mmap shared writes, fsync with redirtied pages, writeback errors `EDQUOT/EFBIG/ENOSPC`, eager/wait mount flags, swap activation on sparse and nonsparse NFS files, local-lock mount options, delegation-aware locks, and cache invalidation around lock acquire/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/filelayout/Makefile -->
# sources/distributed-fs/ceph-client/fs/nfs/filelayout/Makefile

## Purpose
This Makefile builds the pNFS NFSv4.1 files layout driver module when `CONFIG_PNFS_FILE_LAYOUT` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_PNFS_FILE_LAYOUT) += nfs_layout_nfsv41_files.o` and composes that object from `filelayout.o` and `filelayoutdev.o`.

## Control flow
During kernel build, Kbuild includes the composite object only for enabled configurations. The resulting module/object contains the layout-driver registration code from `filelayout.c` and deviceid/data-server helpers from `filelayoutdev.c`.

## State and persistence behavior
The Makefile has no runtime state. Its build-time state determines whether the file layout driver can register and handle `LAYOUT_NFSV4_1_FILES`.

## Dependencies and integration points
It integrates with Kbuild and the NFS/pNFS configuration system. The object name becomes the loadable module name for the files layout driver.

## Risks
If source membership is wrong, the module may register without deviceid helpers or fail to link. Configuration tests need to ensure both implementation files are present when pNFS files layout is enabled.

## Test signals
Build with `CONFIG_PNFS_FILE_LAYOUT=m`, `y`, and disabled; verify module link symbols, module alias availability, and successful layout-driver registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/filelayout/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayout.c -->
# sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayout.c

## Purpose
`filelayout.c` implements the pNFS NFSv4.1 files layout driver. It decodes file layout segments, validates deviceids, maps logical file offsets to data-server offsets, routes reads/writes/commits to data servers, handles data-server errors and fallback to the metadata server, maintains pNFS commit buckets, and registers the layout driver with the generic pNFS client.

## Important APIs, types, and functions
The driver registers `filelayout_type` with layout id `LAYOUT_NFSV4_1_FILES`. Key operations are `filelayout_alloc_layout_hdr`, `filelayout_free_layout_hdr`, `filelayout_alloc_lseg`, `filelayout_free_lseg`, `filelayout_read_pagelist`, `filelayout_write_pagelist`, `filelayout_commit_pagelist`, `filelayout_alloc_deviceid_node`, and `filelayout_free_deviceid_node`.

Offset and striping helpers include `filelayout_get_dense_offset`, `filelayout_get_dserver_offset`, `filelayout_pg_test`, `select_bucket_index`, `calc_ds_index_from_commit`, and `select_ds_fh_from_commit`. Error and callback machinery includes `filelayout_async_handle_error`, read/write/commit prepare and done callbacks, `filelayout_reset_read`, `filelayout_reset_write`, and `filelayout_set_layoutcommit`.

## Control flow
Layout allocation decodes opaque `LAYOUTGET` data with XDR into a `struct nfs4_filelayout_segment`: deviceid, utilization flags, dense/sparse mode, commit-through-MDS flag, stripe unit, first stripe index, pattern offset, and file-handle array. The layout is validated for sane pattern offset and stripe unit, and later `filelayout_check_deviceid` binds the segment to a cached deviceid node, validates stripe index and file-handle counts, and atomically installs `fl->dsaddr`.

Read and write pageio initialization uses `fl_pnfs_update_layout` to acquire an appropriate layout segment. If no segment is available or a recoverable error occurs, pageio falls back to MDS operations. Coalescing is limited by generic pNFS checks and, for striped layouts, by stripe-unit boundaries so a single pageio header does not cross an incompatible data-server stripe.

For a DS read/write, the driver computes `j` from file offset, pattern offset, stripe unit, and first stripe index, maps it to a DS index through the device stripe map, prepares the DS connection, selects a data-server file handle, converts dense-layout offsets when needed, and initiates an async NFS RPC against the DS client. Completion callbacks handle NFSv4 sequence setup, stateid selection, stats, and propagation back to generic NFS pageio code.

Unstable writes are assigned to MDS or DS commit lists depending on `commit_through_mds` and stripe type. DS commit initiation selects the correct data server and file handle, then uses generic NFS commit setup with filelayout-specific call ops. Commit completion can request resend through MDS or set layoutcommit state.

## State and persistence behavior
Runtime state includes per-layout `struct nfs4_filelayout` commit info, per-segment file handles and deviceid reference, data-server client references on active RPC headers, layout failure flags, pNFS commit arrays, and layoutcommit markers. Persistent file data and layout metadata remain on the NFS server/MDS; this driver only caches decoded layout and device state.

Layout invalidation and fallback are explicit. Fatal DS layout errors destroy or mark the layout for return, wake waiters on the session slot table, and resend failed I/O through the MDS. Connection errors mark deviceids unavailable and set layout failure so future I/O avoids the broken DS until recovery.

## Dependencies and integration points
The driver depends on generic pNFS layout management, NFSv4.1 sessions, NFS pageio, NFS commit infrastructure, NFSv4 stateid/delegation helpers, SUNRPC task call ops, deviceid cache management from `filelayoutdev.c`, and layout-driver registration. It integrates directly with `direct.c` and buffered writeback through generic NFS pageio and commit abstractions.

## Risks
Offset math and stripe selection are correctness-critical. Dense layouts rewrite offsets; sparse layouts preserve offsets but may have one, zero, or many file handles. Bad file-handle count validation, stripe-unit crossing, or commit-bucket mapping can send data or COMMIT to the wrong DS. Error handling also must distinguish recoverable delays/session issues from layout-invalidating or device-unavailable failures.

Reference management is sensitive: DS client references, lseg references, commit-array lifetime, and RCU layout header freeing must align with asynchronous RPC completion. Fallback paths must set `NFS_IOHDR_REDO` exactly once and avoid double sequence completion.

## Test signals
Test sparse and dense layouts, single and multiple file handles, zero file-handle sparse layout, stripe-boundary pageio coalescing, commit-through-MDS and DS commit modes, DS session errors, DS connection failures, stale/badhandle layout errors, layout return after failure, verifier mismatch on commit, layoutcommit end-offset behavior, and module register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayout.h -->
# sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayout.h

## Purpose
`filelayout.h` defines the data structures, constants, inline accessors, and cross-file prototypes for the pNFS NFSv4.1 files layout driver.

## Important APIs, types, and functions
It sets `NFS4_PNFS_MAX_STRIPE_CNT` to 4096 and `NFS4_PNFS_MAX_MULTI_CNT` to 256, reflecting a memory-saving representation of wire stripe indices as `u8`. `enum stripetype4` defines `STRIPE_SPARSE` and `STRIPE_DENSE`.

`struct nfs4_file_layout_dsaddr` represents decoded GETDEVICEINFO data: generic deviceid node, stripe count, compact stripe-index array, data-server count, and a flexible array of `struct nfs4_pnfs_ds *`. `struct nfs4_filelayout_segment` wraps a generic layout segment with striping mode, commit policy, stripe unit, first stripe index, pattern offset, deviceid, bound dsaddr, and file-handle array. `struct nfs4_filelayout` wraps a generic layout header with pNFS DS commit info.

Inline helpers include `FILELAYOUT_FROM_HDR`, `FILELAYOUT_LSEG`, `FILELAYOUT_DEVID_NODE`, and `filelayout_test_devid_invalid`. Prototypes expose data-server file-handle selection, stripe math, DS preparation, deviceid allocation/put/free, and unavailable-device tests.

## Control flow
The header is included by `filelayout.c` and `filelayoutdev.c`. `filelayout.c` owns layout segment decode, I/O, commits, and registration; `filelayoutdev.c` owns deviceid decode and DS connection. The shared structures let both files consistently translate layout segments into deviceid and data-server choices.

## State and persistence behavior
The structures describe cached runtime copies of MDS-provided layouts and deviceid information. References to deviceids and data servers are managed by pNFS caches, with RCU freeing on deviceid destruction. There is no local persistent state.

## Dependencies and integration points
The header depends on `../pnfs.h` and NFS/pNFS types. It is part of the module-private contract between layout routing code and deviceid management, and it exposes only the symbols needed across the two source files.

## Risks
The compact `u8` stripe-index representation requires strict validation that decoded stripe indices fit below 256 and below the DS count. Accessors assume `fl->dsaddr` is non-NULL when deriving the deviceid node, so callers must run deviceid validation first. Counted flexible arrays and file-handle arrays must be allocated and freed consistently.

## Test signals
Build tests should catch prototype drift. Runtime tests should cover maximum stripe counts, maximum multipath counts, invalid stripe indices, dense/sparse file-handle count validation, NULL dsaddr avoidance, and deviceid unavailable/invalid flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayoutdev.c -->
# sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayoutdev.c

## Purpose
`filelayoutdev.c` implements deviceid and data-server operations for the pNFS files layout driver. It decodes GETDEVICEINFO opaque device data, builds the stripe-index table and data-server list, manages deviceid lifetime, computes stripe/data-server indices, selects per-stripe file handles, and connects to data servers on demand.

## Important APIs, types, and functions
Public functions are `nfs4_fl_alloc_deviceid_node`, `nfs4_fl_free_deviceid`, `nfs4_fl_put_deviceid`, `nfs4_fl_calc_j_index`, `nfs4_fl_calc_ds_index`, `nfs4_fl_select_ds_fh`, and `nfs4_fl_prepare_ds`. Module parameters `dataserver_timeo` and `dataserver_retrans` tune DS RPC connection retry behavior.

## Control flow
`nfs4_fl_alloc_deviceid_node` initializes an XDR stream over `pnfs_device` pages, decodes the stripe count, reads each 32-bit wire stripe index into a compact `u8` array, decodes the multipath/data-server count, validates limits and index ranges, allocates a flexible `nfs4_file_layout_dsaddr`, and initializes its generic deviceid node.

For each data-server entry, it decodes the multipath count and repeatedly calls `nfs4_decode_mp_ds_addr` to collect usable addresses. The address list is added to or looked up in the pNFS DS cache with `nfs4_pnfs_ds_add`; decoded temporary addresses are then drained. Failures unwind scratch folio, stripe indices, DS addresses, and any partially built dsaddr.

Stripe math uses `(offset - pattern_offset) / stripe_unit + first_stripe_index`, modulo stripe count, to derive `j`. The DS index is `stripe_indices[j]`. File-handle selection differs by sparse versus dense layouts: sparse layouts can use one shared file handle, the MDS OPEN file handle when `num_fh == 0`, or the DS index; dense layouts use the stripe index directly.

`nfs4_fl_prepare_ds` checks that the chosen DS exists, verifies or establishes the DS client connection with `nfs4_pnfs_ds_connect`, marks the deviceid unavailable on connection failure, and refuses to return a DS if the deviceid has become invalid/unavailable.

## State and persistence behavior
Decoded deviceid state is cached in memory and tied to the generic pNFS deviceid cache. Each dsaddr owns the stripe-index array and references to cached `struct nfs4_pnfs_ds` objects. Freeing drops DS references, frees the stripe table, and RCU-frees the dsaddr. Data-server connections are created lazily and cached in each DS object.

No local persistent state exists. Device availability state is runtime recovery state maintained through generic pNFS deviceid flags.

## Dependencies and integration points
This file depends on XDR decode helpers, folios for scratch decode, NFSv4 session/deviceid helpers, pNFS DS address decode/cache helpers, network namespace state from the server NFS client, and `filelayout.h` structures shared with `filelayout.c`.

## Risks
Malformed device data can otherwise corrupt routing. The code must reject excessive stripe counts, excessive multipath counts, stripe indices outside the DS list, empty usable DS address lists, and oversized file handles selected later by layout code. The compact `u8` array depends on enforcing the 256 multipath maximum before assignment.

Connection races are controlled by memory barriers and cached `ds_clp` checks; callers must handle NULL returns by falling back. If unavailable deviceids are not marked correctly, the client can repeatedly try broken DS paths or fail to return layouts.

## Test signals
Test valid and invalid GETDEVICEINFO blobs, zero/large stripe counts, maximum 4096 stripes, multipath count above 256, stripe index equal to DS count, empty multipath address lists, duplicate DS cache hits, DS connect failure, deviceid invalid/unavailable transitions, sparse zero-FH selection, dense stripe file-handle selection, and module parameter effects on DS connection attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/filelayout/filelayoutdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/Makefile -->
# sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/Makefile

## Purpose
This Makefile builds the pNFS flexfile layout driver module when `CONFIG_PNFS_FLEXFILE_LAYOUT` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_PNFS_FLEXFILE_LAYOUT) += nfs_layout_flexfiles.o` and composes that object from `flexfilelayout.o` and `flexfilelayoutdev.o`.

## Control flow
Kbuild includes the composite object only for configurations that enable the flexfile layout driver. The two implementation files are linked together into the module/object that registers the flexfile layout type elsewhere in the directory.

## State and persistence behavior
The file has no runtime state. Its only effect is build-time inclusion of flexfile layout support.

## Dependencies and integration points
It integrates with the kernel NFS/pNFS configuration and module build system. It is parallel to the files-layout Makefile but targets the flexfile driver implementation files.

## Risks
Incorrect object membership would cause link failures or a module missing either layout logic or device/data-server support. Configuration drift between Kconfig and object names would prevent flexfile layout support from loading.

## Test signals
Build with `CONFIG_PNFS_FLEXFILE_LAYOUT=m`, `y`, and disabled; verify the resulting object links, module loads when modular, and the layout driver registers with its implementation objects present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/Makefile -->
