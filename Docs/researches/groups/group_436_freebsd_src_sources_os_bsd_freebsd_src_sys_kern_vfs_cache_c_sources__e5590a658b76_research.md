# Group Research: group_436_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_vfs_cache_c_sources__e5590a658b76

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_cache.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_cache.c

## Purpose
Implements FreeBSD's VFS name cache and fast pathname lookup machinery. It caches individual path components, supports positive and negative lookup entries, resolves vnode-to-path strings for getcwd/realpath/auditing, provides cache maintenance hooks for VOP operations, and implements SMR/sequence-counter based lockless pathname lookup.

## Main Elements
- Cache data model:
  - `struct namecache` stores `(directory vnode, component name) -> vnode` mappings or negative entries.
  - `struct namecache_ts` extends entries with filesystem-supplied timestamps.
  - `struct negstate` and per-CPU-ish negative lists track negative cache hot/cold state and eviction.
  - Vnodes maintain source-entry lists, destination-entry lists, and `v_cache_dd` parent/dotdot shortcuts.
- Allocation and sizing:
  - Four UMA SMR zones hold small/large entries with or without timestamps.
  - `cache_symlink_alloc()` / `cache_symlink_free()` reuse namecache UMA zones for cached symlink bodies.
  - `nchinit()` initializes zones, hash table, bucket locks, vnode lock arrays, and negative-entry lists.
  - `cache_changesize()` rebuilds the hash table while preserving lockless lookup safety with temporary tables and SMR synchronization.
- Hashing and locking:
  - Hashes use FNV over the component name seeded by a per-vnode prehash.
  - Bucket locks protect hash chains; vnode-lock arrays protect vnode cache lists.
  - Insertion/removal code orders vnode locks and bucket locks carefully, including 3-vnode cases around directory parent entries.
- Lookup path:
  - `cache_lookup()` handles normal cache lookup using SMR when possible, with locked fallback.
  - Special cases support `"."`, `".."`, negative hits, whiteouts, CREATE-time negative invalidation, and timestamp returns.
  - `vfs_cache_lookup()` is the filesystem-facing VOP lookup wrapper that performs directory/read-only/execute checks, consults the cache, then calls `VOP_CACHEDLOOKUP()` on misses.
- Entry creation and invalidation:
  - `cache_enter_time()` inserts positive, negative, dotdot, and timestamped entries.
  - `cache_enter_time_flags()` supports `VFS_CACHE_DROPOLD`, mainly for filesystems such as NFS where target mappings may change.
  - `cache_remove_cnp()`, `cache_zap_locked()`, and helper paths remove entries by component.
  - `cache_purge()`, `cache_purge_vgone()`, `cache_purge_negative()`, and `cache_purgevfs()` remove entries for vnodes or entire mounts.
  - `cache_vop_rename()` and `cache_vop_rmdir()` keep cache state aligned with rename/rmdir operations.
- Negative-entry policy:
  - Negative entries are tracked separately from positive destination lists.
  - Hits increment a small hit counter and promote entries to hot lists after a threshold.
  - `cache_neg_evict()` demotes hot entries and evicts cold entries when total cache pressure or negative-entry ratios cross thresholds.
- Reverse path and syscall support:
  - `sys___getcwd()` and `vn_getcwd()` produce current working directory strings.
  - `sys___realpathat()` / internal realpath logic performs lookup then reconstructs canonical paths.
  - `vn_fullpath()`, `vn_fullpath_jail()`, and `vn_fullpath_global()` build paths relative to chroot, jail root, or global root.
  - `vn_fullpath_hardlink()` handles non-directory vnode path reconstruction using the parent/name captured by lookup.
  - `vn_vptocnp()` uses namecache reverse entries first, then falls back to `VOP_VPTOCNP()`.
  - `vn_path_to_global_path()` and hardlink variant rebuild a global path and re-lookup it to detect rename races.
