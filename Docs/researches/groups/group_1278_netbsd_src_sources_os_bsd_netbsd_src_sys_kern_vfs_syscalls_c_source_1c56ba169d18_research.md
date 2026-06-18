# Group Research: group_1278_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_vfs_syscalls_c_source_1c56ba169d18

Scope checked against `Docs/research_subset_a.md`: subset A includes `sources/os/bsd/netbsd-src`. All four listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_syscalls.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_syscalls.c

Read completely: 5056 lines.

## Purpose
Implements NetBSD's VFS-facing syscall layer. It translates user ABI calls into pathname lookup, file descriptor, mount, vnode, quota, filehandle, namespace, metadata, sync, and storage-allocation operations.

## Main Interfaces
- Mount/statfs/quota: `sys___mount50`, `do_sys_mount`, `mount_update`, `mount_getargs`, `sys_unmount`, `do_sys_sync`, `vfs_syncwait`, `do_sys_quotactl`, `dostatvfs`, `do_sys_getvfsstat`.
- Directory context: `do_sys_fchdir`, `sys_fchroot`, `do_sys_chdir`, `sys_chroot`, `change_root`, `chdir_lookup`.
- Open/file handles: `do_open`, `fd_open`, `do_sys_openat`, `sys_open`, `sys_openat`, `vfs_composefh*`, `vfs_fhtovp`, `vfs_copyinfh_alloc`, `sys___getfh30`, `dofhopen`, `do_fhstat`, `do_fhstatvfs`.
- Namespace changes: `do_sys_mknodat`, `do_sys_mkfifoat`, `do_sys_linkat`, `do_sys_symlinkat`, `do_sys_unlinkat`, `do_sys_renameat`, `do_sys_mkdirat`, `sys_rmdir`.
- File and metadata operations: `sys_lseek`, `sys_pread*`, `sys_pwrite*`, `do_sys_accessat`, `do_sys_statat`, `kern_pathconf`, `do_sys_readlinkat`, `change_flags`, `change_mode`, `change_owner`, `do_sys_utimensat`, `sys_truncate`, `sys_ftruncate`, `sys_fsync*`, `dorevoke`, `sys_posix_fallocate`, `sys_fdiscard`.

## Control Flow And State
Most routines copy in paths or arguments, build `pathbuf`/`nameidata`, optionally apply `*at` directory-fd roots through `fd_nameiat`, acquire vnodes or files, authorize via kauth or filesystem access checks, call `VOP_*`/`VFS_*`, and unwind vnode locks/references and file descriptor holds.

Mount handling resolves the covered vnode, gets or autoloads `vfsops`, copies mount data, and dispatches to getargs/update/new mount. Successful mount/unmount posts `EVFILT_FS` events on `fs_klist`.

Open allocates a descriptor before `vn_open`, handles `EDUPFD`/`EMOVEFD`, installs `vnops`, processes advisory `O_EXLOCK`/`O_SHLOCK`, close-on-exec/fork flags, and affixes the file descriptor.

Rename is the most complex path: it brackets the source mount with `fstrans_start`, performs source and target lookups, rejects `.`/`..`, enforces same-mount rename, enters the filesystem rename lock, relookups the target for the legacy `VOP_RENAME` protocol, checks directory/type and POSIX retain semantics, optionally consults veriexec, then transfers vnode ownership to `VOP_RENAME`.

## Dependencies And Integration
Integrates with namei/pathbuf, file descriptor tables, vnode and mount operation vectors, fstrans, kauth, kqueue filesystem events, quota wrappers, stat/statvfs buffers, NFS filehandle formats, veriexec, fileassoc, ktrace, syncer state, and generic file I/O helpers.

## Risks And Edge Cases
- `do_sys_renameat` documents legacy `VOP_RENAME` locking weaknesses and stale vnode identity windows.
- `fd_nameiat` ignores directory fds for absolute paths by inspecting copied path text.
- Mount updates temporarily mutate flags under suspension and must restore syncer/worklist state on failure.
- Filehandle import validates variable handle sizes and includes an NFSv2 padded-handle compatibility path.
- `access` normally checks real IDs by cloning credentials unless `AT_EACCESS` is requested.
- Timestamp updates handle `UTIME_NOW`, `UTIME_OMIT`, null-time authorization semantics, and birthtime adjustment.
- `posix_fallocate` returns POSIX-style errors in `retval` while the syscall itself returns success.

## Filesystem Relevance
Central syscall-to-VFS entry point for filesystem administration, pathname mutation, file creation/opening, metadata changes, synchronization, filehandle access, and hole/allocation operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_trans.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_trans.c

Read completely: 1140 lines.

## Purpose
Implements filesystem transaction tracking, suspend/resume coordination, per-LWP mount transaction state, lower-mount aliasing for layered filesystems, and copy-on-write handler registration/execution.

