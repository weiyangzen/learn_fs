# subset-b-007752 grouped research

This grouped report covers the OpenAFS Linux and NetBSD OS-interface files assigned to `subset-b-007752`. Each source file section is wrapped with the required reconciliation markers and preserves the source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_syscall.c -->
## sources/distributed-fs/openafs/src/afs/LINUX/osi_syscall.c

Purpose: Linux kernel-module syscall-hook support for OpenAFS PAG and `afs_syscall` entry points when `LINUX_KEYRING_SUPPORT` is not used. With keyring support enabled, `osi_syscall_init` and `osi_syscall_clean` are no-op stubs because PAG state is tracked through keyrings instead of group IDs.

Important APIs and state: exports `osi_syscall_init(void)` and `osi_syscall_clean(void)`, and maintains static syscall-table pointers and saved entries such as `afs_sys_call_table`, `afs_ni_syscall`, architecture-specific 32-bit tables, `sys_setgroupsp`, and `sys_setgroups32p`. It references AFS handlers `afs_syscall`, `afs_xsetgroups`, `afs_xsetgroups32`, and 32-bit compatibility variants. It uses `SYSCALLTYPE`, `POINTER2SYSCALL`, and `SYSCALL2POINTER` to normalize table entry width for SPARC64/S390X, IA64, PPC64, AMD64 compat, and common Linux builds.

Control flow: initialization locates the native syscall table with `osi_find_syscall_table(0)`, detects an already-installed AFS syscall, saves the existing `__NR_afs_syscall` and `setgroups` handlers, and replaces them with OpenAFS dispatchers. AMD64 and SPARC64 also probe a 32-bit syscall table with `osi_find_syscall_table(1)` and patch IA32/SPARC compat `afs_syscall` and `setgroups` slots. IA64 uses hand-written function-descriptor stubs, PPC64 creates TOC-aware jump stubs, and S390X can allocate low-memory jump pages if module code is too high for syscall-table entries. Cleanup reverses all table patches and frees S390X jump pages.

Dependencies and integration: this file depends on Linux syscall numbers, OpenAFS PAG group hooks, architecture compile-time probes, and `osi_find_syscall_table`. It integrates with the global module lifecycle; a bad restore can leave kernel syscall slots pointing at unloaded module text.

State and persistence: the only persistent state is in live kernel memory: saved syscall-table entries, allocated trampoline pages, and patched syscall table slots. No on-disk state is created.

Risks: direct syscall-table patching is high risk and kernel-version/architecture fragile. Failures include incomplete cleanup, double installation, pointer-width mistakes, W^X/protection conflicts, stale trampoline pages, and races with concurrent syscalls. The keyring no-op path is lower risk but must match the rest of the build configuration.

Test signals: boot/load/unload module tests, `setpag`/PAG retention across `setgroups`, `fs sysname`/PIOCTL exercises through `afs_syscall`, 32-bit compatibility syscall tests on AMD64/SPARC64/PPC64, repeated load/unload cycles, and negative tests for already-occupied syscall slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_sysctl.c -->
## sources/distributed-fs/openafs/src/afs/LINUX/osi_sysctl.c

Purpose: exposes selected OpenAFS runtime tuning and statistics variables through Linux `sysctl` when `CONFIG_SYSCTL` is enabled.

Important APIs and state: defines `osi_sysctl_init(void)` and `osi_sysctl_clean(void)`. The central table `afs_sysctl_table[]` maps integer variables such as `hm_retry_RO`, `hm_retry_RW`, `hm_retry_int`, `afs_gcpags`, `afs_rx_deadtime`, `afs_bkvolpref`, cache block counters, cache percentage watermarks, `afs_cacheBlocks`, `afs_md5inum`, and `afs_usednlc`. The macros `AFS_SYSCTL_INT`, `AFS_SYSCTL_INT2`, `AFS_SYSCTL_NAME`, and `AFS_SYSCTL_SENTINEL` hide kernel API differences, including numbered vs unnumbered ctl tables and the Linux 6.8 no-sentinel convention.

Control flow: initialization registers either an `"afs"` subtree with `register_sysctl("afs", ...)` or a legacy `fs/afs` table with `register_sysctl_table`. On failure it returns `-1`; on success it stores the `ctl_table_header` in `afs_sysctl`. Cleanup unregisters that header once and clears the pointer.

Dependencies and integration: depends on Linux `<linux/sysctl.h>`, OpenAFS global cache/stat variables, and compile-time kernel feature probes. It integrates with administrator observability and runtime tuning via `/proc/sys`/sysctl.

State and persistence: sysctl entries directly expose live kernel variables; writes mutate in-memory OpenAFS behavior and do not persist across module unload or reboot unless userspace reapplies them.

Risks: permissions matter because many entries are `0644`; writable sysctl values can change cache behavior and retry policy. Kernel API drift is also a risk, handled here with feature macros and the Linux 6.8 sentinel branch. Missing cleanup would leave stale sysctl entries.

Test signals: verify table registration on supported kernels, read-only vs writable permissions, successful updates of writable knobs, cleanup after module unload, and builds across `HAVE_LINUX_REGISTER_SYSCTL`, `REGISTER_SYSCTL_TABLE_NOFLAG`, and Linux 6.8+ configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vcache.c -->
## sources/distributed-fs/openafs/src/afs/LINUX/osi_vcache.c

Purpose: Linux-specific vcache/vnode lifecycle helpers that bridge OpenAFS `struct vcache` objects to Linux `struct inode` and dentry-cache behavior.