- Lockless fast lookup:
  - `cache_fplookup()` is the fast path entered by `namei`.
  - `struct cache_fpl` tracks lookup state, saved fallback state, current/target vnodes, sequence counters, path position, and outcome.
  - `cache_can_fplookup()` rejects unsupported flags, Capsicum/cap-tracing, audit, explicit start directories, disabled fast lookup, and MAC cases.
  - `cache_fplookup_impl()` parses each component, runs filesystem `VOP_FPLOOKUP_VEXEC`, consults cache entries, crosses mount points, follows supported symlinks, and finalizes vnode refs/locks.
  - Partial fallback preserves progress by installing `ni_startdir` and compatible `nameidata` state for the regular locked lookup path.
  - `cache_symlink_resolve()` lets filesystem fast symlink handlers rewrite the remaining path buffer.
- Filesystem fast-lookup registration:
  - `cache_vop_vector_register()` ensures filesystems provide both fast lookup VOPs or neither.
  - `cache_validate_vop_vector()` asserts fast lookup mounts have valid `vop_fplookup_vexec` and `vop_fplookup_symlink`.
  - `cache_fast_lookup_enabled_recalc()` disables the fast path when sysctl or MAC policy makes it unsafe.
- Observability and diagnostics:
  - Numerous `vfs:namecache` and `vfs:fplookup` SDT probes expose lookup, insertion, purge, fullpath, and fast-lookup outcomes.
  - Sysctls expose cache size, hit percentage, positive/negative hit/miss counters, fullpath failures, negative eviction counters, and debug stats.
  - DDB `show vpath` prints cached reverse path chains.
- Inotify integration:
  - `cache_vop_inotify()` logs self and parent-directory events using cached destination entries and lazily clears `VIRF_INOTIFY_PARENT`.

## Dependencies And Integration
Uses FreeBSD VFS vnode/mount/namei interfaces, SMR, sequence counters, vnode ref/lock APIs, UMA, sysctl, DTrace SDT probes, Capsicum, MAC hooks, audit checks, inotify, KTRACE, DDB, and filesystem VOP methods. Filesystems integrate by routing lookup through `vfs_cache_lookup()`, inserting entries with `cache_enter*()`, purging via `cache_purge*()` or VOP cache hooks, and optionally implementing fast lookup VOPs under `MNTK_FPLOOKUP`.

## Risk Notes
This file is highly concurrency-sensitive. Correctness depends on SMR lifetime guarantees, sequence-counter validation, lock ordering across vnode and bucket locks, and careful fallback from lockless to locked lookup. Reverse path reconstruction is inherently best-effort for hardlinks and can race with rename. Negative-entry eviction is intentionally approximate and can fail under contention. The file also documents several known limitations: component rather than full-path caching, incomplete hardlink tracking, optional filesystem participation, wasted fixed-size entry space, duplicated tmpfs-style name storage, and performance bottlenecks around hashing and namei detours.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_cluster.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_cluster.c

## Purpose
Implements clustered VFS buffer I/O for FreeBSD: synchronous reads with read-ahead, read cluster construction, delayed-write clustering, write-behind, and per-vnode cluster state initialization.

## Main Elements
- Initialization and tunables:
  - `cluster_init()` creates the secondary pbuf zone used for synthetic cluster buffers.
  - `vfs.write_behind` controls clustered write-behind behavior.
  - `vfs.read_max` and `vfs.read_min` bound read-ahead behavior.
- Read path:
  - `cluster_read()` replaces simple `bread` style access for filesystems that want clustered reads.
  - It fetches the requested logical block with `getblkx()`, honors cached hits, marks read-ahead positions with `B_RAM`, and detects sequential access using `seqcount`.
  - For non-cached sequential reads, it calls `VOP_BMAP()` to discover physical contiguity and builds larger I/O with `cluster_rbuild()`.
  - It issues the synchronous requested read first, then asynchronously schedules read-ahead buffers while respecting mount I/O size, file size, cache state, delayed writes, and sparse/unmapped flags.
