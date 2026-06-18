# Chunk Research: sources/os/darwin/xnu/bsd/vfs/vfs_syscalls.c lines 1-10623

## Scope

This chunk covers the first 10,623 lines of Darwin/XNU BSD VFS syscall implementation. It includes mount and unmount plumbing, graft/ungraft image support, sync/statfs/getfsstat, fd-to-vnode and file-id lookup helpers, cwd/root changes, open/openat/open-by-id, mknod/mkfifo, path construction helpers, link/symlink/unlink/delete, lseek/access/stat/pathconf/readlink, flags/mode/owner/time/truncate/fsync, copyfile/clonefile, rename, mkdir, and the beginning of `rmdirat_internal()`. The source tree `sources/os/darwin/xnu` is included by `Docs/research_subset_a.md`.

## APIs and Entry Points

- Mount entry points include `mount()`, `__mac_mount()`, `fmount()`, `kernel_mount()`, `vfs_mount_at_path()`, `mount_common()`, `prepare_coveredvp()`, and `vfs_notify_mount()`.
- Cryptex/graft entry points include `graftdmg()`, `ungraftdmg()`, `graft_secureboot_cryptex()`, `graft_secureboot_read_metadata()`, and fd-backed metadata readers.
- Unmount entry points include `unmount()`, `funmount()`, `vfs_unmountbyfsid()`, `safedounmount()`, `dounmount()`, `dounmount_submounts()`, and `mount_dropcrossref()`.
- Sync/statfs surfaces include `sync()`, `sync_internal()`, `quotactl()`, `statfs()`, `fstatfs()`, `statfs64()`, `fstatfs64()`, `getfsstat()`, `__mac_getfsstat()`, and `getfsstat64()`.
- Lookup/fd helper APIs include `vnode_getfromfd()`, `vnode_getfromid()`, and `nameiat()`.
- Directory context APIs include `fchdir()`, `sys_fchdir()`, `__pthread_fchdir()`, `sys_chdir()`, `__pthread_chdir()`, `chroot()`, `pivot_root()`, and the shared `change_dir()`.
- File creation/opening APIs include `open1()`, `open1at()`, `open_extended()`, `openat_dprotected_np()`, `open_dprotected_np()`, `open()`, `open_nocancel()`, `openat()`, `openat_nocancel()`, `openbyid_np()`, `mknod()`, `mknodat()`, `mkfifo()`, `mkfifoat()`, and `mkfifo_extended()`.
- Namespace mutation APIs include `link()`, `linkat()`, `symlink()`, `symlinkat()`, `delete()`, `unlink()`, `unlinkat()`, `rename()`, `renameat()`, `renameatx_np()`, `mkdir()`, `mkdirat()`, `mkdir_extended()`, and `rmdirat_internal()`.
- Metadata and data-integrity APIs include `access()`, `faccessat()`, `access_extended()`, `stat*()`, `fstatat*()`, `readlink*()`, `chflags()`, `fchflags()`, `chmod*()`, `fchmod*()`, `chown()`, `lchown()`, `fchown()`, `fchownat()`, `utimes()`, `futimes()`, `truncate()`, `ftruncate()`, `fsync()`, `fsync_nocancel()`, `fdatasync()`, `copyfile()`, `clonefileat()`, and `fclonefileat()`.

## Core Control Flow

Mounting flows from syscall wrappers into `mount_common()`. User mounts copy in the filesystem type, look up the covered vnode with `namei()`, optionally copy a MAC label, normalize root updates, reject unsupported union configurations, and retry on `EBUSY` caused by concurrent mounts. Kernel mounts may pass vnodes directly or resolve the mount path themselves, then mark the operation with internal kernel-mount flags.

`mount_common()` has two major paths. For `MNT_UPDATE`, it verifies the vnode is a mount root, excludes concurrent mount/unmount, takes `mnt_rwlock`, preserves sticky mount properties such as content protection/removable, checks ownership/root authorization, runs MAC remount hooks, adjusts non-root mount flags, and dispatches to `VFS_MOUNT()` or special mount-by-role ioctls. Fresh mounts resolve the `vfstable`, call `prepare_coveredvp()` to authorize and set `VMOUNT`, allocate and initialize `struct mount`, optionally resolve/open a block device, call the filesystem mount callback, publish the mount on `v_mountedhere`, bump `mount_generation`, update process/root directories via `checkdirs()`, add the mount to the global list, cache capabilities/subtype, enable HFS quotas, mark the device mounted-on, and emit VFS/IOBSD/MAC notifications.

Unmounting enters through path, fd, or fsid lookup and then `safedounmount()`. That wrapper denies unsafe unmounts of root, system-associated, root-backing, nonresponsive `MNT_NOBLOCK`, or unauthorized mounts, then hands a consumed mount reference to `dounmount()`. `dounmount()` sets unmount state, optionally force-unmounts submounts, invalidates mount-generation caches, drains mount iteration, syncs and flushes vnodes for non-forced unmounts, calls `VFS_UNMOUNT()`, closes local backing devices, removes the mount from the list, clears the covered vnode hook, decrements vfsconf refs, purges name cache entries, marks the mount dead, drains refs, tears down disk-conditioner state, and finally releases the cross-reference/free path.

