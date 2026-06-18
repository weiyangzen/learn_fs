# sources/distributed-fs/openafs/src/afsmonitor/afsmonitor.c

## Purpose

`afsmonitor.c` is the main implementation of the OpenAFS `afsmonitor` performance monitoring tool. It parses command-line and optional config-file inputs, builds file-server and cache-manager monitor lists, configures xstat probe collections, receives asynchronous xstat callback results, converts raw probe structures into display-ready strings, checks thresholds, optionally writes raw output, and drives the GTX UI refresh functions implemented in `afsmon-win.c`.

## Important APIs, types, and functions

The file owns most shared globals used by the monitor: debug/output flags, probe frequency, host lists, xstat collection counts, circular result buffers, current and previous display buffers, alert counts, and display maps. Local list types include `afsmon_fs_Results_list`, `afsmon_fs_Results_CBuffer`, `afsmon_cm_Results_list`, and `afsmon_cm_Results_CBuffer`. Public structs used across files come from `afsmonitor.h`, especially `afsmon_hostEntry`, `Threshold`, `fs_Display_Data`, and `cm_Display_Data`.

Key routines include `afsmonInit`, the command syntax handler; `process_config_file`, which performs a two-pass parse of config files; `parse_hostEntry`, `parse_threshEntry`, `parse_showEntry`, and `store_threshold`, which build monitor configuration; `afsmon_execute`, which resolves hosts, sets ports, chooses xstat collection IDs, initializes xstat FS/CM probes, and starts GTX input; `afsmon_FS_Handler` and `afsmon_CM_Handler`, xstat callbacks; `save_*_results_inCB`, optional circular-buffer persistence; `save_*_data_forDisplay`, completed-cycle display snapshot logic; `fs_Results_ltoa`, `fs_FullPerfs_ltoa`, `fs_CallBackStats_ltoa`, and `cm_Results_ltoa`, which flatten xstat structures into strings; `check_*_thresholds` and `execute_thresh_handler`; and `afsmon_Exit`, the central cleanup/exit path.

## Control flow

`main` defines the `initcmd` syntax and dispatches through the OpenAFS `cmd` package. `afsmonInit` opens debugging and output files, validates frequency and option combinations, accepts host lists directly or processes a config file, initializes default or requested display maps, sets a SIGINT handler, allocates optional circular buffers and mandatory display buffers, initializes GTX, and then calls `afsmon_execute`.

Config-file parsing is deliberately two-pass. The first pass validates syntax, resolves and records host names, counts global and per-host thresholds, and processes `show` directives into display maps. After global threshold counts are added to each host's allocation count, the second pass allocates threshold arrays and stores threshold metadata with positional indexes into FS/CM display arrays. Global thresholds are applied to all known hosts, while local thresholds apply to the last host of the correct type.

`afsmon_execute` resolves all FS and CM host names to sockets and initializes xstat. FS collection IDs are chosen based on requested display fields: full performance stats, callback stats, or both. CM always requests full performance stats. After `xstat_fs_Init` and/or `xstat_cm_Init`, the GTX input server runs. xstat invokes `afsmon_FS_Handler` and `afsmon_CM_Handler` as probe results arrive.

Each handler optionally writes output, detects a new probe cycle by comparing probe numbers, advances circular-buffer indexes when needed, stores raw-ish copied probe results if circular buffers are enabled, and passes the current result to the display path. The display path finds the matching host slot, marks failed probes, converts successful probe data to strings, checks thresholds, and increments a static received-result count. Once all hosts and collections for the cycle have arrived, it verifies probe sequence continuity, copies `curr_*Data` to `prev_*Data`, clears current values while preserving threshold flags, recomputes alert totals, marks data available, and calls `ovw_refresh` plus the relevant detail-frame refresh.

## State and persistence behavior

Most state is in process globals and is reset at startup. The optional `-buffers` setting creates an in-memory circular history of copied xstat probe results, one linked-list row per host per buffer slot and per collection. This history is not persisted to disk and is freed in `afsmon_Exit`. Persistent filesystem effects are limited to the optional debug file and optional output file written via `afsmon_fsOutput`/`afsmon_cmOutput`. Threshold handlers can fork and exec external programs, passing host, host type, threshold name, threshold value, actual value, and handler-specified arguments.

## Dependencies and integration points

The file depends on OpenAFS command parsing (`afs/cmd.h`), GTX UI APIs through the exported functions in `afsmonitor.h`, xstat FS/CM client APIs and global `xstat_*_Results` objects, label/category arrays from other afsmonitor compilation units, host resolution through libc, and OpenAFS utility macros such as `opr_min`. It integrates with `afsmon-output.c` for optional output, `afsmon-win.c` for UI refresh/initialization, and xstat server/cache-manager collection contracts for raw data layout.

## Risks and edge cases

The implementation uses many fixed-size buffers and unbounded `sscanf`, `sprintf`, and some `strncpy` patterns. Long config tokens, host names, output names, handler strings, or label values are important risk areas. Threshold handler parsing is whitespace-only and stores at most 20 arguments in fixed 256-byte slots. A forked handler path calls `afsmon_Exit`, which performs broad cleanup before `execvp`; this is intentional but complex. Raw xstat conversion relies on fixed result-length constants and layout assumptions; comments note that those constants must be changed if xstat structures change. `fs_FullPerfs_ltoa` has special handling for 64-bit `struct timeval`, while CM conversion casts the full result buffer directly to `struct afs_stats_CMFullPerf` without an explicit decoder. Allocation failure handling in circular-buffer creation frees only allocations from the current partial item and relies on later `afsmon_Exit` for already-linked objects. `init_print_buffers` appears to initialize `tmp_fsData2` from `curr_fsData` instead of `prev_fsData`, and similarly for CM, which can leave `prev_*Data` host names empty until the first completed copy.

## Test signals

High-value tests include config parsing with global thresholds, per-host thresholds, duplicated threshold names, invalid section/group/variable names, command-line host lists, and mutually exclusive option combinations. xstat integration tests should cover successful and failed probes, missed probe numbers, FS full-perf-only, FS callback-only, both FS collections, and CM full-perf collection. UI smoke tests should confirm `prev_*Data` is populated before first refresh, threshold transitions trigger handlers only on crossing transitions, alert counts match failed probes plus overflows, and output/debug files are written when requested. Memory-checking runs should exercise `-buffers` with multiple slots and shutdown.