- Read cluster construction:
  - `cluster_rbuild()` synthesizes a `B_CLUSTER` buffer over VM pages from multiple logical buffers.
  - It stops clustering on locked buffers, cached buffers, non-VMIO buffers, partially valid pages, invalid mappings, or mount I/O size limits.
  - It handles page busying, page-in-progress accounting, bogus-page replacement for already valid pages, optional unmapped buffers, and pmap temporary mappings.
- Cluster completion:
  - `cluster_callback()` propagates I/O errors from the synthetic cluster buffer to children, clears dirty/error state on success, restores `B_RELBUF` for direct I/O, completes child buffers, releases the pbuf vnode binding, and frees the pbuf.
- Write path:
  - `cluster_write()` tracks sequential write state in `struct vn_clusterw`.
  - It decides whether to start, extend, flush, delay, or bypass a cluster based on logical and physical contiguity, end-of-file position, async mount state, memory pressure, and `seqcount`.
  - It may call `VOP_REALLOCBLKS()` to make pending sequential logical writes physically contiguous.
  - It falls back to `bdwrite()` or `bawrite()` when clustering is not useful or possible.
- Write cluster construction:
  - `cluster_wbuild()` scans delayed-write buffers in logical order, locks only immediately available buffers, requires matching VMIO/cluster/write-credential characteristics, aggregates pages into a synthetic cluster buffer, transfers barriers, marks children async clean, and submits the cluster with `bawrite()`.
  - Returns the total byte count submitted.
- Helpers:
  - `cluster_wbuild_wb()` applies the `write_behind` policy.
  - `cluster_collectbufs()` reads and collects existing buffers plus the current buffer for block reallocation.
  - `cluster_init_vn()` resets per-vnode cluster-write tracking fields.

## Dependencies And Integration
Integrates with vnode buffer objects, `getblk`/`bread_gb`/`bdwrite`/`bawrite`, `VOP_BMAP()`, `VOP_REALLOCBLKS()`, VM page busying and object pip accounting, pbuf allocation, mount `mnt_iosize_max`, resource accounting, and process I/O statistics. Filesystems use these routines to improve sequential I/O throughput without implementing clustering internally.

## Risk Notes
Cluster construction is sensitive to buffer flags, page validity, VMIO state, physical block mappings, mount I/O limits, and lock availability. The code intentionally abandons clustering on many edge cases to preserve correctness. Non-page-aligned buffers require careful `b_data` offset inheritance, and the callback must correctly propagate errors to all child buffers. Write clustering can change behavior depending on memory pressure and the `write_behind` sysctl.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_cluster.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_default.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_default.c

## Purpose
Provides FreeBSD's default vnode operation vector and standard VOP/VFS helper implementations. Filesystems inherit these functions when they do not provide specialized operations.

## Main Elements
- Default vnode operation vector:
  - `default_vnodeops` wires common defaults for access, locking, polling, buffer mapping, fsync, paging, stat, inotify, ioctl, file locking, writecount/text handling, copy-file-range, and unsupported operations.
  - Missing operations generally return `EOPNOTSUPP`, `EINVAL`, `ENOTDIR`, or panic where a missing implementation indicates a filesystem bug.
- Generic return/panic stubs:
  - `vop_eopnotsupp()`, `vop_ebadf()`, `vop_enotty()`, `vop_einval()`, `vop_enoent()`, `vop_eagain()`, `vop_null()`, and `vop_panic()`.
  - `vop_nolookup()` reports `ENOTDIR`; `vop_norename()` releases rename arguments and returns unsupported; `vop_nostrategy()` completes the buffer with `BIO_ERROR`.
- Access and locking:
  - `vop_stdaccess()` and `vop_stdaccessx()` convert between classic and extended access masks.
  - `vop_stdlock()`, `vop_stdunlock()`, and `vop_stdislocked()` honor `v_vnlock`.
  - `vop_lock()`, `vop_unlock()`, and `vop_islocked()` are optimized variants for vnodes using their embedded lock.
