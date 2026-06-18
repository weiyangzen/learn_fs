# Group Research: group_1086_linux_stable_sources_os_linux_linux_stable_fs_super_c_sources_os_li_cd3248e0886b

Scope: `Docs/research_subset_a`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/super.c

Purpose: Implements core VFS superblock lifecycle, lookup/reuse, mount tree acquisition, shutdown, block-device superblock integration, remount/reconfigure handling, filesystem iteration, freeze/thaw, emergency operations, anonymous device allocation, and per-superblock cache shrinking.

Key responsibilities:
- Maintains global superblock lists and per-filesystem `fs_supers` membership under `sb_lock`.
- Allocates and initializes `struct super_block`, including shrinkers, LRUs, freeze semaphores, namespace state, security state, backing-dev defaults, and lockdep classes.
- Provides active and temporary superblock reference management through `s_active`, `s_count`, `deactivate_super()`, `deactivate_locked_super()`, `put_super()`, and `grab_super()`.
- Publishes superblocks via `sget_fc()` and legacy `sget()`, including namespace compatibility and exclusive mount checks.
- Implements `generic_shutdown_super()`, `kill_anon_super()`, and `kill_block_super()` cleanup paths.
- Provides `get_tree_nodev()`, `get_tree_single()`, `get_tree_keyed()`, `get_tree_bdev_flags()`, `get_tree_bdev()`, and `vfs_get_tree()` helpers for filesystem mount setup.
- Handles block-device ownership callbacks through `fs_holder_ops`: mark-dead, sync, freeze, and thaw.
- Implements `reconfigure_super()` for remount flag changes, read-only transitions, security remount checks, and filesystem-specific reconfigure callbacks.
- Implements emergency remount, emergency thaw, system-wide freeze/thaw, and direct-IO completion workqueue creation.
- Implements `freeze_super()` and `thaw_super()` state transitions across write, pagefault, internal-FS, and complete freeze levels.

Important interactions:
- Calls into filesystem `super_operations`, fs_context callbacks, security hooks, fscrypt cleanup, fsnotify, cgroup writeback, writeback/sync, block layer, bdi, shrinker, and dcache/inode eviction code.
- `super_wake()` and `super_lock()` coordinate `SB_BORN`, `SB_DYING`, and `SB_DEAD` visibility for concurrent mount/shutdown paths.
- Block-device mounting uses `lookup_bdev()`, `bdev_file_open_by_dev()`, freeze-count checks, and holder callbacks.
- Freeze/thaw depends on `s_writers` counters and may distinguish userspace, kernel, nested block-device, and exclusive kernel freeze owners.

Notable invariants and risks:
- Newly allocated superblocks are published before `SB_BORN`; walkers must wait for born or dying state.
- `s_umount` ordering and `sb_start_write()` ordering drive the careful unlock/relock behavior in freeze and remount paths.
- Reusing superblocks across user namespaces is rejected unless allowed by the filesystem context.
- Freeze counts and owner semantics are subtle: all freeze holders share one active reference, and thaw only fully unlocks when both kernel and userspace counts reach zero.
- Shutdown poisons busy inodes after unmount corruption detection to make later misuse fail loudly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sync.c -->
# File Research: sources/os/linux/linux-stable/fs/sync.c

Purpose: Provides high-level sync, fsync, fdatasync, syncfs, emergency sync, and sync_file_range implementations.

Key responsibilities:
- `sync_filesystem()` writes back inode data, calls filesystem `sync_fs()` in nowait and wait phases, and syncs the backing block device.
- `ksys_sync()` implements global sync by waking flusher threads, iterating superblocks, syncing filesystem metadata, and syncing block devices.
- Implements syscalls: `sync`, `syncfs`, `fsync`, `fdatasync`, `sync_file_range`, compat `sync_file_range`, and `sync_file_range2`.
- `vfs_fsync_range()` and `vfs_fsync()` dispatch to file `f_op->fsync`, including lazytime sync for full fsync.
- `emergency_sync()` schedules async work that runs multiple sync passes.

Important interactions:
- Uses `iterate_supers()`, `sync_inodes_sb()`, `writeback_inodes_sb()`, `sync_bdevs()`, and block-device sync helpers.
- `syncfs()` reports both sync failure and accumulated writeback errors through `errseq_check_and_advance()`.

