# Group Research: group_1277_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_vfs_lockf_c_sources_o_34440384a8c1

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/os/bsd/netbsd-src` source tree. All five listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_lockf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_lockf.c

Read completely: 975 lines.

Implements NetBSD advisory byte-range locking for vnode-backed files, covering POSIX `fcntl` locks and BSD `flock`-style locks. Locks are stored as sorted `struct lockf` ranges hanging from a per-vnode head pointer, while a single global `lockf_lock` serializes lock-list mutation and deadlock checks.

Core structures and policy:
- `struct lockf` records lock type, range start/end, owner identity, lock semantics flags, list linkage, wait queues, condition variable, and cached `uidinfo`.
- `lf_next` is dual-purpose: for granted locks it links the vnode lock list; for blocked locks it points at the blocking lock whose `lf_blkhd` contains the waiter.
- EOF-extended locks use `lf_end == -1`.
- Lock allocation is charged to the effective uid through `ui_lockcnt`; non-root users are capped by `MAXLOCKSPERUID`, with special allowance for unlock-time splitting.
- The implementation intentionally uses a coarse global mutex; comments note that more parallelism would only matter under heavy byte-range lock contention.

Range matching and mutation:
- `lf_findoverlap()` walks sorted ranges and classifies six overlap cases: none, equal, existing contains requested, requested contains existing, existing starts before, or existing ends after.
- `lf_split()` splits an existing lock around a contained new/unlock range, consuming a preallocated spare lock when three pieces are required.
- `lf_clearlock()` removes or shrinks owned locks for `F_UNLCK`, waking waiters on affected ranges.
- `lf_wakelock()` drains a blocking queue, clears each waiter’s blocking pointer, and broadcasts its condition variable.
- `lf_getblock()` returns the first conflicting lock owned by another id, with shared/read locks allowed to coexist.

Lock acquisition behavior:
- `lf_setlock()` first checks for conflicting locks. Nonblocking requests fail with `EAGAIN`.
- Waiting POSIX locks perform bounded deadlock detection by following single-LWP process wait channels through lock wait chains, returning `EDEADLK` on cycles or excessive depth.
- Waiting `flock` exclusive locks first drop any shared locks held by the same owner to match flock upgrade semantics.
- Waiters sleep with `cv_wait_sig()` and clean themselves from block queues if interrupted.
- Once unblocked, the new lock is merged with, replaces, splits, or removes overlapping same-owner locks depending on overlap case and type changes.

External interface:
- `lf_advlock()` converts `struct flock` `whence/start/len` fields into normalized inclusive ranges, including `SEEK_END`, zero-length-to-EOF, and negative-length `lockf()` ranges.
- It preallocates the main lock and any needed spare lock before taking `lockf_lock`.
- Supports `F_SETLK`, `F_UNLCK`, and `F_GETLK`.
- `lf_getlock()` fills a `struct flock` with the blocking lock’s type, range, and pid, or returns `F_UNLCK` if no blocker exists.
- `lf_init()` initializes the subsystem mutex.

Risks and notes:
- Correctness depends on strict global-lock discipline around all lock-list and wait-queue operations.
- The owner API is still `void *`; comments note it should ideally expose POSIX owners as `struct proc *`.
- Deadlock detection is conservative and bounded; it skips multi-LWP processes and non-POSIX locks.
- Range arithmetic is overflow-checked in `lf_advlock()`, but EOF and negative-length cases remain subtle.
- Unlock operations may allocate even beyond the normal user cap so that range splitting can complete.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_lockf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_lookup.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_lookup.c

Read completely: 2349 lines.

Implements NetBSD pathname lookup: path buffer management, `namei()`, namecache fast-forwarding, mount traversal, symlink handling, emulation-root retry, NFS server lookup variants, `relookup()`, and simple lookup wrappers.

Path and helper infrastructure:
- `symlink_magic()` expands optional magic symlink tokens such as machine, hostname, OS release, emulation name, domain, uid/gid, and real uid/gid.
- `namei_hash()` computes namecache-compatible hashes while optionally finding the next path separator.
- `struct pathbuf` owns a pathname buffer and an optional saved copy of the original string.
- `pathbuf_create()`, `pathbuf_copyin()`, `pathbuf_maybe_copyin()`, `pathbuf_assimilate()`, and `pathbuf_destroy()` centralize pathname buffer ownership.
- `pathbuf_stringcopy_get/put()` support retry paths where lookup mutates the active path buffer.

Namei state and startup:
- `struct namei_state` wraps `nameidata`, component state, cache policy, readonly state, slash count, retry state, and root-reference bookkeeping.
- `namei_getstartdir()` chooses the start vnode from absolute root, current directory, `at` directory, chroot root, or emulation root.
- It references root and emulation root during lookup so concurrent `chroot` changes cannot invalidate them.
- `namei_getstartdir_for_nfsd()` provides a reduced start-directory path for NFS server callers.
- `namei_start()` validates nonempty paths, computes path length, obtains the start directory, rejects non-directory starts, and emits ktrace records for normal lookups.

Component lookup flow:
- `lookup_parsepath()` delegates component parsing to `VOP_PARSEPATH()`, updates `ni_next`, tracks trailing slashes, sets `REQUIREDIR`, `ISLASTCN`, `MAKEENTRY`, and `ISDOTDOT`.
- `lookup_lktype()` chooses shared vs exclusive directory locks based on filesystem shared-lookup support and whether the operation can modify the directory.
- `lookup_once()` handles one filesystem lookup, including `..` chroot containment, mountpoint-up traversal, VOP lookup, `ENOLCK` retry with exclusive lock, union mount fallback, creation via `EJUSTRETURN`, and parent locking.
- `lookup_crossmount()` descends through mounted-on directories using mount-root cache entries when possible and `VFS_ROOT()` under filesystem transaction protection otherwise.
- `lookup_fastforward()` uses namecache node locks to traverse easy cached components without repeated vnode references or locks, rolling back to filesystem lookup when unsupported.

Symlink and full-path behavior:
- `namei_follow()` enforces `MAXSYMLINKS`, optionally checks `VEXEC` on symlinks under `MNT_SYMPERM`, reads the link target, performs magic substitution when enabled, splices remaining path text, and restarts from root or emulation root for absolute links.
- `namei_oneroot()` drives the full loop: fast-forward/cache lookup, fallback lookup, mount crossing, symlink following, required-directory checks, final parent/leaf lock handling, readonly operation checks, and emulation-root normalization.
- It handles `NONEXCLHACK` for open-with-create-but-not-exclusive cases that should tolerate missing parent vnode returns across mountpoints.
- `namei_tryemulroot()` retries from the real root when an emulation-root lookup fails in retry-eligible cases.

External entry points:
- `namei()` is the main public interface.
- `lookup_for_nfsd()` supports NFS server lookups with forced current directory, optional no-follow behavior, and magic symlink inhibition.
- `lookup_for_nfsd_index()` performs a constrained single-component WebNFS index lookup.
- `relookup()` reacquires a previously parsed final component under a locked parent directory.
- `namei_simple_*()` and `nameiat_simple_*()` provide simple kernel/user pathname-to-vnode wrappers with follow/no-follow and emulation-root flags.

Risks and notes:
- This file is highly sensitive to vnode reference, lock, and mount transaction ordering; several comments call out deliberately awkward cases.
- `searchdir` can intentionally become `NULL` after crossing mountpoints, so callers must honor the documented parent-return contract.
- Namecache fast-forwarding is performance-critical but must roll back precisely when references cannot be acquired.
- Magic symlinks expose kernel/process-derived strings inside pathname resolution and are gated by `vfs_magiclinks`.
- Emulation-root retry mutates and restores the path buffer, making saved-path lifetime important.
- NFS server lookup interfaces are special-case compatibility paths and are explicitly marked as candidates for interface cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_mount.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_mount.c

Read completely: 1729 lines.

Implements mount structure allocation, reference/busy management, mount list iteration, vnode iteration by mount, vnode flushing, mount and unmount orchestration, root filesystem mounting, per-mount specific data, and mounted-device checks.

Global mount state:
- Defines `rootvnode`, the global mount list, mount-list lock, VFS list lock, mount-specific data domain, mount id lock, and generation counter.
- `vfs_mount_sysinit()` initializes mount list infrastructure and mount-specific data support.
- `vfs_mountalloc()` allocates and initializes `struct mount`, mutex objects, vnode list, lower-level transaction state, specific data, and generation number.
- `vfs_rootmountalloc()` finds a filesystem type, allocates a root mount, marks it read-only initially, fills root mount names, and busies the mount.

Reference and busy lifecycle:
- `vfs_getnewfsid()` builds a unique fsid from filesystem type and a mount counter, checking existing mounts directly under `mountlist_lock`.
- `vfs_getvfs()` locates a mount by fsid using the iterator; a comment notes it should add a reference.
- `vfs_ref()` and `vfs_rele()` manage atomic mount references; final release tears down specific data, mutexes, vfsops reference, and filesystem transaction state.
- `vfs_busy()`/`vfs_trybusy()` start filesystem transactions, reject gone mounts, and take an extra mount reference.
- `vfs_unbusy()` ends the transaction and drops that reference.
- `vfs_set_lowermount()` swaps stacked/lower mount references, rejecting the dead root mount and using busy/ref protection.

Vnode list and flushing:
- `vfs_vnode_iterator_init/destroy/next()` implement marker-based iteration over a mount’s vnode list, avoiding unstable traversal while vnodes are reclaimed.
- `vfs_insmntque()` moves a vnode between mount vnode lists and donates/releases mount references accordingly.
- `vflush()` repeatedly walks vnodes, flushes deferred releases, and calls `vflush_one()` until busy vnodes are gone or retries are exhausted.
- `vflush_one()` skips selected/system vnodes, handles `WRITECLOSE` filtering, fsync/getattr checks, tries recycling, and forcibly kills or anonymizes vnodes under `FORCECLOSE`.

Mount path:
- `mount_domount()` authorizes a new mount, rejects non-directory mount points and unsupported exported-new-mount flags, allocates a mount, calls `VFS_MOUNT()`, suspends the new filesystem, validates the mount point path with `namei()`, invalidates buffers on the covered vnode, appends the mount to the global list, adds it to the syncer when appropriate, links `v_mountedhere`, updates process cwd/root references through `mount_checkdirs()`, runs `VFS_STATVFS()` and `VFS_START()`, and optionally starts extended attributes.
- Error cleanup force-unmounts a freshly mounted filesystem, resumes if needed, clears lower mount state, and releases the mount.

Unmount and shutdown:
- `dounmount()` checks veriexec, suspends the filesystem if needed, marks unmount in progress, clears async writes temporarily, purges namecache entries, removes syncer state, syncs unless forced/read-only, calls `VFS_UNMOUNT()`, marks `IMNT_GONE`, detaches the covered vnode, resumes, removes the mount list entry, asserts no dangling vnodes, calls unmount hooks, clears lower mount, and releases mount/covered vnode references.
- `vfs_unmount_next()` chooses mounts by descending generation to unmount newer/stacked filesystems first.
- `vfs_unmount_forceone()` and `vfs_unmountall1()` provide forced and full unmount passes.
- `vfs_sync_all()` suspends scheduling, performs sync, and waits for the syncer before shutdown.
- `vfs_shutdown()` syncs and unmounts unless the kernel has panicked.

Root mounting and utilities:
- `vfs_mountroot()` validates the root device class, opens disk root devices, honors a configured root filesystem type or tries all registered root-capable filesystems, marks the root mount, obtains `/`, initializes process cwd state, and enables module loading from VFS.
- Mount-specific data helpers wrap the `specificdata` API.
- `vfs_mountedon()` and `rawdev_mounted()` detect mounted block devices or corresponding raw character devices.
- `makefstype()` derives a compact numeric filesystem type from a name.
- Mount-list iterators use marker entries and busy mounts while yielding them to callers.
- `_mountlist_next()` is an unlocked DDB-only traversal helper.

Risks and notes:
- The file’s correctness depends on disciplined ownership of mount references, busy counts, filesystem transactions, and vnode references.
- `vfs_getvfs()` is documented as lacking a mount reference, so consumers must be careful about lifetime.
- Unmount failure paths restore async and syncer state and may restart extattrs, which is easy to regress.
- Successful unmount panics on dangling vnodes, making filesystem reclaim behavior part of the contract.
- `rawdev_mounted()` has an explicit limitation: it checks a specific slice, not all slices on the same disk.
- Marker-based mount and vnode iterators are central to avoiding list corruption during concurrent mutation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_quotactl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_quotactl.c

Read completely: 194 lines.

Provides typed helper wrappers for the NetBSD quota-control VFS operation. Each function initializes a local `struct quotactl_args`, sets a specific `QUOTACTL_*` opcode, fills the relevant union fields, and dispatches through `VFS_QUOTACTL()`.

Covered operations:
- `vfs_quotactl_stat()` requests filesystem-wide quota status.
- `vfs_quotactl_idtypestat()` requests status for a quota id type.
- `vfs_quotactl_objtypestat()` requests status for a quota object type.
- `vfs_quotactl_get()` retrieves a quota value for a key.
- `vfs_quotactl_put()` writes a quota value for a key.
- `vfs_quotactl_del()` deletes quota data for a key.
- `vfs_quotactl_cursoropen()` and `vfs_quotactl_cursorclose()` manage quota iteration cursors.
- `vfs_quotactl_cursorskipidtype()`, `vfs_quotactl_cursorget()`, `vfs_quotactl_cursoratend()`, and `vfs_quotactl_cursorrewind()` wrap cursor traversal.
- `vfs_quotactl_quotaon()` and `vfs_quotactl_quotaoff()` enable or disable quotas by id type.

Risks and notes:
- This file performs no validation of ids, object types, paths, cursors, or buffers; validation is delegated to the filesystem `vfs_quotactl` implementation.
- All wrappers depend on the `struct quotactl_args` union layout matching each opcode exactly.
- Callers must provide correctly owned kernel pointers; these routines do not copy user memory.
- Locking and MPSAFE behavior are inherited from the `VFS_QUOTACTL()` wrapper in `vfs_subr.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_quotactl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_subr.c

