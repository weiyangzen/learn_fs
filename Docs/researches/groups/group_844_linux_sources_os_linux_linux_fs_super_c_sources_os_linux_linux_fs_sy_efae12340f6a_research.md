# Group Research: group_844_linux_sources_os_linux_linux_fs_super_c_sources_os_linux_linux_fs_sy_efae12340f6a

Scope confirmed against `Docs/research_subset_a.md`. All listed source files were read completely. This group covers Linux VFS superblock lifecycle and syncing, sysfs and tracefs virtual filesystem plumbing, timerfd syscall backing, small KUnit tests, and UBIFS authentication, budgeting, and commit machinery.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/super.c -->
# File Research: sources/os/linux/linux/fs/super.c

Purpose: Core VFS superblock management: allocation, lookup/reuse, reference lifetimes, shutdown, mount tree construction helpers, block-device-backed superblocks, freeze/thaw, emergency remount/thaw, and per-superblock backing device setup.

Key APIs and entry points:
- Exports lifecycle helpers: `deactivate_locked_super`, `deactivate_super`, `retire_super`, `generic_shutdown_super`, `put_super`, `drop_super`, `drop_super_exclusive`.
- Exports lookup/mount helpers: `sget_fc`, `sget_dev`, `get_tree_nodev`, `get_tree_single`, `get_tree_keyed`, `get_tree_bdev_flags`, `get_tree_bdev`, `vfs_get_tree`.
- Exports block/anonymous helpers: `get_anon_bdev`, `free_anon_bdev`, `set_anon_super`, `kill_anon_super`, `setup_bdev_super`, `kill_block_super`, `fs_holder_ops`.
- Exports freeze APIs: `freeze_super`, `thaw_super`, plus `filesystems_freeze`, `filesystems_thaw`, `emergency_thaw_all`.
- Exports BDI/workqueue setup: `super_setup_bdi_name`, `super_setup_bdi`, `sb_init_dio_done_wq`.

Implementation notes:
- Maintains global `super_blocks` under `sb_lock`; individual lifecycle transitions use `s_umount`, `s_count`, `s_active`, and flags including `SB_BORN`, `SB_DYING`, `SB_DEAD`, `SB_ACTIVE`.
- `alloc_super()` initializes locks, lists, shrinker state, writeback/error state, freeze/writer counters, LRU structures, and namespace ownership.
- `generic_shutdown_super()` performs the main teardown sequence: mark dying, shrink/evict dentries and inodes, call filesystem shutdown hooks, unregister shrinkers, clean BDI, and release bdev/anode resources.
- `sget_fc()` implements the central find-or-create path for fs_context-based mounts, handling test/set callbacks, user namespace choice, active references, and races with existing superblocks.
- Block-device path coordinates `blkdev_get_by_path`, holder ops, block size, `SB_RDONLY`, `FMODE_EXCL`, bdev sync, freeze, thaw, and surprise removal marking.
- Freeze logic supports userspace and kernel holders, nesting rules, exclusive/nonexclusive owners, partial-freeze waiting, lockdep annotations, and staged writer exclusion.

Concurrency and correctness:
- Heavy use of `sb_lock`, `s_umount`, per-super wait queues, percpu rwsems for write levels, and memory ordering around no-space/lifecycle flags.
- `super_lock()` can return false if a superblock is not born or has begun dying/dead transition.
- Freeze/thaw state is intentionally guarded by `s_umount`; writer exclusion proceeds through freeze levels before filesystem `->freeze_fs`.
- Block holder callbacks must avoid racing bdev removal with superblock teardown.

Dependencies:
- VFS fs_context/mount API, block layer holder API, writeback/BDI, shrinker, quota, security, lockdep, IDA anonymous devices.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sync.c -->
# File Research: sources/os/linux/linux/fs/sync.c

Purpose: High-level implementation of `sync`, `syncfs`, `fsync`, `fdatasync`, and `sync_file_range` behavior.

