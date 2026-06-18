# Group Research: group_437_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_vfs_extattr_c_source_cd68722721ee

Scope: `Docs/research_subset_a.md`, FreeBSD VFS kernel sources under `sources/os/bsd/freebsd-src/sys/kern`.

Files read completely:
- `sources/os/bsd/freebsd-src/sys/kern/vfs_extattr.c`
- `sources/os/bsd/freebsd-src/sys/kern/vfs_hash.c`
- `sources/os/bsd/freebsd-src/sys/kern/vfs_init.c`
- `sources/os/bsd/freebsd-src/sys/kern/vfs_inotify.c`
- `sources/os/bsd/freebsd-src/sys/kern/vfs_lookup.c`
- `sources/os/bsd/freebsd-src/sys/kern/vfs_mount.c`
- `sources/os/bsd/freebsd-src/sys/kern/vfs_mountroot.c`

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_extattr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_extattr.c

## Role

Implements the FreeBSD extended-attribute syscall layer for VFS objects. It translates fd/path/link-oriented extattr syscalls into vnode operations (`VOP_SETEXTATTR`, `VOP_GETEXTATTR`, `VOP_DELETEEXTATTR`, `VOP_LISTEXTATTR`) and provides `extattrctl(2)` plumbing to the filesystem `VFS_EXTATTRCTL` method.

## Main Entry Points

- `sys_extattrctl()` resolves a target mount from `path`, optionally resolves and locks a backing `filename` vnode, starts a write section, and invokes `VFS_EXTATTRCTL()`.
- `sys_extattr_set_fd()`, `sys_extattr_get_fd()`, `sys_extattr_delete_fd()`, `sys_extattr_list_fd()` copy or construct arguments and dispatch to `kern_extattr_*_fd()`.
- `sys_extattr_set_file/link()`, `sys_extattr_get_file/link()`, `sys_extattr_delete_file/link()`, `sys_extattr_list_file/link()` differ mainly by `FOLLOW` vs `NOFOLLOW`.
- `kern_extattr_*_path()` variants accept a pathname segment type and are reusable by in-kernel callers.
- Internal helpers `extattr_set_vp()`, `extattr_get_vp()`, `extattr_delete_vp()`, and `extattr_list_vp()` implement the vnode operation common path.

## Behavior

Set operations validate `nbytes <= IOSIZE_MAX`, acquire write permission through `vn_start_write()`, lock the vnode exclusively, create a single-element userspace `uio`, run MAC checks when enabled, call `VOP_SETEXTATTR()`, and return bytes written through `td_retval[0]`.

Get operations lock the vnode shared. If the user data pointer is non-NULL, they pass a read `uio`; if it is NULL, they request only the attribute size via the `sizep` argument and return that size in `td_retval[0]`.

Delete operations start a write section, lock exclusively, run MAC checks, call `VOP_DELETEEXTATTR()`, and fall back to `VOP_SETEXTATTR(..., NULL, ...)` when delete is not supported by the filesystem.

List operations accept either a caller-supplied `uio` or NULL for size-only queries, lock shared, run MAC list checks, call `VOP_LISTEXTATTR()`, and return bytes listed or required size.

## Security And Capability Model

The fd paths use `getvnode_path()` with Capsicum rights specific to the operation: `CAP_EXTATTR_SET`, `CAP_EXTATTR_GET`, `CAP_EXTATTR_DELETE`, or `CAP_EXTATTR_LIST`. Path variants use `namei()` with audit vnode flags. MAC hooks gate set, get, delete, and list behavior when `MAC` is compiled in.

## Locking And Lifetime

Path lookup returns a referenced vnode; helpers operate on an unlocked vnode reference and handle vnode locking internally. `extattrctl()` carefully balances mount busying, write-start/write-finish, `filename_vp` lock handoff to `VFS_EXTATTRCTL()`, and final `vrele()`.

## Dependencies