Important APIs and state: exports `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, `osi_ResetRootVCache`, `osi_vnhold`, `osi_ShouldDeferRemunlink`, and `osi_ResetVCache`. Important internal state includes Linux inode aliases, dentry `d_time`, `afs_globalVp`, `afs_globalVFS`, per-vcache pagewriter lists, `target_link`, unlink state, and vcache reference/open counts.

Control flow: `osi_TryEvictVCache` first tries to prune dcache aliases, dropping AFS and vcache locks around Linux dcache operations, then calls `afs_FlushVCache` if reference/open counts allow. Directory alias eviction uses `shrink_dcache_parent` and `__d_drop` carefully under dentry locks. `osi_NewVnode` allocates a new inode with `new_inode(afs_globalVFS)` and either gets the embedded vcache from inode allocation hooks or allocates one manually. `osi_ResetRootVCache` rebuilds the root fid for a new root volume, obtains the new vcache, fills its inode, moves the root dentry alias from the old root inode to the new inode, releases the old root, and updates `afs_globalVp`.

Dependencies and integration: depends on Linux inode/dentry APIs, OpenAFS vcache locks, global GLOCK discipline, and `osi_compat.h` wrappers for dentry alias iteration. It integrates with Linux VFS root handling, cache invalidation, and silly-unlink cleanup.

State and persistence: all state is in kernel memory. `osi_ResetVCache` marks cached dentries and direct children stale by zeroing `d_time`; later dentry revalidation performs the actual refresh.

Risks: dentry alias manipulation is race-prone. The code deliberately drops locks around dcache pruning, restarts alias iteration after drops, and avoids `d_invalidate` in places to prevent CWD `ENOENT` and submount loss. `osi_ShouldDeferRemunlink` avoids known panics when `current->fs == NULL` with UFS disk cache and security modules.

Test signals: vcache recycle under open/closed reference patterns, root volume change, directory dentry invalidation, mountpoint/submount retention, unlink during process exit with UFS cache, and stress tests involving concurrent lookup, rename, and cache flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vfs.h -->
## sources/distributed-fs/openafs/src/afs/LINUX/osi_vfs.h

Purpose: Linux vnode/VFS compatibility header that maps portable OpenAFS vnode and vattr concepts onto Linux inode and superblock types.

Important APIs and types: defines `vnode_t` as `struct inode`, aliases `vnode` to `inode`, maps vnode-style fields such as `v_op`, `v_fop`, `v_type`, `v_vfsp`, and `v_data` to inode fields, and maps vnode type constants (`VREG`, `VDIR`, `VLNK`, etc.) to Linux mode bits. It defines `enum vcexcl { EXCL, NONEXCL }`, file flag aliases (`FWRITE`, `FTRUNC`, `IO_APPEND`, `FSYNC`), permission aliases (`VREAD`, `VWRITE`, `VEXEC`, `VSUID`, `VSGID`), `vfs` as `super_block`, and `struct vattr`.

Control flow: no runtime control flow. This is compile-time glue consumed by Linux OSI and common AFS vnode code.

Dependencies and integration: depends on Linux inode, mode, time, uid/gid, and OpenAFS `afs_size_t` definitions included by callers. The `vattr_t` structure is central to `afs_getattr`, `afs_setattr`, `afs_fill_inode`, and Linux inode operation wrappers in `osi_vnodeops.c`.

State and persistence: no storage. Its macro mappings determine how other files read and write Linux inode state.

Risks: macro field aliases are sensitive to kernel structure evolution. The `v_data` alias to `u.generic_ip` is only valid on older kernels and must be guarded by surrounding compatibility macros elsewhere. `i_size_read`/`i_size_write` fallback macros are non-locking fallbacks for kernels lacking helpers.

Test signals: compile coverage across supported Linux kernel versions, attribute round-trips through `vattr2inode`/`iattr2vattr`, and vnode operation builds that exercise all mapped constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vfsops.c -->
## sources/distributed-fs/openafs/src/afs/LINUX/osi_vfsops.c

Purpose: Linux filesystem-type and superblock operations for mounting, rooting, statfs, inode allocation, and unmounting the OpenAFS filesystem.

Important APIs and state: defines `afs_fs_type`, `afs_sops`, global `afs_globalVp`, `afs_globalVFS`, `afs_cacheMnt`, `afs_was_mounted`, and `afs_backing_dev_info`. Main functions include `afs_fill_super`, `afs_root`, mount/get-tree wrappers, `afs_alloc_inode`, `afs_destroy_inode`, `afs_evict_inode`/`afs_clear_inode`, `afs_put_super`, `afs_statfs`, `afs_init_inodecache`, and `afs_destroy_inodecache`.

Control flow: mount enters through modern `fs_context` `get_tree_nodev`, `mount_nodev`, or older `get_sb_nodev` depending on kernel features. `afs_fill_super` takes the AFS global lock, rejects remount after prior mount via `afs_was_mounted`, pins the module, populates superblock flags and operations, configures dentry operations, initializes backing-device info/read-ahead settings, optional export ops, max file size, and calls `afs_root`. `afs_root` creates a request, checks initialization, fetches `afs_rootFid`, fills the root inode, and creates `s_root`. On failure, setup is unwound and vcaches are flushed. Unmount uses `afs_put_super` to clear globals, call `afs_shutdown(AFS_WARM)`, release the cache mount, verify allocations, destroy backing-device info, clear `s_dev`, and release the module.

Dependencies and integration: depends on Linux superblock, mount, BDI, slab/inode-cache, and dentry APIs. It integrates with `osi_vnodeops.c` through `afs_dentry_operations` and `afs_fill_inode`, and with NFS export support via `afs_export_ops` when enabled.

State and persistence: mount state is global and intentionally single-instance. The filesystem fakes statfs capacity with `AFS_VFS_FAKEFREE`; actual cache/server state lives elsewhere.

Risks: single-remount prevention requires module reload after mount/unmount. Failure cleanup must match partially initialized BDI and module refs. Inode eviction panics if a vcache is still on VLRU/hash queues, which is correct as an invariant check but can crash if lifecycle accounting is wrong.

Test signals: mount/unmount, failed root acquisition, repeated mount without reload, backing-device setup on old/new kernels, inode cache create/destroy, statfs values, NFS export builds, and leak checks after unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vm.c -->
## sources/distributed-fs/openafs/src/afs/LINUX/osi_vm.c

Purpose: Linux VM/pagecache invalidation and writeback helpers used by common OpenAFS cache-management paths.

Important APIs: `osi_VM_FlushVCache`, `osi_VM_TryToSmush`, `osi_VM_FSyncInval`, `osi_VM_StoreAllSegments`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: `osi_VM_FlushVCache` checks vcache reference count and open count, then truncates inode pages via `afs_truncate(ip, 0)` to recycle a vcache. `osi_VM_TryToSmush` invalidates remote inode pages through `invalidate_remote_inode`. `osi_VM_StoreAllSegments` avoids duplicate work if the per-vcache `pagewriters` list is non-empty, drops the vcache lock and GLOCK, calls `filemap_fdatawrite` and `filemap_fdatawait`, then reacquires locks. `osi_VM_FlushPages` locks the inode, calls `truncate_inode_pages`, and unlocks. `osi_VM_Truncate` delegates to `afs_truncate`.

Dependencies and integration: depends on Linux pagecache/writeback helpers and `osi_compat.h` inode locking wrappers. It is invoked by callback breaks, `fs flush`, truncation, writeback/store-all-segments paths, and vcache recycling. Comments note Linux treats VM as a cache updated by AFS writes and reads through the cache, so normal VM flushing is not required the way it is on some other platforms.

State and persistence: mutates Linux pagecache state for AFS inodes. No durable metadata is written here; server/cache persistence is handled by higher AFS writeback and dcache layers.

Risks: concurrency is the main risk. Several functions intentionally drop and reacquire locks, so pages can be recreated by concurrent activity before return. `osi_VM_StoreAllSegments` skips if another pagewriter is active; caller behavior must tolerate that. `osi_VM_FSyncInval` is intentionally empty on Linux.

Test signals: callback revocation invalidates stale mapped/read pages, truncation removes pages beyond EOF, `fs flush`/`fs flushv`, writeback waits for dirty pages, concurrent read/write during flush, and vcache recycle refuses busy objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vnodeops.c -->
## sources/distributed-fs/openafs/src/afs/LINUX/osi_vnodeops.c

Purpose: the main Linux vnode/inode/file/dentry/address-space operation bridge for OpenAFS. It translates Linux VFS calls into common AFS vnode operations and manages Linux pagecache, dcache, locks, mmap, readdir, symlinks, and writeback.

Important APIs and tables: exports file operation tables `afs_dir_fops` and `afs_file_fops`, dentry operations `afs_dentry_operations`, inode operation tables for file/dir/symlink, address-space operations `afs_file_aops` and symlink aops, and `afs_fill_inode`. Key wrappers include read/write iter/aio/sync handlers, `afs_linux_readdir`, `afs_linux_open`, `afs_linux_release`, `afs_linux_fsync`, byte-range/flock locking, `afs_linux_flush`, dentry revalidation, create/lookup/link/unlink/symlink/mkdir/rmdir/rename, readlink/follow-link, readpage/readahead, bypass-cache reads, writepage/writepages/write_begin/write_end, permission, getattr, and setattr.

Control flow: read and mmap verify vcaches, flush stale pages, drop GLOCK, and call generic Linux file operations. Writes fake-open/fake-close around Linux generic writes so AFS write accounting and core dumps work. Readdir fetches the directory dcache, waits for fetch completion, verifies freshness, marks `CReadDir`, scans directory blobs, emits Linux dirents, and handles corruption. Lookup uses optional `@sys` VFS expansion, calls `afs_lookup`, fills/inserts inodes, manages directory aliases with `d_splice_alias`, and guards old d_splice races. Dentry revalidation compares parent DataVersion (`d_time`) and CStatd state, re-lookups names when needed, updates inode attributes, handles mountpoint fakestat, negative dentries, submounts, and ENOENT filtering during task death. Page reads try a UFS-cache fast path, otherwise call `afs_rdwr`; bypass-cache mode schedules no-cache reads. Readahead batches dcache/cache-file use and can use asynchronous page-copy tasks. Writeback tracks per-vcache pagewriter PIDs to avoid recursion, writes dirty pages through `afs_write`, then calls partial writeback to server/cache. Directory mutations call common AFS ops and maintain Linux dcache state.

Dependencies and integration: depends on Linux VFS, dentry, pagecache, folio/pagevec, locking, writeback, and many compatibility macros. It integrates deeply with OpenAFS `afs_lookup`, `afs_rdwr`, `afs_write`, `afs_lockctl`, `afs_getattr`, `afs_setattr`, dcache, fakestat, disconnected mode, cache-bypass policy, and NFS export behavior.

State and persistence: Linux inode attributes, `d_time`, pagecache dirty/writeback state, vcache flags (`CStatd`, `CReadDir`, `CMAPPED`, `CUnlinked`, `CCorrupt`), dcache hints, silly-rename names/credentials, and bypass-cache state are live kernel state. Durable data reaches cache files or AFS servers through common AFS store/write paths.

Risks: this is the highest-risk Linux OSI surface. Notable risks include stale dentry validity, mountpoint/fakestat alias confusion, writeback recursion/deadlocks, folio API drift, incorrect positive-vs-negative errno conversion, lock ordering between GLOCK, inode locks, dcache locks, and Linux VFS callbacks, bypass-cache page lifetime, and rename/unlink dcache coherency. The code has explicit workarounds for RCU pathwalk, d_splice_alias races, submount invalidation, NFS readdirplus deadlocks, and killed-process ENOENT pollution.

Test signals: comprehensive Linux VFS tests: lookup/revalidate under rename, mountpoints and `@sys`, readdir on corrupt and changing directories, read/write/mmap/fsync/flush, pagecache invalidation after callback breaks, large-file bypass-cache, readpage/readahead/writepages on folio and non-folio kernels, byte-range and flock locks, sillyrename/unlink of open files, symlink read/follow, permissions/getattr/setattr, NFS export/readdirplus, disconnected-mode dirty handling, and kernel-version build matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/Makefile.in -->
## sources/distributed-fs/openafs/src/afs/Makefile.in

Purpose: automake-style makefile fragment for generating and installing common AFS client headers, trace catalogs, and unified error/message sources.

Important targets and outputs: `all` delegates to `depinstall`. `generated` builds `afs_trace.h`, `afs_trace.msf`, `unified_afs.c`, and `unified_afs.h`. The `afs_trace.*` and `unified_afs.*` targets run `COMPILE_ET_H`/`COMPILE_ET_C` against `.et` inputs. `afszcm.cat` invokes `GENCAT` with OS-specific flags. `depinstall`, `install`, and `dest` install headers such as `afs.h`, `afs_consts.h`, `afs_stats.h`, `exporter.h`, `nfsclient.h`, `sysctl.h`, generated headers, and the platform-specific `${MKAFS_OSTYPE}/osi_inode.h`. Linux installs also copy `${MKAFS_OSTYPE}/osi_vfs.h`. `clean` removes generated and object artifacts.

Control flow: make dependencies ensure generated trace/error artifacts exist before install. The `case ${SYS_NAME}` blocks handle catalog generation syntax differences for SGI, Linux/umlinux, Darwin, and other systems, and selectively install VFS headers only on Linux.

Dependencies and integration: depends on `Makefile.config`, `Makefile.lwp`, configured variables (`TOP_OBJDIR`, `TOP_INCDIR`, `DESTDIR`, `includedir`, `afsdatadir`, `DEST`, `SYS_NAME`, `MKAFS_OSTYPE`), install tools, error-table compilers, `GENCAT`, and `Makefile.version`. It integrates the `src/afs` headers into both build-tree dependency includes and staged installation trees.

State and persistence: writes generated C/header/message catalog files and installed header/catalog copies. No runtime state.

Risks: OS-specific `gencat` flags and install paths can diverge. The `install` and `dest` targets have parallel but not identical destination roots, so changes must be mirrored. Platform header selection via `${MKAFS_OSTYPE}` is sensitive to configure output. Linux-only `osi_vfs.h` installation is guarded with `|| true`, which can hide missing-file issues.

Test signals: `make depinstall`, `make generated`, staged `make install DESTDIR=...`, `make dest`, catalog generation on Linux/Darwin/other targets, clean regeneration, and include-tree checks for `afs/osi_inode.h`, `afs/osi_vfs.h` on Linux, and generated `unified_afs.h`/`afs_trace.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_crypto.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_crypto.c