Key APIs and syscalls:
- `sync_filesystem(sb)` writes back inodes, invokes `s_op->sync_fs()` in nowait and wait phases, syncs block device cache, and requires `s_umount` to be held.
- `ksys_sync()` and `SYSCALL_DEFINE0(sync)` sync all superblocks and block devices.
- `emergency_sync()` schedules asynchronous emergency writeback work.
- `SYSCALL_DEFINE1(syncfs)` syncs one filesystem and reports writeback errors via `errseq_check_and_advance`.
- `vfs_fsync_range()` and `vfs_fsync()` are exported helpers for file operation `->fsync`.
- `fsync`, `fdatasync`, `sync_file_range`, compat `sync_file_range`, and `sync_file_range2` syscalls are implemented.

Implementation notes:
- Global sync wakes flusher threads first, then iterates superblocks to sync inodes and filesystem metadata, then syncs block devices.
- `sync_file_range()` validates flags and signed offsets, handles 32-bit pagecache address limits, supports wait-before/write/wait-after ordering, and only accepts regular files, block devices, and directories.
- `sync_file_range()` explicitly does not sync metadata or flush disk caches; comments document application-visible limitations.

Concurrency and correctness:
- `syncfs` holds `sb->s_umount` around `sync_filesystem`.
- Emergency sync runs from workqueue context and performs two passes to reduce missed locked pages.
- `sync_file_range` propagates writeback errors from wait operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sysctls.c -->
# File Research: sources/os/linux/linux/fs/sysctls.c

Purpose: Registers shared `/proc/sys/fs` sysctls used by multiple filesystems.

Key behavior:
- Defines `fs_shared_sysctls` with `overflowuid` and `overflowgid`.
- Both sysctls use `proc_dointvec_minmax`, mode `0644`, lower bound `SYSCTL_ZERO`, and upper bound `SYSCTL_MAXOLDUID`.
- `init_fs_sysctls()` registers the table under `"fs"` using `register_sysctl_init`.
- Registration runs via `early_initcall`.

Dependencies:
- Global `fs_overflowuid` and `fs_overflowgid` variables from filesystem core headers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sysctls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sysfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/sysfs/Kconfig

Purpose: Kconfig option for sysfs support.

Key behavior:
- Defines `config SYSFS`, default `y`, visible under `EXPERT`.
- Selects `KERNFS`.
- Help text describes sysfs as a virtual filesystem exposing kernel objects, attributes, relationships, devices, drivers, and tunables.
- Notes that system agents and hotplug-style policy can rely on sysfs.
- Documents boot/root-device implications if sysfs is disabled and suggests embedded systems may disable it for space.

Dependencies:
- `KERNFS` is selected automatically when sysfs is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sysfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sysfs/Makefile -->
# File Research: sources/os/linux/linux/fs/sysfs/Makefile

Purpose: Builds the sysfs core object set.

Build contents:
- `obj-y := file.o dir.o symlink.o mount.o group.o`

Notes:
- sysfs is built as core kernel object code when enabled, not as a standalone module in this Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sysfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sysfs/dir.c -->
# File Research: sources/os/linux/linux/fs/sysfs/dir.c

Purpose: sysfs directory creation, removal, rename/move, duplicate warnings, and mount-point directory helpers.

Key APIs:
- `sysfs_create_dir_ns(kobj, ns)` creates a kernfs directory for a kobject with namespace tag and ownership from `kobject_get_ownership`.
- `sysfs_remove_dir(kobj)` disassociates `kobj->sd` and removes the kernfs directory.
- `sysfs_rename_dir_ns()` and `sysfs_move_dir_ns()` wrap kernfs namespace-aware rename/move.
- `sysfs_create_mount_point()` and `sysfs_remove_mount_point()` create/remove always-empty directories; both are GPL exported.
- `sysfs_warn_dup()` logs duplicate filename errors and dumps stack.

Concurrency and correctness:
- Defines `sysfs_symlink_target_lock`, used to protect `kobj->sd` against races between directory removal and symlink operations.
- `sysfs_remove_dir()` clears `kobj->sd` under that spinlock before kernfs removal.
- Duplicate creation paths warn on `-EEXIST`.

Dependencies:
- kernfs directory primitives and kobject ownership/name APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sysfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sysfs/file.c -->
# File Research: sources/os/linux/linux/fs/sysfs/file.c

Purpose: sysfs regular and binary attribute file implementation over kernfs.