This file is a syscall facade over the VFS vnode operation table. It depends on namei lookup, file descriptor capability lookup, audit annotation, MAC policy checks, vnode locking, and filesystem-specific extattr VOP implementations.

## Notes

The file is intentionally repetitive: fd, file path, and link path syscall wrappers share small differences in rights, path following, and argument copying. The actual semantic differences are concentrated in the four vnode helpers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_extattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_hash.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_hash.c

## Role

Provides the global VFS vnode hash table used by filesystems to locate, insert, remove, and rehash vnodes by filesystem-specific hash values. Hash buckets are salted with each mount's `mnt_hashseed`.

## Main Entry Points

- `vfs_hash_index()` computes the salted index value visible to callers.
- `vfs_hash_get()` finds and locks a matching vnode, using an optional comparison callback.
- `vfs_hash_ref()` finds a matching vnode and returns it referenced but not locked.
- `vfs_hash_insert()` inserts a newly created vnode or detects an existing matching vnode and returns that instead.
- `vfs_hash_remove()` removes a vnode from the hash list.
- `vfs_hash_rehash()` moves a vnode to a new hash bucket while the vnode is exclusively locked.
- `vfs_hash_changesize()` rebuilds the hash table when the vnode target count changes.

## Data Structures

`vfs_hash_tbl` is an array of `LIST_HEAD(vfs_hash_head, vnode)` buckets allocated with `hashinit(desiredvnodes, M_VFS_HASH, ...)`. `vfs_hash_side` temporarily holds losing insert candidates that must be `vgone()` after a duplicate is found. `vfs_hash_lock` is a global rwlock.

## Behavior

Lookup walks a salted bucket under a read lock, filters by `v_hash`, `v_mount`, and optional callback, prepares vnode acquisition with `vget_prep()`, then drops the hash lock and finishes with `vget_finish()`. If a waitable acquisition races with reclamation and returns `ENOENT`, it restarts.

Insert takes the write lock, searches for duplicates, and either inserts the new vnode into the correct bucket or abandons it by moving it to the side list, calling `vgone()` and `vput()`, and returning the existing vnode when it can be acquired.

Resize allocates a replacement table before taking the lock, swaps global table pointers under the write lock, relinks all old bucket entries using the new mask and mount salts, then frees the old table.

## Locking And Lifetime

The rwlock protects bucket membership and table replacement. Vnode lifetime during lookup is stabilized through `vget_prep()`/`vget_finish()` or `vhold()` plus `vref()` in `vfs_hash_ref()`. `vfs_hash_rehash()` requires an exclusive vnode lock, enforced by `ASSERT_VOP_ELOCKED()`.

## Dependencies

This is a low-level helper for filesystem inode-to-vnode caches. It relies on mount hash seeds initialized during mount allocation and on vnode lifecycle primitives from the broader VFS.

## Notes

The implementation prioritizes correctness under vnode reclamation races. Duplicate detection is intentionally tied to caller-provided comparison logic so filesystem-specific keys can extend beyond the integer hash.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_init.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_init.c

## Role

Maintains the global filesystem-type registry and module event path for FreeBSD VFS implementations. It also fills default `vfsops` methods and wraps selected filesystem operations with signal-stop deferral for filesystems marked with `VFCF_SBDRY`.

## Main Entry Points

- `vfs_byname()` finds a registered filesystem type by name and increments `vfc_refcount`; it aliases `ffs` to `ufs`.
- `vfs_byname_kld()` tries `vfs_byname()`, attempts `kern_kldload()` on miss, then looks up again and may unload the module if registration failed.
- `vfs_unref_vfsconf()` releases a registry reference.
- `vfs_modevent()` handles `MOD_LOAD` by calling `vfs_register()` and `MOD_UNLOAD` by calling `vfs_unregister()`.

## Registration Flow