## Main Interfaces
- Lifecycle: `fstrans_init`, `fstrans_lwp_dtor`, `fstrans_mount`, `fstrans_unmount`.
- Transactions: `fstrans_start`, `fstrans_start_nowait`, `fstrans_start_lazy`, `fstrans_done`, `fstrans_held`, `fstrans_is_owner`.
- State/suspension: `fstrans_setstate`, `fstrans_getstate`, `vfs_suspend`, `vfs_resume`.
- COW hooks: `fscow_establish`, `fscow_disestablish`, `fscow_run`.
- Diagnostics: `fstrans_dump` under DDB.

## Control Flow And State
Global transaction state is guarded by `fstrans_lock` with pserialize for fast visibility. Each mount has `fstrans_mount_info` recording state, refcount, gone flag, owner LWP, optional lower mount, and COW handlers. Each LWP has cached `fstrans_lwp_info` entries recording mount, alias, transaction count, COW recursion count, and lock type.

Shared transactions block once a filesystem is suspending; lazy transactions may pass during `FSTRANS_SUSPENDING` but not once fully suspended. Recursive transactions increment per-LWP counts. `fstrans_setstate` publishes a new state, waits for incompatible transactions to drain, and assigns/clears exclusive ownership.

Layered filesystems can alias their transaction accounting to a lower mount. Unmount marks mount info gone, removes it from the hash, and later per-LWP cleanup drops dead entries when transaction, COW, and alias counts reach zero.

COW handler list mutation waits for in-flight handlers with pserialize and `fli_cow_cnt`. `fscow_run` finds the mount from the buffer vnode or block-device mounted filesystem, runs registered handlers, and marks buffers `B_COWDONE` on success.

## Dependencies And Integration
Uses mount structures, pserialize, pool caches, condition variables, deadfs, specfs block-device lookup, buffers, and `VFS_SUSPENDCTL`. It is called by mount update/unmount/reclaim paths and filesystem code needing suspension barriers.

## Risks And Edge Cases
- Any missing `fstrans_done` can indefinitely block suspension.
- Lower-mount aliasing requires exact alias-count cleanup.
- `fstrans_mount_dtor` frees a copied/dead mount only after refcount and gone accounting align.
- COW handler removal must wait for active callbacks before freeing handler storage.
- `vfs_suspend` serializes all suspensions with `vfs_suspend_lock` and must resume on gone-mount errors.

## Filesystem Relevance
High. It provides the transaction barrier used to suspend filesystems safely, coordinate unmount/reclaim windows, and run filesystem COW hooks before buffer writes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_vnode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_vnode.c

Read completely: 2178 lines.

## Purpose
Implements NetBSD vnode lifecycle and vnode cache management: allocation, reference/hold accounting, LRU draining, deferred release, cache lookup by key, vnode creation, rekeying, reclaim, revocation, dead-vnode transition, and sharing helpers.

## Main Interfaces
- Setup/drain: `vfs_vnode_sysinit`, `vcache_init`, `vfs_drainvnodes`.
- Markers/LRU: `vnalloc_marker`, `vnfree_marker`, `vnis_marker`, `vrele_flush`.
- References: `vrefcnt`, `vput`, `vrele`, `vrele_async`, `vref`, `vhold`, `vholdl`, `holdrele`, `holdrelel`.
- Recycling/revocation: `vrecycle`, `vrevoke`, `vgone`, `vcache_make_anon`, `vdead_check`.
- Cache operations: `vcache_tryvget`, `vcache_vget`, `vcache_get`, `vcache_new`, `vcache_rekey_enter`, `vcache_rekey_exit`.
- Reclaim/free: `vcache_reclaim`, `vcache_free`, `vcache_dealloc`.
- Miscellaneous: `vwakeup`, `vnpanic`, `vshareilock`, `vshareklist`.

## Control Flow And State
The file defines a six-state vnode model: marker, loading, loaded, blocked, reclaiming, and reclaimed. State is protected by `v_interlock`, except transitions out of loading also require `vcache_lock`. High bits in `v_usecount` act as a gate for lockless `vcache_tryvget` and as a successful-vget race flag.

`vcache_get` hashes a mount/key pair, waits for loading nodes, references existing nodes, or allocates a loading vnode, inserts it, calls `VFS_LOADVNODE`, installs it on the mount list, and transitions to loaded. `vcache_new` creates a filesystem node first with `VFS_NEWVNODE`, then inserts the keyed vnode after any previous instance is reclaimed.

Last-reference release runs through `vrelel`: it drops fast non-last references atomically, otherwise obtains/defer-locks the vnode, clears mapping/text flags, calls `VOP_INACTIVE`, blocks new references when recycling, and may reclaim. Deferred releases are processed by a threadpool `vrele` job; memory pressure draining uses LRU marker iteration.

`vcache_reclaim` purges namecache, snapshots cache keys, invalidates buffers/pages, revokes special nodes, calls `VOP_RECLAIM`, removes the cache key, switches to dead vnode operations, and moves the vnode to `dead_rootmount`.

