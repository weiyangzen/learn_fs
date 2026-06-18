# Group Research: subset-b-005768

This grouped report covers the exact source files assigned to `subset-b-005768`. Each section is source-tree-aligned and bounded by reconciliation markers for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/super.c -->
# sources/distributed-fs/ceph-client/fs/super.c

## Purpose
This is the VFS superblock core. It allocates, publishes, finds, reconfigures, freezes, thaws, synchronizes, and tears down `struct super_block` instances. It also provides common helpers for anonymous, nodev, single-instance, keyed, and block-device-backed mounts.

## Important APIs, Types, and Functions
Key exports include `sget_fc()`, `sget()`, `vfs_get_tree()`, `get_tree_nodev()`, `get_tree_single()`, `get_tree_keyed()`, `get_tree_bdev_flags()`, `get_tree_bdev()`, `deactivate_super()`, `deactivate_locked_super()`, `generic_shutdown_super()`, `reconfigure_super()`, `freeze_super()`, `thaw_super()`, `get_anon_bdev()`, `kill_anon_super()`, `kill_block_super()`, `super_setup_bdi()`, and `sb_init_dio_done_wq()`. Internal state is coordinated through global `super_blocks`, `sb_lock`, `s_umount`, `s_count`, `s_active`, `s_flags`, per-superblock shrinkers, LRUs, freeze counters, and optional block-device holder callbacks.

## Control Flow and State
Mount construction flows through `alloc_super()` then `sget_fc()` or `sget()`, which either reuses a matching live superblock or publishes a new nascent one on both the global list and filesystem-type list. `vfs_get_tree()` calls the filesystem `get_tree` operation, requires `fc->root`, then marks the superblock `SB_BORN` with release ordering so waiters can safely see initialized fields. Shutdown reverses this: active references drain through `deactivate_locked_super()`, filesystem `kill_sb()` runs, `generic_shutdown_super()` evicts dentries/inodes and calls `put_super`, and waiters are notified through `SB_DYING`/`SB_DEAD`.

Freeze control is staged by `freeze_super()`: block normal writers, block page faults, sync, block internal filesystem writers, invoke `->freeze_fs`, record holder counts/owner, and leave the filesystem in `SB_FREEZE_COMPLETE`. `thaw_super()` validates holder/owner rules and unwinds the staged rwsems and optional `->unfreeze_fs`.

## Persistence, Dependencies, and Integration
The file sits between mount API/fs_context, block layer holder operations, writeback, shrinkers, fsnotify, fscrypt, security hooks, cgroup writeback, and filesystem-specific `super_operations`. Block-backed mounts open and claim the source bdev, reject frozen/read-only-incompatible devices, set block size and BDI, and register `fs_holder_ops` for block-device death, sync, freeze, and thaw.