`vfs_register()` validates `VFS_VERSION`, prevents duplicate names, assigns `vfc_typenum`, appends to the global `vfsconf` TAILQ, fills missing `vfsops` methods with standard implementations, optionally installs the signal-defer wrapper table, calls filesystem `vfs_init`, registers jail support, and renumbers matching `vfs.<fstype>` sysctl nodes to match the filesystem type number.

When `vfs.typenumhash` is enabled, type numbers are derived from an FNV-1 hash of `vfc_name` and collision-resolved in the 1..255 range where possible. This is meant to keep NFS file handles stable across different module load orders.

`vfs_unregister()` refuses removal when the filesystem is unknown or has outstanding references, calls `vfs_uninit`, removes the entry, and recomputes `maxvfsconf`.

## Signal-Deferral Wrappers

The `vfsops_sigdefer` table wraps mount, unmount, root, cachedroot, quotactl, statfs, sync, vget, fhtovp, checkexp, extattrctl, sysctl, purge, and lock-report operations. Each wrapper calls `sigdeferstop(SIGDEFERSTOP_SILENT)` around the underlying filesystem method and restores stop handling afterward.

## Locking And Lifetime

The registry is protected by `vfsconf_sx`. Reference counts are manipulated while holding this sx lock. Registration and unregistration also coordinate with sysctl locking when modifying filesystem sysctl OIDs.

## Dependencies

This file is central to mount-time lookup in `vfs_mount.c` and root-mount lookup in `vfs_mountroot.c`. It depends on linker KLD loading, prison/jail VFS registration, sysctl internals, and standard VFS fallback methods.

## Notes

The design supports third-party extension of operation vectors by normalizing missing methods at registration time and allows binary-compatible additions through multiple operation-vector descriptors, as described in the file comments.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_inotify.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_inotify.c

## Role

Implements FreeBSD's inotify-compatible descriptor, watch, event queue, and vnode notification integration. It exposes inotify file operations and kernel helpers used by VFS/vnode code to create, remove, and log watches.

## Main Entry Points

- `inotify_create_file()` initializes an inotify descriptor and installs `inotifyfdops`.
- `kern_inotify_add_watch()` validates masks, resolves the watched path, enforces access and watch limits, and delegates to `VOP_INOTIFY_ADD_WATCH()`.
- `vn_inotify_add_watch()` creates or updates a watch on a vnode.
- `kern_inotify_rm_watch()` removes a watch by watch descriptor and queues `IN_IGNORED`.
- `vn_inotify()` converts vnode/directory events into inotify self and parent-directory notifications.
- `inotify_log()` and `inotify_log_one()` enqueue matching events for watchers.
- File operations include `inotify_read()`, `inotify_ioctl()`, `inotify_poll()`, `inotify_kqfilter()`, `inotify_stat()`, `inotify_close()`, and `inotify_fill_kinfo()`.

## Data Structures

`struct inotify_softc` represents one descriptor. It contains a mutex, pending event queue, preallocated overflow record, watch descriptor allocator, byte/event pending counts, RB tree of active watches, list of dead watches waiting for asynchronous `vrele()`, a taskqueue reap task, selinfo/knote state, and held credentials.

`struct inotify_watch` links a descriptor to a watched vnode, with RB-tree linkage by watch descriptor and TAILQ linkage from vnode pollinfo. `struct inotify_record` stores an `inotify_event` plus variable-sized name payload.

## Event Queue Behavior

Reads block unless nonblocking flags are set. They dequeue as many records as fit in the user buffer, requeue the first record and return `EINVAL` if the first event cannot fit, and reuse the per-descriptor overflow record after it is read.

`inotify_queue_record()` coalesces duplicate tail events when enabled, enforces `max_queued_events`, converts queue or allocation failures to `IN_Q_OVERFLOW`, updates drop counters, and wakes `select`, `poll`, `kqueue`, and blocking readers.

## Watch Behavior