Purpose: NetBSD kernel random-byte provider for OpenAFS.

Important API: `osi_readRandom(void *data, afs_size_t len)`.

Control flow: for NetBSD 7.0 and newer (`AFS_NBSD70_ENV`), asserts the requested length is within `CPRNG_MAX_LEN` and calls `cprng_strong(kern_cprng, data, len, 0)`. Older NetBSD builds include random-device private headers and call `rnd_extract_data(data, len, RND_EXTRACT_ANY)`. The function returns 0 unconditionally after filling the buffer.

Dependencies and integration: depends on NetBSD kernel CPRNG or rnd APIs. It integrates with OpenAFS code paths needing random material, such as identifiers, crypto-adjacent tokens, or cache/protocol randomness supplied through OSI.

State and persistence: no OpenAFS-owned state. Entropy and generator state are owned by the NetBSD kernel.

Risks: the newer path asserts instead of gracefully splitting requests larger than `CPRNG_MAX_LEN`; callers must respect the maximum. The older `rnd_extract_data` path uses `RND_EXTRACT_ANY`, so randomness quality follows old NetBSD random semantics. Errors are not propagated because neither branch returns failure here.

Test signals: compile on pre-7 and 7+ NetBSD, request boundary tests around `CPRNG_MAX_LEN`, nonzero/random-looking output, and consumers that expect a zero return code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_file.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_file.c

