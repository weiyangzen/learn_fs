# Group Research: group_1137_lvm2_sources_block_storage_lvm2_libdm_dm_tools_dmsetup_c_sources_bl_c3a11decbcc8

Scope: `Docs/research_subset_a.md`; source tree `sources/block-storage/lvm2` is included in subset A.

Read coverage: complete read of all listed files, 8,129 total source lines.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/dmsetup.c -->
# File Research: sources/block-storage/lvm2/libdm/dm-tools/dmsetup.c

Purpose: implements the main device-mapper userspace command driver for `dmsetup`, `dmstats`, `dmsetup stats`, `devmap_name`, `dmvdostats`, and limited `losetup`/`dmlosetup` compatibility.

Read coverage: complete file read, 7,282 lines.

Key responsibilities:
- Parses global command-line switches, selects the active base command, validates option combinations, and dispatches to command tables.
- Implements core device-mapper operations through libdevmapper tasks: create, load/reload, suspend, resume, clear, remove/remove_all, wait, message, rename, setgeometry, mknodes, info, deps, status, table, targets, target-version, version, mangle, and IMA measurement.
- Parses mapping tables from files, stdin, `--table`, and `--concise` device specifications, including concise escaping for comma, semicolon, and backslash.
- Coordinates udev cookies, udev rule suppression flags, transaction completion, semaphore cleanup/listing, and library fallback behavior when compiled with udev sync support.
- Builds long and columnar `dm_report` output for mapped-device fields, dependency fields, LVM split-name fields, tree relationship fields, and statistics fields.
- Builds and displays device dependency trees with ASCII, UTF-8, or VT100 drawing symbols plus active/read-write/open-count/UUID annotations.
- Implements `dmstats` region lifecycle and reporting: create, clear, delete, print, list, report, group, ungroup, filemap creation, and filemap update.
- Supports dmstats intervals with timerfd where available or timestamp-adjusted `usleep`, then uses measured intervals for derived per-second metrics.
- Supports precise counters and latency histograms when the kernel driver exposes those features.
- Integrates `dmvdostats` by filtering for single-target `vdo` devices, sending the VDO `stats` message, and delegating verbose/tabular rendering to `dmvdostats.c`.
- Implements limited `losetup` compatibility by translating loop-file arguments into a device-mapper `loop` target table.

Important entry points:
- `main()` performs environment setup, switch parsing, command lookup, report initialization, repeat/interval execution, output flushing, and cleanup.
- `_process_switches()` parses command-line options and normalizes aliases such as `dmstats`, `dmsetup stats`, `devmap_name`, and `vdostats`.
- `_create_one_device()`, `_load()`, `_simple()`, `_status()`, `_info()`, `_deps()`, `_remove()`, and `_remove_all()` are the main DM task operation helpers.
- `_report_init()` selects report object types, default fields, formatting flags, selection expressions, sort keys, and VDO-specific reporting.
- `_stats_create()`, `_stats_delete()`, `_stats_report()`, `_stats_print()`, `_stats_group()`, `_stats_ungroup()`, and `_stats_update_file()` implement dmstats subcommands.
- `_vdostats()` and `_vdostats_process_device()` bridge the main CLI to the VDO stats parser/reporting module.

Dependencies:
- Includes `libdm/misc/dm-logging.h`, `libdm/dm-tools/util.h`, and `libdm/dm-tools/dmvdostats.h`.
- Uses broad libdevmapper APIs: `dm_task`, `dm_info`, `dm_deps`, `dm_tree`, `dm_report`, `dm_stats`, histograms, timestamps, udev helpers, name mangling, device-name resolution, and filemap daemon support.
- Uses libc/POSIX facilities for files, stdio, getopt, locale, fork/exec/wait, ioctl window size, stat/statvfs, semctl, timerfd, canonical path lookup, and environment variables.

Risk and edge cases:
- The program is highly global-state driven; `_switches`, `_int_args`, `_string_args`, `_table`, `_report`, `_dtree`, `_statstype`, `_program_id`, and timer state must be reset or sequenced carefully.
- Several commands reuse common helpers but have subtly different legality rules for UUID, major/minor, all-devices, selection, inactive table queries, open-count suppression, and table input.
- Udev cookie handling is race-sensitive: externally supplied cookies disable fallback in some paths, while forced remove and multi-step operations can conflict with transaction semantics.
- `remove --force` first reloads the device with an `error` target; failure during this sequence can leave the original device cleared/reloaded or require follow-up cleanup.
- Table/status output masks `crypt` and selected `integrity` keys unless `--showkeys` is used; new target parameters with secret material need similar handling.
- `--concise` parsing mutates the input string in place and temporarily reuses global switches for each created device.
- Stats interval reporting depends on measured sample duration; missed timerfd expirations and interrupted sleeps directly affect derived metrics.
- Filemap stats rely on canonical paths, open file descriptors, dmfilemapd mode semantics, and fallback one-shot updates when daemon startup fails.
- Tree output uses fixed `MAX_DEPTH` arrays and truncation logic that depends on terminal width and UTF-8 byte handling.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/dmsetup.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/dmvdostats.c -->
# File Research: sources/block-storage/lvm2/libdm/dm-tools/dmvdostats.c

Purpose: implements VDO statistics retrieval and formatting for `dmsetup vdostats`/`dmvdostats`, supporting legacy-style verbose output and `dm_report` tabular output.