Adding a directory watch first populates name-cache state for existing entries so later vnode-only events can be associated with names. Existing watches on the same descriptor/vnode are updated unless `IN_MASK_CREATE` forbids replacement. New watch descriptors avoid reuse as long as possible.

One-shot watches and self-delete/unmount events queue `IN_IGNORED` and remove the watch from the descriptor and vnode. Vnode reference release is deferred to a taskqueue when removal happens from notification context.

## Limits And Tuning

Sysctls control max queued events, max instances per user, max watches per user, max watches system-wide, current watches, event coalescing, and event drop count. Defaults for user and system watch limits are derived from `desiredvnodes`.

## Locking And Lifetime

Descriptor state is serialized by `sc->lock`. Vnode watch lists are protected by `vp->v_pollinfo->vpi_lock`. The code carefully orders these locks when adding, logging, removing, and closing watches. Watch counts are tracked both globally and per real UID.

## Dependencies

This file depends on vnode pollinfo, name cache support (`cache_vop_inotify()`), VOP hooks (`VOP_INOTIFY_ADD_WATCH`, `VOP_GETATTR`, `VOP_ACCESS`), Capsicum rights for inotify operations, taskqueue cleanup, kqueue/select/poll integration, and resource counters.

## Notes

The implementation is compatibility-oriented: removed-watch events do not purge already queued events, watch descriptors are not aggressively reused, and overflow handling uses Linux-style `IN_Q_OVERFLOW`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_inotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_lookup.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_lookup.c

## Role

Implements FreeBSD pathname resolution: `namei()`, locked fallback lookup, capability-mode path restrictions, symlink expansion, mount crossing, union fallback, and relookup of final components for filesystem operations.

## Main Entry Points

- `namei()` is the public pathname-to-vnode resolver.
- `vfs_lookup()` performs the locked component-by-component lookup after fast path cache lookup aborts or partially completes.
- `vfs_relookup()` reacquires a final component from a parent directory after a caller has temporarily dropped locks.
- `vfs_lookup_nameidata()` recovers the enclosing `nameidata` from a component name when appropriate.
- `vfs_lookup_isroot()` tests whether `..` would cross a process, jail, chroot, or global root boundary.

## Initialization

`nameiinit()` creates the `NAMEI` UMA zone, registers a special `crossmp` vnode operation vector, allocates the `vp_crossmp` placeholder vnode, and marks it with `VIRF_CROSSMP`. The placeholder is used during mount traversal to represent a synthetic parent when crossing mount points.

## Namei Flow

`namei()` validates debug state and flags, copies in the pathname, records tracing/audit data, then first attempts `cache_fplookup()`. If the fast path handles the request, it returns directly. Otherwise it sets up a starting directory from an explicit start vnode, `AT_FDCWD`, fd-relative lookup, or root, then loops through `vfs_lookup()` and symlink expansion until a final vnode is returned or an error occurs.

Absolute symlinks preserve ABI root during the first pass and switch to native root only after a restarted lookup. Empty paths are handled specially only when `EMPTYPATH` is set.

## Locked Lookup Flow

`vfs_lookup()` trims trailing slashes, locks the starting directory, parses one component at a time, handles `.`/`..` special cases, checks MAC lookup policy, calls `VOP_LOOKUP()`, follows mount points through `vfs_lookup_cross_mount()`, handles symlink detection, enforces read-only restrictions for modifying operations, and returns parent/leaf locks according to `LOCKPARENT`, `WANTPARENT`, `LOCKLEAF`, and `LOCKSHARED`.

It supports `ERELOOKUP` by retrying the same component, `EJUSTRETURN` for create/rename cases where the leaf does not exist, and union mounts by retrying lookup on the covered vnode when a root vnode lookup misses.

## Capability And Boundary Enforcement