Notable invariants and risks:
- `sync_filesystem()` requires `s_umount` protection and skips read-only superblocks.
- `sync_file_range()` deliberately does not sync metadata or flush disk caches; it validates range arithmetic and allowed file types before page-cache operations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sysctls.c -->
# File Research: sources/os/linux/linux-stable/fs/sysctls.c

Purpose: Registers shared `/proc/sys/fs` sysctls used by multiple filesystems.

Key responsibilities:
- Defines `overflowuid` and `overflowgid` sysctl entries.
- Binds them to `fs_overflowuid` and `fs_overflowgid`.
- Uses `proc_dointvec_minmax` with bounds from zero to `SYSCTL_MAXOLDUID`.
- Registers the table under `fs` at early init.

Important interactions:
- Exposes fallback UID/GID behavior through the sysctl subsystem.
- Runs via `early_initcall(init_fs_sysctls)`.

Notable invariants and risks:
- The table is intentionally small and shared rather than filesystem-specific.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sysctls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/sysfs/Kconfig

Purpose: Defines the kernel configuration option for sysfs.

Key responsibilities:
- Declares `CONFIG_SYSFS` as a boolean option, default enabled.
- Selects `KERNFS`.
- Documents sysfs as the virtual filesystem for kernel objects, attributes, and relationships.
- Notes userspace dependencies such as hotplug and root device discovery.

Important interactions:
- Sysfs can be disabled only under expert-style configuration, mainly for constrained embedded systems.
- The option supports driver core, block device discovery, and policy agents relying on sysfs.

Notable invariants and risks:
- Disabling sysfs can require specifying root devices by major/minor numbers and may break userspace agents that assume `/sys`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/sysfs/Makefile

Purpose: Builds the sysfs virtual filesystem implementation.

Key responsibilities:
- Adds `file.o`, `dir.o`, `symlink.o`, `mount.o`, and `group.o` to `obj-y`.

Important interactions:
- Sysfs is built as core kernel code when enabled, with functionality split across file attributes, directories, symlinks, mounting, and attribute groups.

Notable invariants and risks:
- There is no conditional object split inside this Makefile; `CONFIG_SYSFS` controls entry from the parent build.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/sysfs/dir.c

Purpose: Implements sysfs directory creation, removal, rename, movement, and empty mount-point helpers on top of kernfs.

Key responsibilities:
- Defines `sysfs_symlink_target_lock`, shared with symlink and compatibility link paths to protect `kobj->sd` target access.
- `sysfs_create_dir_ns()` creates a kobject directory under its parent or sysfs root, applying kobject ownership and optional namespace tag.
- `sysfs_remove_dir()` clears `kobj->sd` under the symlink target lock and removes the kernfs directory.
- Provides rename and move helpers with namespace support.
- Implements exported empty mount-point helpers.

Important interactions:
- Uses kernfs directory APIs and `kobject_get_ownership()`.
- Duplicate creation emits a sysfs warning and stack dump via `sysfs_warn_dup()`.

Notable invariants and risks:
- Sysfs itself does not generally serialize object lifetime; owners must avoid races, except for symlink target dereference protection through `sysfs_symlink_target_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/sysfs/file.c

Purpose: Implements sysfs regular and binary attribute files using kernfs callbacks.

Key responsibilities:
- Maps kernfs nodes back to kobjects and their `sysfs_ops`.
- Implements text attribute show/store callbacks through seq_file or preallocated buffers.
- Implements binary attribute read, write, mmap, llseek, and open callbacks.
- Selects kernfs operation tables based on readable/writable/preallocated/binary/mmap capabilities.
- Creates and removes individual attributes, arrays of attributes, group members, and binary attributes.
- Implements `sysfs_notify()` for poll notification.
- Provides active-protection break/unbreak helpers for self-removing attributes.
- Implements chmod and ownership changes for files, symlinks, and kobject default groups.
- Provides `sysfs_emit()`, `sysfs_emit_at()`, and `sysfs_bin_attr_simple_read()` helpers.

Important interactions:
- Depends on kobject `ktype->sysfs_ops`.
- Uses kernfs for active references, file creation, notification, ownership, and removal.
- Coordinates ownership changes with group helpers from `group.c`.

Notable invariants and risks:
- Text `show()` buffers are page-sized; returning `PAGE_SIZE` or more is treated as suspicious and truncated.
- Preallocated text reads require the kernfs prealloc buffer.
- `sysfs_break_active_protection()` deliberately weakens deletion protection and must be paired with `sysfs_unbreak_active_protection()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/group.c -->
# File Research: sources/os/linux/linux-stable/fs/sysfs/group.c

