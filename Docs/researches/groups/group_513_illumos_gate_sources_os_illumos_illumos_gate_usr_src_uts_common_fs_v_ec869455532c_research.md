# Group Research: group_513_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_v_ec869455532c

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/vfs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/vfs.c

## Purpose
`vfs.c` is the illumos kernel’s core VFS mount/filesystem-instance manager. It owns VFS operation-vector construction, root filesystem mounting, common mount/unmount paths, mount option parsing, VFS list/hash management, filesystem switch lookup/loading, VFS reference lifetime, mount-table timestamps/events, VFS feature bits, and lofi-backed file mounts.

## Major Responsibilities
- Provides `fsop_*` dispatch wrappers for VFS operations: mount, unmount, root, statvfs, sync, vget, mountroot, freefs, vnstate, syncfs.
- Builds `vfsops_t` vectors from filesystem templates through `fs_copyfsops()` and shared `fs_build_vector()`.
- Initializes global VFS state in `vfsinit()`, including the VFS kmem cache, vnode cache, FEM, stray/EIO VFS ops, built-in filesystem init, vopstats startup, xattrs, and reparse support.
- Mounts the root filesystem in `vfs_mountroot()` and then mounts required early filesystems such as `/devices`, `/dev`, `ctfs`, `proc`, `mntfs`, `tmpfs`, `objfs`, `bootfs`, and global-zone `sharefs`.
- Implements `domount()`, the central common mount path used by syscall/autofs/NFS trigger/PxFS callers.
- Implements `dounmount()` and `vfs_unmountall()` for individual and shutdown unmount flows.
- Maintains the global circular VFS list, per-zone VFS lists, and fsid hash buckets.
- Maintains `/etc/mnttab` change timestamps, polling wakeups, and dummy vnode operations for file-event notification.
- Manages mount option tables, option cancellation, tags, parsing, stringification, copying, merging, and freeing.
- Manages `vfssw` lookup/autoload/reference counts and `vfs_t` allocation/reference lifecycle.
- Supports VFS feature bit registration/query/propagation.
- Supports file-backed filesystem mounting by automatically mapping eligible regular files through `lofi`.

## Key Data and Globals
- `rootdir`, `devicesdir`, `devdir`: global root/device vnodes.
- `rootvfs`: root VFS and global circular VFS list anchor.
- `rvfs_list`, `vfshsz`: VFS fsid hash table and bucket count.
- `vfslist`: global VFS list/mnttab lock.
- `vfssw_lock`: filesystem switch table lock.
- `vfs_miplist`: mount-in-progress device list used to detect concurrent device mounts.
- `vfs_mnttab_ctime`, `vfs_mnttab_mtime`, `vfs_pollhd`, `vfs_mntdummyvp`: mnttab event state.
- `vfs_mntopts`: generic VFS option prototype covering `ro/rw`, `suid/nosuid`, `devices/nodevices`, `setuid/nosetuid`, `nbmand/nonbmand`, `exec/noexec`, and `remount`.

## Mount Flow
`domount()` is the central function. It:
- Marks the mountpoint vnode with `VVFSLOCK`.
- Resolves the filesystem type from explicit `fsname`, string options, numeric fstype, or rootfs default.
- Holds and validates the `vfssw` entry, checks `VFS_INSTALLED`, and applies `secpolicy_fs_allowed_mount()`.
- Copies prototype mount options, parses option strings, and lets flag bits override option state.
- Validates remount support, read-only transitions, and NBMAND immutability on remount.
- Resolves resource and mountpoint paths, including non-global-zone rootpath expansion.
- Locks the mountpoint with `vn_vfswlock()` unless `MS_NOSPLICE` is used.
- Allocates or reuses a `vfs_t`, initializes ops, holds it, optionally creates a lofi mapping, and applies forced `nosuid` for lofi mounts.
- Adds device mounts to the mount-in-progress list before calling the filesystem.
- Swaps final option tables into `vfsp`, sets resource/mountpoint strings, emits mounted-over events, and calls `VFS_MOUNT()`.
- On success, updates VFS flags from options, builds the returned option string, initializes vopstats, links into the namespace with `vfs_add()` or holds an unspliced VFS, and returns the held `vfsp`.
- On failure, restores remount state, removes lofi/mip state, unlocks, frees partial VFS/mnttab data, and unreferences the `vfssw`.

## Root and Boot Integration
- `vfs_mountroot()` initializes locks/hash structures, calls `rootconf()`, establishes `rootdir`, sets early process cwd/root, records the global zone root vnode, enables module root access, initializes ZFS boot support, sets root resource info, and mounts required pseudo filesystems.
- `rootconf()` chooses and loads the root filesystem module, handles x86 HVM boot hooks, cluster boot hooks, NFS/iSCSI boot plumbing, initializes `rootvfs`, mounts root read-only first, and records `rootdev`.
- `getrootfs()` derives root filesystem type/module from boot properties, including special NFS type mapping and ZFS bootfs detection.

