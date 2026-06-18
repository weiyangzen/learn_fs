# Group Research: group_319_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_autofs_autofs_vnops_92a6976c8bc8

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely and summarized separately below.

Files read completely:
- `sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_vnops.c` (603 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/deadfs/dead_vnops.c` (211 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_core.c` (3046 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_helper.c` (235 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_rules.c` (486 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vfsops.c` (284 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vnops.c` (2309 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs.h` (283 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_subr.c` (893 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vfsops.c` (359 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vnops.c` (1587 lines)
- `sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/Makefile` (8 lines)

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_vnops.c

Read completely: 603 lines.

## Role

This file implements the vnode operations and in-memory node helpers for DragonFlyBSD autofs directories. Autofs exposes synthetic directories that can trigger automountd-driven mounts when looked up or read. It also manages the autofs node tree and maps each `autofs_node` to a directory vnode on demand.

## Main Responsibilities

- Detect whether an autofs vnode has been covered by a real filesystem root with `test_fs_root()` and `nlookup_fs_root()`.
- Trigger automount resolution through `autofs_trigger_vn()` when a directory or child lookup is not cached and the calling thread is not an automountd-descendant thread.
- Implement VOPs:
  - `autofs_access()` permits all access; autofs-specific creation control is handled in mkdir.
  - `autofs_getattr()` synthesizes directory attributes from the autofs node.
  - `autofs_nresolve()` resolves child names from the autofs red-black child tree, or triggers automount first.
  - `autofs_nmkdir()` lets only automountd-descendant threads create synthetic autofs directories.
  - `autofs_readdir()` emits `.`, `..`, and child directory entries, or forwards readdir to a mounted real filesystem if the trigger resolves to a non-autofs root.
  - `autofs_reclaim()` disconnects a vnode from its autofs node without freeing the node.
  - `autofs_mountctl()` currently delegates to `vop_stdmountctl()`.
  - `autofs_print()` emits node diagnostics.
- Provide node lifecycle helpers:
  - `autofs_node_new()`
  - `autofs_node_find()`
  - `autofs_node_delete()`
  - `autofs_node_vn()`
- Define `autofs_vnode_vops`, the vnode operation table used by autofs.

## Synchronization and Lifetime Model

- Mount/node tree operations use `amp->am_lock`; child lookup requires the mount lock, and node creation/deletion require it exclusively.
- Each node has `an_vnode_lock` to serialize `an_vnode` association changes.
- `autofs_node_vn()` retries around `vget()` races and uses `vhold()`/`vdrop()` to stabilize an existing vnode.
- `autofs_reclaim()` clears `anp->an_vnode` and `vp->v_data`; node memory is intentionally freed by `autofs_node_delete()`, not by reclaim.
- Triggering releases the namecache lock around automount activity, then relocks and may return `ESTALE` when a real filesystem was mounted over the autofs node.

## Important Interactions

- Calls into generic name lookup with `nlookup_init()`, `nlookup()`, and `nlookup_done()` to verify whether an automount succeeded.
- Calls autofs control-layer functions from `autofs.h`, including `autofs_trigger()`, `autofs_cached()`, `autofs_ignore_thread()`, `autofs_path()`, and `autofs_node_uncache()`.
- Uses the generic VFS directory writer `vop_write_dirent()`.
- Delegates to the mounted filesystem's `VOP_READDIR()` when a trigger resolves to a non-autofs root vnode.

## Research Notes

- The key correctness path is avoiding duplicate automount triggers. `autofs_trigger_vn()` explicitly rechecks for a mounted root before and after calling `autofs_trigger()`.
- `autofs_getattr()` contains a disabled FreeBSD-style mount-on-stat path because DragonFly's current trigger mechanism could hang in `nlookup_fs_root()`.
- Directory offsets are reclen-based and strict: seeking into the middle of a synthetic dirent returns `EINVAL`.
- Security is intentionally narrow: ordinary threads cannot mkdir synthetic autofs nodes, while automountd descendants can build the autofs tree.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/deadfs/dead_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/deadfs/dead_vnops.c

Read completely: 211 lines.

## Role

This file defines DragonFlyBSD's dead vnode operation table. Dead vnodes are vnodes whose backing filesystem object has been revoked, reclaimed, forcibly unmounted, or otherwise made unusable. The operations mostly fail predictably while allowing cleanup paths such as close and inactive/reclaim to complete safely.

## Main Responsibilities

- Define `dead_vnode_vops` and export `dead_vnode_vops_p`.
- Return stable errors for operations on dead vnodes:
  - Access, getattr, setattr, readdir, readlink, pathconf, and advisory locking use `vop_ebadf`.
  - Lookup returns `ENOTDIR`.
  - Open returns `ENXIO`.
  - Read returns EOF for tty vnodes and `EIO` otherwise.
  - Write and bmap return `EIO`.
  - Ioctl returns `ENOTTY`.
- Allow safe cleanup:
  - `dead_close()` succeeds and carefully decrements `v_opencount` and `v_writecount` if they are positive.
  - Inactive and reclaim are no-ops.
- Panic on operations that should never be issued to dead vnodes via `dead_badop()`.
- Provide `dead_print()` diagnostics.

## Synchronization and Lifetime Model

- `dead_close()` upgrades/retries the vnode lock before touching open/write counts.
- The close path deliberately avoids warning or panicking on surprising open-count state because forced unmount or revoke can close the backing object underneath a descriptor.
- `VNODEOP_SET(dead_vnode_vops)` registers the table with the vnode operation framework.

## Important Interactions

- Used by generic vnode reclamation/revocation paths to replace filesystem-specific operations after a vnode is no longer backed by a valid object.
- TTY read behavior supports legacy semantics where reads from a revoked tty can return EOF rather than a hard I/O error.

## Research Notes

- This is defensive infrastructure: its correctness is mostly about returning stable errors and avoiding panics during teardown.
- The only operation with meaningful state mutation is `dead_close()`.
- `dead_badop()` marks old create/link/mkdir/mknod/remove/rename/rmdir/symlink operations as impossible on dead vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/deadfs/dead_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_core.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_core.c

Read completely: 3046 lines.

## Role

This is the core implementation of DragonFlyBSD devfs. It owns global device registration, per-mount devfs topology, devfs node allocation/destruction, alias propagation, clone-handler registration, cdev allocation/reference integration, rule application triggers, devfs message serialization, wildcard matching, and per-file character-device private data.

## Main Responsibilities

- Allocate and free devfs nodes:
  - `devfs_allocp()` creates `Nroot`, `Ndir`, `Nlink`, `Nreg`, or `Ndev` nodes, initializes dirent metadata, permissions, timestamps, parent links, cookies, mount counters, and rules.
  - `devfs_allocv()` maps a devfs node to a DragonFly vnode and attaches character devices through `v_associate_rdev()`.
  - `devfs_freep()` safely tears down vnode association, symlink storage, names, orphan tracking, and final node memory.
  - `devfs_unlinkp()` removes a node from the visible topology and invalidates namecache entries.
- Maintain per-mount topology:
  - `devfs_iterate_topology()` recursively walks the tree.
  - `devfs_gc()` removes nodes, related aliases, and empty generated directories.
  - `devfs_mount_add()` and `devfs_mount_del()` synchronize mount registration/removal with the core thread.
- Maintain global cdev state:
  - `devfs_new_cdev()` allocates and initializes `struct cdev` through `sysref`.
  - `devfs_link_dev()` and `devfs_unlink_dev()` maintain `devfs_dev_list`.
  - `devfs_create_dev()` and `devfs_destroy_dev()` are asynchronous public entry points.
  - `devfs_create_dev_worker()` and `devfs_destroy_dev_worker()` run in the serialized core context.
  - Related-device helpers recursively clear flags or destroy child devices.
- Propagate devices and aliases:
  - `devfs_create_all_dev_worker()` populates a mount with existing devices.
  - `devfs_propagate_dev()` creates or destroys a device node across all devfs mounts.
  - `devfs_make_alias()`, `devfs_destroy_alias()`, and their worker functions maintain `devfs_alias_list`.
  - `devfs_alias_create()` creates `Nlink` nodes pointing at target nodes and increments target link counts.
- Resolve and mutate topology paths:
  - `devfs_resolve_or_create_path()`
  - `devfs_resolve_name_path()`
  - `devfs_create_device_node()`
  - `devfs_destroy_device_node()`
  - `devfs_destroy_node()`
  - `devfs_find_device_node_by_name()`
- Manage clone handlers:
  - `devfs_clone_handler_add()`
  - `devfs_clone_handler_del()`
  - `devfs_clone()` invokes registered clone callbacks outside `devfs_lock`.
- Serialize devfs state through a core message thread:
  - `devfs_msg_core()`
  - `devfs_msg_exec()`
  - `devfs_msg_send()`
  - `devfs_msg_send_sync()`
  - helper send wrappers for names, mounts, ops, handlers, devices, and links.
- Integrate with system facilities:
  - `devfs_config()` waits for pending async devfs work.
  - `devfs_assume_knotes()` takes over device knotes on detach.
  - `devfs_sysctl_devname_helper()` backs `kern.devname` lookup.
  - `devfs_WildCmp()` and `devfs_WildCaseCmp()` implement wildcard matching for rule/name comparisons.
  - `devfs_get_cdevpriv()`, `devfs_set_cdevpriv()`, and `devfs_clear_cdevpriv()` manage per-open file private data.

## Synchronization and Lifetime Model

- `devfs_lock` is the central recursive lock for devfs node, mount, alias, and device-list state.
- `devfs_token` serializes the core message thread.
- Asynchronous public operations post messages to `devfs_msg_port`; synchronous operations wait for replies through `lwkt_domsg()`.
- If a caller is already on the core thread, `devfs_msg_send()` executes directly to avoid self-deadlock.
- Node destruction is interlocked by `DEVFS_DESTROYED`, `DEVFS_NLINKSWAIT`, orphan-list flags, and vnode association checks.
- `devfs_allocv()` and `devfs_freep()` temporarily drop `devfs_lock` around `vget()`/`getnewvnode()`-style vnode operations to avoid deadlocks, then revalidate state.
- `struct cdev` lifetime uses `sysref` plus explicit `reference_dev()`/`release_dev()` references. Device-list membership owns one reference.
- Device-op major IDs are allocated from a clone bitmap and reference-counted in `devfs_dev_ops_list`.

## Important Interactions

- Used by `devfs_vfsops.c` for mount creation, root vnode lookup, mount removal, and file-handle vnode lookup.
- Used by `devfs_vnops.c` for name resolution, vnode allocation, node accessibility checks, cloning, permissions, orphan cleanup, aliases, and cdev private data.
- Used by `devfs_rules.c` for applying hide/show/link/permission rules and resetting rule-created state.
- Sends `udev_event_attach()`/`udev_event_detach()` and `devctl_notify()` events when devices and aliases are created or destroyed.
- Uses VFS helpers such as `v_associate_rdev()`, `v_release_rdev()`, `cache_inval_vp()`, and `vfs_timestamp()`.

## Notable Design Details

- Per-mount devfs trees are regenerated from global `devfs_dev_list` when a mount is added.
- Aliases are implemented as `Nlink` devfs nodes with a `link_target`, not as normal symlink path text unless user-created through vnode operations.
- Lookup of aliases follows up to eight link-target hops to avoid recursion loops.
- PTY devices have special handling: unix98 pty masters and pty-like names can be hidden or invisible until opened.
- Device node names may contain paths; devfs creates intermediate directories on demand.
- `devfs_inode_to_vnode()` walks the topology and allocates a vnode if needed for a matching inode.

## Research Notes

- The highest-risk areas are lock dropping/reacquisition around vnode operations, node destruction while aliases still reference targets, and cdev reference balancing during destroy paths.
- `devfs_destroy_dev_worker()` releases multiple references after unlink and detach; callers must understand which references are owned by device creation, linkage, and the destroy message.
- `devfs_uninit()` sends `DEVFS_TERMINATE_CORE` with a null message even though ordinary send paths expect message storage; this is intentional in context but sensitive to messaging assumptions.
- Wildcard matching allocates temporary backtracking state proportional to the number of `*` wildcards.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_helper.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_helper.c

Read completely: 235 lines.

## Role

This file implements devfs clone bitmap helpers. The bitmap tracks available clone/unit numbers, where a clear bit means allocated and a set bit means free.

## Main Responsibilities

- Initialize and destroy bitmap storage:
  - `devfs_clone_bitmap_init()`
  - `devfs_clone_bitmap_uninit()`
- Grow bitmap storage with `devfs_clone_bitmap_extend()`.
- Find the first free unit with `devfs_clone_bitmap_fff()`.
- Test, allocate, free, and conditionally allocate units:
  - `devfs_clone_bitmap_chk()`
  - `devfs_clone_bitmap_set()`
  - `devfs_clone_bitmap_put()`
  - `devfs_clone_bitmap_get()`

## Synchronization and Lifetime Model

- A file-local recursive `devfs_bitmap_lock` protects structural bitmap integrity.
- Callers using check-then-set flows are still expected to hold their own higher-level lock to prevent semantic races.
- `devfs_clone_bitmap_get()` holds the bitmap lock and then calls `devfs_clone_bitmap_set()`, which is why the lock is recursive.
- `devfs_clone_bitmap_put()` first calls `devfs_config()` so pending devfs messages complete before a unit is made reusable.

## Important Interactions

- `devfs_core.c` uses this through `DEVFS_DEFINE_CLONE_BITMAP(ops_id)` to allocate compact IDs for `dev_ops` major-device encoding.
- Clone devices and device-op IDs rely on this helper not to reuse units before all pending devfs state has drained.

## Research Notes

- The bit representation is inverted relative to the public return values: bit set means free, `devfs_clone_bitmap_chk()` returns true when allocated.
- `devfs_clone_bitmap_get()` treats `unit > limit` as failure; if limits are meant to be inclusive this behavior is deliberate but worth noting.
- Growth adds two chunks when extending, reducing immediate repeat reallocations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_helper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_rules.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_rules.c

Read completely: 486 lines.

## Role

This file implements the `/dev/devfs` rule-control device and the in-kernel devfs rule list. Rules can hide, show, create aliases, or change ownership/permissions for devfs nodes, scoped by mount point, jail state, device type, and wildcard name patterns.

## Main Responsibilities

- Define the `devfs` control character device and its open/close/ioctl handlers.
- Allocate, insert, remove, clear, and free rules:
  - `devfs_rule_alloc()`
  - `devfs_rule_free()`
  - `devfs_rule_insert()`
  - `devfs_rule_remove()`
  - `devfs_rule_clear()`
- Apply or reset rules on nodes:
  - `devfs_rule_check_apply()`
  - `devfs_rule_reset_node()`
- Match rule names against node paths with `devfs_rule_checkname()`.
- Create rule-driven aliases with `devfs_rule_create_link()`.
- Handle ioctls:
  - `DEVFS_RULE_ADD`
  - `DEVFS_RULE_APPLY`
  - `DEVFS_RULE_CLEAR`
  - `DEVFS_RULE_RESET`
- Initialize and uninitialize the control device and rule object cache.

## Synchronization and Lifetime Model

- `devfs_rule_lock` serializes the global `devfs_rule_list`.
- `devfs_rule_check_apply()` can be called when the rule lock is already held; otherwise it takes the lock itself.
- Rules own duplicated strings for mount point, optional device name pattern, and optional link name.
- Rule reset can garbage-collect rule-created links and decrement their target node link counts.

## Important Interactions

- Calls into `devfs_core.c` helpers:
  - `devfs_alias_create()`
  - `devfs_gc()`
  - `devfs_resolve_name_path()`
  - `devfs_resolve_or_create_path()`
  - `devfs_WildCaseCmp()`
  - `devfs_apply_rules()`
  - `devfs_reset_rules()`
- Rule filtering uses mount jail state from `DEVFS_MNTDATA(mp)->jailed`.
- Device-type filtering uses `dev_is_good()` and `dev_dflags()`.

## Notable Design Details

- The control device can only be opened read-write and rejects nonblocking open.
- A `* hide` rule intentionally does not hide `/dev/devfs`, so rule management remains possible.
- Name rules resolve optional path prefixes and only match children of the resolved parent directory.
- Link rules support a trailing `*` in the rule name; generated link names append the wildcard suffix from the matching device name.

## Research Notes

- The rule allocator validates required strings only by null/empty checks and duplicates them into kernel memory.
- `devfs_dev_uninit()` notes that rule cleanup is incomplete with a comment: rules should be destroyed before the cache is destroyed.
- Rule application mutates node visibility and permissions directly; vnode/namecache users rely on devfs vnode operations to honor those flags.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_rules.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vfsops.c

Read completely: 284 lines.

## Role

This file implements DragonFlyBSD devfs mount-level VFS operations. It creates a per-mount devfs tree, attaches devfs vnode operation tables, exposes filesystem statistics, and tears down per-mount devfs state on unmount.

## Main Responsibilities

- `devfs_vfs_mount()`:
  - Rejects update mounts.
  - Copies optional `devfs_mount_info`.
  - Marks the mount local, synthetic-friendly, all-MPSAFE, no-stack-mount, and quick-halt.
  - Fills mount stat names and fsid.
  - Allocates `struct devfs_mnt_data`.
  - Determines jailed behavior from mount flags or credentials.
  - Creates the root `Nroot` devfs node.
  - Adds normal and special vnode op tables.
  - Registers the mount with devfs core, which populates existing devices.
- `devfs_vfs_unmount()`:
  - Flushes vnodes with optional forced close.
  - Cleans orphan nodes.
  - Removes the mount from the devfs core.
  - Frees mount data.
- `devfs_vfs_root()` returns the root vnode through `devfs_allocv()`.
- `devfs_vfs_statfs()` reports synthetic filesystem statistics and file counts.
- `devfs_vfs_fhtovp()`, `devfs_vfs_vptofh()`, and `devfs_vfs_vget()` translate between file handles/inodes and devfs vnodes.
- Namecache generation hooks store and test `mnt_namecache_gen` for devfs negative cache invalidation.
- Registers `devfs_vfsops` through `VFS_SET(devfs_vfsops, devfs, VFCF_SYNTHETIC | VFCF_MPSAFE)`.

## Synchronization and Lifetime Model

- Mount setup and root-node allocation occur under `devfs_lock`.
- Mount add/delete operations are sent synchronously to the devfs core thread.
- Unmount first calls `vflush()` so active vnodes are reclaimed before mount data is freed.
- The root node and all generated nodes are ultimately cleaned by `devfs_mount_del()`.

## Important Interactions

- Depends on `devfs_core.c` for node allocation, vnode allocation, mount registration, mount deletion, orphan counting, and inode-to-vnode lookup.
- Installs vnode op tables from `devfs_vnops.c`.
- Uses jail checks from `sys/jail.h`.

## Research Notes

- File handles use `boottime.tv_sec` as generation; stale boot-generation handles are rejected.
- `devfs_vfs_statfs()` reports two blocks to avoid divide-by-zero behavior in userland tools.
- Mount data is assigned before root node creation, so helpers can use `DEVFS_MNTDATA(mp)` during setup.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vnops.c

Read completely: 2309 lines.

## Role

This file implements devfs vnode operations and optimized file operations for character-device vnodes. It covers directory/namecache behavior for the synthetic devfs tree, user-created directories and symlinks, permissions/attributes, device open/close, direct device read/write/ioctl/kqueue calls, disk safety checks, buffer strategy splitting, device getpages, and device-backed `stat`/`seek`.

## Main Responsibilities

- Define vnode operation tables:
  - `devfs_vnode_norm_vops` for directories, links, and synthetic non-device nodes.
  - `devfs_vnode_dev_vops` for character-device vnodes.
- Define `devfs_dev_fileops`, installed on opened device files to bypass generic vnode fileops for read/write/ioctl/kqueue/stat/seek/close.
- Define standard and special-device vnode operations, including access, inactive, reclaim, readdir, nresolve, nlookupdotdot, getattr, setattr, readlink, mkdir, symlink, rmdir, remove, open, close, fsync, read, write, ioctl, kqfilter, strategy, freeblks, bmap, advlock, and getpages.
- Implement optimized device fileops:
  - `devfs_fo_read()` and `devfs_fo_write()` call `dev_dread()`/`dev_dwrite()` directly and maintain file offsets and sequential heuristics.
  - `devfs_fo_ioctl()` handles `FIODTYPE`, `FIODNAME`, delegates to `dev_dioctl()`, and updates controlling tty state for `TIOCSCTTY`.
  - `devfs_fo_stat()` builds `struct stat` from vnode/device attributes and device last-read/write times.
  - `devfs_fo_kqfilter()` delegates to `dev_dkqfilter()`.
  - `devfs_fo_seek()` implements regular seek semantics while allowing negative offsets for device address use.

## Synchronization and Lifetime Model

- `devfs_lock` protects devfs node topology operations and alias/link resolution.
- Vnode locks are upgraded or released around slow device operations to avoid deadlocks and to allow driver callbacks.
- Device references are acquired around direct fileops before dereferencing `vp->v_rdev`.
- Reclaim handles being called with or without `devfs_lock` already held.
- Device close warns that the devfs node can disappear during `dev_dclose()` if the device destroys itself.
- `devfs_spec_open()` releases `devfs_lock` around clone-handler callbacks because drivers may call back into devfs.
- Buffer-strategy chunking uses a separate allocated buffer with a completion callback and preserves the original bio for final `biodone()`.

## Important Interactions

- Heavy dependency on `devfs_core.c`:
  - node accessibility
  - vnode allocation
  - clone creation
  - cdev private storage
  - topology updates
- Uses the character-device dispatch layer:
  - `dev_dopen()`
  - `dev_dclose()`
  - `dev_dread()`
  - `dev_dwrite()`
  - `dev_dioctl()`
  - `dev_dkqfilter()`
  - `dev_dstrategy()`
  - `dev_dstrategy_chain()`
- Integrates with generic VFS helpers:
  - `vop_helper_access()`
  - `vop_helper_chown()`
  - `vop_helper_chmod()`
  - `vop_stdopen()`
  - `vop_stdclose()`
  - `vfsync()`
  - `vinitvmio()`
  - `vfs_mountedon()`
  - `vn_stat()`
- Uses tty/session state for controlling terminal assignment.
- Uses VM and buffer-cache primitives for disk-backed getpages and strategy calls.

## Notable Design Details

- Device vnodes switch their file pointer to `devfs_dev_fileops` after open, so ordinary reads/writes avoid the VOP table.
- Disk devices opened for write are restricted by `securelevel` and existing read-write mounts.
- D_QUICK devices take a shorter open/close path and retain only a shared vnode lock.
- `FIODNAME` copies the device name to userland through a caller-supplied buffer descriptor.
- `devfs_vop_getattr()` uses `DIOCGPART` to report disk size so `lseek()` works properly.
- `devfs_spec_getpages()` zero-fills short reads so VM pages never expose stale KVA data.

## Research Notes

- This file is a major safety boundary: it must balance vnode locking, device driver callbacks, cdev references, session tty state, and buffer-cache/VM interactions.
- Last-close detection notes an SMP weakness because `count_dev()` is not fully safe across multiple vnodes referencing the same cdev.
- `devfs_vop_nremove()` and `devfs_vop_nrmdir()` only allow removal of `DEVFS_USER_CREATED` nodes, protecting kernel-generated device entries.
- Alias resolution and hidden-node checks are critical for rule enforcement.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs.h

Read completely: 283 lines.

## Role

This header defines DragonFlyBSD dirfs shared structures, flags, macros, globals, inline reference helpers, and function prototypes. Dirfs is a vkernel filesystem that exposes a host directory tree through DragonFly vnode operations.

## Main Contents

- Allocation type declarations:
  - `M_DIRFS`
  - `M_DIRFS_NODE`
  - `M_DIRFS_MISC`
- State and cache flags:
  - `DIRFS_NOFD`
  - `DIRFS_ROOT`
  - `DIRFS_PASVFD`
  - `DIRFS_NODE_RD`
  - `DIRFS_NODE_WR`
  - `DIRFS_NODE_EXE`
- Buffer-cache constants:
  - `BSIZE` is 16384.
  - `BMASK` is `BSIZE - 1`.
- Debugging macros:
  - `dbg()`
  - `debug_node()`
  - `debug_node2()`
- Locking macros:
  - `dirfs_node_lock()`
  - `dirfs_node_unlock()`
  - `dirfs_mount_lock()`
  - `dirfs_mount_unlock()`
  - token helpers for mount-level serialization.
- `struct dirfs_node`: vnode type, state flags, passive-fd cache entry, inode-tree entry, refcount, host fd, parent pointer, vnode pointer, name, advisory lock state, node lock, stat-derived metadata, and file size.
- `struct dirfs_mount`: inode tree, passive fd list, mount lock/token, root node, VFS mount pointer, read-only state, fd counters, vkernel uid/gid, and host root path.
- Conversion macros between VFS mounts/vnodes and dirfs objects.
- Global sysctl-backed variables for debug level and passive fd cache stats.
- Inline node reference helpers:
  - `dirfs_node_ref()`
  - `dirfs_node_unref()`
  - `dirfs_node_setflags()`
  - `dirfs_node_clrflags()`
- Prototypes shared by `dirfs_subr.c`, `dirfs_vfsops.c`, and `dirfs_vnops.c`.

## Important Interactions

- The header exposes host libc-style operations that are temporarily needed in `_KERNEL_VIRTUAL`, including `getdirentries()` and `statfs()`.
- `dirfs_vfsops.c` defines the globals and memory allocation types declared here.
- `dirfs_subr.c` implements node, fd, path, permission, and attribute helpers.
- `dirfs_vnops.c` implements the vnode operation table declared as `dirfs_vnode_vops`.

## Research Notes

- The node structure stores host stat fields directly, making it the cache of host filesystem metadata for VFS operations.
- `dn_refcnt` tracks dirfs node lifetime independently of vnode references; children, passive fd cache, and vnode association all hold node refs.
- The passive fd cache is central to avoiding repeated path walks and enabling openat/fstatat-style operations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_subr.c

Read completely: 893 lines.

## Role

This file implements dirfs support routines for node allocation/freeing, vnode association, host-path construction, passive fd cache management, host stat synchronization, open/close helpers, permission derivation, attribute mutation, file-size changes, and debug output.

## Main Responsibilities

- Node naming and lifecycle:
  - `dirfs_node_setname()`
  - `dirfs_node_alloc()`
  - `dirfs_node_drop()`
  - `dirfs_node_free()`
- File/node allocation:
  - `dirfs_alloc_file()` creates a dirfs node for a host child, optionally opens it with `openat()`, stats it, allocates a vnode, and marks the vnode for inactive finalization.
  - `dirfs_alloc_vp()` maps a dirfs node to a vnode, initializes vnode type and VM backing for regular files, and handles vnode allocation races.
  - `dirfs_free_vp()` detaches the vnode and drops the node's vnode-held reference.
- Host metadata:
  - `dirfs_nodetype()` maps host `stat` mode to vnode type.
  - `dirfs_node_stat()` fills dirfs node metadata from `lstat()` or `fstatat()`.
- Host path/fd helpers:
  - `dirfs_node_absolute_path()`
  - `dirfs_node_absolute_path_plus()`
  - `dirfs_findfd()`
  - `dirfs_dropfd()`
- Permission/open helpers:
  - `dirfs_node_getperms()` computes effective read/write/execute flags for the vkernel uid/gid.
  - `dirfs_open_helper()` opens a host file or directory using an existing parent fd or a relative path from `dirfs_findfd()`.
  - `dirfs_close_helper()` currently avoids closing descriptors directly because buffer-cache buffers may still reference them.
- Attribute mutation helpers:
  - `dirfs_node_chtimes()`
  - `dirfs_node_chflags()`
  - `dirfs_node_chmod()`
  - `dirfs_node_chown()`
  - `dirfs_node_chsize()`
- Passive fd cache:
  - `dirfs_node_setpassive()` adds/removes nodes from the per-mount fd cache and enforces `dirfs_fd_limit`.
- Diagnostics:
  - `dirfs_flag2str()`
  - `debug()`

## Synchronization and Lifetime Model

- Each node has a lock and a manual reference count.
- `dirfs_alloc_vp()` retries around vnode reclaim/allocation races and keeps a node reference for the vnode association.
- Parent links hold references from children to parents.
- Passive fd cache membership holds an additional node reference.
- `dirfs_node_setpassive()` closes cached descriptors only when vnode/node refs, inactive state, dirty VM flags, and dirty buffer trees indicate it is safe.
- Root node descriptors are treated specially and are not closed by passive-cache eviction.

## Important Interactions

- Uses host syscalls/functions: `openat()`, `lstat()`, `fstatat()`, `lutimes()`, `lchflags()`, `lchmod()`, `lchown()`, `truncate()`, and `close()`.
- Uses VFS/VM helpers:
  - `getnewvnode()`
  - `vinitvmio()`
  - `nvtruncbuf()`
  - `nvextendbuf()`
  - `VOP_FSYNC()`
- Called throughout `dirfs_vnops.c` for lookups, create/mkdir/symlink, getattr/setattr, read/write strategy, and reclaim/inactive behavior.

## Research Notes

- The host timestamp nanosecond fields are populated as `st_time * 1000000000L`, which appears to convert seconds to nanoseconds rather than using native subsecond fields.
- `dirfs_close_helper()` has the close call disabled under `#if 0`, reflecting a deliberate choice to avoid closing fds while buffer-cache state may still need them.
- Path construction walks parent pointers back to the root and fails if the resulting path exceeds `MAXPATHLEN` or if an unlinked node no longer has a path.
- `dirfs_node_chsize()` updates buffer-cache state before truncating/extending the host file.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vfsops.c

Read completely: 359 lines.

## Role

This file implements dirfs mount-level VFS operations and sysctl/debug registration. Dirfs mounts a host directory into a DragonFly vkernel, using host syscalls to validate and expose the host filesystem tree.

## Main Responsibilities

- Define dirfs allocation types and KTR tracepoints.
- Expose sysctls:
  - `vfs.dirfs.debug`
  - `vfs.dirfs.fd_limit`
  - `vfs.dirfs.fd_used`
  - `vfs.dirfs.passive_fd_list_miss`
  - `vfs.dirfs.passive_fd_list_hits`
- `dirfs_mount()` handles read-only/read-write update toggles, allocates `struct dirfs_mount`, copies/normalizes the host path, verifies it is a directory, initializes mount state, installs vnode ops, records vkernel uid/gid, and fills mount stats.
- `dirfs_unmount()` flushes vnodes, clears passive fd cache, closes/drops the root node if allocated, and frees mount data.
- `dirfs_root()` lazily allocates/stats the root node, opens and permanently keeps a host fd for the root directory, allocates the root vnode, and marks it `VROOT`.
- `dirfs_statfs()` and `dirfs_statvfs()` mirror host filesystem stats into the mounted dirfs view.
- File-handle/export operations return unsupported.
- Registers `dirfs_vfsops` through `VFS_SET(dirfs_vfsops, dirfs, 0)`.

## Synchronization and Lifetime Model

- Mount state has `dm_lock` and `dm_token`, but mount setup largely happens during serialized VFS mount paths.
- Root node is held for the life of the mount by a node reference and an always-open host directory fd.
- Unmount expects `vflush()` to reclaim active vnodes before passive fd cache and root cleanup.

## Important Interactions

- Uses host functions: `stat()`, `open()`, `statfs()`, `statvfs()`, `getuid()`, and `getgid()`.
- Calls shared helpers from `dirfs_subr.c` for root stat, vnode allocation, closing, and node drop.
- Installs the vnode op table from `dirfs_vnops.c`.

## Research Notes

- `dirfs_mount()` has an error-path hazard: after `stat()` failure it jumps to `failure` without freeing `dmp`, unlike some earlier error branches.
- The read-only update path modifies only `dm_rdonly`; VOP paths also consult mount flags for write checks.
- NFS-style export/file-handle support is intentionally unsupported.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vnops.c

Read completely: 1587 lines.

## Role

This file implements dirfs vnode operations. It maps DragonFly VFS/namecache operations onto host filesystem syscalls for a mounted host directory, while using DragonFly's vnode, buffer-cache, VM, kqueue, advisory-lock, and namecache infrastructure.

## Main Responsibilities

- Namecache and creation operations:
  - `dirfs_nresolve()` resolves children from the passive fd cache or creates a new dirfs node through host stat.
  - `dirfs_ncreate()` creates host regular files with `openat(O_CREAT | O_RDWR)`.
  - `dirfs_nmkdir()` creates host directories with `mkdirat()`.
  - `dirfs_nsymlink()` creates host symlinks with `symlink()`.
  - `dirfs_nremove()` removes host non-directories with `unlinkat()`.
  - `dirfs_nrmdir()` removes host directories with `rmdir()`.
  - `dirfs_nrename()` renames host paths with `rename()` and updates namecache/node state.
  - `dirfs_nlookupdotdot()`, `dirfs_nmknod()`, and `dirfs_nlink()` are unsupported.
- Open/close:
  - `dirfs_open()` opens host fds for non-root nodes as needed.
  - `dirfs_close()` syncs regular-file buffers and runs standard vnode close accounting.
- Permissions and attributes:
  - `dirfs_access()` checks mount read-only state and helper permissions.
  - `dirfs_getattr()` refreshes host stat data and fills `vattr`.
  - `dirfs_setattr()` handles flags, size, ownership, mode, and timestamps through dirfs helper functions.
  - `dirfs_fsync()` flushes DragonFly buffers and host fd state.
- Regular-file I/O:
  - `dirfs_read()` reads through the buffer cache with `getcacheblk()`/`bread()` and `uiomovebp()`.
  - `dirfs_write()` enforces file-size limits, handles append, extends host file/buffer state, writes through cached buffers, and schedules dirty writes.
  - `dirfs_strategy()` translates buffer-cache I/O to host `pread()`/`pwrite()`.
  - `dirfs_bmap()` implements identity logical-to-device offset mapping for the synthetic backing.
- Directory and symlink reads:
  - `dirfs_readdir()` uses host `getdirentries()` and writes VFS dirents to the caller.
  - `dirfs_readlink()` reads symlink text with `readlinkat()`.
- Lifecycle:
  - `dirfs_inactive()` recycles unlinked nodes or adds nodes with fds to the passive fd cache.
  - `dirfs_reclaim()` detaches vnode/node association.
- Eventing and locks:
  - `dirfs_advlock()` uses `lf_advlock()`.
  - `dirfs_kqfilter()` supports read, write, and vnode filters.
  - Filter callbacks report readable bytes, write readiness, vnode flags, and revoke EOF.
- Defines `dirfs_vnode_vops`.

## Synchronization and Lifetime Model

- Node-level operations use `dirfs_node_lock()` where parent/node fd or metadata state needs serialization.
- Mount token use appears around some namecache operations that fetch and release target vnodes.
- Passive fd cache lookups in `dirfs_nresolve()` scan `dm_fdlist` for child nodes that can be reactivated.
- Vnode reclaim calls `dirfs_free_vp()`, which may drop the final node reference and free the node.
- Buffer-cache strategy assumes regular-file nodes have an open host fd and panics if missing.

## Important Interactions

- Calls support routines from `dirfs_subr.c` for node allocation, stat refresh, fd/path resolution, host opens, passive cache management, and attribute changes.
- Uses host functions/syscalls:
  - `openat()`
  - `mkdirat()`
  - `unlinkat()`
  - `rename()`
  - `rmdir()`
  - `symlink()`
  - `getdirentries()`
  - `readlinkat()`
  - `pread()`
  - `pwrite()`
  - `lseek()`
- Uses VFS/cache helpers:
  - `cache_setvp()`
  - `cache_setunresolved()`
  - `cache_unlink()`
  - `cache_rename()`
  - `cache_inval_vp()`
  - `vop_write_dirent()`
  - `vfsync()`
  - `bread()`
  - `bdwrite()`/`bwrite()`
  - `biodone()`

## Notable Design Details

- Regular-file reads and writes go through DragonFly's buffer cache rather than direct host `read()`/`write()` from VOP read/write.
- Host `pread()`/`pwrite()` happens in `dirfs_strategy()`, making buffer-cache writeback the actual host persistence path.
- Namecache is updated explicitly after create, remove, rename, mkdir, rmdir, and symlink operations.
- `dirfs_nrename()` updates the renamed node's cached name and marks an overwritten target as unlinked/destroyed.
- `dirfs_readdir()` relies on host directory offsets from `getdirentries()`/`lseek()`.

## Research Notes

- `dirfs_ncreate()` computes a write-permission error but then calls `dirfs_alloc_file()` regardless, which may overwrite the intended `EPERM`.
- `dirfs_getattr()` returns `0` even if `dirfs_node_stat()` failed, while only filling attributes on success.
- `dirfs_fsync()` calls `fsync()` twice on failure and returns `0` regardless of the collected error.
- `dirfs_readlink()` passes `nlen + 1` to `uiomove()` after setting the NUL terminator after the move; symlink read APIs normally return bytes without a trailing NUL.
- The code is designed for vkernel use and depends on host libc/syscall behavior being available in the kernel-virtual environment.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/Makefile

Read completely: 8 lines.

## Role

This Makefile defines the DragonFlyBSD ext2fs kernel module build.

## Main Contents

- Sets `KMOD= ext2fs`.
- Lists ext2fs module source files:
  - allocation and block mapping
  - checksum and extents
  - hash/htree support
  - inode, lookup, subroutines, VFS ops, and vnode ops
- Adds generated/config option header `opt_suiddir.h`.
- Includes the common kernel module build rules with `.include <bsd.kmod.mk>`.

## Research Notes

- No runtime logic is present.
- Build correctness depends on the listed source set matching the ext2fs module implementation dependencies.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/Makefile -->