Capability mode and `RBENEATH` set strict-relative lookup state. The code rejects absolute lookups, `AT_FDCWD` in capability mode, disallowed `..`, and attempts to escape the starting directory. When dotdot traversal is permitted, `nameicap_tracker_add()` records mount rename locks so concurrent renames cannot move a traversed directory out from under the lookup.

`lookup_cap_dotdot` and `lookup_cap_dotdot_nonlocal` sysctls tune dotdot handling and non-local filesystem behavior. Ktrace capability violations are recorded through `NI_CAP_VIOLATION()`.

## Locking Details

The lookup path dynamically chooses shared or exclusive locks. `enforce_lkflags()` upgrades shared locks when a mount lacks `MNTK_LOOKUP_SHARED`; `needs_exclusive_leaf()` chooses exclusive leaf locking for operations that require it. Cross-mount traversal handles special `VV_CROSSLOCK` recursion rules and uses `vfs_busy()` around `VFS_ROOT()`.

## Dependencies

This is one of the central consumers of name cache, vnode locks, mount references, MAC checks, audit hooks, Capsicum state, prison roots, process working directories, and filesystem `VOP_LOOKUP` and `VOP_READLINK` methods.

## Notes

Most complexity comes from preserving legacy VFS lock contracts while supporting fast path lookup, capability restrictions, ABI roots, shared lookup locks, forced unmount races, and mount traversal.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_mount.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_mount.c

## Role

Implements the general mount and unmount subsystem: user-facing `nmount(2)` and legacy `mount(2)`, kernel mount argument construction, mount option parsing and sanitization, mount structure allocation/destruction, update/remount handling, unmount and deferred recursive unmount, mount reference accounting, and mount event notification.

## Main Entry Points

- `sys_nmount()` validates iovec count, filters `MNT_ROOTFS`, builds a `uio`, and calls `vfs_donmount()`.
- `sys_mount()` implements the older API by building mount arguments and calling filesystem `vfs_cmount`.
- `vfs_donmount()` parses and sanitizes option vectors, derives mount flags, handles export-only jail updates, optional auto-readonly retry, and dispatches to `vfs_domount()`.
- `vfs_domount()` resolves the mount path and chooses first mount vs update.
- `vfs_domount_first()` performs a new mount over a vnode.
- `vfs_domount_update()` updates flags, options, exports, and read/write state on an existing mount.
- `sys_unmount()` and `kern_unmount()` resolve target mount and call `dounmount()`.
- `dounmount()` performs the actual unmount and destruction sequence.
- `kernel_mount()` supports in-kernel mounts using accumulated `struct mntarg` arguments.

## Mount Option Handling

`vfs_buildopts()` copies name/value iovec pairs into a `vfsoptlist`, enforces `VFS_MOUNTARG_SIZE_MAX`, requires NUL-terminated option names, and sanitizes duplicates. `vfs_sanitizeopts()` keeps the last occurrence, with special equivalence for `no` prefixes and read-only/read-write aliases.

`vfs_donmount()` recognizes global options such as `update`, `force`, `reload`, `async`, `noatime`, `noexec`, `nosuid`, `nosymfollow`, `ro`, `rw`, `autoro`, `union`, `export`, `automounted`, `nocover`, and `emptydir`. It also keeps `errmsg` copyout behavior aligned with the original option position.

Public helpers include `vfs_filteropt()`, `vfs_getopt()`, `vfs_getopts()`, `vfs_getopt_pos()`, `vfs_getopt_size()`, `vfs_flagopt()`, `vfs_scanopt()`, `vfs_setopt()`, `vfs_setopt_part()`, `vfs_setopts()`, and `vfs_copyopt()`.

## Mount Lifecycle

`vfs_mount_alloc()` initializes a UMA-allocated `struct mount`, vfs operations, statfs identity, mount credential, hash seed, upper-mount lists, and MAC label state. `vfs_domount_first()` validates permissions and covered vnode suitability, marks `VI_MOUNT`, calls `VFS_MOUNT()`, `VFS_STATFS()`, and `VFS_ROOT()`, installs `VIRF_MOUNTPOINT` and `v_mountedhere`, inserts the mount into `mountlist`, fires mount event handlers/devctl, updates process directories, and allocates a sync vnode for writable mounts.