## Risks and Test Signals
Risk centers on lifecycle races: nascent superblocks visible before `SB_BORN`, reuse during shutdown, freeze nesting ownership, bdev surprise removal, and deadlocks between shrinker, `s_umount`, `sb_lock`, and block-device locks. Strong signals are mount/reconfigure/unmount stress, filesystem freeze/thaw with nested userspace/kernel holders, bdev removal tests, lockdep, KASAN/RCU checks, sync-after-unmount assertions, and filesystem xfstests that exercise remount RO/RW and `syncfs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sync.c -->
# sources/distributed-fs/ceph-client/fs/sync.c

## Purpose
This file implements high-level VFS synchronization interfaces: global `sync`, per-superblock `syncfs`, per-file `fsync`/`fdatasync`, and range-based `sync_file_range`.

## Important APIs, Types, and Functions
Exports are `sync_filesystem()`, `vfs_fsync_range()`, `vfs_fsync()`, and `sync_file_range()`. System call entry points include `sync`, `syncfs`, `fsync`, `fdatasync`, `sync_file_range`, compat `sync_file_range`, and architecture-ordered `sync_file_range2`. Helpers include `ksys_sync()`, `emergency_sync()`, `sync_inodes_one_sb()`, and `sync_fs_one_sb()`.

## Control Flow and State
`sync_filesystem()` requires the superblock unmount semaphore to be held. It skips read-only filesystems, starts inode writeback, calls `->sync_fs(wait=0)`, submits block-device writeback, waits on inode writeback, calls `->sync_fs(wait=1)`, then waits on the block device. `ksys_sync()` parallelizes global writeback by waking flusher threads first, then iterates superblocks for inode and filesystem metadata sync and finally syncs all block devices in nowait and wait modes. `syncfs(fd)` locks the referenced superblock, calls `sync_filesystem()`, and returns either sync failure or the advanced writeback error sequence for that file.

Per-file flow checks `file->f_op->fsync`, syncs lazytime metadata unless datasync, then delegates to the filesystem. `sync_file_range()` validates flags and range arithmetic, tolerates out-of-addressable-range starts on 32-bit page-cache systems, limits supported inode types, and performs optional wait-before, write/flush, and wait-after phases.

## Persistence, Dependencies, and Integration
This code depends on writeback, block-device sync, errseq reporting, fd lookup helpers, address-space writeback, and filesystem `file_operations`/`super_operations`. It does not persist metadata itself; it orders and delegates persistence to filesystem and block layers.

## Risks and Test Signals
Risk areas include returning stale or lost writeback errors, arithmetic overflow in ranges, unsupported file types, lock ordering with `s_umount`, and assumptions that `sync_file_range` is data-only and does not flush volatile disk caches. Test signals include fstests for fsync/syncfs error reporting, writeback error injection, 32-bit compat syscall tests, block-device failure tests, and tracing that confirms `->sync_fs` wait phases run in the intended order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysctls.c -->
# sources/distributed-fs/ceph-client/fs/sysctls.c

## Purpose
This small file registers shared `/proc/sys/fs` sysctls for overflow UID and GID values used by filesystems that need to map unrepresentable ownership.

## Important APIs, Types, and Functions
It defines `fs_shared_sysctls[]` with `overflowuid` backed by `fs_overflowuid` and `overflowgid` backed by `fs_overflowgid`. Both use `proc_dointvec_minmax`, mode `0644`, minimum `SYSCTL_ZERO`, and maximum `SYSCTL_MAXOLDUID`. `init_fs_sysctls()` registers the table under `"fs"` and is scheduled by `early_initcall`.

## Control Flow and State
At early init, `register_sysctl_init("fs", fs_shared_sysctls)` installs the two integer controls. Runtime reads and writes are handled by the proc sysctl core, which enforces integer bounds.

## Persistence, Dependencies, and Integration
The values are kernel globals rather than on-disk filesystem state. They integrate with VFS ownership mapping paths and proc sysctl infrastructure. Settings are mutable at runtime and may be persisted only by userspace sysctl configuration.

## Risks and Test Signals
Risk is mainly misconfiguration: changing overflow IDs can affect ownership presentation for legacy or unmappable IDs. Tests should verify sysctl registration, permissions, min/max enforcement, and behavior of ownership display paths that fall back to overflow IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysctls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/sysfs/Kconfig

## Purpose
This Kconfig entry controls `CONFIG_SYSFS`, the virtual filesystem used to expose kernel objects, attributes, and relationships to userspace.

## Important APIs, Types, and Functions
The option is `bool "sysfs file system support" if EXPERT`, defaults to `y`, and selects `KERNFS`. Its help text documents sysfs as a core interface for devices, drivers, subsystem tuning, hotplug policy, and boot discovery.

## Control Flow and State
There is no runtime control flow in this file. Build-time selection enables compilation of sysfs sources and the kernfs dependency. Because the prompt is hidden unless `EXPERT`, normal kernel configurations keep sysfs enabled by default.

## Persistence, Dependencies, and Integration
Sysfs is deeply integrated with kobjects, driver core, block device discovery, and userspace device managers. The entry explicitly notes that disabling sysfs can force root-device specification by major/minor numbers.

## Risks and Test Signals
Disabling sysfs is high blast radius and mainly relevant to constrained embedded builds. Build tests should cover both default-enabled and expert-disabled configurations, while runtime boot tests should verify device discovery and hotplug consumers when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/sysfs/Makefile

## Purpose
This Makefile defines the object composition of the sysfs virtual filesystem.

## Important APIs, Types, and Functions
`obj-y := file.o dir.o symlink.o mount.o group.o` means sysfs is built into the kernel image when the containing Kconfig selects the directory. It composes sysfs from regular/binary file handling, directory management, symlinks, mount initialization, and attribute groups.

## Control Flow and State
There is no runtime logic. Build ordering is simple and all listed objects are always included when sysfs is compiled.

## Persistence, Dependencies, and Integration
The build depends on kernfs and kobject infrastructure selected by `CONFIG_SYSFS`. The object list mirrors the public sysfs API surface used by driver core and subsystems.

## Risks and Test Signals
Risk is accidental omission of an object when sysfs APIs move. Build tests with `CONFIG_SYSFS=y` should catch undefined references, while allmodconfig/tinyconfig-style jobs catch dependency drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/sysfs/dir.c

## Purpose
This file implements core sysfs directory operations for kobjects: create, remove, rename, move, and mount-point directories.

## Important APIs, Types, and Functions
It defines global `sysfs_symlink_target_lock`, duplicate-name diagnostics via `sysfs_warn_dup()`, and public helpers `sysfs_create_dir_ns()`, `sysfs_remove_dir()`, `sysfs_rename_dir_ns()`, `sysfs_move_dir_ns()`, `sysfs_create_mount_point()`, and `sysfs_remove_mount_point()`. The backing implementation is kernfs directory creation/removal.

## Control Flow and State
Directory creation selects the parent from `kobj->parent->sd` or `sysfs_root_kn`, obtains ownership via `kobject_get_ownership()`, then calls `kernfs_create_dir_ns()` with the kobject as private data. On success, `kobj->sd` becomes the kernfs node. Removal first clears `kobj->sd` under `sysfs_symlink_target_lock` to prevent symlink operations from dereferencing a freed target, then removes the kernfs directory.

Rename and move are thin wrappers over `kernfs_rename_ns()`, with namespace support. Mount points are special always-empty kernfs directories under a parent kobject, useful for exposing filesystem mount anchors such as tracefs.

## Persistence, Dependencies, and Integration
Sysfs directories are virtual state derived from live kobjects. Dependencies include kernfs, kobject ownership, namespace tags, and symlink code that observes `kobj->sd`. Integration is with driver core and any subsystem publishing kobjects.

## Risks and Test Signals
Important races involve symlinks to kobjects being removed concurrently, duplicate names, missing parent `sd`, and namespace moves. Test signals include kobject add/remove stress, lockdep for `sysfs_symlink_target_lock`, duplicate filename warning paths, namespace-tagged directory lookups, and module unload tests that remove sysfs directories while links exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/file.c -->
# sources/distributed-fs/ceph-client/fs/sysfs/file.c

## Purpose
This file implements sysfs regular text attributes, binary attributes, notifications, ownership/mode changes, active-protection helpers, and safe emit helpers.

## Important APIs, Types, and Functions
Public APIs include `sysfs_create_file_ns()`, `sysfs_create_files()`, `sysfs_add_file_to_group()`, `sysfs_chmod_file()`, `sysfs_break_active_protection()`, `sysfs_unbreak_active_protection()`, `sysfs_remove_file_ns()`, `sysfs_remove_file_self()`, `sysfs_remove_files()`, `sysfs_remove_file_from_group()`, `sysfs_create_bin_file()`, `sysfs_remove_bin_file()`, `sysfs_link_change_owner()`, `sysfs_file_change_owner()`, `sysfs_change_owner()`, `sysfs_emit()`, `sysfs_emit_at()`, `sysfs_bin_attr_simple_read()`, and `sysfs_notify()`. Internal kernfs callbacks adapt `sysfs_ops->show/store` and `bin_attribute` read/write/mmap/llseek.

## Control Flow and State
Regular text reads normally use seq_file through `sysfs_kf_seq_show()`, which allocates a page-sized buffer and calls `ops->show(kobj, attr, buf)`. Preallocated attributes instead call `sysfs_kf_read()` directly into kernfs' prealloc buffer. Writes call `ops->store()`. Binary files enforce optional size bounds and delegate read/write/mmap/llseek/open to `bin_attribute` callbacks.

`sysfs_add_file_mode_ns()` selects kernfs ops based on available show/store and `SYSFS_PREALLOC`; `sysfs_add_bin_file_mode_ns()` selects binary ops based on callback capabilities. Removal uses `kernfs_remove_by_name[_ns]`. Ownership changes look up kernfs nodes and call `kernfs_setattr()`, with `sysfs_change_owner()` also propagating to default groups.

## Persistence, Dependencies, and Integration
Sysfs file contents are generated from live kernel state, not stored on disk. Dependencies include kobject `ktype->sysfs_ops`, kernfs active protection, lockdep keys in attributes, seq_file, and driver-core default groups.

## Risks and Test Signals
Risk points are invalid `show()` lengths, missing `sysfs_ops`, attributes disappearing during self-removal, binary bounds mistakes, lockdep class mistakes, and exposing mutable subsystem state without proper subsystem locking. Tests should include sysfs read/write ABI checks, self-deleting attributes, binary file bounds/mmap paths, `sysfs_notify()` polling, ownership propagation, and lockdep-enabled sysfs stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/group.c -->
# sources/distributed-fs/ceph-client/fs/sysfs/group.c

## Purpose
This file manages sysfs attribute groups: creating, updating, removing, merging, adding links to groups, and changing group ownership.

## Important APIs, Types, and Functions
Public helpers include `sysfs_create_group()`, `sysfs_create_groups()`, `sysfs_update_group()`, `sysfs_update_groups()`, `sysfs_remove_group()`, `sysfs_remove_groups()`, `sysfs_merge_group()`, `sysfs_unmerge_group()`, `sysfs_add_link_to_group()`, `sysfs_remove_link_from_group()`, `compat_only_sysfs_link_entry_to_kobj()`, `sysfs_group_change_owner()`, and `sysfs_groups_change_owner()`. Internal helpers are `create_files()`, `remove_files()`, `internal_create_group()`, and ownership walkers.

## Control Flow and State
Group creation optionally creates a named subdirectory, with visibility decided by the first visible attribute and group callbacks. `create_files()` iterates text and binary attributes, evaluates per-attribute visibility and binary size callbacks, masks permissions to allowed sysfs bits, and creates kernfs files. On error it unwinds previously added files. Update mode removes existing files first, recalculates visibility/mode, and can remove the group directory if it becomes invisible.

Merging adds extra attributes to an existing named group with rollback on partial failure. Link helpers resolve the group directory and call sysfs symlink functions. Ownership changes update the group node and each visible member's kernfs attributes.

## Persistence, Dependencies, and Integration
Group state mirrors `struct attribute_group` declarations used throughout driver core and subsystem code. It depends on file.c helpers, symlink.c helpers, kernfs, kobject ownership, and visibility callbacks.

## Risks and Test Signals
Risks include partial group creation, visibility callbacks changing between update and removal, invalid permissions, missing named groups during merge/unmerge, and target kobject removal during compatibility symlink creation. Test signals include default group creation/unwind tests, dynamic visibility updates, binary attribute size callbacks, ownership propagation tests, and duplicate-name warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/mount.c -->
# sources/distributed-fs/ceph-client/fs/sysfs/mount.c

## Purpose
This file initializes, mounts, and tears down the sysfs filesystem using kernfs, including namespace-aware mount context setup.

## Important APIs, Types, and Functions
It defines `sysfs_root`, exported internal `sysfs_root_kn`, filesystem type `sysfs_fs_type`, and init function `sysfs_init()`. Context operations are `sysfs_init_fs_context()`, `sysfs_get_tree()`, and `sysfs_fs_context_free()`. `sysfs_kill_sb()` wraps kernfs superblock cleanup and namespace release.

## Control Flow and State
`sysfs_init()` creates a kernfs root with extra open permission checks, records its root node, and registers the `sysfs` filesystem. Mount context setup rejects non-kernel mounts when current network namespace policy forbids mounting, allocates `kernfs_fs_context`, grabs the current net namespace tag, sets `fc->global = true`, and if a namespace exists, switches `fc->user_ns` to the namespace owner's user namespace. `sysfs_get_tree()` delegates to `kernfs_get_tree()` and marks newly created superblocks user-namespace visible.

## Persistence, Dependencies, and Integration
Sysfs mount state is virtual kernfs state rooted at `sysfs_root`. It depends on kobject namespace operations, network namespace tags, fs_context, kernfs, and VFS filesystem registration. `FS_USERNS_MOUNT` allows user namespace mounts subject to sysfs namespace checks.

## Risks and Test Signals
Risk centers on namespace lifetime, user namespace selection, mount permission policy, and correct release of namespace tags on both context free and superblock kill. Tests should cover sysfs mount from initial and non-initial network/user namespaces, failed context allocation paths, kernfs root registration failures, and unmount namespace reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/sysfs/symlink.c

## Purpose
This file implements sysfs symlink creation, deletion, and rename operations between kobjects or from a kernfs directory to a kobject.

## Important APIs, Types, and Functions
Public helpers include `sysfs_create_link_sd()`, `sysfs_create_link()`, `sysfs_create_link_nowarn()`, `sysfs_delete_link()`, `sysfs_remove_link()`, and `sysfs_rename_link_ns()`. The internal `sysfs_do_create_link_sd()` handles target lookup and duplicate warning behavior.

## Control Flow and State
Creation validates name and parent, then acquires `sysfs_symlink_target_lock` while reading `target_kobj->sd`. If the target has a kernfs node, it takes a kernfs reference, drops the lock, and creates a kernfs link. This is paired with `sysfs_remove_dir()` clearing `kobj->sd` under the same lock. Deletion either removes by plain name or, for `sysfs_delete_link()`, derives the target namespace from the target `sd` when the parent is namespace-enabled. Rename finds the existing link in the target namespace, verifies it is a link and still points to the expected target kobject, then calls `kernfs_rename_ns()`.

## Persistence, Dependencies, and Integration
Symlinks are virtual kernfs nodes. The code depends on kobject directory lifetime, kernfs link semantics, namespace tags, and the directory code's synchronization contract.

## Risks and Test Signals
Risks include target removal races, stale namespace selection, renaming a link that no longer points to the expected kobject, and duplicate link names. Useful tests include concurrent kobject unregister/link create, namespace-tagged delete/rename, duplicate-name warning coverage, and module unload paths that remove links and target directories in varied orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/sysfs.h -->
# sources/distributed-fs/ceph-client/fs/sysfs/sysfs.h

## Purpose
This internal header shares private sysfs declarations across the sysfs implementation files.

## Important APIs, Types, and Functions
It exposes `sysfs_root_kn` from mount code, `sysfs_symlink_target_lock` and `sysfs_warn_dup()` from directory code, file creation internals `sysfs_add_file_mode_ns()` and `sysfs_add_bin_file_mode_ns()`, and `sysfs_create_link_sd()` from symlink code.

## Control Flow and State
There is no runtime control flow. The header establishes internal coupling between sysfs components while keeping implementation helpers out of the public sysfs API header.

## Persistence, Dependencies, and Integration
It depends on `<linux/sysfs.h>` for public structures such as `attribute`, `bin_attribute`, and namespace types. The declarations coordinate kernfs root access, symlink race protection, and low-level file creation used by group code.

## Risks and Test Signals
Risk is interface drift: changing one implementation without updating this header causes build failures or mismatched helper semantics. Build coverage of `fs/sysfs/*.o` is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/sysfs/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tests/binfmt_elf_kunit.c -->
# sources/distributed-fs/ceph-client/fs/tests/binfmt_elf_kunit.c

## Purpose
This KUnit test validates ELF loader helper `total_mapping_size()` for PT_LOAD program headers.

## Important APIs, Types, and Functions
The suite defines `total_mapping_size_test()`, `binfmt_elf_test_cases`, and `binfmt_elf_test_suite`. It uses `KUNIT_EXPECT_EQ()` to compare computed mapping spans against expected values.

## Control Flow and State
The test builds several `struct elf_phdr` arrays: empty/no-load cases, a real-world `/bin/mount`-style program header set, and an unordered set of PT_LOAD entries. It checks that no-load inputs report zero and that normal and unordered PT_LOAD inputs produce the same total mapping size.

## Persistence, Dependencies, and Integration
This is test-only code. It depends on KUnit and on the binfmt ELF implementation being compiled into the test translation unit or otherwise making `total_mapping_size()` visible to the test configuration.

## Risks and Test Signals
The targeted risk is ELF mapping-size calculation depending on header order or counting non-loadable segments. The test signal is precise: failures indicate regressions in how the loader determines the virtual span reserved for PT_LOAD mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tests/binfmt_elf_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tests/exec_kunit.c -->
# sources/distributed-fs/ceph-client/fs/tests/exec_kunit.c

## Purpose
This KUnit suite validates `bprm_stack_limits()`, which computes exec argument/environment stack limits and rejects unsafe counts.

## Important APIs, Types, and Functions
The test defines `struct bprm_stack_limits_result`, a table of `linux_binprm` input cases, `exec_test_bprm_stack_limits()`, and suite metadata named `"exec"`. It checks constants `_STK_LIM`, `ARG_MAX`, and `MAX_ARG_STRINGS`, then validates return codes and, under `CONFIG_MMU`, calculated `bprm.argmin`.

## Control Flow and State
Inputs cover negative `argc`/`envc`, maximum string counts, overflow-prone pointer count combinations, pathological `bprm->p`, zero stack rlimit raised to `ARG_MAX`, exact pointer capacity boundaries, and the `_STK_LIM` three-quarter cap. Each table row copies the `linux_binprm`, calls `bprm_stack_limits()`, and compares result/error fields.

## Persistence, Dependencies, and Integration
This is test-only code depending on KUnit and exec internals. It has no persistent state; it exercises pure limit calculation over stack pointer and rlimit fields.

## Risks and Test Signals
The suite targets security-sensitive overflow and bounds risks in exec argument setup, especially 32-bit arithmetic bypasses and off-by-one pointer reservations. Passing tests signal that invalid counts produce `-E2BIG` and valid boundary cases compute expected `argmin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tests/exec_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/timerfd.c -->
# sources/distributed-fs/ceph-client/fs/timerfd.c

## Purpose
This file implements Linux `timerfd`, exposing hrtimer/alarmtimer expirations through file descriptors that can be read, polled, configured, and checkpoint/restore-adjusted.

## Important APIs, Types, and Functions
Core state is `struct timerfd_ctx`: hrtimer or alarm, interval, waitqueue, tick count, clock id, cancel-on-set tracking, RCU head, and locks. System calls are `timerfd_create`, `timerfd_settime`, `timerfd_gettime`, and 32-bit time compat variants. Important helpers include `timerfd_triggered()`, `timerfd_clock_was_set()`, `timerfd_resume()`, `timerfd_setup_cancel()`, `timerfd_setup()`, `timerfd_read_iter()`, `timerfd_poll()`, and optional `TFD_IOC_SET_TICKS` ioctl.

## Control Flow and State
Creation validates flags and supported clocks, requires `CAP_WAKE_ALARM` for alarm clocks, allocates context, initializes timer backend, captures realtime/monotonic offset, and returns an anonymous inode file. `timerfd_settime` validates flags/spec, ensures the fd is a timerfd, sets cancel-on-set list membership for realtime absolute cancelable timers, cancels any running timer, reports old remaining time, then programs the new timer. Expiration increments `ticks`, marks `expired`, and wakes poll waiters. Reads block unless nonblocking, handle cancel-on-set as `-ECANCELED`, return an eight-byte tick count, and lazily forward/restart periodic timers to avoid callback-side denial-of-service from tiny intervals.

## Persistence, Dependencies, and Integration
Timerfd state lives in the file private data and dies on release. It integrates with hrtimer, alarmtimer, time namespaces, anonymous inodes, poll, proc fdinfo, checkpoint/restore, RCU, and timekeeping notifications. The global cancel list is walked when realtime changes or after resume.

## Risks and Test Signals
Risks include races between settime/read/cancel/release, cancel-on-set semantics around time namespace offsets, periodic overrun accounting, capability checks for wake alarms, and returning partial reads. Test signals include timerfd syscall tests, poll/read nonblocking cases, realtime set cancellation, suspend/resume behavior, CRIU tick injection, compat time32 tests, lockdep, and RCU lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/timerfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tracefs/Makefile -->
# sources/distributed-fs/ceph-client/fs/tracefs/Makefile

## Purpose
This Makefile builds tracefs, the tracing virtual filesystem.

## Important APIs, Types, and Functions
It sets `tracefs-objs := inode.o` and adds `event_inode.o`, then includes `tracefs.o` in `obj-$(CONFIG_TRACING)`.

## Control Flow and State
There is no runtime logic. Build composition ensures both the base tracefs filesystem and dynamic eventfs implementation are linked when tracing is enabled.

## Persistence, Dependencies, and Integration
The build depends on `CONFIG_TRACING`. It integrates tracefs into the kernel as the filesystem used by ftrace and event tracing.

## Risks and Test Signals
Risk is build dependency drift if eventfs or inode symbols are split incorrectly. Build testing with `CONFIG_TRACING=y` and disabled tracing configurations verifies composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tracefs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tracefs/event_inode.c -->
# sources/distributed-fs/ceph-client/fs/tracefs/event_inode.c

## Purpose
This file implements eventfs, the dynamic tracefs subtree that lazily creates inodes and dentries for tracing event directories and files from tracing metadata.

## Important APIs, Types, and Functions
Key exported/internal APIs are `eventfs_create_events_dir()`, `eventfs_create_dir()`, `eventfs_remove_dir()`, `eventfs_remove_events_dir()`, `eventfs_remount()`, `eventfs_d_release()`, `eventfs_remount_lock()`, and `eventfs_remount_unlock()`. Important structures are `eventfs_inode`, `eventfs_attr`, and `eventfs_root_inode`. Synchronization uses `eventfs_mutex`, static SRCU `eventfs_srcu`, krefs, and RCU list removal.

## Control Flow and State
Eventfs stores metadata in `eventfs_inode` objects rather than creating all dentries immediately. Lookup under an eventfs directory searches child eventfs directories first, then file entries, invokes the entry callback for file mode/data/fops, and creates an inode/dentry only on demand. Directory iteration emits dynamic file names and child directories while using SRCU and mutex checks to avoid freed metadata. Attribute changes save mode/uid/gid overrides in per-directory or per-entry caches so recreated dentries preserve user changes.

Top-level `eventfs_create_events_dir()` creates a persistent `events` dentry in tracefs, assigns eventfs inode state to `tracefs_inode.private`, and stores default ownership from the parent. Removal recursively marks eventfs metadata freed, deletes list links with RCU, invalidates the top dentry, and makes it discardable.

## Persistence, Dependencies, and Integration
Eventfs state is in-memory tracing metadata. It depends on tracefs inode allocation, security lockdown, fsnotify, VFS lookup/readdir/setattr, SRCU, krefs, and tracing-provided `eventfs_entry` callbacks. Remount integration resets inherited UID/GID overrides when tracefs remount options request that.

## Risks and Test Signals
Risk concentrates in lifetime and locking: callbacks are called under eventfs locks, dentry `d_fsdata` holds krefs, `is_freed` must be observed correctly, and readdir must remain stable while events disappear. Tests should stress event registration/removal during lookup/readdir/open, remount UID/GID changes, chmod/chown persistence on dynamic files, lockdown behavior, and lockdep/SRCU/RCU validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tracefs/event_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tracefs/inode.c -->
# sources/distributed-fs/ceph-client/fs/tracefs/inode.c

## Purpose
This file implements the tracefs filesystem: mount context handling, inode/superblock operations, permission inheritance, creation/removal helpers, tracing instance directory support, and initialization.

## Important APIs, Types, and Functions
Public helpers include `tracefs_create_file()`, `tracefs_create_dir()`, `tracefs_create_instance_dir()`, `tracefs_remove()`, `tracefs_initialized()`, and internal creation helpers `tracefs_start_creating()`, `tracefs_end_creating()`, `tracefs_failed_creating()`, `tracefs_get_inode()`. It defines `tracefs_fs_info`, `tracefs_inode`, super operations, dentry operations, fs_context operations, and filesystem type `trace_fs_type`.

## Control Flow and State
Mount setup parses `uid`, `gid`, and octal `mode`, fills a single-instance superblock through `get_tree_single()`, and applies options to the root inode. Remount copies new options, syncs the filesystem, updates root mode/ownership, and propagates uid/gid reset through all tracefs inodes plus eventfs metadata. Permission and getattr lazily call `set_tracefs_inode_owner()` so inodes inherit from the mount root or tracing instance root unless explicitly chowned/chgrped.

Creation helpers pin the tracefs mount, select the parent/root, call simplefs creation primitives, allocate tracefs inodes, set operation tables, ownership, private data, and fsnotify events. The special instances directory allows user `mkdir/rmdir`; it drops inode locks while invoking tracing callbacks. Removal pins the filesystem and uses `simple_recursive_removal()` with mount ref release per victim.

## Persistence, Dependencies, and Integration
Tracefs is in-memory pseudo filesystem state. It depends on VFS simplefs helpers, fs_context parser, security lockdown, sysfs mount point creation under `kernel_kobj/tracing`, eventfs, and tracing subsystem callbacks. Initialization creates a slab cache, sysfs mount point, and registers the filesystem at `core_initcall`.

## Risks and Test Signals
Risks include remount propagation races, tracefs inode list RCU handling, permission inheritance surprises, instance mkdir/rmdir lock dropping, mount pin leaks, and lockdown bypasses. Tests should cover tracefs mount/remount options, chown/chmod inheritance, instance creation/removal, eventfs interaction, recursive removal, lockdown mode, and lockdep/RCU checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tracefs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tracefs/internal.h -->
# sources/distributed-fs/ceph-client/fs/tracefs/internal.h

## Purpose
This header defines private tracefs/eventfs structures, flags, and helper declarations shared by tracefs implementation files.

## Important APIs, Types, and Functions
It defines tracefs flags `TRACEFS_EVENT_INODE`, `TRACEFS_GID_PERM_SET`, `TRACEFS_UID_PERM_SET`, and `TRACEFS_INSTANCE_INODE`; `struct tracefs_inode`; `struct eventfs_attr`; `struct eventfs_inode`; and inline `get_tracefs()`. It declares creation helpers and eventfs remount/dentry release hooks.

## Control Flow and State
There is no runtime control flow. The state model is important: `tracefs_inode` embeds the VFS inode plus list/flags/private metadata, while `eventfs_inode` stores dynamic event directory entries, child lists, saved attributes, kref, freed/events flags, and stable directory inode number.

## Persistence, Dependencies, and Integration
The header couples eventfs and tracefs without exposing these internals to external users. It depends on VFS inode, list, kref, `eventfs_entry`, uid/gid types, and dentry declarations.

## Risks and Test Signals
Risks are structural invariants: flags must match remount/drop behavior, `private` must point to the expected owner/eventfs object, and `eventfs_inode` lifetime must match dentry references. Build tests and runtime tracefs/eventfs stress are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/tracefs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/ubifs/Kconfig

## Purpose
This Kconfig file defines UBIFS build options, compression support, atime policy, xattrs/security labels, and authentication.

## Important APIs, Types, and Functions
The main option is `UBIFS_FS`, a tristate filesystem depending on `MTD_UBI`. It selects CRC and crypto helpers as needed. Suboptions include `UBIFS_FS_ADVANCED_COMPR`, `UBIFS_FS_LZO`, `UBIFS_FS_ZLIB`, `UBIFS_FS_ZSTD`, `UBIFS_ATIME_SUPPORT`, `UBIFS_FS_XATTR`, `UBIFS_FS_SECURITY`, and `UBIFS_FS_AUTHENTICATION`.

## Control Flow and State
This is build-time configuration. Compressor selections affect which compression algorithms are compiled and therefore which existing UBIFS images can be read. Authentication selects keys, HMAC, and system data verification support but intentionally does not auto-select a hash algorithm.

## Persistence, Dependencies, and Integration
UBIFS integrates with UBI/MTD, crypto compression, fs encryption, xattrs, LSM security labels, keyrings, and data verification. Options affect on-media compatibility, especially compressors and authentication.

## Risks and Test Signals
Risks include building without a compressor required by deployed volumes, enabling atime and increasing flash wear, enabling security labels without xattrs, and authentication misconfiguration without a hash algorithm/key. Build matrix tests and mount tests against images using each compressor/authentication mode are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/Makefile -->
# sources/distributed-fs/ceph-client/fs/ubifs/Makefile

## Purpose
This Makefile composes the UBIFS filesystem object from its implementation modules.

## Important APIs, Types, and Functions
`obj-$(CONFIG_UBIFS_FS) += ubifs.o` builds UBIFS as built-in or module. `ubifs-y` includes shrinker, journal, file, dir, superblock, IO, TNC, master, scan, replay, log, commit, GC, orphan, budget, find, commit helpers, compression, LPT/LPROPS, recovery, ioctl, debug, misc, and sysfs support. Conditional objects add encryption, xattr, and authentication support.

## Control Flow and State
There is no runtime logic. Object composition reflects UBIFS subsystems and controls whether `crypto.o`, `xattr.o`, and `auth.o` are linked.

## Persistence, Dependencies, and Integration
The Makefile integrates UBIFS with Kconfig-selected VFS, UBI, crypto, xattr, and authentication functionality.

## Risks and Test Signals
Risks are missing objects under conditional configs or unresolved symbols when feature options are toggled. Build tests across `CONFIG_UBIFS_FS=m/y`, xattr, encryption, and authentication combinations provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/auth.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/auth.c

## Purpose
This file implements UBIFS authentication helpers: node hashes, HMAC insertion/verification, authentication-node preparation, superblock signature verification, key setup, and cleanup.

## Important APIs, Types, and Functions
Important functions include `__ubifs_node_calc_hash()`, `ubifs_prepare_auth_node()`, `__ubifs_hash_get_desc()`, `ubifs_bad_hash()`, `__ubifs_node_check_hash()`, `ubifs_sb_verify_signature()`, `ubifs_init_authentication()`, `__ubifs_exit_authentication()`, `__ubifs_node_insert_hmac()`, `__ubifs_node_verify_hmac()`, `__ubifs_shash_copy_state()`, `ubifs_hmac_wkm()`, and `ubifs_hmac_zero()`. It uses `crypto_shash`, logon keys, PKCS#7 verification, and fixed-size UBIFS hash/HMAC arrays.

## Control Flow and State
Initialization validates `auth_hash_name`, maps it to a hash algorithm, builds `hmac(<hash>)`, requests the configured logon key, allocates hash and HMAC transforms, checks digest sizes against UBIFS limits, sets the HMAC key from the key payload, marks `c->authenticated`, and creates the running log hash descriptor. Node hash calculation covers the node length from the common header. Auth-node preparation finalizes a copied hash state, HMACs that digest, fills `UBIFS_AUTH_NODE`, and prepares the UBIFS node header.

HMAC insertion/verification hashes a node excluding magic/CRC and the embedded HMAC field, using constant-time comparison for verification. Superblock signature verification scans behind the superblock node for a `UBIFS_SIG_NODE`, validates length/type, and verifies a PKCS#7 signature over the superblock.

## Persistence, Dependencies, and Integration
Authentication state lives in `ubifs_info` crypto transforms and descriptors, while hashes/HMACs/signatures are persisted in UBIFS on-flash nodes. Dependencies include the kernel crypto API, keyrings, asymmetric verification, UBIFS scan/read/write node helpers, and mount-time superblock handling.

## Risks and Test Signals
Risks include wrong key type or revoked key handling, digest size mismatch, HMAC offset mistakes, non-constant comparisons, malformed signature nodes, and failing to clean transforms on partial init errors. Tests should mount authenticated images with correct/wrong keys, corrupt node hashes/HMACs, validate PKCS#7 signed superblocks, exercise memory-failure paths, and run fuzzed scan data through signature parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/budget.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/budget.c

## Purpose
This file implements UBIFS space budgeting: pessimistic reservation of flash space for data, dirty data, and index growth, plus free-space reporting.

## Important APIs, Types, and Functions
Key APIs are `ubifs_budget_space()`, `ubifs_release_budget()`, `ubifs_convert_page_budget()`, `ubifs_release_dirty_inode_budget()`, `ubifs_calc_min_idx_lebs()`, `ubifs_calc_available()`, `ubifs_reported_space()`, `ubifs_get_free_space_nolock()`, and `ubifs_get_free_space()`. Important helpers include `make_free_space()`, `run_gc()`, `shrink_liability()`, `do_budget_space()`, and growth calculators for index/data/dirty-data.

## Control Flow and State
Budget requests describe new pages/inodes/dentries and dirtied existing objects. `ubifs_budget_space()` validates request shape, computes index/data/dirty growth, adds those values under `space_lock`, and calls `do_budget_space()`. That function reserves enough index LEBs for the in-the-gaps commit method, computes available data space after index, GC, journal-head, deletion, dead, and dark-space reservations, and enforces reserved-pool permissions. On failure and non-fast requests, UBIFS tries to shrink liability by writeback, run GC, and run commit, retrying a bounded number of times.

`ubifs_release_budget()` subtracts reservations after the operation and moves index growth into `uncommitted_idx`, which commit later clears. Page-budget conversion changes a new-page reservation into dirty-page liability. Free-space reporting converts raw available bytes into user-visible capacity after UBIFS node and index overhead.

## Persistence, Dependencies, and Integration
Budget state is in-memory `c->bi`, LEB property stats, reserved pool IDs, and counters protected by `space_lock`, `lp_mutex`, and `commit_sem`. It integrates with writeback, garbage collection, commit, LPT/lprops accounting, VFS statfs, and permission checks (`CAP_SYS_RESOURCE`, fsuid/group).

## Risks and Test Signals
Risks include overcommitting flash, false ENOSPC, reserved-pool bypass, stale `nospace` flags, 64-bit arithmetic errors, and deadlock between writeback/GC/commit paths. Tests should include fill-volume workloads, random writes with compression variance, reserved-pool permission tests, GC/commit stress, power-cut recovery after heavy budgeting, and statfs free-space sanity against actual writable capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/budget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/commit.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/commit.c

## Purpose
This file orchestrates UBIFS commits, which atomically write index and LEB-property updates and make the journal empty/replayable.

## Important APIs, Types, and Functions
Core functions are `ubifs_run_commit()`, `ubifs_bg_thread()`, `ubifs_commit_required()`, `ubifs_request_bg_commit()`, `ubifs_gc_should_commit()`, and internal `do_commit()`, `run_bg_commit()`, `wait_for_commit()`, and `nothing_to_commit()`. Debug support includes `dbg_old_index_check_init()` and `dbg_check_old_index()`.

## Control Flow and State
Commits are split into start and end phases. With `commit_sem` held for writing, `do_commit()` syncs journal heads, increments commit number, starts GC/log/TNC/LPT/orphan commit phases, captures LEB stats, then releases `commit_sem` so normal journal activity can resume while heavier end I/O runs. End phase writes TNC, LPT, and orphan updates, validates the old index in debug builds, updates the master node fields for root, log tail, index head, LPT heads, stats, and orphan flags, then finalizes log, GC, and LPT post-commit processing.

Commit state is tracked under `cs_lock` using states such as resting, background, required, running background, running required, and broken. `ubifs_run_commit()` either waits for an in-progress required commit or promotes/runs one synchronously. The background thread handles write-buffer sync and background commits when `need_bgt` is set.

## Persistence, Dependencies, and Integration
The commit persists UBIFS index root, LPT locations, log tail, orphan state, and master-node statistics. It integrates with journal heads, write buffers, GC, log, TNC, LPT, orphan subsystem, debug index checking, freezer-aware kthread behavior, and RO-error transition handling.

## Risks and Test Signals
Risks are severe: partial commit ordering bugs can break power-cut recovery; state-machine races can wait forever or allow concurrent commit corruption; failures must force read-only mode. Tests should include power-cut/replay simulations, concurrent writers plus background commit, GC-triggered commits, forced I/O errors, freezer suspend/resume with background thread, debug old-index checks, and mount-after-crash validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/commit.c -->