## VFS Lists, Hashing, and Locking
- `vfs_add()` attaches a mounted VFS to the covered vnode, sets flags, holds references, and calls `vfs_list_add()`.
- `vfs_list_add()` assigns creation time, zone ownership/ref, inserts into global list, zone list, fsid hash, updates mnttab time, and wakes mnttab pollers.
- `vfs_list_remove()` removes from hash/global/zone lists and updates mnttab state.
- `getvfs()` looks up by `fsid_t` through the hash table and returns a held VFS.
- `vfs_lock()`, `vfs_rlock()`, `vfs_lock_wait()`, `vfs_rlock_wait()`, and `vfs_unlock()` use the shared vnode/VFS lock table implemented in `vnode.c`.
- `vfs_lock_held()` and `vfs_lock_owner()` expose lock diagnostics.

## Mount Options
- Option tables are deep-copied and freed with `vfs_copyopttbl*()` and `vfs_freeopttbl()`.
- `vfs_parsemntopts()` destructively scans comma-separated option strings, supports `key=value`, and can create dynamic option slots.
- `vfs_setmntopt_nolock()` handles value allocation, display flags, `MO_IGNORE`, `VFS_CREATEOPT`, and cancellation lists.
- `vfs_buildoptionstr()` serializes set options back to a comma-separated string.
- `vfs_mergeopttbl()` merges outer/global and inner/filesystem option tables while preserving cancel semantics.
- `vfs_settag()` and `vfs_clrtag()` let privileged callers add/remove arbitrary tag options on a mounted filesystem identified by dev and mountpoint.

## Unmount and Shutdown
- `dounmount()` purges DNLC entries, syncs unless forced, locks the VFS, calls `VFS_UNMOUNT()`, tears down vopstats, removes namespace linkage, unlocks covered vnode, and releases references.
- `vfs_unmountall()` walks the list backwards during shutdown, syncs and unmounts non-root filesystems, and restarts traversal safely if the list changed while unlocked.
- `vfs_syncall()` performs shutdown sync, then loops on dirty buffer/page counts with progress detection and retry limits.

## Filesystem Switch and Operation Vectors
- `allocate_vfssw()` reserves a `vfssw` entry before root is fully available.
- `vfs_getvfssw()` maps public fstype to module name, autoloads modules, and returns a referenced switch entry.
- `vfs_getvfsswbyname()` and `vfs_getvfsswbyvfsops()` search existing entries.
- `vfs_refvfssw()` / `vfs_unrefvfssw()` maintain unload-prevention counts.
- `fs_build_vector()` is the generic vector builder used by both VFS and vnode layers; it maps named operation definitions into fixed vectors, substitutes `fs_default`/`fs_error`, rejects NULL funcs, and reports unused supplied ops.

## Integration Points
- Calls into vnode layer for mountpoint locking, vnode allocation, dummy vnode ops, mounted-over events, and path setting.
- Calls into filesystem modules through `VFS_*` operation vectors.
- Interacts with zones through path translation, `zone_find_by_path()`, `mount_in_progress()`, and VFS zone refs.
- Integrates with DNLC, lofi/LDI, boot properties, ZFS SPA boot, cluster boot, mntfs polling, kstats/vopstats, FEM, xattrs, and reparse points.

## Risks and Invariants
- `domount()` has many partial-initialization exits; correctness depends on paired cleanup for option tables, vnode holds, lofi mappings, mip entries, VFS holds, and locks.
- VFS list updates must hold `vfslist`; hash bucket locking order is list lock before hash lock.
- Mnttab-visible fields must not become NULL while a listed VFS is being remounted.
- Non-global-zone resource/mountpoint expansion must stay below `MAXPATHLEN`.
- `vfs_delmip()` returns without unlocking if the entry is unexpectedly absent; the code comments say this should not happen, but this path would leave `vfs_miplist_mutex` held.
- Lofi mounts are deliberately restricted from remount/global/suid/setuid/devices options and force `nosuid`.
- `VFS_RELE()` calls filesystem `VFS_FREEVFS()` only after successful full initialization; partial mount failures use `vfs_free()` directly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/vnode.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/vnode.c

## Purpose
`vnode.c` is the illumos kernel’s common vnode operation and lifecycle layer. It builds vnode operation vectors, implements generic open/create/link/rename/remove helpers, manages vnode allocation/recycling/reference release, wraps every VOP call with accounting/feature checks/credential mapping, maintains vnode path caches, implements shared vnode/VFS lock hashing, provides vnode-specific data storage, and supports vopstats/reparse helpers.