Read completely: 1856 lines.

Provides shared VFS support routines: vnode/buffer initialization, buffer invalidation and flushing, device vnode helpers, buffer-vnode association, syncer work queues, VFS sysctls, vnode diagnostics, statvfs helpers, timestamp/access-mode helpers, VFS operation wrappers, and DDB/debug printing.

Initialization and buffer/vnode helpers:
- `vntblinit()` initializes the syncer, mount subsystem, and vnode subsystem.
- `vinvalbuf()` flushes pages, optionally fsyncs, and invalidates all clean and dirty buffers for a locked vnode.
- `vtruncbuf()` frees pages and invalidates buffers at or beyond a logical block number.
- `vflushbuf()` pushes dirty pages and buffers, optionally waiting for output completion.
- `bdevvp()` and `cdevvp()` create deadfs-backed block or character device vnodes.
- `bgetvp()` attaches a busy buffer to a held vnode and places it on the clean buffer list.
- `brelvp()` detaches a buffer, updates syncer membership when no dirty buffers remain, and releases the vnode hold.
- `reassignbuf()` moves a buffer between clean and dirty vnode lists and schedules dirty vnodes on the syncer with file, directory, or metadata delay.
- `vfinddev()` and `vdevgone()` locate or revoke special-device vnodes.

Syncer subsystem:
- Defines delayed sync queues with `SYNCER_MAXDELAY`, per-vnode `VI_ONWORKLST`, and per-mount `IMNT_ONWORKLIST`.
- `vn_initialize_syncerd()` allocates sync queues, initializes the syncer lock, and installs `vfs.sync.*` sysctls.
- `vn_syncer_add_to_worklist()` and `vn_syncer_remove_from_worklist()` manage vnode sync work items.
- `vfs_syncer_add_to_worklist()` scatters mount sync slots to avoid all mounts syncing at once.
- `vfs_syncer_remove_from_worklist()` removes mount sync participation.
- `sched_sync()` is the syncer daemon: it lazily syncs eligible mounts with `VFS_SYNC(MNT_LAZY)`, processes expired vnode work items, tries nonblocking vnode references and locks, reschedules failures quickly, and paces work roughly once per second.
- SDT probes instrument syncer queue changes and sync attempts.