Purpose: Provides sysfs attribute-group creation, update, removal, merge/unmerge, symlink-in-group, compatibility link, and ownership-change operations.

Key responsibilities:
- Creates regular and binary attributes from `struct attribute_group`.
- Applies `is_visible`, `is_visible_const`, `is_bin_visible`, and `bin_size` callbacks.
- Handles named subdirectory groups and unnamed groups on the kobject directory.
- Rolls back partial group creation on errors.
- Updates group visibility by removing and re-adding files as needed.
- Removes groups and group lists.
- Merges extra files into existing named groups and unmerges them later.
- Adds/removes symlinks inside groups.
- Implements `compat_only_sysfs_link_entry_to_kobj()` for compatibility symlinks to target groups or attributes.
- Changes ownership of groups and their visible attributes.

Important interactions:
- Uses helpers from `file.c` for file creation and ownership.
- Uses `sysfs_symlink_target_lock` when linking to target kobjects not owned by the caller.
- Uses kernfs for directories, files, removal, lookup, and attribute mutation.

Notable invariants and risks:
- Attribute permissions are masked to allowed sysfs bits and warn on invalid modes.
- Group update semantics can remove existing entries before recreation; callers must tolerate transient changes.
- Visibility callbacks influence both creation and later ownership traversal.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/mount.c -->
# File Research: sources/os/linux/linux-stable/fs/sysfs/mount.c

Purpose: Initializes and registers the sysfs filesystem and connects it to kernfs mount infrastructure.

Key responsibilities:
- Creates the global kernfs root and stores `sysfs_root_kn`.
- Defines sysfs fs_context operations and filesystem type.
- Initializes per-mount kernfs context with root, magic number, and network namespace tag.
- Allows user namespace visible sysfs mounts by setting `SB_I_USERNS_VISIBLE` on newly created superblocks.
- Drops namespace references on context free and superblock kill.
- Registers the `sysfs` filesystem at init.

Important interactions:
- Uses kernfs `kernfs_get_tree()`, `kernfs_kill_sb()`, and fs_context support.
- Integrates with kobject namespace helpers for network namespace tagging.
- Adjusts `fc->user_ns` to the owning network namespace user namespace.

Notable invariants and risks:
- Non-kernel mounts require `kobj_ns_current_may_mount(KOBJ_NS_TYPE_NET)`.
- `fc->global = true` forces global superblock namespace behavior while still tagging kernfs entries by namespace.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/sysfs/symlink.c

Purpose: Implements sysfs symlink creation, deletion, removal, and rename helpers.

Key responsibilities:
- Creates symlinks from a parent kernfs node or kobject directory to a target kobject.
- Provides warning and no-warning creation variants.
- Supports root-level symlink creation when the source kobject is NULL.
- Deletes symlinks with namespace awareness through `sysfs_delete_link()`.
- Removes symlinks by name.
- Renames symlinks while validating that the old entry is a link to the expected target.

Important interactions:
- Uses `sysfs_symlink_target_lock` to safely inspect `target_kobj->sd`.
- Uses kernfs link, lookup, remove, and rename operations.
- Exports public sysfs symlink APIs to GPL modules.

Notable invariants and risks:
- Target kobjects may disappear independently of the link creator; the shared lock prevents dereferencing a freed `sd` pointer.
- Namespace-aware deletion needs target information; plain removal does not validate target namespace.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/sysfs.h -->
# File Research: sources/os/linux/linux-stable/fs/sysfs/sysfs.h

Purpose: Internal sysfs header shared by sysfs implementation files.

Key responsibilities:
- Declares `sysfs_root_kn`.
- Declares `sysfs_symlink_target_lock`.
- Declares `sysfs_warn_dup()`.
- Declares internal file creation helpers for regular and binary attributes with explicit mode, ownership, and namespace.
- Declares `sysfs_create_link_sd()`.

Important interactions:
- Bridges mount, dir, file, group, and symlink implementation files.
- Includes public `<linux/sysfs.h>` while keeping kernfs-oriented internals private to `fs/sysfs`.

Notable invariants and risks:
- This is not a public API header; exported user-facing sysfs APIs live elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/sysfs/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/tests/binfmt_elf_kunit.c -->
# File Research: sources/os/linux/linux-stable/fs/tests/binfmt_elf_kunit.c

Purpose: KUnit tests for ELF loader mapping-size calculation.