Key APIs:
- Attribute creation/removal: `sysfs_create_file_ns`, `sysfs_create_files`, `sysfs_remove_file_ns`, `sysfs_remove_files`, `sysfs_add_file_to_group`, `sysfs_remove_file_from_group`.
- Binary attributes: `sysfs_create_bin_file`, `sysfs_remove_bin_file`, `sysfs_bin_attr_simple_read`.
- Runtime updates: `sysfs_notify`, `sysfs_chmod_file`, `sysfs_break_active_protection`, `sysfs_unbreak_active_protection`.
- Ownership changes: `sysfs_link_change_owner`, `sysfs_file_change_owner`, `sysfs_change_owner`.
- Output helpers: `sysfs_emit`, `sysfs_emit_at`.

Implementation notes:
- Maps `sysfs_ops->show/store` to kernfs seq/read/write callbacks, with preallocated-buffer variants for `SYSFS_PREALLOC`.
- Binary attributes support read, write, mmap, custom llseek, open-time mapping override, and size bounds.
- Attribute mode is masked to sysfs-supported permissions during group creation paths.
- `sysfs_emit*` validate PAGE_SIZE-aligned sysfs buffers and use `vscnprintf`.

Concurrency and correctness:
- `sysfs_file_ops()` requires active kernfs protection and asserts lockdep when `KERNFS_LOCKDEP` is set.
- Active protection break/unbreak is provided for self-deleting sysfs attributes and pins both kobject and kernfs node.
- Ownership change helpers validate object presence in sysfs and symlink target identity before mutation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sysfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sysfs/group.c -->
# File Research: sources/os/linux/linux/fs/sysfs/group.c

Purpose: Batch creation, update, merge, removal, symlink insertion, and ownership changes for sysfs attribute groups.

Key APIs:
- `sysfs_create_group`, `sysfs_create_groups`
- `sysfs_update_group`, `sysfs_update_groups`
- `sysfs_remove_group`, `sysfs_remove_groups`
- `sysfs_merge_group`, `sysfs_unmerge_group`
- `sysfs_add_link_to_group`, `sysfs_remove_link_from_group`
- `compat_only_sysfs_link_entry_to_kobj`
- `sysfs_group_change_owner`, `sysfs_groups_change_owner`

Implementation notes:
- Visibility callbacks `is_visible`, `is_visible_const`, and `is_bin_visible` determine whether files/groups are created and with which mode.
- `SYSFS_GROUP_INVISIBLE` can suppress an entire named group via first-visible check.
- Update mode removes existing files before re-adding currently visible ones.
- Creation unwinds previously created files/groups on error.
- Merge/unmerge operates on pre-existing named groups and fails if the group is absent.

Concurrency and correctness:
- Symlink-to-target compatibility helper uses `sysfs_symlink_target_lock` to safely reference target `kobj->sd`.
- Ownership change walks visible attributes and bin_attrs, applying kernfs `ATTR_UID | ATTR_GID`.
- Missing visible files during ownership change return `-ENOENT`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sysfs/group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sysfs/mount.c -->
# File Research: sources/os/linux/linux/fs/sysfs/mount.c

Purpose: sysfs filesystem registration, fs_context setup, kernfs root creation, namespace handling, and superblock teardown.

Key structures and APIs:
- Maintains `sysfs_root` and exported internal `sysfs_root_kn`.
- `sysfs_init_fs_context()` allocates kernfs fs context, checks namespace mount permission, grabs current network namespace tag, sets magic `SYSFS_MAGIC`, and marks context global.
- `sysfs_fs_context_free()` drops namespace tag and frees kernfs context.
- `sysfs_kill_sb()` kills kernfs superblock and drops namespace tag.
- `sysfs_init()` creates the kernfs root and registers `sysfs_fs_type`.

Namespace/security notes:
- Non-kernel mounts require `kobj_ns_current_may_mount(KOBJ_NS_TYPE_NET)`.
- If a net namespace tag exists, `fc->user_ns` is switched to that namespace’s user namespace.
- Filesystem type uses `FS_USERNS_MOUNT | FS_USERNS_MOUNT_RESTRICTED`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sysfs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sysfs/symlink.c -->
# File Research: sources/os/linux/linux/fs/sysfs/symlink.c