Open flows are centered on `open1()`. It validates access flags, allocates a fileproc, optionally gets an authorization fd, calls `vn_open_auth()`, handles fdesc duplicate open fallback, installs vnode fileops and data, breaks leases for create/truncate, applies advisory flock locks, truncates on `O_TRUNC`, allocates directory-specific fd state, handles secluded-memory hints, sets controlling TTY when applicable, and publishes the fd. `open1at()` and `nameiat()` implement relative path lookup from a directory fd for `*at` syscalls. `openbyid_np()` requires platform-binary or entitlement access, resolves fsid/object id to a path with `fsgetpath_internal()`, opens with fileid/fsid authentication attributes, and retries on vnode recycle races.

Namespace creation and deletion use a consistent pattern: initialize `nameidata`, perform parent/target lookup, authorize via MAC and kauth helpers, break directory leases where configured, call the appropriate VNOP/VFS wrapper, update vnode identity when needed, emit FSEvents and kauth file-operation notifications, and release `nameidone()` before putting parent vnodes. This pattern appears in `mknodat_internal()`, `mkfifo1()`, `linkat_internal()`, `symlinkat_internal()`, `unlinkat_internal()`, `mkdir1at()`, and the visible part of `rmdirat_internal()`.

Rename is the most complex namespace path in this chunk. `renameat_internal()` performs source DELETE and target RENAME lookups, supports `RENAME_EXCL`, `RENAME_SWAP`, no-follow-any, and resolve-beneath flags, validates cross-device constraints, supports renaming certain mount points by switching from root vnode to covered vnode, serializes tree-shaping directory renames with the mount rename lock, authorizes with path-aware `vn_authorize_renamex_with_paths()`, handles compound VNOP continuation (`EKEEPLOOKING`), dataless materialization retry (`EDATALESS`), vnode recycle retry (`ERECYCLE`), and authorization `ENOENT` retry, then emits kauth/FSEvents, updates submount mount-on paths, and fixes vnode name/parent identity.

## State and Synchronization

- Global mount state includes `mount_generation`, `vfs_nummntops`, atomic `mount_unique_id`, `rootvnode`, `rootvnode_rw_lock`, and mount-list/vfsconf refcounts.
- Mount publication uses vnode flags `VMOUNT` and `VMOUNTEDHERE`, `v_mountedhere`, `mnt_vnodecovered`, `mnt_crossref`, `mnt_realrootvp`, `mnt_lflag` bits such as `MNT_LMOUNT`, `MNT_LUNMOUNT`, `MNT_LFORCE`, `MNT_LDEAD`, and `mnt_kern_flag` bits such as `MNTK_KERNEL_MOUNT`, `MNTK_SYSTEM`, `MNTK_BACKS_ROOT`, `MNTK_HAS_MOVED`, `MNTK_UNMOUNT`, and capability cache bits.
- Mount synchronization uses per-mount spin locks, `mnt_rwlock`, mount-list locks, name-cache locks, mount iteration drain/reset, `vfs_busy()`/`vfs_unbusy()`, and SMR synchronization before freeing mounts when name-cache SMR is enabled.
- Current/root directory state lives in `proc->p_fd.fd_cdir`, `fd_rdir`, per-thread `uthread->uu_cdir`, `P_THCWD`, and `FD_CHROOT`. `checkdirs()` iterates processes after mount publication and swaps old covered vnodes for the new filesystem root.
- Open file state uses `fileproc`, `fileglob`, `fg_flag`, `fg_ops`, `fg_data`, `fg_offset`, `fg_cred`, `fg_vn_data`, `FP_CLOEXEC`, `FP_CLOFORK`, and `uu_dupfd`.
- Sync state uses `sync_mtx_lck`, `sync_thread_state`, `SYNC_THREAD_RUN`, `SYNC_THREAD_RUNNING`, `sync_timeout_seconds`, and a timeout log throttle.
- Namespace mutation serializes hardlink-sensitive operations with `vnode_link_lock()`, tree-shaping renames with `mount_lock_renames()`, and uses vnode identity updates to invalidate stale parent/name assumptions after link, unlink, symlink, clone, rename, mkdir, and rmdir operations.

## Dependencies

This chunk depends heavily on XNU VFS/vnode interfaces (`VNOP_*`, `VFS_*`, `vn_*`, `vnode_*`, `namei`, `nameidata`, `componentname`), mount internals, file descriptor/fileproc APIs, kauth authorization, MAC Framework hooks, audit hooks, FSEvents, IOKit BSD mount notifications, UBC/buffer invalidation, VM memory-object hints, quotas, content protection, clonefile/snapshot/graft ioctls, process credential/limit APIs, and user-copy helpers.