`vfs_domount_update()` requires a root vnode, checks privilege or jail export rules, busies the mount, sets update flags, merges options, optionally calls `VFS_MOUNT()`, processes export structures across old and current ABI layouts, restores flags on failure, updates statfs/options, and toggles the sync vnode for read/write transitions.

`vfs_mount_destroy()` drains references, verifies no dangling vnodes or upper registrations remain, releases covered vnode, options, export state, vfsconf reference, MAC state, credentials, and returns the structure to the UMA zone.

## Unmount Lifecycle

`kern_unmount()` supports lookup by FSID or path, rejects recursive/deferred flags from userspace, checks privilege and MAC policy, refuses root unmount, and calls `dounmount()`.

`dounmount()` supports forced and recursive unmount. Recursive forced unmounts enqueue upper mounts through the deferred taskqueue and wait for uppers to drain when needed. The main unmount sequence locks the covered vnode, enters the VFS operation barrier, starts a write drain, marks `MNTK_UNMOUNT`, clears cached root, optionally checks use counts, purges on force, drains lock refs, flushes with `vfs_periodic()`, deallocates the sync vnode, calls `VFS_UNMOUNT()`, removes the mount from `mountlist`, clears mountpoint state, fires unmount notifications, handles root globals, and destroys the mount.

Deferred unmount state is controlled by sysctls under `vfs.deferred_unmount`, with retry limit, retry delay, and total retry counters.

## Reference And Operation Accounting

`vfs_ref_from_vp()`, `vfs_ref()`, and `vfs_rel()` use per-CPU mount counters when safe and fall back to the mount interlock otherwise. `vfs_op_enter()` drains per-CPU counters into stable mount counters and establishes a barrier for operations that need stable accounting. Diagnostic helpers can assert and dump counter state.

Upper/lower stacked mount relationships are managed by `vfs_register_upper_from_vp()`, `vfs_register_for_notification()`, `vfs_unregister_for_notification()`, and `vfs_unregister_upper()`.

## Kernel Mount Argument API

`mount_arg()`, `mount_argf()`, `mount_argsu()`, and `mount_argb()` accumulate iovec name/value pairs in `struct mntarg`; `kernel_mount()` converts them into a sysspace `uio`, calls `vfs_donmount()`, and frees all allocations.

## Additional Utilities

`__vfs_statfs()` normalizes statfs fields before calling the filesystem method. `vfs_mountedfrom()` sets `f_mntfromname`. `mount_devctl_event()` publishes mount/remount/unmount events. `vfs_remount_ro()` force-remounts a busied mount read-only. `suspend_all_fs()` and `resume_all_fs()` suspend/resume writable local filesystems, and `vfs_exjail_clone()` clones export jail credentials.

## Dependencies

This file ties together namei lookup, filesystem registration, vnode mountpoint flags, syncer vnode management, MAC hooks, jail/prison policy, NFS export structures, GEOM-root interactions through callers, taskqueues, event handlers, devctl, per-CPU counters, and filesystem `VFS_*` operations.

## Notes

This is the main policy and lifecycle center for FreeBSD mount state. Its correctness depends on strict lock ordering around covered vnodes, mount interlocks, operation barriers, and option ownership transfer between caller lists and `mp->mnt_opt`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_mountroot.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_mountroot.c

## Role

Implements root filesystem mounting during boot and reroot-style root replacement. It builds the root mount configuration, mounts temporary or persistent devfs, parses boot directives, waits for root devices, mounts candidate root filesystems, shuffles the mount list so the selected root becomes `/`, and finalizes global root state.

## Main Entry Points