- Advisory locking:
  - `vop_stdadvlock()`, `vop_stdadvlockasync()`, and `vop_stdadvlockpurge()` delegate to lockf routines, with special handling for `SEEK_END` and local-filesystem exclusive-open atomicity.
- Filesystem and pathname defaults:
  - `vop_stdpathconf()` returns POSIX/default pathconf values.
  - `vop_stdbmap()` maps logical blocks as contiguous offsets in the vnode's own buffer object when no filesystem bmap exists.
  - `vop_stdvptocnp()` reconstructs a directory name by opening `".."`, reading parent directory entries, matching file IDs, and handling union mount coverage.
  - `dirent_exists()` scans a directory to check whether a named entry exists.
- Buffer, pager, and sync helpers:
  - `vop_stdfsync()` and `vop_stdfdatasync_buf()` flush dirty buffers.
  - `vop_stdgetpages()`, `vop_stdgetpages_async()`, and `vop_stdputpages()` delegate to generic vnode pager routines.
  - `vop_stdread_pgcache()` returns `EJUSTRETURN`.
  - `vfs_stdsync()` iterates mount vnodes and fsyncs dirty ones; `vfs_stdnosync()` is a no-op.
- Allocation/deallocation/advice:
  - `vop_stdallocate()` emulates allocation by reading existing data or zero-filling and writing through the requested range, with partial-progress reporting.
  - `vop_stddeallocate()` emulates deallocation by seeking data/hole ranges and writing zeroes through data ranges.
  - `vp_zerofill()` performs zero writes in bounded chunks.
  - `vop_stdadvise()` handles `POSIX_FADV_DONTNEED` by deactivating VM pages and marking clean/dirty buffers as no-reuse; `WILLNEED` is currently a no-op.
- Poll, kqueue, ioctl, and UNIX socket hooks:
  - `vop_nopoll()` and `vop_stdpoll()` provide simple poll behavior.
  - `vop_stdkqfilter()` delegates to `vfs_kqfilter()`.
  - `vop_stdioctl()` implements default `FIOSEEKDATA` / `FIOSEEKHOLE` behavior for regular files.
  - `vop_stdunp_bind()`, `vop_stdunp_connect()`, and `vop_stdunp_detach()` manage vnode-associated UNIX socket PCB pointers.
- Text and writecount handling:
  - `vop_stdset_text()`, `vop_stdunset_text()`, `vop_stdis_text()`, `vop_stdadd_writecount()`, and `vop_stdadd_writecount_nomsync()` manage `v_writecount`, text-busy protection, lazy msync behavior, and optional vnode references for text mappings.
- Inotify and utility defaults:
  - `vop_stdinotify()` and `vop_stdinotify_add_watch()` delegate to vnode inotify helpers.
  - `vop_stdstat()` builds `struct stat` from `VOP_GETATTR()` and helper pre/post hooks.
  - `vop_stdgetwritemount()`, `vop_stdgetlowvnode()`, and `vop_stdvput_pair()` provide common vnode reference/release behavior.
  - `vop_stdcopy_file_range()` delegates to generic copy-file-range.
- VFS-level defaults:
  - `vfs_stdroot()`, `vfs_stdstatfs()`, `vfs_stdquotactl()`, `vfs_stdvget()`, `vfs_stdfhtovp()`, `vfs_stdextattrctl()`, and `vfs_stdsysctl()` return unsupported defaults.
  - `vfs_stdinit()` and `vfs_stduninit()` are no-ops.
  - `vop_sigdefer()` invokes a vector operation with stop signals deferred.

## Dependencies And Integration
This file is central to vnode/VFS dispatch. It depends on VOP descriptors, vnode locks and reference APIs, buffer cache, generic vnode pager, VM page/object helpers, directory iteration, namei/open helpers, lockf, kqueue, inotify, MAC/audit includes, mount iteration, and generic syscall helpers. Filesystems compose these defaults through their VOP vectors instead of reimplementing common behavior.