Sysctl and introspection:
- `sysctl_vfs_generic_fstypes()` returns registered filesystem type names.
- `sysctl_kern_vnode()` exports vnode pointer/value snapshots across all mounts.
- `vattr_null()` initializes `struct vattr` fields to `VNOVAL`.
- `vstate_name()`, `vprint_common()`, and `vprint()` format vnode state for diagnostics.
- DDB/debug helpers print buffers, vnodes, vnode locks, mounts, all mounts, and locked vnodes.

VFS metadata helpers:
- `vfs_getopsbyname()` looks up a registered filesystem operations table and increments its refcount.
- `copy_statvfs_info()` copies stable/statistical mount information into a `statvfs`.
- `set_statvfs_info()` fills mount-on and mount-from names from user or kernel strings, including chroot-relative mount path handling.
- `vfs_timestamp()` produces timestamps at configurable precision: seconds, HZ, microseconds, or nanoseconds.
- `vfs_unixify_accmode()` reduces rich access-mode bits to Unix-style checks, rejecting delete permissions that cannot be represented by mode/POSIX.1e ACLs.
- `setrootfstime()` records known root filesystem time.
- `vtype2dt()` maps vnode types to directory-entry `d_type` values.

VFS operation wrappers:
- `VFS_MOUNT()`, `VFS_START()`, `VFS_UNMOUNT()`, `VFS_ROOT()`, `VFS_QUOTACTL()`, `VFS_STATVFS()`, `VFS_SYNC()`, `VFS_FHTOVP()`, `VFS_VPTOFH()`, `VFS_SNAPSHOT()`, and `VFS_SUSPENDCTL()` call filesystem operations while taking the big kernel lock for non-MPSAFE mounts/vnodes.
- `VFS_MOUNT()` snapshots the MPSAFE state on entry because a mount operation may set `IMNT_MPSAFE`.
- `VFS_EXTATTRCTL()` unconditionally takes the kernel lock, with comments marking this as an SMP audit area.

Risks and notes:
- Buffer flushing depends on vnode locks, UVM object locks, `bufcache_lock`, and busy-buffer retry semantics; ordering mistakes can deadlock or lose delayed writes.
- Syncer membership uses vnode and mount flags plus separate queue locks; stale flags or missed removals can leave invalid queue state.
- `sched_sync()` accepts that vnodes can be recycled while syncing and rechecks queue heads accordingly.
- `sysctl_kern_vnode()` copies live vnode snapshots, useful for diagnostics but inherently race-sensitive.
- VFS wrappers assume operation vectors are valid for the mounted filesystem and encode legacy big-kernel-lock compatibility.
- `vfs_unixify_accmode()` intentionally collapses richer ACL semantics; callers must handle unsupported permissions separately.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_subr.c -->