Purpose: NetBSD UFS cache-file I/O helpers used by OpenAFS disk-cache code.

Important APIs and state: defines `osi_UFSOpen`, `afs_osi_Stat`, `osi_UFSClose`, `osi_UFSTruncate`, `osi_DisableAtimes`, `afs_osi_Read`, `afs_osi_Write`, `afs_osi_MapStrategy`, and `shutdown_osifile`. Global `afs_osicred_initialized` is reset during cold shutdown. `osi_file` instances hold a vnode, cached size, offset, optional completion callback, and proc pointer.

Control flow: `osi_UFSOpen` verifies UFS cache mode, allocates an `osi_file`, drops GLOCK, uses `VFS_VGET` on `cacheDev.mp` and the supplied inode, rejects `VNON`, unlocks the vnode, and initializes offset/size. Stat/getattr, truncate/setattr, read, and write all drop GLOCK around NetBSD vnode operations. Reads and writes use `vn_rdwr` with `AFS_UIOSYS`, `IO_UNIT`, `afs_osi_credp`, and `osi_curproc`; successful calls advance `afile->offset`, and writes update cached size. Truncate first stats and only shrinks if needed. Close releases the vnode and frees the small-space allocation.

Dependencies and integration: depends on NetBSD vnode/VFS operations, FFS inode size (`VTOI(vp)->i_ffs1_size`), OpenAFS cache device state, credentials, stats counters, tracing, and GLOCK discipline. It is the platform backend for the OpenAFS UFS disk cache.