Read coverage: complete file read, 639 lines.

Key responsibilities:
- Sends the `stats` message to a named VDO device with `DM_DEVICE_TARGET_MSG` and returns the kernel target response string.
- Parses VDO stats through `dm_vdo_stats_parse()` in libdevmapper, using full parsing for verbose output and basic parsing for tabular report output.
- Computes derived values: physical size, logical size, used size, available size, write amplification, used percentage, saving percentage, and 512-byte emulation state.
- Computes verbose-only journal backlog fields: entries batching/writing and blocks batching/writing.
- Applies legacy label fixups by stripping selected prefixes, renaming fields, hiding obsolete fields, and printing `N/A` for recovery/read-only/abnormal modes.
- Prints verbose key/value output with aligned labels and inserted derived fields at stable positions.
- Defines a VDO `dm_report` object type and fields for device name, physical size, used size, available size, used percent, and saving percent.
- Initializes VDO reports with default fields and optional user fields, sorting, separator, output flags, and selection expression.
- Emits one report row per VDO device.

Important entry points:
- `vdo_get_stats()` retrieves raw stats text from the device-mapper VDO target.
- `vdostats_print_verbose()` parses full stats and prints legacy verbose output.
- `vdostats_report_init()` creates the tabular report handle.
- `vdostats_report_device()` parses basic stats and submits one object to `dm_report`.

Dependencies:
- Includes `libdm/misc/dm-logging.h`, `libdm/libdevmapper.h`, and `dmvdostats.h`.
- Depends on libdevmapper VDO parsing structures: `dm_vdo_stats_full`, `dm_vdo_stats`, and `dm_vdo_stats_field`.
- Uses display-unit helpers exported from `dmsetup.c`: `get_disp_units()`, `get_disp_factor()`, and `show_units()`.

Risk and edge cases:
- Missing or unparsable stats strings return failure without partial output.
- Many derived values become `N/A` outside normal VDO operating mode, and negative sentinel values are used internally for unavailable sizes/percentages.
- Available size is guarded against used-size overflow beyond physical size.
- Percent calculations assume block counters fit into signed intermediate arithmetic.
- Label fixups mutate parsed field labels and values in place, so they depend on libdevmapper field buffer sizes and exact label names.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/dmvdostats.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/dmvdostats.h -->
# File Research: sources/block-storage/lvm2/libdm/dm-tools/dmvdostats.h

Purpose: declares the VDO stats helper API shared between `dmsetup.c` and `dmvdostats.c`.

Read coverage: complete file read, 39 lines.

Key contents:
- Includes `libdm/libdevmapper.h` for `struct dm_report`, `uint32_t`, and libdm allocation conventions.
- Declares display-unit accessors implemented by `dmsetup.c`: `get_disp_factor()`, `get_disp_units()`, and `show_units()`.
- Declares `vdo_get_stats()` for retrieving raw VDO stats text; the caller must release the returned string with `dm_free()`.
- Declares verbose output and report-mode functions: `vdostats_print_verbose()`, `vdostats_report_init()`, and `vdostats_report_device()`.

Dependencies:
- Coupled to `dmsetup.c` for unit-display state and to `dmvdostats.c` for implementation.
- Uses libdevmapper report types rather than defining a separate reporting abstraction.

Risk and edge cases:
- Ownership of `vdo_get_stats()` output is part of the API contract; callers must use `dm_free()`, not plain `free()`.
- The display-unit functions expose process-global CLI state, so VDO report formatting follows the active `dmsetup` option state.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/dmvdostats.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/util.h -->
# File Research: sources/block-storage/lvm2/libdm/dm-tools/util.h

Purpose: provides small shared utility macros and portability helpers for device-mapper tools.

Read coverage: complete file read, 169 lines.

Key contents:
- Includes `libdm/libdevmapper.h`.
- Defines GCC analyzer diagnostic suppression macros for file-descriptor, malloc-leak, and buffer warnings on GCC 10+ non-Clang builds.
- Defines type-checked GNU-style `min()` and `max()` expression macros.
- Defines `is_power_of_2()`.
- Wraps `dm_strncpy()` as `_dm_strncpy()` with `warn_unused_result`.
- Provides `clz()` and `clzll()` using compiler builtins when available, with fallback implementations for older compilers.
- Requires either system `ffs()` or `__builtin_ffs`; otherwise compilation fails.
- Defines `KERNEL_VERSION()` and printf-format helper macros for sizes, signed/unsigned integer widths, pid values, pointers, and LVM VG IDs.

Dependencies:
- Relies on configuration macros such as `HAVE___BUILTIN_CLZ`, `HAVE___BUILTIN_CLZLL`, `HAVE_FFS`, and `HAVE___BUILTIN_FFS`.
- Relies on libdevmapper macros such as `DM_TO_STRING()` and `ID_LEN`.

Risk and edge cases:
- `min()` and `max()` rely on GNU statement expressions and compile-time type comparison, so they are not ISO C portable.
- `_dm_strncpy()` enforces checked return values only when callers use this wrapper rather than `dm_strncpy()` directly.
- The fallback `clzll()` delegates to `clz()` for 32-bit halves and assumes the configured `clz()` behavior returns bit-width for zero.
- Missing `ffs()` support is a hard build-time error.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/util.h -->