Key responsibilities:
- Tests `total_mapping_size()` with no headers, empty headers, non-`PT_LOAD` headers, real-world `/bin/mount`-like program headers, and unordered `PT_LOAD` headers.
- Verifies that mapping size is based on loadable segments and is order-independent.

Important interactions:
- Uses KUnit suite registration through `kunit_test_suite()`.
- Exercises ELF program header behavior from binfmt ELF code included in the fs test build context.

Notable invariants and risks:
- Captures regression coverage for a historical linux-fsdevel case involving unordered load segments.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/tests/binfmt_elf_kunit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/tests/exec_kunit.c -->
# File Research: sources/os/linux/linux-stable/fs/tests/exec_kunit.c

Purpose: KUnit tests for exec argument/environment stack-limit calculation.

Key responsibilities:
- Defines table-driven cases for `bprm_stack_limits()`.
- Covers negative `argc`/`envc`, maximum string counts, pointer-count overflow-style inputs, zero stack limits, `ARG_MAX` boundaries, and `_STK_LIM` clamping.
- Verifies expected return codes and, under MMU builds, expected `bprm.argmin`.

Important interactions:
- Tests `struct linux_binprm` fields consumed by exec setup.
- Uses KUnit expectations and suite registration named `exec`.

Notable invariants and risks:
- The tests encode important boundary assumptions: `ARG_MAX == 32 * SZ_4K`, `_STK_LIM == SZ_8M`, and `MAX_ARG_STRINGS == 0x7fffffff`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/tests/exec_kunit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/timerfd.c -->
# File Research: sources/os/linux/linux-stable/fs/timerfd.c

Purpose: Implements Linux timerfd file descriptors and syscalls for timer creation, arming, reading expirations, polling, fdinfo, checkpoint/restore tick injection, and 32-bit time compatibility.

Key responsibilities:
- Defines `timerfd_ctx`, wrapping either an hrtimer or alarmtimer.
- Implements expiration callbacks that increment ticks and wake poll/read waiters.
- Supports `CLOCK_MONOTONIC`, `CLOCK_REALTIME`, `CLOCK_BOOTTIME`, and realtime/boottime alarm clocks.
- Maintains a cancel-on-set list for absolute realtime timers with `TFD_TIMER_CANCEL_ON_SET`.
- Handles clock-set and resume notifications through `timerfd_clock_was_set()` and deferred work.
- Implements file operations: release, poll, read_iter, fdinfo, ioctl, and noseek.
- Implements `timerfd_create`, `timerfd_settime`, `timerfd_gettime`, and 32-bit time variants.
- Supports periodic timers by forwarding/restarting on read or gettime rather than from the timer callback.

Important interactions:
- Uses anon inodes, wait queues, hrtimer, alarmtimer, RCU, time namespaces, capabilities, and user-copy helpers.
- Alarm clocks require `CAP_WAKE_ALARM`.
- Checkpoint/restore can set nonzero ticks with `TFD_IOC_SET_TICKS`.

Notable invariants and risks:
- Cancel-on-set timers return `-ECANCELED` and clear ticks/expired state when realtime offset changes.
- Short-period periodic timers are rearmed from user access paths to avoid timer callback denial-of-service behavior.
- File descriptor validation checks `f_op == &timerfd_fops`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/timerfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/tracefs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/tracefs/Makefile

Purpose: Builds tracefs when tracing is enabled.

Key responsibilities:
- Defines `tracefs-objs` as `inode.o` plus `event_inode.o`.
- Adds `tracefs.o` under `CONFIG_TRACING`.

Important interactions:
- Tracefs is tied to the tracing subsystem rather than being a standalone always-built filesystem.

Notable invariants and risks:
- Eventfs support is built into the same tracefs object.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/tracefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/tracefs/event_inode.c -->
# File Research: sources/os/linux/linux-stable/fs/tracefs/event_inode.c

Purpose: Implements eventfs, the dynamic tracefs subtree that lazily materializes tracing event directories and files.

Key responsibilities:
- Defines `eventfs_inode` lifetime, reference counting, SRCU-based freeing, and mutex-protected mutation.
- Creates eventfs directory descriptors and top-level `events` directory.
- Dynamically looks up event files and subdirectories from metadata callbacks.
- Implements directory iteration without precreating all dentries/inodes.
- Caches user-modified mode/uid/gid attributes for eventfs directories and files.
- Propagates remount uid/gid changes through eventfs saved attributes.
- Removes eventfs directories recursively and invalidates the top-level events dentry.
- Exposes remount lock/unlock helpers combining mutex and SRCU.