State and persistence: reads/writes/truncates actual cache files on the local filesystem. `afile->offset` and `afile->size` mirror current per-open state. `shutdown_osifile` clears credential initialization on cold shutdown.

Risks: `osi_UFSOpen` panics on failed inode lookup, which is severe if cache metadata is corrupt. GLOCK must not be held across blocking vnode I/O. `osi_DisableAtimes` is a no-op, so cache reads may still affect atime depending on NetBSD behavior. Positive vnode errors are converted to negative return values in read/write paths.

Test signals: UFS cache open/stat/read/write/truncate/close, corrupt or missing cache inode behavior, shutdown cold vs warm, short read/write residual accounting, callback invocation after write, and cache consistency after vnode I/O errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_gcpags.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_gcpags.c

Purpose: this source file is empty in the inspected tree. It is likely a platform placeholder for PAG garbage-collection support where other OS ports provide code.

Important APIs/types/functions: none are defined.

Control flow: none.

Dependencies and integration: integration is only through the build system if it includes the file to satisfy a uniform platform source list. No symbols are exported from this file.

State and persistence: none.

Risks: if higher-level NetBSD code expects active PAG GC from this translation unit, it will not get it. The practical risk is silent absence of platform-specific cleanup rather than a code bug inside the file.

Test signals: build/link tests proving no required symbols are missing, PAG lifetime tests on NetBSD, and audits comparing NetBSD PAG cleanup behavior to platforms with non-empty `osi_gcpags.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_groups.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_groups.c

Purpose: NetBSD PAG group manipulation and `setgroups` syscall interception support.

Important APIs and state: defines `Afs_xsetgroups`, `setpag`, and static helpers `osi_getgroups` and `osi_setgroups`. It uses NetBSD `kauth_cred` group APIs and constants `NOUID`, `NOGID`, and `NGROUPS`. PAG values are encoded into group slots through `afs_get_groups_from_pag` and decoded with `afs_get_pag_from_groups`.

Control flow: `Afs_xsetgroups` initializes an AFS request from the process credentials, calls the real `sys_setgroups`, and if the resulting credentials no longer contain a PAG but the original request UID was a PAG id, it calls `AddPag` to restore it. `setpag` generates a PAG if requested, reads current groups, makes room for two PAG groups at positions 1 and 2 if none are present, encodes the new PAG, and calls `osi_setgroups`. `osi_setgroups` enters NetBSD credential modification, optionally duplicates credentials when not changing the parent, calls `kauth_cred_setgroups`, and leaves credential modification.

Dependencies and integration: depends on NetBSD syscall args, kauth credentials, OpenAFS PAG helpers, and the syscall hook installed by `osi_kmod.c` or legacy LKM code in `osi_vfsops.c`. It integrates process authentication state with OpenAFS PAG semantics.

State and persistence: modifies process credential group lists in memory. PAGs persist with credentials across process lifetime/fork semantics, not on disk.

Risks: group-list manipulation is sensitive to `NGROUPS` limits and exact PAG group slot placement. Incorrect `change_parent` semantics can modify the wrong credential object. `Afs_xsetgroups` must preserve PAGs without overwriting explicit PAGs supplied by the caller.

Test signals: `setpag` with and without existing PAG, near-`NGROUPS` group lists returning `E2BIG`, ordinary `setgroups` preserving PAG, child/parent credential behavior, and kauth group visibility through NetBSD APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_inode.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_inode.c

Purpose: this inspected file contains only the standard OpenAFS license/comment block and no executable code.

Important APIs/types/functions: none are defined in this file.

Control flow: none.

Dependencies and integration: likely retained for source-list symmetry with platforms that implement inode-level cache helpers. NetBSD inode definitions are not provided here; platform header installation uses `osi_inode.h`, which is also effectively a placeholder in this subset.

State and persistence: none.

Risks: no direct runtime risk. The risk is build-system or common-code drift assuming NetBSD has inode helper symbols here when it does not.

Test signals: NetBSD build/link coverage, cache backends that might include `osi_inode.c`, and comparison against other OS ports to confirm missing inode helpers are intentional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_inode.h -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_inode.h

Purpose: placeholder NetBSD inode header. The file contains only an identifying comment in the inspected tree.

Important APIs/types/functions: no macros, types, or prototypes are defined.

Control flow: none.

Dependencies and integration: installed by `src/afs/Makefile.in` as `${MKAFS_OSTYPE}/osi_inode.h` for the selected platform. It satisfies include/install expectations for OpenAFS code that has a platform `osi_inode.h` contract.

State and persistence: none.

Risks: because it is empty, any future common code that expects NetBSD-specific inode definitions must add them here or guard its usage. Empty installed headers can hide missing implementation until a consumer uses a symbol.

Test signals: include-tree install checks, NetBSD client build, and downstream code that includes `<afs/osi_inode.h>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_kmod.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_kmod.c

