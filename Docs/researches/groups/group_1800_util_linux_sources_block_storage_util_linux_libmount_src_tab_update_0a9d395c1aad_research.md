# Group Research: group_1800_util_linux_sources_block_storage_util_linux_libmount_src_tab_update_0a9d395c1aad

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/block-storage/util-linux` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab_update.c -->
# File Research: sources/block-storage/util-linux/libmount/src/tab_update.c

## Scope

Implements libmount's userspace mount-table update abstraction, centered on `struct libmnt_update`. It prepares and applies updates to the private utab file, writes/replaces fstab-like tables, handles mount/umount/move/remount update cases, and emits activity/event files used by libmount monitoring.

## Public And Internal APIs Covered

- Lifecycle: `mnt_new_update()`, `mnt_free_update()`.
- Update setup: `mnt_update_set_filename()`, `mnt_update_get_filename()`, `mnt_update_set_fs()`, `mnt_update_get_fs()`, `mnt_update_get_mflags()`, `mnt_update_is_ready()`, `mnt_update_force_rdonly()`.
- Table writing: `mnt_table_write_file()`, `mnt_table_replace_file()`.
- Update execution: `mnt_update_table()`, `mnt_update_already_done()`.
- Event/activity coordination: `mnt_update_emit_event()`, `mnt_update_start()`, `mnt_update_end()`.
- Internal operations: `utab_new_entry()`, `set_fs_root()`, `update_add_entry()`, `update_remove_entry()`, `update_modify_target()`, `update_modify_options()`, `update_add_options()`.

## Control Flow And Behavior

- `mnt_update_set_fs()` resets the update object and classifies the operation:
  - `target` with no `fs` means umount/removal.
  - `fs` with normal mount flags prepares a new utab entry.
  - `MS_MOVE` copies an mtab-style fs template for later target rewriting.
  - `MS_REMOUNT` prepares option modification.
  - propagation-only flags return `1` because no utab update is needed.
- `utab_new_entry()` extracts only mtab-visible userspace options, preserves attributes, and skips utab creation when no user options or attributes exist.
- `set_fs_root()` uses `/proc/self/mountinfo` for bind mounts and btrfs/auto cases to resolve source path, filesystem type, bind source, and root.
- `update_table()` writes a temporary unique file, serializes entries with `fprintf_utab_fs()`, flushes, chmods, copies ownership from the old file when present, and atomically renames.
- `mnt_table_write_file()` and `mnt_table_replace_file()` serialize fstab/mtab-style entries with mangled source, target, fstype, options, freq, passno, and comments.
- `mnt_update_table()` locks the utab file and dispatches to remove/add/move/remount/missing-option update paths.
- `mnt_update_already_done()` detects whether a helper already added/removed an entry; for mounts it also marks `missing_options` if helper-written options do not contain all expected userspace options.
- `mnt_update_start()` creates and shared-locks `<utab>.act` so monitors can suppress intermediate kernel events; `mnt_update_end()` unlocks and removes the activity file only when no other shared users remain.

## State And Data Structures

- `struct libmnt_update` stores target, prepared fs, utab filename, mount flags, activity-file fd/name, readiness flags, parsed mountinfo, and an optional lock.
- Utab entries are serialized as key-value fields: `ID`, `UNIQID`, `SRC`, `TARGET`, `ROOT`, `BINDSRC`, `ATTRS`, and `OPTS`.

## Dependencies

- libmount fs/table/cache/lock helpers from `mountP.h`.
- Option filtering from `mnt_optstr_get_options()` and `mnt_optstr_get_missing()`.
- Path and table sources including `/proc/self/mountinfo`, utab path detection, and mangle/unmangle helpers.
- POSIX file APIs: `mkstemp`, `fdopen`, `fflush`, `fchmod`, `fchown`, `rename`, `flock`, `umask`.

## Risks And Invariants

- The update object must only be marked ready after filename and operation state are valid.
- Atomic replacement depends on successful write/flush/metadata setup before `rename()`.
- File locking is required around read-modify-write table updates.
- Move updates rewrite targets whose paths begin with the old source target and preserve subpaths.
- Activity-file deletion is coordinated with advisory locks to avoid removing an in-use marker.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab_update.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/test.c -->
# File Research: sources/block-storage/util-linux/libmount/src/test.c

## Scope

Provides the small shared test-program dispatcher used by libmount files compiled with `TEST_PROGRAM`.

## Public And Internal APIs Covered

- `mnt_run_test(struct libmnt_test *tests, int argc, char *argv[])`.

## Control Flow And Behavior

- Requires at least one command argument and treats `--help` / `-h` as usage.
- Initializes libmount debugging with `mnt_init_debug(0)`.
- Searches the supplied `struct libmnt_test` array by command name and calls the matched test body with shifted argc/argv.
- Prints `FAILED [rc=%d]` for nonzero test return codes.
- Prints generated usage including every test name and usage string when no test matches or arguments are insufficient.
- Converts test result to process exit status: zero becomes `EXIT_SUCCESS`, any nonzero/usage failure becomes `EXIT_FAILURE`.

## Dependencies

- Requires `TEST_PROGRAM` mode and `mountP.h`.
- Uses `program_invocation_short_name`, `assert`, `strcmp`, and standard exit constants.

## Risks And Invariants

- Test arrays must be NULL-terminated.
- Negative return values are treated as bad usage and trigger the usage text.
- The dispatcher assumes test bodies understand the shifted argument vector where `argv[0]` is the test name.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/test.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/utils.c -->
# File Research: sources/block-storage/util-linux/libmount/src/utils.c

## Scope

Implements miscellaneous libmount utility routines for safe path probing, filesystem/tag parsing, mount ID lookup, filesystem classification, account parsing, utab path probing, temporary file creation, mountpoint discovery, kernel command-line parsing, and root-device guessing.

## Public And Internal APIs Covered

- File/path helpers: `is_file_empty()`, `mnt_safe_stat()`, `mnt_safe_lstat()`, `mnt_is_path()`, `mnt_chdir_to_parent()`, `mnt_is_readonly()`.
- Tag parsing: `mnt_valid_tagname()`, `mnt_tag_is_valid()`, `mnt_parse_offset()`.
- Mount IDs: `mnt_id_from_fd()`, `mnt_id_from_path()`.
- String encoding: `mnt_mangle()`, `mnt_unmangle()`.
- Filesystem classification: `mnt_fstype_is_pseudofs()`, `mnt_fstype_is_netfs()`, `mnt_statfs_get_fstype()`, `mnt_match_fstype()`.
- Filesystem list handling: `mnt_get_filesystems()`, `mnt_free_filesystems()`.
- User/group/mode parsing: `mnt_get_username()`, `mnt_get_uid()`, `mnt_get_gid()`, `mnt_parse_uid()`, `mnt_parse_gid()`, `mnt_parse_mode()`, `mnt_in_group()`.
- Table path helpers: `mnt_has_regular_mtab()`, `mnt_has_regular_utab()`, `mnt_get_swaps_path()`, `mnt_get_fstab_path()`, `mnt_get_mtab_path()`, `mnt_get_utab_path()`.
- File replacement helper: `mnt_open_uniq_filename()`.
- Mount/root helpers: `mnt_get_mountpoint()`, `mnt_get_kernel_cmdline_option()`, `mnt_guess_system_root()`.

## Control Flow And Behavior

- `safe_stat()` prefers `statx()` with `AT_STATX_DONT_SYNC` and `AT_NO_AUTOMOUNT`, falling back to `fstatat()` or `stat/lstat`; this avoids triggering automounts where possible.
- `mnt_chdir_to_parent()` moves into an absolute path's parent and optionally returns the final component.
- `mnt_is_readonly()` distinguishes permission denial from read-only filesystems using `access()` and, when available, `utimensat()`.
- Mount ID helpers wrap `statx()` `STATX_MNT_ID` and optional `STATX_MNT_ID_UNIQUE`, returning `-ENOSYS` when unsupported.
- Pseudofs detection uses a sorted static array and `bsearch`; network filesystem detection uses explicit string comparisons.
- `mnt_statfs_get_fstype()` maps many Linux statfs magic values to filesystem names.
- `mnt_get_filesystems()` reads `/etc/filesystems` first, respects `*` continuation semantics, and falls back to `/proc/filesystems`, skipping comments and `nodev` entries.
- UID/GID parsers try names first and numeric values when the string begins with a digit.
- `mnt_has_regular_utab()` verifies utab is regular and optionally creates the containing directory/file to test writability.
- `mnt_open_uniq_filename()` builds `<filename>.XXXXXX`, masks group/world permissions while calling `mkstemp_cloexec()`, and returns the fd plus allocated temporary path.
- `mnt_get_mountpoint()` walks upward comparing `st_dev` to find the mountpoint, with a warning in comments that overlay-style filesystems can defeat this traditional method.
- `mnt_get_kernel_cmdline_option()` scans `/proc/cmdline`, stops at ` -- `, and returns the last matching bare option or `name=` value.
- `mnt_guess_system_root()` tries sysfs devno resolution first, then `root=` kernel command-line forms: `major:minor`, hex encoded dev_t, device names, and tags.

## State And Data Structures

- Static pseudofs list must remain sorted.
- Filesystem lists are NULL-terminated dynamically grown arrays.
- Root guessing uses sysfs paths, optional libmount cache, and allocated result strings.

## Dependencies

- libblkid tag parser.
- libmount canonicalization, mangle, match, cache, sysfs, env, and path helpers.
- Linux/POSIX APIs: `statx`, `statfs`, `getpwuid_r`, `getpwnam_r`, `getgrnam_r`, `getgroups`, `mkstemp`, `posix` file operations.

## Risks And Invariants

- `mnt_fstype_is_pseudofs()` relies on the array being sorted for `bsearch`.
- `mnt_get_mountpoint()` uses device-number transitions and is not authoritative for all modern filesystems.
- UID/GID numeric conversion checks both `ULONG_MAX` and cast round-trip to avoid truncation.
- Utab writability checks may create `/run/mount` and the utab file when requested.
- Kernel command-line parsing is intentionally approximate and does not fully emulate kernel parsing.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/version.c -->
# File Research: sources/block-storage/util-linux/libmount/src/version.c

## Scope

Provides libmount version and compile-time feature reporting.

## Public And Internal APIs Covered

- `mnt_parse_version_string()`.
- `mnt_get_library_version()`.
- `mnt_get_library_features()`.

## Control Flow And Behavior

- `mnt_parse_version_string()` removes dots and accumulates leading digits until a non-digit, so a version like `2.18.0` becomes an integer release code.
- `mnt_get_library_version()` optionally returns the static `LIBMOUNT_VERSION` string and always returns the parsed numeric code.
- `mnt_get_library_features()` returns a static NULL-terminated feature array and item count.

## Feature Flags

Feature strings are conditionally compiled for support such as `selinux`, `smack`, `btrfs`, `verity`, `namespaces`, `idmapping`, `fd-based-mount`, `statmount`, `statx`, `fanotify`, `udev`, `assert`, and always `debug`.

## Dependencies

- Compile-time configuration macros from `mountP.h`.
- `ctype.h` for digit parsing.

## Risks And Invariants

- The feature array is static and must remain NULL-terminated.
- Numeric version parsing is simple and intentionally ignores suffixes after the digit/dot prefix.
- `mnt_get_library_features()` requires a non-NULL output pointer.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/version.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/Makemodule.am -->
# File Research: sources/block-storage/util-linux/sys-utils/Makemodule.am

## Scope

Automake module defining build targets, sources, manpages, installation hooks, conditional feature builds, static variants, and library dependencies for util-linux `sys-utils`.

## Build Targets Covered

- Memory/CPU tools: `lsmem`, `chmem`, `lscpu`, `chcpu`.
- IPC and scheduling tools: `ipcmk`, `ipcrm`, `ipcs`, `lsipc`, `renice`.
- Interrupt tools: `irqtop`, `lsirq`.
- Device/block tools: `fstrim`, `blkdiscard`, `blkzone`, `blkpr`, `losetup`, `zramctl`, `wdctl`.
- Mount/namespace tools: `mount`, `umount`, `mountpoint`, `unshare`, `nsenter`, `pivot_root`, `switch_root`.
- Misc system utilities: `flock`, `choom`, `rfkill`, `setpgid`, `setsid`, `readprofile`, `tunelp`, `ctrlaltdel`, `fsfreeze`, `ldattach`, `rtcwake`, `setarch`, `eject`, `prlimit`, `swapon`, `swapoff`, `fallocate`, `hwclock`, `setpriv`.

## Control Flow And Behavior

- Each `if BUILD_*` block adds programs to the relevant install class (`bin_PROGRAMS`, `sbin_PROGRAMS`, `usrbin_exec_PROGRAMS`, `usrsbin_exec_PROGRAMS`), adds manpages and `.adoc` sources, and sets source files plus `LDADD`/`CFLAGS`.
- `dmesg` adds a `test_dmesg` check program compiled with `-DTEST_DMESG`.
- `blkdiscard` conditionally links `libblkid.la` when libblkid is built.
- `irqtop` links either slang or ncurses depending on availability.
- `mount` and `umount` use SUID flags and install hooks to chown/chmod setuid root when configured.
- Static variants are conditionally defined for `losetup`, `mount`, `umount`, `unshare`, and `nsenter`.
- `setarch` generates architecture alias links and corresponding manpage symlinks.
- `fstrim` optionally installs systemd service/timer units.

## Dependencies

- Internal libraries: `libcommon.la`, `libmount.la`, `libblkid.la`, `libsmartcols.la`, `libtcolors.la`, `libcommon_logindefs.la`.
- Optional external libraries/macros: realtime, POSIX IPC, message queues, ncurses/slang, SELinux, systemd, RTAS, audit, math, cap-ng.
- Shared generated variables: `MANPAGES`, `dist_noinst_DATA`, `PATHFILES`, `EXTRA_DIST`, `INSTALL_EXEC_HOOKS`, `UNINSTALL_HOOKS`.

## Risks And Invariants

- Conditional blocks must match configure-time `BUILD_*` and `HAVE_*` definitions or installed utilities/manpages diverge from compiled features.
- SUID mount/umount installation behavior depends on `MAKEINSTALL_DO_CHOWN` and `MAKEINSTALL_DO_SETUID`.
- Generated `setarch` links are architecture-dependent and must be mirrored by uninstall hooks.
- Programs using internal library headers add the correct include directory flags, such as libmount/libsmartcols/libblkid include dirs.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/Makemodule.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/blkdiscard.c -->
# File Research: sources/block-storage/util-linux/sys-utils/blkdiscard.c

## Scope

Implements the `blkdiscard` command, which discards, securely discards, or zero-fills ranges of a block device using Linux block ioctls.

## Public And Internal APIs Covered

- Main command-line entry point.
- Internal actions: discard, secure discard, zeroout.
- Optional signature probing via libblkid.
- Progress/stat reporting through `print_stats()`.

## Control Flow And Behavior

- Parses offset, length, step, force, quiet, secure, zeroout, and verbose options.
- Opens the device read/write, using `O_EXCL` unless `--force` is supplied.
- Verifies the target is a block device.
- Reads device size with `BLKGETSIZE64` and logical sector size with `BLKSSZGET`.
- Validates offset and length alignment to sector size and clamps length to device end.
- With libblkid and without force, probes existing filesystem/partition signatures and warns; on interactive stdin, an existing signature requires `--force`.
- Iterates over the requested range in optional `--step` chunks and calls one of:
  - `BLKDISCARD`
  - `BLKSECDISCARD`
  - `BLKZEROOUT`
- Verbose stepped mode reports progress at most once per second.

## Dependencies

- Linux block ioctls from `<linux/fs.h>`.
- Optional libblkid probing.
- util-linux helpers for size parsing, monotonic time, block device helpers, i18n, and exit codes.

## Risks And Invariants

- Offset and length must be sector-aligned.
- Range arithmetic guards overflow and clamps to block-device size.
- `--force` bypasses exclusive open and signature protection.
- Unsupported ioctls return `EXIT_NOTSUPP` when `errno == EOPNOTSUPP`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/blkdiscard.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/blkpr.c -->
# File Research: sources/block-storage/util-linux/sys-utils/blkpr.c

## Scope

Implements `blkpr`, a command-line frontend for Linux block persistent reservation ioctls.

## Public And Internal APIs Covered

- Main command-line entry point.
- Command parsing for `register`, `reserve`, `release`, `preempt`, `preempt-abort`, `clear`, and conditionally `read-keys` / `read-reservation`.
- Type parsing for persistent reservation access types.
- Flag parsing for `ignore-key`.
- Ioctl executor `do_pr()`.

## Control Flow And Behavior

- Static descriptor tables map user strings to kernel persistent-reservation command/type/flag constants and usage text.
- `do_pr()` opens the device read/write and dispatches by command:
  - `IOC_PR_REGISTER` uses `struct pr_registration`.
  - `IOC_PR_RESERVE` / `IOC_PR_RELEASE` use `struct pr_reservation`.
  - `IOC_PR_PREEMPT` / `IOC_PR_PREEMPT_ABORT` use `struct pr_preempt`.
  - `IOC_PR_CLEAR` uses `struct pr_clear`.
  - Optional read commands print registered keys or current reservation.
- `do_pr_read_keys()` grows the key buffer until the kernel-reported key count fits.
- `do_pr_read_reservation()` prints key, generation, and reservation type, or `No reservation`.

## Dependencies

- Linux persistent reservation API from `<linux/pr.h>`.
- util-linux string parsing, allocation, usage, and i18n helpers.

## Risks And Invariants

- String tables must stay aligned with kernel reservation type/command constants.
- Missing command validation is limited: `command` defaults to `-1`, and `do_pr()` handles unknown commands as `EINVAL`.
- Positive ioctl return values are treated as device-model error codes and reported separately from syscall failure.
- Optional read commands depend on kernel headers defining `IOC_PR_READ_KEYS` / `IOC_PR_READ_RESERVATION`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/blkpr.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/blkzone.c -->
# File Research: sources/block-storage/util-linux/sys-utils/blkzone.c

## Scope

Implements `blkzone`, a command-line utility for zoned block devices. It reports zone metadata/capacity and performs zone reset/open/close/finish operations.

## Public And Internal APIs Covered

- Main command-line entry point.
- Commands: `report`, `capacity`, `reset`, `open`, `close`, `finish`.
- Device setup: `init_device()`.
- Zone size lookup: `blkdev_chunk_sectors()`.
- Reporting: `blkzone_report()`.
- Mutating actions: `blkzone_action()`.

## Control Flow And Behavior

- The first non-option argument selects a command.
- `init_device()` opens the target, verifies block-device type, reads total sectors and sector size.
- `blkdev_chunk_sectors()` maps the device to its whole-disk sysfs path and reads `queue/chunk_sectors`.
- `report` / `capacity` use `BLKREPORTZONE` in batches of 4096 zones:
  - `report` prints start, length, optional capacity, write pointer, reset/non-sequential flags, condition, and type.
  - `capacity` sums zone capacities and prints the total.
- Action commands validate offset alignment to zone size, compute range from `--count`, `--length`, or device size, clamp to device end, and issue the configured zone ioctl.
- `--count` and `--length` are mutually exclusive.

## Dependencies

- Linux zoned block API from `<linux/blkzoned.h>`, with fallback definitions for newer ioctls if headers lack them.
- Sysfs helpers for whole-disk mapping and `chunk_sectors`.
- util-linux block-device, option-exclusion, allocation, parsing, and i18n helpers.

## Risks And Invariants

- Offsets and lengths are expressed in 512-byte sectors, not bytes.
- Zone actions require zone-size alignment except the final range may end at device size.
- Zone condition/type arrays assume kernel enum values fit expected indexes.
- Capacity reporting adapts to whether `BLK_ZONE_REP_CAPACITY` is available.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/blkzone.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/chcpu.c -->
# File Research: sources/block-storage/util-linux/sys-utils/chcpu.c

## Scope

Implements `chcpu`, a sysfs-based CPU hotplug/configuration utility for enabling, disabling, configuring, deconfiguring, rescanning CPUs, and setting CPU dispatch mode.

## Public And Internal APIs Covered

- Main command-line entry point.
- CPU operations: `cpu_enable()`, `cpu_configure()`, `cpu_rescan()`, `cpu_set_dispatch()`.
- CPU set parsing and discovery: `cpu_parse()`, `read_cpulist()`.

## Control Flow And Behavior

- Parses one exclusive operation: enable, disable, configure, deconfigure, dispatch, or rescan.
- Supports `--sysroot` by prefixing the sysfs path context rooted at `/sys/devices/system/cpu`.
- `read_cpulist()` determines `maxcpus` from `kernel_max` or fallback CPU count, allocates a CPU set, and reads the `online` cpulist when available.
- `cpu_enable()` writes `cpuN/online`, checks hotplug capability, avoids disabling the last online CPU, and reports already-enabled/disabled states.
- `cpu_configure()` writes `cpuN/configure`, skips non-configurable CPUs, and refuses deconfiguration while a CPU is online.
- `cpu_rescan()` writes `1` to `rescan`.
- `cpu_set_dispatch()` writes `0` or `1` to `dispatching` for horizontal or vertical dispatch mode.

## Dependencies

- util-linux `path_cxt` sysfs helpers.
- CPU set parsing from `cpuset.h`.
- Option exclusion utilities and i18n/closestream helpers.

## Risks And Invariants

- Only one primary operation may be requested.
- Partial success returns `64` (`CHCPU_EXIT_SOMEOK`) rather than generic failure.
- Disabling CPUs updates the cached online CPU set to preserve the last-online-CPU invariant.
- Sysfs attribute availability determines support for hotplug, configure, dispatching, and rescan operations.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/chcpu.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/chmem.c -->
# File Research: sources/block-storage/util-linux/sys-utils/chmem.c

## Scope

Implements `chmem`, a sysfs-based memory hotplug/configuration utility for bringing memory blocks online/offline, configuring/deconfiguring memory ranges, selecting zones, and setting `memmap_on_memory`.

## Public And Internal APIs Covered

- Main command-line entry point.
- Online/offline by size or range: `chmem_onoff_size()`, `chmem_onoff_range()`.
- Configure/deconfigure by size or range: `chmem_config_size()`, `chmem_config_range()`, `chmem_config()`.
- Sysfs discovery: `read_info()`, `read_conf()`, `filter()`, `have_mem_blk_zones()`.
- Parameter parsing: `parse_parameter()`, `parse_single_param()`, `parse_range_param()`.
- Zone handling: `zone_name_to_id()`.

## Control Flow And Behavior

- Accepts exactly one action and one size/range/block-range argument.
- Supports byte/address ranges or memory block numbers via `--blocks`.
- Reads `/sys/devices/system/memory`, scans `memoryN` directories, and reads `block_size_bytes`.
- Optional `/sys/firmware/memory` support is used for configure/deconfigure and `memmap_on_memory`.
- Online operations can choose a zone:
  - `online_movable` for `Movable`.
  - `online_kernel` for other selected zones.
  - default online prefers `Movable` when valid.
- Disable/deconfigure operations iterate from high to low blocks for size-based requests; enable/configure iterate low to high.
- Range operations iterate matching memory block indexes and report total, partial, or failed completion.
- Verbose mode prints per-block actions using physical address ranges derived from block size.

## State And Data Structures

- `struct chmem_desc` holds path contexts, scanned memory and memconfig directories, block size, selected range/size, feature flags, zone state, and verbosity.
- Zone names include `DMA`, `DMA32`, `Normal`, `Highmem`, `Movable`, and `Device`.

## Dependencies

- util-linux sysfs path helpers, string-vector splitting, size parsing, option exclusion, allocation, and i18n helpers.
- Kernel sysfs memory attributes: `state`, `valid_zones`, `block_size_bytes`, optional firmware `config` and `memmap_on_memory`.

## Risks And Invariants

- Sizes and address ranges must align to memory block size.
- Disabling a block in a zone-aware system checks `valid_zones` and may reject zone mismatch.
- Configure/deconfigure paths require firmware memory config support; otherwise the utility tells users to use enable/disable.
- Partial success returns `64` (`CHMEM_EXIT_SOMEOK`).
- Directory scans and feature detection must stay consistent with the sysfs layout exposed by the running kernel or sysroot.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/chmem.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/choom.c -->
# File Research: sources/block-storage/util-linux/sys-utils/choom.c

## Scope

Implements `choom`, a small utility to inspect or change Linux OOM killer scoring, or run a command under a selected `oom_score_adj`.

## Public And Internal APIs Covered

- Main command-line entry point.
- `/proc` helpers: `get_score()`, `get_score_adj()`, `set_score_adj()`.

## Control Flow And Behavior

- Supports three modes:
  - `-p PID` with no adjust value prints `oom_score` and `oom_score_adj`.
  - `-p PID -n VALUE` changes an existing process's `oom_score_adj`.
  - `-n VALUE COMMAND ...` changes the current process's `oom_score_adj` then `execvp()`s the command.
- Validates that PID mode and command mode are not mixed.
- Uses `/proc/<pid>` path context, with `getpid()` for command-launch mode.
- Prints old and new adjustment values when changing an existing PID.

## Dependencies

- Linux `/proc/<pid>/oom_score` and `/proc/<pid>/oom_score_adj`.
- util-linux path, PID/int parsing, closestream, i18n, and exec error helpers.

## Risks And Invariants

- Running a command requires an explicit adjust value.
- Setting `oom_score_adj` may fail due to permissions or kernel constraints.
- In command mode, the path context must be released before replacing the process image.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/choom.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ctrlaltdel.c -->
# File Research: sources/block-storage/util-linux/sys-utils/ctrlaltdel.c

## Scope

Implements `ctrlaltdel`, which reads or sets the Linux Ctrl-Alt-Del behavior.

## Public And Internal APIs Covered

- Main command-line entry point.
- `get_cad()` reads current mode.
- `set_cad()` sets hard or soft mode.

## Control Flow And Behavior

- With no positional argument, reads `_PATH_PROC_CTRL_ALT_DEL` and prints `soft` for `0`, `hard` for `1`, or `implicit hard` plus warning for unexpected values.
- With an argument, accepts `hard` or `soft`.
- Uses `reboot(LINUX_REBOOT_CMD_CAD_ON)` for hard reset behavior and `reboot(LINUX_REBOOT_CMD_CAD_OFF)` for soft behavior.

## Dependencies

- Linux `reboot()` command constants, with local definitions for CAD on/off.
- `/proc/sys/kernel/ctrl-alt-del` path from pathnames.
- util-linux path, usage, i18n, and closestream helpers.

## Risks And Invariants

- Setting behavior requires sufficient privileges for `reboot()`.
- The program does not reject extra positional arguments; it uses `argv[1]`.
- Unexpected proc values return failure after printing the inferred mode.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ctrlaltdel.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/dmesg.c -->
# File Research: sources/block-storage/util-linux/sys-utils/dmesg.c

## Scope

Implements `dmesg`, a full-featured kernel ring-buffer display and control utility. It can read `/dev/kmsg`, syslog/klogctl buffers, or files; parse kernel records; filter by facility/level/time; format timestamps; output raw/text/JSON; colorize; page output; follow new records; clear the buffer; and set console logging controls.

## Public And Internal APIs Covered

- Main command-line entry point.
- Buffer backends: `init_kmsg()`, `read_kmsg_one()`, `read_syslog_buffer()`, `mmap_file_buffer()`, `prepare_buffer()`, `release_buffer()`.
- Parsers: `parse_level()`, `parse_facility()`, `parse_faclev()`, `parse_syslog_timestamp()`, `parse_kmsg_timestamp()`, `parse_callerid()`, `get_next_syslog_record()`, `parse_kmsg_record()`.
- Filtering/time: `record_time()`, `accept_record()`, `record_localtime()`, `record_ctime()`, `iso_8601_time()`, `record_count_delta()`.
- Formatting/output: `print_record()`, `print_buffer()`, `print_kmsg()`, `print_kmsg_file()`, `raw_print()`, `safe_fwrite()`.
- Time format management: `reset_time_fmts()`, `include_time_fmt()`, `exclude_time_fmt()`, `replace_time_fmt()`, `replace_delta_fmt()`, `which_time_format()`.

## Control Flow And Behavior

- Default read method is `/dev/kmsg`; if unavailable, it falls back to syslog/klogctl.
- `--file` reads syslog-style buffers via mmap; `--kmsg-file` reads `/dev/kmsg` record format from a file.
- `/dev/kmsg` records are parsed as `faclev,seq,timestamp[,optional...];message`, including optional `caller=` metadata when present.
- Syslog-style records parse `<facility.priority>` and `[seconds.useconds]` prefixes when needed for filters/decode/color/JSON/time.
- Filtering supports:
  - levels/priorities by number or name,
  - facilities by number or name,
  - kernel-only/userspace-only facility masks,
  - `--since` / `--until` wall-clock timestamps.
- Timestamp formats include raw monotonic time, ctime, ctime+delta, delta-only, relative time, ISO-8601, and no timestamp. Combination rules merge delta with ctime/raw formats and resolve `--notime` conflicts.
- Human mode enables relative time, color auto mode, and pager by default.
- JSON mode disables raw/pager/escaping behavior, resets time formatting, and emits a `dmesg` array of objects.
- Color output highlights timestamps, subsystem prefixes, warning/error levels, and messages containing `segfault at`.
- `--force-prefix` repeats prefixes on each line of multi-line kmsg messages and is only allowed for kmsg.
- Control actions use klogctl for clear, read-clear, console on/off, and console level.

## State And Data Structures

- `struct dmesg_control` stores filter bitsets, last timestamp, boot/suspended time, selected action/method, buffer state, kmsg fd and first read, time format list, JSON writer, output mode flags, and caller-id width.
- `struct dmesg_record` stores message pointer/size, level/facility, timestamp, caller id, and parser cursor state.
- Static level and facility tables mirror syslog priority/facility names.
- Static color table maps semantic dmesg color roles to terminal color schemes.

## Dependencies

- Linux syslog/klogctl API and `/dev/kmsg`.
- util-linux helpers for colors, pager, JSON writing, timestamp parsing, monotonic/boot time, mangle decoding, safe I/O, bit arrays, option exclusion, and wide-character handling.
- `/proc/sys/kernel/pid_max` for caller-id field width estimation.

## Risks And Invariants

- `/dev/kmsg` read uses `PRINTK_MESSAGE_MAX + 1` so the kernel does not reject records as too small.
- `read_kmsg_one()` retries on `EPIPE` because records can change while reading.
- Raw syslog filtering is only allowed with `/dev/kmsg`; other raw buffers cannot be reliably filtered.
- mmap file handling progressively unmaps already printed pages to reduce memory use.
- Wall-clock timestamps depend on boot time and suspended-time estimation and can be inaccurate around suspend/resume.
- JSON mode intentionally changes several formatting flags to produce valid machine-readable output.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/dmesg.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/eject.c -->
# File Research: sources/block-storage/util-linux/sys-utils/eject.c

## Scope

Implements `eject`, a removable-media utility that resolves devices or mountpoints, optionally unmounts mounted filesystems/partitions, and performs tray, CD-ROM, SCSI, floppy, tape, changer, speed, auto-eject, and manual-lock operations.

## Public And Internal APIs Covered

- Main command-line entry point.
- Argument handling: `parse_args()`, `usage()`.
- Device resolution/mount handling: `find_device()`, `device_get_mountpoint()`, `get_disk_devname()`, `umount_partitions()`, `umount_one()`, `is_ejectable()`, `open_device()`.
- CD-ROM operations: `auto_eject()`, `manual_eject()`, `changer_select()`, `close_tray()`, `eject_cdrom()`, `toggle_tray()`, `select_speed()`, `read_speed()`, `list_speeds()`.
- Other eject methods: `eject_scsi()`, `eject_floppy()`, `eject_tape()`.
- Verbose/info helpers.

## Control Flow And Behavior

- Resolves default `/dev/cdrom`, explicit `/dev/...`, relative device names under `/dev`, mountpoints, tags/specs via libmount, and whole-disk devices for partition inputs.
- Uses libmount to parse mtab or `/proc/mountinfo` and determine whether the device or mountpoint is mounted.
- Unless `--no-unmount` is used, unmounts mounted partitions or the whole-device mountpoint by forking `/bin/umount`, dropping permissions in the child.
- `--no-partitions-unmount` changes partition handling into a safety check: if multiple mounted partitions remain, eject fails with device-in-use.
- After unmounting, later open uses `O_EXCL` unless `--force` is set, reducing races with remounts.
- Direct action options handle:
  - default-device printing,
  - no-op resolved-device display,
  - manual eject lock/unlock,
  - auto-eject on/off,
  - tray close/toggle,
  - list/set CD speed,
  - changer slot selection.
- If no eject method is explicitly selected, it tries CD-ROM, SCSI, floppy, and tape methods in order until one succeeds.
- SCSI eject uses SG_IO commands: allow medium removal, start/stop stop, then start/stop eject, with selected sense errors ignored for compatibility.

## Dependencies

- Linux CD-ROM, floppy, tape, block, SCSI SG_IO, and mount APIs.
- libmount for mount table parsing, cache, source/target lookup, and spec/path resolution.
- Sysfs helpers for hotplug/removable checks, whole-disk lookup, and partition scanning.
- util-linux helpers for timing, file/path utilities, parsing, allocation, i18n, and permission dropping.

## Risks And Invariants

- By default, non-hotpluggable/non-removable devices are rejected unless `--force` is used.
- Device resolution may replace a partition device with its whole disk before ejecting.
- Unmount is delegated to `/bin/umount`; failures abort eject.
- Tray toggle has two implementations: drive-status based when available, timing heuristic otherwise.
- SCSI handling intentionally tolerates unsupported medium-removal and no-medium sense codes but rejects other driver/host failures.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/eject.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fallocate.c -->
# File Research: sources/block-storage/util-linux/sys-utils/fallocate.c

## Scope

Implements `fallocate`, a file space allocation/deallocation utility using `fallocate(2)`, `posix_fallocate(3)`, and sparse-file hole detection/punching.

## Public And Internal APIs Covered

- Main command-line entry point.
- Allocation wrappers: `xfallocate()`, `xposix_fallocate()`.
- Number parsing: `cvtnum()`.
- Hole detection/reporting: `dig_holes()`, `is_nul()`, `update_holestat()`, `summary_holestat()`.

## Control Flow And Behavior

- Supports range operations:
  - allocate default range,
  - keep size,
  - punch hole,
  - collapse range,
  - insert range,
  - zero range,
  - write zeroes,
  - POSIX fallocate.
- Supports sparse-file analysis:
  - `--dig-holes` scans data extents and punches zero-filled regions into sparse holes.
  - `--report-holes` reports filesystem holes and zero-filled data holes without modifying the file.
- Uses option-exclusion rules to prevent incompatible modes.
- Requires `--length` for normal allocation/deallocation operations, while dig/report default to the whole file when no length is supplied.
- Validates range overflow against `off_t`.
- Opens with `O_CREAT` only for default allocation or write-zeroes-style allocation, not destructive/special range modes.
- `dig_holes()` uses `SEEK_DATA` / `SEEK_HOLE` to skip existing holes, reads data extents in filesystem block-sized chunks, detects all-zero buffers with a sentinel word scan, and optionally punches those ranges using `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`.
- Uses `posix_fadvise()` when available to mark sequential access and drop cache chunks during scanning.

## Dependencies

- Linux fallocate flags, with fallback definitions when libc headers lack newer constants.
- POSIX `fallocate`, `posix_fallocate`, `lseek(SEEK_DATA/SEEK_HOLE)`, `pread`, `fstat`, and close/write-error handling.
- util-linux parsing, option exclusion, allocation, human size, and i18n helpers.

## Risks And Invariants

- `FALLOC_FL_PUNCH_HOLE` implies `FALLOC_FL_KEEP_SIZE`.
- Zero-length normal fallocate is rejected; dig/report use length zero as whole-file sentinel.
- `is_nul()` requires the caller to allocate extra sentinel space after the buffer.
- Hole punching near extent ends may enlarge allocation size to meet block boundaries while reporting the true zero-data size.
- Close errors are treated as write failures.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/fallocate.c -->