Important interactions:
- Depends on tracefs inode allocation and dentry operations from `inode.c`.
- Uses tracing-provided `eventfs_entry` callback/release hooks.
- Uses fsnotify, security lockdown checks, RCU/SRCU, kref, and tracefs create helpers.

Notable invariants and risks:
- Callback functions run while eventfs internal locks are held and must not reenter tracefs/eventfs.
- Eventfs directory recursion is expected to stay within `events/group/event/file` depth.
- File inodes share a fixed inode number while directories get stable generated numbers.
- `is_freed` marks descriptors before SRCU and dentry references finish draining.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/tracefs/event_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/tracefs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/tracefs/inode.c

Purpose: Implements the tracefs filesystem core: registration, mount options, inode cache, file/directory creation APIs, removal, and permission propagation.

Key responsibilities:
- Maintains tracefs inode slab cache and global inode list for remount updates.
- Implements default tracefs file operations and inode operations for regular files, directories, and tracing instance directories.
- Parses and applies mount options: `uid`, `gid`, and `mode`.
- Reconfigures tracefs on remount and propagates uid/gid changes to tracefs and eventfs inodes.
- Defines superblock, dentry, and fs_context operations.
- Registers the `tracefs` filesystem and creates `/sys/kernel/tracing` mount point.
- Provides exported APIs: `tracefs_create_file()`, `tracefs_create_dir()`, `tracefs_remove()`, and `tracefs_initialized()`.
- Provides `tracefs_create_instance_dir()` for the tracing instances directory with mkdir/rmdir callbacks.

Important interactions:
- Uses simplefs helpers, fs_context parser, security lockdown, sysfs mount-point creation, fsnotify, and eventfs hooks.
- Pins tracefs while creating/removing entries with `simple_pin_fs()` and `simple_release_fs()`.
- Instance directory mkdir/rmdir drops inode locks before calling tracing callbacks.

Notable invariants and risks:
- Tracefs default mode is `0700`.
- Lockdown can prevent creating tracefs/eventfs entries.
- Dentry operations distinguish eventfs dentries by `d_fsdata`; eventfs dentries are kept differently from ordinary tracefs dentries.
- Remount uid/gid updates clear per-inode override flags unless users explicitly changed ownership.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/tracefs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/tracefs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/tracefs/internal.h

Purpose: Internal tracefs/eventfs shared declarations and data structures.

Key responsibilities:
- Defines tracefs inode flags for eventfs, gid/uid permission overrides, and instance directories.
- Defines `struct tracefs_inode`, embedding the VFS inode plus tracefs metadata.
- Defines `struct eventfs_attr` for saved mode/uid/gid.
- Defines `struct eventfs_inode` metadata for dynamic eventfs directories and files.
- Provides `get_tracefs()` container helper.
- Declares tracefs creation lifecycle helpers and eventfs remount/dentry release hooks.

Important interactions:
- Used by both tracefs core and eventfs dynamic inode code.
- Encodes the private contract for remount propagation and eventfs lazy materialization.

Notable invariants and risks:
- `tracefs_inode` fields after `vfs_inode` are zeroed by cache initialization.
- `eventfs_inode` uses bitfields for freed/events state and entry count.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/tracefs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/Kconfig

Purpose: Defines UBIFS filesystem configuration options.

Key responsibilities:
- Declares `CONFIG_UBIFS_FS` as a tristate filesystem depending on `MTD_UBI`.
- Selects CRC, compression, crypto hash info, encryption support, and xattr dependencies as needed.
- Provides advanced compression options for LZO, zlib, and Zstd.
- Defines optional atime support, disabled by default to reduce flash wear.
- Defines xattr and security label support.
- Defines authentication support, selecting keys, HMAC crypto, and system data verification.

Important interactions:
- UBIFS depends on UBI flash volumes.
- Compression selections affect ability to read existing compressed filesystems.
- Authentication requires users to also select a suitable hash algorithm.

Notable invariants and risks:
- Enabling atime can increase writes and flash wear.
- Removing compressor support can make existing UBIFS images unreadable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/Makefile

Purpose: Builds UBIFS core and optional feature objects.

Key responsibilities:
- Builds `ubifs.o` under `CONFIG_UBIFS_FS`.
- Includes core journal, file, dir, superblock, tree, scan, replay, log, commit, GC, orphan, budget, LPT, compression, recovery, ioctl, debug, misc, and sysfs objects.
- Adds encryption, xattr, and authentication objects conditionally.