Purpose: sysfs symlink creation, deletion, removal, and rename helpers.

Key APIs:
- `sysfs_create_link_sd()` creates a link under a kernfs node.
- `sysfs_create_link()` and `sysfs_create_link_nowarn()` create links under kobject directories; both exported.
- `sysfs_delete_link()` removes namespace-aware symlinks when target kobject is known.
- `sysfs_remove_link()` removes a symlink by name; exported.
- `sysfs_rename_link_ns()` validates symlink target and renames with a new namespace; exported.

Concurrency and correctness:
- Link creation and namespace lookup synchronize against target directory removal with `sysfs_symlink_target_lock`.
- Target kernfs node is temporarily referenced before link creation.
- Rename validates that the found kernfs node is a link and points to the expected target kobject.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sysfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/sysfs/sysfs.h -->
# File Research: sources/os/linux/linux/fs/sysfs/sysfs.h

Purpose: Internal sysfs header shared by sysfs implementation files.

Contents:
- Includes public `<linux/sysfs.h>`.
- Declares internal `sysfs_root_kn`.
- Declares `sysfs_symlink_target_lock`.
- Declares `sysfs_warn_dup`.
- Declares file creation helpers `sysfs_add_file_mode_ns` and `sysfs_add_bin_file_mode_ns`.
- Declares symlink helper `sysfs_create_link_sd`.

Role:
- Keeps kernfs-level internals private to `fs/sysfs` while allowing dir/file/group/symlink/mount code to cooperate.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/sysfs/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/tests/binfmt_elf_kunit.c -->
# File Research: sources/os/linux/linux/fs/tests/binfmt_elf_kunit.c

Purpose: KUnit coverage for ELF loader `total_mapping_size()` behavior.

Test coverage:
- Verifies null/empty program header inputs return zero.
- Verifies non-`PT_LOAD` headers do not contribute to mapping size.
- Uses a realistic `/bin/mount` program-header layout and expected mapping size `0xE070`.
- Confirms unordered `PT_LOAD` headers produce the same total mapping size.

Structure:
- Single test case `total_mapping_size_test`.
- KUnit suite name is `KBUILD_MODNAME`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/tests/binfmt_elf_kunit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/tests/exec_kunit.c -->
# File Research: sources/os/linux/linux/fs/tests/exec_kunit.c

Purpose: KUnit coverage for `bprm_stack_limits()` argument/environment stack accounting.

Test coverage:
- Negative `argc`/`envc` and counts at/above `MAX_ARG_STRINGS` return `-E2BIG`.
- Includes overflow-oriented 32-bit-sensitive argument count cases.
- Under `CONFIG_MMU`, verifies pathological low `bprm->p` is rejected.
- Tests `rlim_stack` clamping to at least `ARG_MAX`, upper cap at `_STK_LIM / 4 * 3`, pointer accounting, and argc minimum of one.
- Confirms expected constants: `_STK_LIM == SZ_8M`, `ARG_MAX == 32 * SZ_4K`, `MAX_ARG_STRINGS == 0x7FFFFFFF`.

Structure:
- Test data table of `linux_binprm` inputs and expected return/argmin.
- Single test case `exec_test_bprm_stack_limits`.
- KUnit suite name is `"exec"`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/tests/exec_kunit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/timerfd.c -->
# File Research: sources/os/linux/linux/fs/timerfd.c

Purpose: Implements timerfd file descriptors and syscalls over hrtimer/alarmtimer.

Key syscalls and file operations:
- `timerfd_create(clockid, flags)`
- `timerfd_settime`, `timerfd_gettime`
- 32-bit time compat variants under `CONFIG_COMPAT_32BIT_TIME`
- File ops: release, poll, read_iter, noop llseek, proc fdinfo show, optional checkpoint/restore ioctl.

Implementation notes:
- `timerfd_ctx` stores hrtimer or alarm, interval, time namespace offset, waitqueue, tick count, clock id, cancel-on-set state, RCU node, and cancel-list linkage.
- Supports `CLOCK_MONOTONIC`, `CLOCK_REALTIME`, `CLOCK_BOOTTIME`, and realtime/boottime alarm clocks.
- Alarm clocks require `CAP_WAKE_ALARM`.
- `TFD_TIMER_CANCEL_ON_SET` absolute realtime timers are tracked in global RCU `cancel_list`; clock changes wake waiters and cause `-ECANCELED`.
- Periodic timers are rearmed lazily in read/gettime paths to avoid callback-side rearm abuse.