- `root_mount_hold()`, `root_mount_hold_token()`, and `root_mount_rel()` let subsystems delay root mounting until devices or prerequisites are ready.
- `root_mounted()` reports completion.
- `vfs_mountroot()` is the top-level boot root mount sequence.
- Internal helpers mount devfs, parse configuration, mount candidates, read `/.mount.conf`, wait for devices, and shuffle root/devfs mounts.

## Root Hold Mechanism

Root holds are stored in a TAILQ protected by `root_holds_mtx`. Holds are visible through `vfs.root_mount_hold`. `vfs_mountroot_wait()` waits for GEOM idleness and an empty hold list, printing waiting tokens at a rate-limited cadence.

`root_mount_timeout` defaults to 3 seconds and is tunable via `vfs.mountroot.timeout`. `vfs.root_mount_always_wait` can force waiting even when the target device already exists.

## Devfs And Root Shuffle

`vfs_mountroot_devfs()` either reuses an existing `rootdevmp` or allocates/mounts a devfs mount at `/dev`, inserts it at the head of `mountlist`, sets `rootvnode`, and creates a temporary `/dev -> /` symlink.

`vfs_mountroot_shuffle()` rearranges `mountlist` so the newly mounted root is first and devfs is placed under `/dev`. It clears old mountpoint state, updates `rootvnode`, remounts the previous root under `/.mount` or `/mnt` when possible, repairs devfs coverage, purges name caches, and removes the temporary `/dev/dev` symlink when devfs was the old root.

## Configuration Parser

The parser consumes a line-oriented mountroot language. Mount entries use `fstype:device [options]`. Directives include:

- `.ask` for interactive manual root selection.
- `.md <path>` to attach a vnode-backed md device for root mounting.
- `.onfail continue|panic|reboot|retry` to set failure policy.
- `.timeout <seconds>` to change retry timeout.

`vfs_mountroot_conf0()` seeds the configuration from boot flags, `ROOTDEVNAME`, `RB_CDROM`, loader variables `vfs.root.mountfrom` and `vfs.root.mountfrom.options`, and `rootdevnames[]`, with `.ask` as a fallback when not already requested.

## Mount Attempt Flow

`parse_mount()` splits `fstype:device`, substitutes `md#` when an md unit was attached, parses optional comma-separated options, validates filesystem availability, waits for the root device when needed, builds kernel mount arguments (`fstype`, `/`, `from`, `errmsg`, `ro`, options), and calls `kernel_mount(..., MNT_ROOTFS)`. Failed attempts are retried for `root_mount_timeout` except for selected terminal errors.

`vfs_mountroot_parse()` walks the configuration until a new root mount appears after devfs in `mountlist`, then applies the configured on-failure action.

After a successful first root mount and shuffle, `vfs_mountroot()` attempts to read `/.mount.conf` from the mounted root and parse it as another configuration, allowing boot media to redirect to the final root.

## Device Waiting

`vfs_mountroot_wait_if_neccessary()` waits unconditionally for ZFS, NFS-like filesystems, p9fs, empty device strings, or forced wait mode. For ordinary device paths it first checks whether the path exists, waits for root holds and GEOM idleness, then polls until timeout.

## Finalization

`vfs_mountroot()` computes the largest mount timestamp for `inittodr()`, updates prison0's root vnode, marks `root_mount_complete` with release semantics, wakes waiters, and invokes the `mountroot` event handler.

## Dependencies

This file depends on the generic mount API in `vfs_mount.c`, filesystem lookup in `vfs_init.c`, pathname lookup, devfs, GEOM device discovery, md device ioctls, kernel file operations, jail/prison root state, name cache purge, and event handlers.

## Notes

The parser is deliberately small and boot-oriented. It tolerates invalid directives by advancing to the next line, supports interactive recovery through `.ask`, and always mounts initial root candidates read-only by ignoring `rw`/`noro` options in `parse_mountroot_options()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_mountroot.c -->