Important interactions:
- Feature object inclusion mirrors Kconfig options for encryption, xattrs, and authentication.

Notable invariants and risks:
- The Makefile shows UBIFS as a single linked object composed of many tightly coupled subsystems.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/auth.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/auth.c

Purpose: Implements UBIFS authentication helpers for node hashes, HMACs, superblock signature verification, authentication initialization, and cleanup.

Key responsibilities:
- Calculates and checks node hashes.
- Builds authentication nodes by finalizing a running hash state and storing an HMAC.
- Reports hash mismatches with expected and calculated digests.
- Verifies signed superblocks using a following `UBIFS_SIG_NODE` and PKCS#7 verification.
- Initializes authentication from mount-selected hash and logon key, allocating hash and HMAC transforms.
- Manages the log hash descriptor and frees authentication resources.
- Inserts and verifies embedded node HMACs while excluding magic/CRC and the HMAC field itself.
- Copies shash state by export/import.
- Computes a HMAC over the well-known `"UBIFS"` message and tests all-zero HMACs.

Important interactions:
- Uses Linux crypto shash APIs, keyring logon keys, PKCS#7 verification, and UBIFS scan/read helpers.
- Authentication fields live in `struct ubifs_info` and are gated by `ubifs_authenticated(c)`.

Notable invariants and risks:
- Hash and HMAC digest sizes must fit fixed UBIFS on-media arrays.
- The authentication key must be a logon key and can be revoked while being requested, so key semaphore checks matter.
- HMAC verification uses constant-time comparison semantics via `crypto_memneq()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/budget.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/budget.c

Purpose: Implements UBIFS space budgeting and free-space reporting.

Key responsibilities:
- Tracks and reserves estimated index growth, new data growth, and dirty-data growth.
- Shrinks liability by writing back dirty inodes/pages.
- Runs garbage collection and commits to recover space when pessimistic budgeting fails.
- Calculates minimum index LEB reservations for the in-the-gaps commit method.
- Calculates available flash space after reserving index, GC, journal heads, deletion, dead space, and dark space.
- Enforces reserved pool rules for root, configured UID/GID, and `CAP_SYS_RESOURCE`.
- Implements `ubifs_budget_space()` and `ubifs_release_budget()`.
- Converts new-page budget into dirty-page budget when a page becomes an update instead of new data.
- Releases dirty inode budget after writeback.
- Reports user-visible free space with UBIFS node and index overhead accounted for.

Important interactions:
- Coordinates with writeback, GC, commit, LEB properties, journal head counts, and UBIFS budget accounting under `space_lock`.
- Uses `commit_sem` around GC and `s_umount` around writeback.

Notable invariants and risks:
- Budgeting is deliberately pessimistic so UBIFS can always flush dirty pages, inodes, and znodes.
- Index space is reserved at roughly three times consolidated index size to preserve commit safety.
- `nospace` and `nospace_rp` are cached flags and require memory barriers when changed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/budget.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/commit.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/commit.c

Purpose: Manages UBIFS commit execution, background commit thread behavior, commit state transitions, and old-index debug checking.

Key responsibilities:
- Detects when there is nothing to commit by checking mounting/remount state, dirty TNC root, dirty LPT nodes, and dirty counters.
- Implements two-phase commit: a short exclusive start phase under `commit_sem`, then a longer end phase after releasing it.
- Syncs journal write buffers, starts GC/log/TNC/LPT/orphan commit components, updates master node fields, ends and post-processes commit components.
- Maintains commit state machine: resting, background requested/running, required/running required, and broken.
- Runs background thread work for write-buffer sync and background commits.
- Provides APIs to require a commit, request background commit, run or wait for commit, and let GC escalate background commit to required.
- On commit failure, marks commit broken and switches UBIFS to read-only error mode.
- Includes debug helpers to record and verify the old on-flash index remains intact across commit.

Important interactions:
- Coordinates UBIFS modules: GC, log, TNC, LPT, orphan handling, master node, write buffers, and debug checks.
- Uses `commit_sem`, `cs_lock`, `cmt_wq`, freezer-aware kthread behavior, and UBIFS read-only error handling.

Notable invariants and risks:
- Commit start must minimize I/O while holding exclusive journal access to avoid latency spikes.
- The old index must remain recoverable until the new committed state is durable.
- Background and foreground commit paths race through a shared state machine; transitions carefully upgrade background work to required commits when needed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/commit.c -->