## Risk Notes
Defaults are intentionally conservative, but some are only approximations. `vop_stdallocate()` and `vop_stddeallocate()` emulate space operations with reads/writes and may be slower or semantically weaker than filesystem-native implementations. `vop_stdvptocnp()` depends on parent directory scanning and can be expensive or race-prone. Writecount/text transitions rely on atomic state discipline. Filesystems must implement either `vop_access` or `vop_accessx`; otherwise the default access pair can recurse indefinitely as noted in the file.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_default.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_export.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_export.c

## Purpose
Implements generic VFS export management for NFS/WebNFS-style filesystem exports. It stores per-mount export policies, address-based export credentials, public filesystem metadata, jail-scoped export ownership, and export access checks.

## Main Elements
- Export data structures:
  - `struct netcred` stores radix nodes, export flags, anonymous credential, and accepted security flavors.
  - `struct netexport` stores a default export plus IPv4 and IPv6 radix trees.
  - Static `nfs_pub` stores the single public WebNFS export.
- Address-list construction:
  - `vfs_hang_addrlist()` installs default or address-specific export entries from `struct export_args`.
  - Default exports populate `ne_defexported` and set `MNT_DEFEXPORTED`.
  - Address exports copy in user-supplied sockaddr and optional mask, create AF_INET/AF_INET6 radix heads as needed, add the entry, and build an anonymous credential rooted in `prison0`.
  - If `ex_numsecflavors` is zero in `vfs_export()`, AUTH_SYS is installed as the default flavor.
- Address-list cleanup:
  - `vfs_free_netcred()` deletes radix entries and frees anonymous credentials.
  - `vfs_free_addrlist_af()` walks and destroys one address-family radix tree.
  - `vfs_free_addrlist()` frees IPv4/IPv6 lists and the default anonymous credential.
- Export update/delete:
  - `vfs_export()` validates add/delete flags, serializes on `mnt_explock`, creates or resets `mnt_export`, manages `MNT_EXPORTED`, `MNT_DEFEXPORTED`, and `MNT_EXPUBLIC`, and records the jail credential owning the export when applicable.
  - Delete paths remove public export state, free address lists, clear mount flags, drop jail credentials, and decrement the prison export count.
  - It removes the transient `"export"` mount option from current and new mount option lists after processing.
- Jail cleanup:
  - `vfs_exjail_delete()` is called during prison cleanup to find mounts exported by the prison, invalidate or delete those exports, drop credential references, and clear export flags so the prison can be released.
- Public filesystem:
  - `vfs_setpublicfs()` installs or clears the single public filesystem.
  - On install it gets the mount root vnode, obtains a file handle, records the mount fsid, and optionally copies and validates an index filename.
- Export lookup and access checks:
  - `vfs_export_lookup()` matches a client sockaddr against the mount's AF-specific radix tree and falls back to the default export.
  - `vfs_stdcheckexp()` is the generic export verifier used after filesystem file-handle validation. It returns export flags, holds the anonymous credential, and copies security flavors for the caller.

## Dependencies And Integration
Uses mount export locks and flags, radix trees, socket address families, credentials and prison references, NFS public-export structures, `VFS_ROOT()`, `VOP_VPTOFH()`, copyin/copyinstr from user export arguments, and mount option helpers. Filesystems use `vfs_stdcheckexp()` as the generic authorization half of file-handle-to-vnode export checks after validating filesystem-specific file handles.

## Risk Notes
Export state is security-sensitive because it determines remote filesystem access. Correctness depends on `mnt_explock` serialization, jail ownership checks, proper credential reference management, radix tree cleanup, and careful distinction between host-root and jailed export deletion. Address and mask lengths are constrained but copied from userspace, and only one public filesystem can be active. A notable implementation quirk is that anonymous export credentials are synthesized manually from uid/groups and then attached to `prison0`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_export.c -->