## Major Responsibilities
- Defines `vn_ops_table`, mapping named VOP operations into `vnodeops_t` offsets and default/error functions.
- Creates and frees vnode operation vectors with `vn_make_ops()` / `vn_freevnodeops()`.
- Initializes and manages the vnode kmem cache.
- Implements `vn_rdwr()`, `vn_openat()`, `vn_createat()`, `vn_linkat()`, `vn_renameat()`, and `vn_removeat()`.
- Handles vnode release variants: normal, DNLC-aware, stream-clearing, and async inactive dispatch.
- Maintains VFS/vnode mount locks through a hashed `rwstlock` table used by both vnode and VFS code.
- Implements VOP wrapper functions `fop_*()` called by `VOP_*` macros.
- Maintains vnode open counts, mmap counts, vopstats counters, DTrace probes, and cached vnode paths.
- Implements vnode event helper calls for FEM/event notification.
- Provides vnode-specific data key/value storage with destructors.
- Implements xvattr helpers and reparse-point marking/query support.

## Key Data and Globals
- `vn_ops_table`: operation translation table for all standard vnode operations.
- `vn_cache`: kmem cache for `vnode_t`.
- `iftovt_tab`, `vttoif_tab`: mode/vnode-type translation tables.
- `vopstats_fstype`, `vs_templatep`, `vskstat_tree`, `vsk_anchor_cache`, `vopstats_enabled`: vopstats/kstat infrastructure.
- `vn_vpath_empty`: shared empty path sentinel for vnode path caching.
- `max_vnode_path`: cap for cached path allocation, defaulting to four `MAXPATHLEN`s.
- `vn_vfslocks_buckets`: hashed lock table keyed by vnode or VFS pointer.
- `vsd_lock`, `vsd_nkeys`, `vsd_list`, `vsd_destructor`: vnode-specific data registry.

## Vopstats and Kstats
- `create_vopstats_template()` initializes all named counters once, including operation counts and byte counters for read/write/readdir.
- `initialize_vopstats()` copies the template into a per-VFS stats structure.
- `get_fstype_vopstats()` finds per-filesystem-type stats, accounting for NFS variants and special VFS instances.
- `get_vskstat_anchor()` uses `VFS_STATVFS()` fsid to create a per-mounted-filesystem kstat anchor in an AVL tree.
- `teardown_vopstats()` removes the anchor, deletes kstats, and frees anchor state.
- `VOPSTATS_UPDATE` and `VOPSTATS_UPDATE_IO` update per-mounted and per-fstype counters and fire fsinfo DTrace probes.

## Generic File Operations
- `vn_rdwr()` builds a single-iovec `uio`, checks read-only writes and negative lengths, applies NBMAND conflict checks, takes `VOP_RWLOCK()`, dispatches read/write, unlocks, and reports residuals.
- `vn_openat()` handles create vs lookup open, large-file checks, write/truncate restrictions, mandatory lock checks, access checks, `FNOFOLLOW`, `FNOLINKS`, socket restrictions, NBMAND share reservations, `VOP_OPEN()`, truncate via `VOP_SETATTR()`, direct I/O enablement, and ESTALE retry.
- `vn_createat()` resolves parent/target, applies default ACL/umask behavior, handles read-only and existing-file cases, mandatory lock truncation checks, mount-root special handling, large-file overflow checks, mkdir/create dispatch, audit hooks, and ESTALE retry.
- `vn_linkat()` resolves source and target parent, verifies same fsid and writable target filesystem, then calls `VOP_LINK()`.
- `vn_renameat()` resolves both parents/targets, verifies same fsid, rejects directory mount-root rename, checks NBMAND conflicts for source/target, and calls `VOP_RENAME()`.
- `vn_removeat()` resolves parent/entry, rejects mounted roots unless `VFS_UNLINKABLE`, handles namefs unmount-over-file behavior, checks parent VFS read-only state, performs NBMAND remove checks, and calls `VOP_RMDIR()` or `VOP_REMOVE()`.

## Vnode Lifecycle
- `vn_rele()` calls `VOP_INACTIVE()` when dropping the final reference, leaving `v_count` at 1 during inactive to prevent races.
- `vn_rele_dnlc()` treats multiple DNLC holds as one vnode reference through `v_count_dnlc`.
- `vn_rele_stream()` clears `v_stream` under `v_lock` before release.
- `vn_rele_async()` dispatches final inactive work to a taskq.
- `vn_recycle()` clears reusable vnode state: open/mmap counts, FEM head, cached path, file-event data, MPSS data, and VSD.
- `vn_reinit()` resets core vnode fields but preserves synchronization objects, `v_data`, and `v_op`.
- `vn_alloc()` allocates from `vn_cache` and reinitializes; `vn_free()` validates lock state/counts, frees path/FEM/file-event/VSD state, and returns to cache.
- `vn_reclaim()`, `vn_idle()`, `vn_exists()`, and `vn_invalid()` forward vnode state transitions to VFS FEM hooks when installed.