Concurrency and correctness:
- Waitqueue lock protects `ticks`, `expired`, timer rearm, and read/poll visibility.
- Separate `cancel_lock` protects per-context cancel-list membership; global `cancel_lock` protects the list.
- Release removes cancel-list membership, cancels hrtimer/alarm, then frees context with `kfree_rcu`.
- Settime loops with `try_to_cancel` plus `hrtimer_cancel_wait_running` to avoid reprogramming while callbacks run.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/timerfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/tracefs/Makefile -->
# File Research: sources/os/linux/linux/fs/tracefs/Makefile

Purpose: Builds tracefs core objects.

Build contents:
- `obj-$(CONFIG_TRACING) += tracefs.o`
- `tracefs-objs := inode.o event_inode.o`

Notes:
- tracefs is tied to `CONFIG_TRACING`.
- Main implementation is split between general tracefs inode/mount code and dynamic eventfs inode code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/tracefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/tracefs/event_inode.c -->
# File Research: sources/os/linux/linux/fs/tracefs/event_inode.c

Purpose: Implements eventfs, the dynamic tracefs subtree used for tracing events. It stores metadata and creates dentries/inodes just in time.

Key APIs:
- `eventfs_create_events_dir()` creates the top-level events directory.
- `eventfs_create_dir()` creates child eventfs metadata directories.
- `eventfs_remove_dir()` and `eventfs_remove_events_dir()` remove metadata and invalidate persistent event dentries.
- `eventfs_remount()` updates saved ownership after tracefs remount.
- `eventfs_d_release()` releases eventfs_inode references held by dentries.
- `eventfs_remount_lock()` / `eventfs_remount_unlock()` coordinate tracefs remount with eventfs SRCU/mutex.

Implementation notes:
- `eventfs_inode` metadata tracks children, file entry table, per-entry saved attrs, default attr, data pointer, kref, freed/events flags, entry count, and stable inode number.
- Top-level events dir uses `eventfs_root_inode`, adding a persistent `events_dir` dentry pointer.
- File and directory dentries are created during lookup/readdir using callbacks in `eventfs_entry`.
- All event files use synthetic inode number `EVENTFS_FILE_INODE_INO`; directories lazily allocate stable inode numbers.
- Attribute changes are cached back into eventfs metadata so dynamic dentries preserve user changes.

Concurrency and correctness:
- `eventfs_mutex` protects mutation and freed-state checks.
- `eventfs_srcu` protects traversal/lifetime after removal from parent lists.
- `kref` is driven by dentry `d_fsdata` references; final release calls per-entry `release` callbacks and frees after SRCU.
- Removal is recursive and capped by expected events/group/event/file depth.
- Lookup callbacks run under eventfs locking, and comments warn callbacks must not re-enter tracefs/eventfs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/tracefs/event_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/tracefs/inode.c -->
# File Research: sources/os/linux/linux/fs/tracefs/inode.c

Purpose: General tracefs filesystem implementation: inode cache, mount options, filesystem registration, file/dir creation helpers, recursive removal, and interaction with eventfs.

Key APIs:
- `tracefs_get_inode()`
- `tracefs_start_creating`, `tracefs_failed_creating`, `tracefs_end_creating`
- `tracefs_create_file()` exported GPL
- `tracefs_create_dir()`
- `tracefs_create_instance_dir()`
- `tracefs_remove()`
- `tracefs_initialized()`

Implementation notes:
- Maintains a custom `tracefs_inode` slab cache and a global RCU list of tracefs inodes for remount ownership propagation.
- Mount options: `uid`, `gid`, `mode`; default mode is `0700`.
- `tracefs_apply_options()` updates root inode mode/ownership and, on remount, clears per-inode saved UID/GID flags and calls `eventfs_remount` for eventfs inodes.
- Instance directory supports userspace mkdir/rmdir callbacks and temporarily drops inode locks while invoking tracing callbacks.
- Creation helpers pin the tracefs mount with `simple_pin_fs`, create persistent dentries, initialize ownership from parent, and emit fsnotify events.
- Lockdown check `LOCKDOWN_TRACEFS` suppresses tracefs/eventfs file creation.