Purpose: modern NetBSD kernel module entry point for OpenAFS. It attaches the AFS VFS and installs syscall hooks for `afs3_syscall`, `setgroups`, and `ioctl`.

Important APIs and state: defines `MODULE(MODULE_CLASS_VFS, openafs, NULL)` and static `openafs_modcmd`. It declares `openafs_sysent` for `AFS_SYSCALL`, saves `old_sysent`, `old_setgroups`, and `old_ioctl`, and references `afs_vfsops`, `afs3_syscall`, `Afs_xsetgroups`, and `afs_xioctl`. `SYS_NOSYSCALL` maps to the right no-module/no-syscall function for NetBSD 7, 6, or older LKM environments.

Control flow: on `MODULE_CMD_INIT`, it selects the syscall table (`sysent` or `emul_netbsd.e_sysent` for RUMP), attaches `afs_vfsops`, saves old syscall handlers, and if the AFS syscall slot is unused (or always in RUMP) patches AFS syscall, `SYS_setgroups`, and `SYS_ioctl`. NetBSD 6+ wraps table mutation in `kernconfig_lock`. If the slot is busy it returns `EBUSY`. On `MODULE_CMD_FINI`, it restores all saved syscall handlers, detaches VFS ops, and returns detach errors. NetBSD 7 autounload returns `EBUSY`.

Dependencies and integration: depends on NetBSD module, syscall, VFS, and optional RUMP APIs. It integrates the NetBSD files in this subset: `osi_groups.c` provides `Afs_xsetgroups`, `osi_vfsops.c` provides `afs_vfsops`, and common AFS code provides syscall/ioctl handlers.

State and persistence: mutates live kernel syscall table and VFS registry only during module lifetime. No disk persistence.

Risks: partial initialization failure after `vfs_attach` but before syscall patching may need careful unwind; the inspected code breaks with error but does not visibly detach in the busy-slot branch. Syscall table patching must be restored exactly on fini. Autounload refusal prevents unsafe unload while mounted or hooked.

Test signals: module load/unload, busy `AFS_SYSCALL` slot, RUMP module load, NetBSD 6+ kernconfig locking builds, VFS attach/detach, syscall/ioctl routing, and failed-init cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_kmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_machdep.h -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_machdep.h

Purpose: central NetBSD OSI compatibility header mapping OpenAFS portable kernel abstractions to NetBSD kernel types, functions, locks, credentials, syscall args, vnode/VFS fields, and time/string helpers.

Important APIs/types/macros: defines `RXK_LISTENER_ENV`, `AFS_DIRENT`, `osi_vfs`/mount field aliases, `VN_HOLD`, `VN_RELE`, `struct afs_sysargs`, uio field aliases and `AFS_UIOSYS`/`AFS_UIOUSER`, `afs_proc_t`, `osi_curproc`, `getpid`, `afs_ucred_t`, credential accessors and ref/free macros, `afs_hz`, `osi_Time`, string helpers, `printk`, `setgroups`, `UVM`, lookup wrappers, GLOCK macros, `SPLVAR`/`NETPRI`/`USERPRI`, `enum vcexcl`, vnode type setters, `IsAfsVnode`, `SetAfsVnode`, `AFS_USE_NBSD_NAMECACHE`, and inline `osi_GetTime`.

Control flow: no standalone runtime flow, but macros expand into real lock/credential/time behavior throughout the NetBSD port. GLOCK implementation differs by `AFS_GLOBAL_SUNLOCK` and NetBSD version: NetBSD 5+ uses `kmutex_t`, older code uses `struct lock`, and a fallback branch asserts GLOCK as always true.

Dependencies and integration: included indirectly by `afs_osi.h`. It depends on NetBSD kernel headers for locks, mutexes, rwlocks, syscall args, kauth, vnode/mount structures, and time. It declares `afs_nbsd_lookupname` and `afs_nbsd_getnewvnode`, tying into `osi_vfsops.c` and `osi_vcache.c`.

State and persistence: no storage itself, but determines how global locking, credentials, process identity, vnode fields, and time are accessed.

Risks: macro-heavy OS ports are fragile under kernel API changes. Duplicate `ISAFS_GLOCK` definitions in conditional branches, older lock APIs, and field aliases can break silently at compile time or create lock assertion gaps. Credential macros map directly to kauth APIs and must match NetBSD lifecycle rules.

Test signals: full NetBSD build matrix, lock-debug kernels, credential/PAG tests, vnode creation/access, lookupname calls, uio read/write paths, and time-dependent callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_misc.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_misc.c

Purpose: miscellaneous NetBSD OSI routines for superuser checks and unsupported inode syscalls.

Important APIs: `afs_osi_suser`, `afs_syscall_icreate`, `afs_syscall_iopen`, and `afs_syscall_iincdec`.

Control flow: `afs_osi_suser` calls NetBSD `kauth_authorize_generic` with `KAUTH_GENERIC_ISSUSER`, passing either `curlwp->l_ru` on NetBSD 5+ or `curlwp->l_acflag` on older builds, and returns boolean success without setting errno. The inode syscall helpers all return `EINVAL`, indicating unsupported functionality on NetBSD.

