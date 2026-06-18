# File Research: sources/block-storage/lvm2/libdm/dm-tools/dmsetup.c

Purpose: implements the main device-mapper userspace command driver for `dmsetup`, `dmstats`, `dmsetup stats`, `devmap_name`, `dmvdostats`, and limited `losetup`/`dmlosetup` compatibility.

Read coverage: complete file read, 7,282 lines.

Key responsibilities:
- Parses global command-line switches, selects the active base command, validates option combinations, and dispatches to command tables.
- Implements core device-mapper operations through libdevmapper tasks: create, load/reload, suspend, resume, clear, remove/remove_all, wait, message, rename, setgeometry, mknodes, info, deps, status, table, targets, target-version, version, and mangle.
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