Concurrency and correctness:
- `tracefs_inode_lock` protects global inode list updates.
- Dentry ops use `d_fsdata` to distinguish eventfs dentries, route release to eventfs, and invalidate freed eventfs nodes.
- `tracefs_drop_inode()` clears eventfs flag before inode teardown to avoid remount updates racing stale eventfs state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/tracefs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/tracefs/internal.h -->
# File Research: sources/os/linux/linux/fs/tracefs/internal.h

Purpose: Shared internal declarations and data structures for tracefs/eventfs.

Contents:
- Tracefs inode flags: `TRACEFS_EVENT_INODE`, `TRACEFS_GID_PERM_SET`, `TRACEFS_UID_PERM_SET`, `TRACEFS_INSTANCE_INODE`.
- `struct tracefs_inode`: embeds VFS inode, list node, flags, and private pointer.
- `struct eventfs_attr`: saved mode/uid/gid for dynamic eventfs entries.
- `struct eventfs_inode`: children/list/RCU union, entry table, name, attr cache, data, kref, flags, entry count, inode number.
- `get_tracefs()` container helper.
- Prototypes for tracefs creation helpers and eventfs remount/release locking helpers.

Role:
- Defines the shared lifetime and metadata contract between `inode.c` and `event_inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/tracefs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/Kconfig -->
# File Research: sources/os/linux/linux/fs/ubifs/Kconfig

Purpose: Kconfig options for UBIFS.

Key options:
- `UBIFS_FS`: tristate UBIFS support, depends on `MTD_UBI`, selects CRC/hash/encryption-related helpers as needed.
- `UBIFS_FS_ADVANCED_COMPR`: exposes compressor choices.
- `UBIFS_FS_LZO`, `UBIFS_FS_ZLIB`, `UBIFS_FS_ZSTD`: compressor support, default `y`.
- `UBIFS_ATIME_SUPPORT`: optional atime updates, default `n` due to flash wear.
- `UBIFS_FS_XATTR`: extended attributes, default `y`.
- `UBIFS_FS_SECURITY`: LSM security labels, depends on xattrs, default `y`.
- `UBIFS_FS_AUTHENTICATION`: authentication support, selects `KEYS`, `CRYPTO_HMAC`, and `SYSTEM_DATA_VERIFICATION`.

Notes:
- Authentication help text warns that hash algorithms such as sha256 are not auto-selected.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/Makefile -->
# File Research: sources/os/linux/linux/fs/ubifs/Makefile

Purpose: UBIFS object composition.

Build contents:
- `obj-$(CONFIG_UBIFS_FS) += ubifs.o`
- Core objects include shrinker, journal, file, dir, super, sb, io, tnc, master, scan, replay, log, commit, gc, orphan, budget, find, tnc_commit, compression, lpt/lprops, recovery, ioctl, debug, misc, sysfs.
- Conditional objects: `crypto.o` for `CONFIG_FS_ENCRYPTION`, `xattr.o` for `CONFIG_UBIFS_FS_XATTR`, `auth.o` for `CONFIG_UBIFS_FS_AUTHENTICATION`.

Role:
- Shows `auth.c`, `budget.c`, and `commit.c` are part of the main UBIFS aggregate object, not standalone modules.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/auth.c -->
# File Research: sources/os/linux/linux/fs/ubifs/auth.c

Purpose: UBIFS authentication helpers: node hashing, HMAC generation/verification, superblock PKCS#7 signature verification, key setup, and authentication teardown.

Key APIs:
- `__ubifs_node_calc_hash`, `__ubifs_node_check_hash`, `ubifs_bad_hash`
- `ubifs_prepare_auth_node`
- `ubifs_sb_verify_signature`
- `ubifs_init_authentication`, `__ubifs_exit_authentication`
- `__ubifs_node_insert_hmac`, `__ubifs_node_verify_hmac`
- `__ubifs_shash_copy_state`
- `ubifs_hmac_wkm`, `ubifs_hmac_zero`

Implementation notes:
- Node hashes use `c->hash_tfm` over common header length.
- Authentication nodes store an HMAC over the running hash state.
- HMAC excludes common node magic/CRC and excludes the embedded HMAC field itself.
- `ubifs_init_authentication()` resolves hash algorithm name, requests a logon key, allocates hash and HMAC shash transforms, validates digest sizes, sets HMAC key from key payload, marks filesystem authenticated, and initializes `c->log_hash`.
- Superblock signature verification scans after the superblock node for `UBIFS_SIG_NODE`, checks type `UBIFS_SIGNATURE_TYPE_PKCS7`, then calls `verify_pkcs7_signature`.

Security/correctness:
- HMAC compare uses `crypto_memneq`.
- Revoked or wrong-type keys are rejected.
- Oversized hash/HMAC algorithms are rejected against UBIFS fixed arrays.
- On init failure, allocated crypto transforms are freed and key semaphore/reference is released.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/budget.c -->
# File Research: sources/os/linux/linux/fs/ubifs/budget.c

Purpose: UBIFS budgeting and free-space accounting. It pessimistically reserves space for data, dirty data, and index growth so operations can later be committed safely.

Key APIs:
- `ubifs_calc_min_idx_lebs`
- `ubifs_calc_available`
- `ubifs_budget_space`
- `ubifs_release_budget`
- `ubifs_convert_page_budget`
- `ubifs_release_dirty_inode_budget`
- `ubifs_reported_space`
- `ubifs_get_free_space_nolock`
- `ubifs_get_free_space`

Implementation notes:
- `make_free_space()` tries writeback, GC, then commit, retrying up to `MAX_MKSPC_RETRIES`.
- Index budgeting reserves roughly three times consolidated index size to support the in-the-gaps commit method.
- Available space subtracts GC reserve, journal heads, deletion reserve, dead/dark space, and excess index dark space.
- Reserved pool access is allowed for configured UID, `CAP_SYS_RESOURCE`, or configured GID membership.
- Budget requests calculate separate `idx_growth`, `data_growth`, and `dd_growth`.
- Released index growth moves into `uncommitted_idx` until commit clears it.

Concurrency and correctness:
- `space_lock` protects budget info and no-space flags.
- Writeback uses `s_umount` read lock.
- GC runs under `commit_sem` read lock.
- `nospace` and `nospace_rp` flags use memory barriers around updates.
- Assertions enforce bounded request shapes and alignment.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/budget.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/commit.c -->
# File Research: sources/os/linux/linux/fs/ubifs/commit.c

Purpose: UBIFS commit orchestration: transitions journal/index/LPT/orphan state from mutable journal updates into committed on-flash metadata while minimizing latency.

Key APIs:
- `ubifs_bg_thread`
- `ubifs_commit_required`
- `ubifs_request_bg_commit`
- `ubifs_run_commit`
- `ubifs_gc_should_commit`
- Debug helpers: `dbg_old_index_check_init`, `dbg_check_old_index`

Implementation notes:
- Commit is split into commit start under write-locked `commit_sem` and commit end after releasing it, allowing foreground filesystem work during bulk I/O.
- `nothing_to_commit()` avoids unnecessary flash writes when TNC and LPT are clean, except during mount/recovery/remount cases.
- `do_commit()` syncs journal heads, starts GC/log/TNC/LPT/orphan commit phases, captures lprops stats, ends TNC/LPT/orphan commit, checks old index, updates master node fields, completes log/GC/LPT post-commit, and returns state to resting.
- Background thread syncs write buffers and runs background commit when requested.
- Commit state machine includes resting, background, required, running-background, running-required, and broken states.

Concurrency and correctness:
- `cs_lock` protects commit state and wakeups.
- `commit_sem` serializes commit start with journal/TNC/LPT mutation.
- Failed commit marks `COMMIT_BROKEN`, wakes waiters, logs error, and switches UBIFS to read-only error mode.
- `ubifs_run_commit()` upgrades background-running commit to required and waits when another commit is already active.
- Debug old-index checking walks the previous index tree to verify recovery invariants: root level/sqnum, child ordering, key ranges, and old index preservation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/commit.c -->