Dependencies and integration: depends on NetBSD kauth and current LWP fields. `afs_osi_suser` is used by common AFS authorization checks through the `afs_suser` macro in `osi_machdep.h`. The unsupported inode syscalls satisfy common syscall dispatch symbols while refusing operations.

State and persistence: no OpenAFS-owned state; authorization consults live credential/kernel state.

Risks: NetBSD accounting-field differences are handled by preprocessor branches, but future kauth API changes could break superuser checks. Returning `EINVAL` for inode operations must match userspace expectations; callers must not assume those legacy operations work on NetBSD.

Test signals: root vs non-root authorization, NetBSD 5+ and older compile paths, syscall dispatch for unsupported inode operations, and callers handling `EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_prototypes.h -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_prototypes.h

Purpose: NetBSD OSI prototypes header placeholder.

Important APIs/types/functions: the file only defines include guards (`_OSI_PROTO_H_`) and contains no prototypes. Its comment says "Exported macos support routines", which appears stale or copied and does not match the NetBSD path.

Control flow: none.

Dependencies and integration: may be included by common/platform code expecting an OSI prototypes header. In this tree it does not expose any NetBSD declarations; declarations instead appear in other headers such as `osi_machdep.h` or source-local prototypes.

State and persistence: none.

Risks: stale comments and empty headers can mislead maintainers. If new NetBSD OSI functions need shared prototypes, adding them here would reduce implicit-declaration or source-local duplication risk.

Test signals: include hygiene, warnings-as-errors builds for missing prototypes, and audit for functions declared only in C files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_sleep.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_sleep.c

Purpose: NetBSD sleep/wakeup/wait primitives for OpenAFS, with separate implementations for pre-NetBSD-5 `tsleep` and NetBSD-5+ condition-variable kernels.

Important APIs and state: defines `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, and `afs_osi_Wakeup`; NetBSD 5+ also defines `afs_osi_InitWaitHandle`, `afs_osi_TimedSleep`, event hash table `afs_evhasht`, and `afs_evhashcnt`. Static `waitV` is used for generic wait cancellation.

Control flow: older builds set a wait-handle proc, drop GLOCK, loop with `tsleep` until timeout, signal, or cancellation, then reacquire GLOCK. Sleep and wakeup map to `tsleep` and `wakeup`. NetBSD 5+ uses `afs_getevent` to map arbitrary event addresses to reusable `afs_event_t` entries containing a condition variable, sequence number, and refcount. Sleep waits while the sequence is unchanged; wakeup increments the sequence and broadcasts when there are waiters. Timed sleep uses `cv_timedwait` or `cv_timedwait_sig` with millisecond-to-tick conversion.

Dependencies and integration: depends on `afs_global_mtx` from `osi_machdep.h` for CV waits, OpenAFS GLOCK assertions, small-space allocation, stats counters, NetBSD time/tick APIs, and event structures from common AFS headers.

State and persistence: in-memory wait handles and event hash entries. Event structures are reused when refcount reaches zero but are not removed from the hash table in this file.

Risks: missed wakeups are prevented by sequence checks, but event reuse and refcount handling must stay under GLOCK. Older `tsleep` code drops GLOCK around blocking calls. `afs_osi_Wakeup` in the NetBSD 5+ path sets a local `ret` but returns 0 unconditionally, which may be intentional or a bug if callers rely on the return value.

Test signals: timed wait timeout vs signal, cancellation, multiple waiters on same event, repeated event reuse, interruptible sleep, wakeup return expectations, and lock-debug runs ensuring CV waits occur with `afs_global_mtx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vcache.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_vcache.c

Purpose: NetBSD vcache/vnode allocation and recycling hooks for OpenAFS.

Important APIs: `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

Control flow: `osi_TryEvictVCache` optionally logs debug messages, calls `osi_VM_FlushVCache`, and reports success if VM flush succeeds. `osi_NewVnode` allocates a `struct vcache` with `afs_osi_Alloc` and clears `tvc->v` so later attach logic knows no vnode exists yet. `osi_PrePopulateVCache` zeros the entire vcache. `osi_AttachVnode` drops `afs_xvcache` and GLOCK, calls `afs_nbsd_getnewvnode(avc)` to allocate/attach a NetBSD vnode with one refcount, reacquires locks, and initializes an older-kernel vnode rwlock when needed. `osi_PostPopulateVCache` sets the vnode mount to `afs_globalVFS` and default type to regular file. `osi_vnhold` wraps `VN_HOLD`.

Dependencies and integration: depends on NetBSD vnode allocation helper `afs_nbsd_getnewvnode`, global VFS state from `osi_vfsops.c`, NetBSD VM flush routines, and common vcache locks. It is called by common OpenAFS vcache allocation/reuse paths.

State and persistence: creates and mutates in-memory vcaches and attached NetBSD vnodes. No durable state.

Risks: dropping locks during vnode allocation is necessary but opens races; code reacquires `afs_xvcache` afterward. Zeroing the full vcache in `osi_PrePopulateVCache` must only occur before fields needing preservation are initialized. The TODO comment asks whether `vgone()` or `vrecycle()` should be used for eviction, suggesting lifecycle semantics may be incomplete.

Test signals: vcache allocation/attach, vnode refcount behavior, recycle under low-memory/cache pressure, NetBSD 5 and older lock initialization, and root/global mount assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vfs.h -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_vfs.h

Purpose: small NetBSD VFS compatibility header for mode-bit aliases.