## Shared Vnode/VFS Locks
- `vn_vfslocks_getlock()` hashes an arbitrary vnode/VFS pointer to a bucket, finds or allocates a lock entry, and references it.
- `vn_vfslocks_rele()` decrements the refcount, removes zero-ref entries, destroys the rwst lock, and panics on invalid negative/not-found states.
- `vn_vfswlock_wait()`, `vn_vfsrlock_wait()`, `vn_vfswlock()`, `vn_vfsrlock()`, `vn_vfsunlock()`, and `vn_vfswlock_held()` protect `v_vfsmountedhere` and are also used by `vfs.c` for VFS locking.
- The lock release protocol intentionally drops two references: one temporary lookup reference and one lock-holder reference.

## VOP Wrapper Layer
The `fop_*()` wrappers are the common path behind `VOP_*` macros. They:
- Dispatch through `vp->v_op`.
- Map credentials with `VOPXID_MAP_CR()` when the filesystem lacks `VFS_XID`.
- Update vopstats after each operation.
- Gate feature-specific behavior, including case-insensitive lookup, dirent flags, ACL-on-create, xvattr, ACE-mask access, and zero-copy buffers.
- Maintain path cache updates on successful lookup/create/mkdir and path copying if `VOP_OPEN()` swaps vnodes.
- Maintain regular-file read/write open counts in `fop_open()` and `fop_close()`.
- Maintain mmap read/write page counts in `fop_addmap()` and `fop_delmap()`, including NFS `EAGAIN` delayed-delmap behavior.
- Validate dump block arguments before `vop_dump()`.
- Mark symlink creates as reparse points when the filesystem supports reparse data and the target uses the reparse tag format.

## Path Cache
- `vn_clearpath()` clears cached path conditionally by timestamp.
- `vn_setpath_common()` is the core path installer for direct strings, parent/name composition, and rename updates.
- `vn_updatepath()` updates child paths from parent lookup when safe and meaningful.
- `vn_setpath_str()` installs a complete root-relative path, used by VFS root handling.
- `vn_renamepath()` forces path update during filesystem rename.
- `vn_copypath()` copies an existing path to a newly returned vnode, mainly after `VOP_OPEN()` substitution.
- The implementation uses `v_path_stamp` to avoid replacing newer path data after lock drops and avoids updating paths through `VTRAVERSE` parents.

## Vnode Events and Accessors
- `vnevent_*()` helpers call `VOP_VNEVENT()` only when a vnode has FEM/event state.
- Accessors report read-only state, flock presence, mandatory locks, cached data, mountpoint status, mounted VFS, DNLC references, open modes, mapped modes, and zone-change safety.
- `vn_can_change_zones()` resolves real vnode, checks backing filesystem `vfssw` flags, and blocks zone movement for `VSW_NOTZONESAFE` filesystems unless `nfs_global_client_only` is set.

## Vnode-Specific Data
- `vsd_create()` allocates a global key and optional destructor, growing the destructor table as needed.
- `vsd_destroy()` clears a key globally and calls its destructor on every vnode that has a value.
- `vsd_get()` / `vsd_set()` access per-vnode values under `v_vsd_lock`.
- `vsd_free()` destroys all values attached to a vnode, unlinks its VSD node from the global list, and frees storage.
- `vsd_realloc()` is a zeroing grow/copy/free helper.

## Reparse and Extended Attributes
- `xva_init()` initializes an extensible attribute request structure.
- `xva_getxoptattr()` returns optional xvattr storage when `AT_XVATTR` is set.
- `fs_reparse_mark()` validates a reparse target and marks the symlink create attributes with `XAT_REPARSE`.
- `vn_is_reparse()` queries a symlink’s xvattr reparse bit when the filesystem supports xvattrs.

## Risks and Invariants
- Final vnode release depends on `VOP_INACTIVE()` tolerating the vnode still having `v_count == 1`.
- `vn_openat()` and `vn_createat()` have many multi-resource exits; correctness depends on paired close/unshare/VN_RELE/nbl_end paths.
- `fop_open()` increments counts before filesystem open to avoid false-negative open-count races, then must adjust counts if open fails or swaps vnodes.
- Path-cache code allocates while locks are dropped and relies on stamps to avoid stale overwrites.
- `vn_vfslocks_getlock()` can race allocation; the second bucket scan is required to avoid duplicate lock entries.
- `vsd_destroy()` assumes callers prevent concurrent `vsd_set()`/`vsd_get()` for the destroyed key.
- Feature gates intentionally fail early with `EINVAL`/`ENOTSUP` before calling filesystems that do not advertise support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/vnode.c -->