## Dependencies And Integration
Integrates with UVM vnode objects, namecache, mount reference/list management, fstrans, WAPBL, specfs, deadfs, threadpool jobs, sysctl hash stats, kqueue vnode lists, readahead contexts, PAX segvguard cleanup, and filesystem vnode operation vectors.

## Risks And Edge Cases
- Last-reference cleanup relies on `VUSECOUNT_GATE`, `VUSECOUNT_VGET`, vnode locks, interlocks, and UVM object locks remaining coherent.
- Deferred releases are necessary from pagedaemon or failed-lock contexts but depend on worker progress.
- Reclaim copies vnode keys because filesystem-owned key storage may vanish during `VOP_RECLAIM`.
- `vrevoke` suspends mounts while revoking device aliases and must handle aliases across mounts.
- `vcache_rekey_enter/exit` uses a temporary loading placeholder to prevent duplicate cache keys during filesystem key changes.
- `vshareklist` assumes external synchronization and shared interlocks for layered vnode event state.

## Filesystem Relevance
High. This is the core vnode identity, caching, reference, reclaim, and revocation machinery that every NetBSD filesystem relies on.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_vnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_vnops.c

Read completely: 1672 lines.

## Purpose
Implements vnode-backed `fileops` and common vnode operation wrappers: open, close, read/write, readdir, stat, ioctl, mmap, seek, advisory locking, pathconf, fadvise, truncate, extended attributes, block-device open helpers, FIFO bypass, and vnode kqueue bookkeeping.

## Main Interfaces
- Fileops table: `vnops` with `vn_read`, `vn_write`, `vn_ioctl`, `vn_fcntl`, `vn_poll`, `vn_statfile`, `vn_closefile`, `vn_kqfilter`, `vn_mmap`, `vn_seek`, `vn_advlock`, `vn_fpathconf`, `vn_posix_fadvise`, `vn_truncate`.
- Open/close: `vn_open`, `vn_openchk`, `vn_writechk`, `vn_close`.
- I/O: `vn_rdwr`, `vn_readdir`, `vn_read`, `vn_write`, `enforce_rlimit_fsize`.
- Metadata/control: `vn_stat`, `vn_ioctl`, `vn_fcntl`, `vn_poll`, `vn_kqfilter`, `vn_lock`.
- Mapping/advice: `vn_mmap`, `vn_seek`, `vn_posix_fadvise`.
- Attributes/devices/events: `vn_extattr_get`, `vn_extattr_set`, `vn_extattr_rm`, `vn_fifo_bypass`, `vn_bdev_open`, `vn_bdev_openpath`, `vn_knote_attach`, `vn_knote_detach`.

## Control Flow And State
`vn_open` performs namei-based open/create handling, including `O_CREAT`, `O_EXCL`, `O_NOFOLLOW`, `NONEXCLHACK`, veriexec checks, `VOP_CREATE`, `VOP_OPEN`, truncation, writecount increments, and special descriptor-return errors. `vn_openchk` validates vnode type and read/write/execute access.

`vn_read` and `vn_write` convert file flags into `IO_*` flags, lock the vnode, set `uio_offset`, call `VOP_READ`/`VOP_WRITE`, and update offsets when requested. Writes enforce `RLIMIT_FSIZE` on regular files and signal `SIGXFSZ` before `EFBIG`.

`vn_mmap` validates vnode type and offset overflow, handles `/dev/zero`, defaults missing sharing modes, converts private device mappings to shared, computes `maxprot` from file mode and file flags, rejects noexec executable mappings, calls `VOP_MMAP` or `udv_attach`, marks executable/writable mappings, and applies veriexec policy.

`vn_readdir` wraps `VOP_READDIR`, updates descriptor offset under file locking, and supports union-mount fallback by switching `fp->f_vnode` to the covered vnode.

## Dependencies And Integration
Depends on file descriptors, namei, vnode ops, mount flags, kauth credentials, veriexec, WAPBL assertions, UVM objects/device mappings/readahead, specfs, fifofs, tty session vnode tracking, kqueue knotes, and extended attribute VOPs.

## Risks And Edge Cases
- `vn_open` has delicate cleanup paths around `O_CREAT`, `NONEXCLHACK`, and optional `ni_dvp`.
- Writecount and text/executable mapping flags enforce `ETXTBSY` behavior and executable-page accounting.
- Directory reads can mutate `fp->f_vnode` and reset offsets when crossing union mount boundaries.
- `FIONREAD` on directories reads `fp->f_offset` under the file lock; block-map ioctls call `VOP_BMAP`.
- `vn_mmap` must keep `maxprot`, `VV_MAPPED`, `VI_WRMAP`, and `VI_EXECMAP` consistent with vnode/UVM state.
- `POSIX_FADV_DONTNEED` shrinks ranges to page boundaries before `VOP_PUTPAGES`, so sub-page requests may do nothing.
- Knotes maintain an interest bitmask to avoid unnecessary vnode-event traversal.

## Filesystem Relevance
High. This is the reusable vnode-as-file implementation used by regular files, directories, devices, FIFOs, mmap, fadvise, directory reads, and descriptor operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_vnops.c -->