Important APIs/macros: defines include guard `_OSI_VFS_H` and maps `VSUID` to `S_ISUID` and `VSGID` to `S_ISGID`.

Control flow: none.

Dependencies and integration: included by platform/common code needing portable vnode mode-bit names. The actual richer NetBSD vnode/VFS mappings are in `osi_machdep.h`.

State and persistence: none.

Risks: minimal. The header assumes `S_ISUID` and `S_ISGID` are in scope before use. Future mode aliases should be coordinated with `osi_machdep.h` to avoid split definitions.

Test signals: compile coverage for NetBSD code paths using `VSUID`/`VSGID`, and include-order checks ensuring mode constants are defined.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vfsops.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_vfsops.c

Purpose: NetBSD VFS operations, mount/root/unmount/statfs lifecycle, pathname lookup wrapper, and legacy LKM registration for OpenAFS.

Important APIs and state: defines `afs_vfsops`, `afs_nbsd_lookupname`, `afs_mount`, `afs_unmount`, `afs_root`, `afs_statvfs`, `afs_sync`, `afs_init`, `afs_reinit`, `afs_done`, and older `libafs_lkmentry`/LKM load-unload helpers. Globals include `afs_globalVFS`, `afs_globalVp`, and `afs_dynamic_fsid`. For older NetBSD it also defines `afs_sysent`, `old_sysent`, `old_setgroups`, and `lkmid`.

Control flow: `afs_nbsd_lookupname` builds a NetBSD `nameidata`/`pathbuf` according to kernel version, calls `namei`, and returns the leaf vnode. `afs_mount` rejects updates and multiple mounts, initializes disconnected vcaches when enabled, records the mount globally, populates mount stat fields and names, obtains a new fsid, and calls `afs_statvfs`. `afs_unmount` gives up callbacks for disconnected mode, releases global root vnode, flushes vnodes with `vflush`, clears globals, calls `afs_shutdown(AFS_COLD)`, clears `mnt_data`, and logs unmount. `afs_root` loops until it has a stable `afs_globalVp`, initializes request/checks AFS, fetches root vcache, refs and locks vnode, sets `VV_ROOT`, updates global VFS, and returns it. `afs_statvfs` reports fake capacity. `afs_sync` stores dirty vcaches when disconnected mode is enabled. Legacy LKM load patches `AFS_SYSCALL` and `SYS_setgroups`; unload restores them.

Dependencies and integration: depends on NetBSD VFS/vnode/namei APIs, OpenAFS root fid/cache initialization, disconnected-mode helpers, common shutdown, syscall handlers, and vnode operation descriptors. Modern module attachment is handled in `osi_kmod.c`, while this file still contains older LKM support for non-NetBSD-6 builds.

State and persistence: maintains one live AFS mount in kernel globals and reports fake filesystem capacity. Shutdown affects in-memory AFS client state and local cache lifecycle via common shutdown.

Risks: `afs_root` has delicate races around `afs_globalVp`, vnode locking, and stale root vcaches. `vflush` does not support forced unmount here. Multiple mount rejection is global. The code checks `VOP_ISLOCKED(*vpp)` before `*vpp` is assigned, which is suspicious and should be validated in the target NetBSD API context. Legacy syscall patching has the same restore risks as other syscall-hook code.

Test signals: mount/update/remount rejection, root lookup under callback/root-volume change, unmount with active vnodes, statvfs values, disconnected dirty sync, name lookup for user/system paths, modern module vs legacy LKM builds, and load/unload syscall restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vm.c -->
## sources/distributed-fs/openafs/src/afs/NBSD/osi_vm.c

Purpose: NetBSD VM/buffer-cache integration for OpenAFS vcache recycling, page flush, store, invalidation, and truncation.

Important APIs: `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: `osi_VM_FlushVCache` validates that the vcache has a vnode, drops GLOCK, calls `cache_purge(vp)` and `vflushbuf(vp, 1)`, then reacquires GLOCK. `osi_VM_StoreAllSegments` drops the vcache lock and GLOCK, enters the vnode interlock, calls `VOP_PUTPAGES` for all pages with clean/synchronous flags, then reacquires AFS locks. `osi_VM_TryToSmush` releases the vcache lock, flushes the vcache, and reacquires it. `osi_VM_FlushPages` purges name/cache state and invalidates buffers with `vinvalbuf`. `osi_VM_Truncate` calls `vtruncbuf` to purge buffers beyond the new length.

Dependencies and integration: depends on NetBSD vnode buffer/page APIs (`cache_purge`, `vflushbuf`, `VOP_PUTPAGES`, `vinvalbuf`, `vtruncbuf`), `curlwp`, AFS debug flags, and GLOCK/vcache locks. It is used by callback invalidation, vcache recycle, flush commands, truncation, and store-all-segments paths.

State and persistence: mutates NetBSD VM/buffer-cache state for AFS vnodes. Durable data movement is performed by NetBSD vnode paging/buffer machinery and common AFS store logic, not by this file directly.

Risks: correct lock dropping is essential because VM operations can block. `osi_VM_FlushVCache` returns 0 even for `vp == NULL` after logging, so callers treat missing vnode as flush success. `osi_VM_StoreAllSegments` explicitly enters `v_interlock` before `VOP_PUTPAGES`; API expectations must match target NetBSD versions.

Test signals: callback page invalidation, dirty page store on fsync/sync, truncate behavior, vcache recycle with/without vnode, debug-lock kernels, and NetBSD version matrix for vnode paging APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/NBSD/osi_vm.c -->