Compile-time feature dependencies include `CONFIG_MACF`, `CONFIG_FSE`, `CONFIG_IMGSRC_ACCESS`, `CONFIG_UNION_MOUNTS`, `CONFIG_TRIGGERS`, `CONFIG_FILE_LEASES`, `CONFIG_APPLEDOUBLE`, `CONFIG_ROSV_STARTUP`, `CONFIG_MOUNT_VM`, `CONFIG_BASESYSTEMROOT`, `CONFIG_MOUNT_PREBOOTRECOVERY`, `CONFIG_MNT_ROOTSNAP`, `NAMEDSTREAMS`, `NAMEDRSRCFORK`, `QUOTA`, and platform-specific `XNU_TARGET_OS_OSX` behavior.

## Risks and Edge Cases

- Mount setup has many staged side effects: `VMOUNT`, device refs, device opens, vfsconf refs, MAC labels, mount locks, mount-list insertion, covered vnode references, and `mnt_crossref`. Cleanup labels must remain ordered or mount/device/vnode state can leak or be freed while reachable.
- Concurrent mounts on the same covered vnode are intentionally surfaced as `EBUSY` and retried by `__mac_mount()`. `prepare_coveredvp()` must wake waiters whenever it clears `VMOUNT`.
- Name-cache fast paths depend on `mount_generation`, `mnt_realrootvp`, and exclusive name-cache locking around mount/unmount publication.
- Forced unmount intentionally skips some normal sync/flush guarantees and can leave submount failures dangling; covered vnode iocount acquisition uses `vnode_getalways()` to avoid deadlocks during forced unmount.
- Non-root mount/update behavior silently enforces `MNT_NOSUID`, `MNT_NODEV`, and sometimes `MNT_NOEXEC`, which can surprise callers and must be preserved across update paths.
- `sync_internal()` is deliberately timeout bounded for power management and can return before all filesystem sync work completes.
- `access()` and `access_extended()` use real credentials unless `AT_EACCESS` is requested; this differs from most mutating syscalls and is easy to regress.
- `fstatat_internal()` supports `AT_FDONLY`, real-device reporting, named-stream special handling, and xsecurity size/copyout semantics; incorrect cleanup can leak `file_drop()`, vnode iocounts, or file security allocations.
- Link/unlink/rename/rmdir authorization can return transient `ENOENT` because MAC path generation races with hardlink/name-cache lookups. The code uses bounded retries (`MAX_AUTHORIZE_ENOENT_RETRIES`, `MAX_LINK_ENOENT_RETRIES`, `MAX_RENAME_ERECYCLE_RETRIES`).
- Compound VNOP paths can return `EKEEPLOOKING` and mutate `nameidata` continuation state; callers must not assume one lookup maps to one VNOP call.
- Dataless rename requires materialization outside the rename lock and then retries with `VFS_RENAME_DATALESS`; a repeated dataless error becomes `EIO`.
- `openbyid_np()` reconstructs a path from fsid/object id, then revalidates by passing expected object id/fsid through vnode attributes. This guards path races but still needs bounded recycle retries.
- `truncate_validate_common()` sends `SIGXFSZ` and returns `EFBIG` when `RLIMIT_FSIZE` is exceeded; ftruncate also rejects descriptors without `FWRITE` and append-only files.
- The visible `rmdirat_internal()` path is incomplete at the chunk boundary, but it already shows restart loops for AppleDouble cleanup, compound rmdir continuation, dataless-directory fallback, and delete notifications.

## Cross-Chunk References

- Lines after 10623 complete `rmdirat_internal()`, define `rmdir()`, and then begin directory-reading support (`DIRENT64_LEN`, `DIRENT_LEN`, `DIRENT_END`, `vnode_readdir64()`, and later `getdirentries*()` paths). The adjacent read showed that `rmdirat_internal()` continues with compound-`ENOENT` retry handling, dataless directory fallback through `vn_remove()`, AppleDouble cleanup retry, delete notifications, cleanup, and `rmdir()`.
- Later chunks in this file also contain `getdirentries_common()`, `revoke()`, `getdirentriesattr()`, `searchfs()`, namespace resolver/dataless materialization machinery, `fsctl*()`, extended attributes, `fsgetpath*()`, purge, snapshot, and additional VFS control APIs. Several current-chunk callers depend on those later definitions, especially `fsgetpath_internal()` used by `openbyid_np()` and `vfs_materialize_reparent()` used by rename.
- `rmdirat_internal()` is declared near the top of this chunk and called by `unlinkat()` for `AT_REMOVEDIR`/`AT_REMOVEDIR_DATALESS`, but its public `rmdir()` wrapper falls just after this chunk boundary.
- `clonefile_internal()` and `renameat_internal()` depend on filesystem-specific VNOP implementations outside this file (`VNOP_CLONEFILE`, `vn_rename`, compound lookup/VNOP support) and on later dataless materialization helpers.
- Mount-by-role, snapshot-root, imageboot relocation, and graft flows depend on configuration-specific code and filesystem ioctls outside this line range.