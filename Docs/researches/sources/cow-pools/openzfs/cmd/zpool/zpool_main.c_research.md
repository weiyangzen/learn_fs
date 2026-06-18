# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool_main.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9956, source bytes 262134, report `Docs/researches/chunks/chunk_sources_cow_pools_openzfs_cmd_zpool_zpool_main_c_1_1_9956_f84ed2fad383_research.md`
- chunk 2: lines 9957-13962, source bytes 109863, report `Docs/researches/chunks/chunk_sources_cow_pools_openzfs_cmd_zpool_zpool_main_c_2_9957_13962_6f1c50fe1d65_research.md`

## Chunk Research

### Chunk 1: lines 1-9956

# Chunk Research: sources/cow-pools/openzfs/cmd/zpool/zpool_main.c lines 1-9956

## Scope

This chunk is the first 9,956 lines of OpenZFS `cmd/zpool/zpool_main.c`, the main implementation file for the `zpool` CLI. It covers command registration and usage, pool/vdev creation and mutation commands, import/export, list/iostat output, parts of status output, scan/scrub/trim commands, and the beginning of the JSON status emitter. The chunk ends inside `scan_status_nvlist()`, so the complete `zpool status` JSON and CLI status command flow continue in the next chunk.

## Command Dispatch and Global State

- Includes standard POSIX/system headers plus OpenZFS public and private CLI-facing headers: `libzfs.h`, `libzutil.h`, `zpool_util.h`, `zfs_comutil.h`, `zfeature_common.h`, `zfs_valstr.h`, and `statcommon.h`.
- Global process state:
  - `libzfs_handle_t *g_zfs` is the shared libzfs handle used by all subcommands.
  - `mount_tp_nthr` defaults to 512 and controls parallel dataset mounting during import/split.
  - `current_command`, `current_prop_type`, `history_str`, `log_history`, and `timestamp_fmt` coordinate usage text, property help, zpool history logging, and repeated-output timestamps.
- `zpool_help_t`, `zpool_command_t`, and `command_table[]` define the recognized subcommands and connect names such as `create`, `import`, `status`, `iostat`, `trim`, `wait`, and `ddtprune` to implementation functions.
- `usage()` prints either global or command-specific help, conditionally lists pool/vdev properties for `get`, `set`, and `list`, honors `ZFS_ABORT` for debug core dumps, and exits directly. This makes error paths throughout the file terminate rather than return.

## Shared Helpers and Data Model

- Several string tables map kernel/libzfs enum values to output strings:
  - pool scan function/state, vdev rebuild state, checkpoint state, vdev state/aux, initialize state, and trim state.
  - These arrays are indexed directly by enum values; additions or enum reordering in headers must be kept in sync.
- Vdev display helpers:
  - `print_vdev_tree()`, `print_cache_list()`, and `print_spare_list()` recursively render dry-run pool topologies.
  - `max_width()` recursively calculates name column width across children, spares, and L2ARC.
  - `fill_vdev_info()` converts an nvlist vdev into JSON-ish metadata including name, type, GUID, path, physical path, devid, class, and state.
- Property helpers:
  - `add_prop_list()` validates pool/vdev/filesystem properties, normalizes names, blocks duplicate properties except cachefile, rejects invalid `feature@`/`version` combinations, and enforces compatibility/version constraints.
  - `add_prop_list_default()` sets a default only when absent.
  - `prop_list_contains_feature()` detects explicit feature properties.
- JSON helpers:
  - `zpool_json_schema()` adds an `output_version` object including `zpool <command>`.
  - `nice_num_str_nvlist()` stores numbers either as formatted strings or integers depending on literal/JSON options.
  - `fill_pool_info()` and `fill_vdev_info()` are reused by `list` and `status` JSON output.
- Spare discovery:
  - `find_vdev()`, `find_spare()`, and `used_by_other()` recursively search pool configs to identify whether a spare is in use by another pool.
- Power-control helpers:
  - `zpool_power_on()`, `zpool_power_on_and_disk_wait()`, `zpool_power_on_pool_and_wait_for_devices()`, and `zpool_power_off()` wrap libzfs slot power APIs and disk-wait behavior.
  - These are used by `online`, `offline --power`, `clear --power`, and status power reporting.

## Pool Creation and Mutation Commands

- `zpool_do_create()` implements `zpool create`.
  - Parses force/dry-run/disable-feature flags, altroot, mountpoint, temporary name, pool properties, root filesystem properties, and feature compatibility.
  - Delegates vdev nvlist construction to `make_root_vdev()` in another file.
  - Validates pool names, altroot, mountpoint syntax and emptiness, and requires at least one allocatable top-level vdev.
  - For non-dry-run creation, loads the requested compatibility feature set with `zpool_do_load_compat()` and auto-enables supported features unless disabled by `-d` or legacy version selection.
  - Calls `zpool_create()`, then opens/mounts/shares the root dataset.
- `zpool_do_add()` implements `zpool add`.
  - Parses force/dry-run/name-format flags, ashift property, and long options that independently relax in-use, replication, or ashift checks.
  - Defaults add-time ashift from the pool property when set.
  - Uses `make_root_vdev()` and either prints the merged dry-run topology or calls `zpool_add()`.
- `zpool_do_remove()` implements vdev removal and removal cancellation.
  - Supports dry-run memory estimate (`-n`), parsable output (`-p`), stop (`-s`), and wait (`-w`).
  - Calls `zpool_vdev_indirect_size()`, `zpool_vdev_remove()`, `zpool_vdev_remove_cancel()`, and optionally `zpool_wait(..., ZPOOL_WAIT_REMOVE)`.
- `zpool_do_attach_or_replace()` backs both `attach` and `replace`.
  - Parses force, ashift, sequential rebuild, and wait options.
  - Builds a new vdev config with `make_root_vdev()` and calls `zpool_vdev_attach()`.
  - Wait mode selects `ZPOOL_WAIT_REPLACE`, `ZPOOL_WAIT_RESILVER`, or `ZPOOL_WAIT_RAIDZ_EXPAND` based on replacing/rebuild context.
- `zpool_do_detach()` simply validates pool/device arguments and calls `zpool_vdev_detach()`.
- `zpool_do_split()` handles mirror split dry-runs, optional import with altroot/mount options, and optional key loading. The actual split topology comes from `split_mirror_vdev()`, then import/mount uses `zpool_open_canfail()`, `zfs_crypto_attempt_load_keys()`, and `zpool_enable_datasets()`.
- `zpool_do_labelclear()` resolves a vdev path, opens it read-write, flushes block-device cache, reads labels, checks pool-use state, and clears labels. It deliberately refuses active/spare/L2ARC devices unless force is acceptable and the device is not active under `O_EXCL`.
- `zpool_do_destroy()` disables datasets, disables separate history logging because destroy logs during export, and calls `zpool_destroy()`.
- `zpool_do_checkpoint()` and `zpool_do_prefetch()` are small wrappers around checkpoint/discard/wait and DDT/BRT prefetch libzfs operations.
- `zpool_do_online()`, `zpool_do_offline()`, `zpool_do_clear()`, `zpool_do_reguid()`, and `zpool_do_reopen()` implement operational state changes, including slot power support, fault/offline semantics, clear policy nvlist allocation, explicit GUID setting, and pool reopen with optional scrub restart suppression.

## Import and Export

- Export:
  - `export_cbdata_t` carries taskq, mnttab mutex, force/hardforce flags, and aggregate return value.
  - `zpool_export_one()` serializes `zpool_disable_datasets()` for parallel `-a` export because mnttab access is not thread-safe, then calls `zpool_export()` or `zpool_export_force()`.
  - `zpool_export_task()` reopens pools by saved name in worker threads.
  - `zpool_do_export()` supports `-a`, `-f`, and hidden hard force `-F`, creates a taskq sized from CPU count for export-all, and disables normal CLI history logging because export logs its own history.
- Import discovery and display:
  - `show_import()` renders available imported candidates, status reasons, action text, msg URLs, comments, and imported vdev config, using `zpool_import_status()`, `zpool_collect_unsup_feat()`, and config nvlists.
  - `zfs_force_import_required()` checks pool state, hostid, and MMP state to decide whether `-f` is required.
  - `do_import()` validates SPA version, rejects foreign/MMP-active imports unless `ZFS_IMPORT_ANY_HOST` is set, calls `zpool_import_props()`, optionally loads encryption keys, and mounts/shares datasets unless `ZFS_IMPORT_ONLY`.
  - `import_pools()` post-processes discovered candidate configs, filters destroyed/non-destroyed pools, handles duplicate names/GUID search, parallelizes `import -a`, and displays candidates when no pool is selected.
  - `zpool_do_import()` parses discovery paths/cachefile/env (`ZPOOL_IMPORT_PATH`), force, rewind, destroyed-pool, key-load, mount-only, altroot, temporary name, txg, verbatim, checkpoint rewind, and scan options. It builds a load policy nvlist and invokes `zpool_search_import()`, then falls back from cachefile import to scanned directories on failure.

## Listing and I/O Statistics

- `zpool_do_iostat()` is a large repeated-output command with pool/vdev argument disambiguation.
  - Supports script execution per vdev with `-c`, guarded by `ZPOOL_SCRIPTS_ENABLED` and `ZPOOL_SCRIPTS_AS_ROOT`.
  - Supports pool/vdev names, GUID names, full paths, follow-links, verbose trees, parsable/scripted output, latency/queue stats, latency/request-size histograms, timestamps, omit-since-boot, and header-once behavior.
  - Uses `pool_list_get()`, `pool_list_refresh()`, `pool_list_iter()`, and `pool_list_free()` to handle changing pool sets during interval loops.
  - `get_stat_flags()` intersects module-supported stat fields across all selected pools before enabling extended iostat views.
  - `print_vdev_stats()` recursively prints normal, dedup, special, log, and L2ARC devices; it subtracts old/new vdev stats and scales by timestamp delta.
  - Histogram support uses `ZPOOL_CONFIG_VDEV_STATS_EX`, `calc_and_alloc_stats_ex()`, `single_histo_average()`, and fixed nvlist-name tables to format latency and request-size distributions.
- `zpool_do_list()` implements pool and optional verbose vdev listing with text or JSON output.
  - Parses property lists using `zprop_get_list()`, supports timestamps, JSON integer mode, and pool GUIDs as JSON object keys.
  - `collect_pool()` gathers pool properties, including feature/user properties.
  - `collect_list_stats()` recursively emits vdev properties for normal, class, L2ARC, and spare devices, with special handling for vdev-only properties such as size, alloc/free, checkpoint, expandsize, fragmentation, capacity, and health.
  - JSON output nests pool data under `pools`, with optional `vdevs`, `l2cache`, `spares`, and class-specific sections.

## Status Output Covered in This Chunk

- Text status support begins in this chunk:
  - `status_cbdata_t` carries all status-format flags, including verbose, literal, explain, dedup stats, unhealthy-only, slow I/O, direct I/O verify, init/trim details, custom script output, power state, JSON options, and flat-vdev JSON.
  - `print_status_config()` recursively prints live pool vdev trees with health coloring, read/write/checksum/slow I/O columns, power state, direct I/O verify errors, aux fault text, non-native ashift warnings, removal/noalloc markers, resilver/repair/rebuild annotations, custom script columns, and leaf init/trim state.
  - `print_import_config()` and `print_class_vdevs()` render import candidate vdev trees and class vdevs.
  - `vdev_health_check_cb()` supports unhealthy-only pruning.
  - `zpool_print_cmd()` and `zpool_nvlist_cmd()` merge user script columns into text and JSON status/iostat outputs.
- Scan/rebuild status formatting:
  - `secs_to_dhms()`, `print_err_scrub_status()`, `print_scan_scrub_resilver_status()`, `print_rebuild_status_impl()`, `print_rebuild_status()`, `print_checkpoint_scan_warning()`, and `check_rebuilding()` convert scan, resilver, error scrub, checkpoint, and rebuild stats into human-readable progress and warning text.
- JSON status support begins near the end:
  - `vdev_stats_nvlist()` recursively converts vdev stats to nvlists, including parent links for flat output, spare state, alloc/space/error counters, scan/checkpoint/removal flags, power, custom script output, init state, and trim state.
  - `class_vdevs_nvlist()`, `l2cache_nvlist()`, and `spares_nvlist()` emit class/L2ARC/spare vdev groups or flatten leaves depending on `cb_flat_vdevs`.
  - `errors_nvlist()` adds error counts and, in verbose mode, attempts to convert errlog dataset/object IDs to paths via `zpool_obj_to_path()`.
  - `ddt_stats_nvlist()` and `dedup_stats_nvlist()` emit DDT totals, object stats, cached/in-core size, and histogram entries.
  - `raidz_expand_status_nvlist()`, `checkpoint_status_nvlist()`, and `removal_status_nvlist()` emit pool-level operation progress.
  - The chunk ends inside `scan_status_nvlist()` after adding scan `skipped`; the rest of scan/rebuild JSON assembly and the caller are cross-chunk.

## Scrub, Resilver, Initialize, and Trim

- `zpool_do_initialize()` handles pool/vdev initialization.
  - Supports all pools (`-a`), cancel/suspend/uninitialize/start modes, and wait.
  - Uses `zpool_initialize_one()` for whole-pool/all-pool flows and `zpool_initialize()` or `zpool_initialize_wait()` for selected leaf vdevs.
- `zpool_do_scrub()` supports normal scrub, error scrub, stop, pause, continuation from last txg, start/end date ranges, all pools, and wait.
  - Validates mutually exclusive combinations and restricts date ranges to normal scrubs.
  - Dispatches through `for_each_pool()` to `scrub_callback()`, which calls `zpool_scan_range()` and warns when checkpoints exclude checkpoint-only blocks.
- `zpool_do_resilver()` restarts resilvering by reusing `scrub_callback()` with `POOL_SCAN_RESILVER`.
- `zpool_do_trim()` supports full-pool/all-pool trim, selected vdev trim, cancel, suspend, secure trim, rate limiting, and wait.
  - Uses `zpool_trim_one()` for full pool/all pool and `zpool_trim()` for selected vdevs.

## External Dependencies and APIs

- Heavy libzfs/libzutil dependencies: `zpool_open*`, `zpool_close`, `zpool_get_config`, `zpool_create`, `zpool_add`, `zpool_destroy`, `zpool_export*`, `zpool_import_props`, `zpool_search_import`, `zpool_enable_datasets`, `zpool_disable_datasets`, `zpool_wait`, `zpool_vdev_*`, `zpool_power*`, `zpool_clear`, `zpool_set_guid`, `zpool_prefetch`, `zpool_checkpoint`, `zpool_discard_checkpoint`, `zpool_scan_range`, `zpool_trim`, `zpool_trim_one`, and many property helpers.
- Nvlist/fnvlist APIs are the primary data exchange format with libzfs and kernel-derived pool configs.
- Task queues (`taskq_create`, `taskq_dispatch`, `taskq_wait`, `taskq_destroy`) are used for parallel export/import.
- POSIX APIs used directly include `getopt/getopt_long`, `open/close`, `opendir/readdir/closedir`, `stat`, `ioctl(TIOCGWINSZ)`, `strptime/mktime/ctime`, `getuid/geteuid`, `sysconf`, and environment variables.
- Other source files are required for complete behavior: vdev parsing/building (`make_root_vdev`, `split_mirror_vdev`), pool iteration/list management (`for_each_pool`, `pool_list_*`), zpool utility callbacks (`zpool_sync_one`, `zpool_reopen_one`, `zpool_initialize_one`, `zpool_trim_one`), command script execution, and the remaining status/history/get/set/wait/upgrade/main code after this chunk.

## Control-Flow Risks and Edge Cases

- Many helpers index string tables directly by kernel enum fields. Unknown enum values from newer kernels could cause out-of-bounds reads unless upstream enum compatibility is preserved.
- Many config reads use `verify()`/`fnvlist_lookup_*`, so malformed or incomplete nvlists can abort the process instead of producing recoverable CLI errors.
- `usage()` exits, so callers sometimes allocate before validation and rely on process termination rather than cleanup on bad usage.
- `import -a` and `export -a` update shared integer return state from taskq workers without explicit locking. It is only used as an aggregate failure flag, but it is still shared mutable state.
- `zpool_do_online()` returns immediately on power-on failure without closing the opened pool handle; this is a local leak on that error path.
- `zpool_do_offline()` error text says `-0` for `--power` conflicts, which looks like a user-facing typo.
- `zpool_do_add()` and attach/replace call `nvlist_exists(props, ...)` while `props` may still be `NULL`; correctness depends on nvlist API tolerance for NULL or this is a latent null dereference.
- Several JSON builders allocate temporary nvlists conditionally. Review next chunk for cleanup after `scan_status_nvlist()` because this chunk ends mid-function.
- Date parsing for scrub uses local timezone via `mktime()` and inclusive end rounding; behavior around DST boundaries depends on libc.
- `zpool_do_import()` mutates option strings in-place when splitting `-o key=value`; callers must provide mutable argv storage, which is normal for C `argv` but worth noting for tests/fuzzing.

## Cross-Chunk References

- `scan_status_nvlist()` starts at line 9932 and is incomplete at the line-9956 boundary. The next chunk must cover the rest of this function and how it is called.
- The actual `zpool_do_status()` implementation is declared and partially supported by helpers here but appears after this chunk.
- The command table references functions implemented after this chunk: `zpool_do_upgrade`, `zpool_do_history`, `zpool_do_events`, `zpool_do_get`, `zpool_do_set`, `zpool_do_version`, `zpool_do_wait`, `zpool_do_ddt_prune`, `zpool_do_help`, `zpool_do_load_compat`, and likely `main()`.
- Helpers defined here are consumed later by status JSON/text output and possibly by final command dispatch/history handling.

### Chunk 2: lines 9957-13962

# Chunk Research: sources/cow-pools/openzfs/cmd/zpool/zpool_main.c lines 9957-13962

## Scope

This report covers chunk 2 of `sources/cow-pools/openzfs/cmd/zpool/zpool_main.c`, lines 9957-13962, within `Docs/research_subset_a.md` COW pool/OpenZFS scope. The chunk is the tail of the `zpool` CLI implementation. It covers status JSON/text rendering, pool upgrade, history, event display, pool/vdev property get/set, wait/progress reporting, DDT pruning, version/help compatibility helpers, and the program `main()` dispatcher. The line range starts inside `scan_status_nvlist()` and ends at process exit.

## Primary APIs In This Chunk

- Status report APIs:
  - `scan_status_nvlist()` completes JSON scan/error-scrub/rebuild status export.
  - `print_scan_status()`, `print_removal_status()`, `print_raidz_expand_status()`, `print_checkpoint_status()`, `print_error_log()`, `print_spares()`, `print_l2cache()`, and `print_dedup_stats()` render human-readable `zpool status` details.
  - `print_status_reason()` maps `zpool_status_t` and `zpool_errata_t` values to user-facing status/action text or JSON fields.
  - `status_callback_json()` and `status_callback()` are the per-pool callbacks used by `zpool_do_status()`.
- Command entry points:
  - `zpool_do_status()`
  - `zpool_do_upgrade()`
  - `zpool_do_history()`
  - `zpool_do_events()`
  - `zpool_do_get()`
  - `zpool_do_set()`
  - `zpool_do_wait()`
  - `zpool_do_ddt_prune()`
  - `zpool_do_version()`
  - `zpool_do_help()`
- Upgrade helpers:
  - `check_unsupp_fs()`
  - `upgrade_version()`
  - `upgrade_enable_all()`
  - `upgrade_cb()`
  - `upgrade_list_older_cb()`
  - `upgrade_list_disabled_cb()`
  - `upgrade_one()`
- History/event helpers:
  - `print_history_records()`
  - `get_history_one()`
  - `zpool_do_events_short()`
  - `zpool_do_events_nvprint()`
  - `zpool_do_events_next()`
  - `zpool_do_events_clear()`
- Property helpers:
  - `get_callback_vdev()`
  - `get_callback_vdev_cb()`
  - `get_callback()`
  - `set_pool_callback()`
  - `set_callback()`
- Wait helpers:
  - `vdev_activity_remaining()`
  - `vdev_activity_top_remaining()`
  - `vdev_any_spare_replacing()`
  - `print_wait_status_row()`
  - `wait_status_thread()`
- Dispatch/support helpers:
  - `find_command_idx()`
  - `zpool_do_load_compat()`
  - `main()`

## Core Data And State

- `status_cbdata_t` is the main `zpool status` state carrier. In this chunk it controls JSON mode, literal/integer formatting, health-only filtering, vdev name flags, dedup stats, command-column output, flat JSON vdev layout, slow I/O/power/DIO columns, first-pool spacing, and all-pools accounting.
- Pool configuration and statistics are carried through nvlists from `zpool_get_config()` and fields under `ZPOOL_CONFIG_VDEV_TREE`, including `ZPOOL_CONFIG_SCAN_STATS`, `ZPOOL_CONFIG_REBUILD_STATS`, `ZPOOL_CONFIG_REMOVAL_STATS`, `ZPOOL_CONFIG_CHECKPOINT_STATS`, `ZPOOL_CONFIG_RAIDZ_EXPAND_STATS`, `ZPOOL_CONFIG_L2CACHE`, `ZPOOL_CONFIG_SPARES`, `ZPOOL_CONFIG_DDT_*`, and `ZPOOL_CONFIG_ERRCOUNT`.
- Status rendering uses on-disk/kernel statistics structs exposed through nvlist uint64 arrays: `pool_scan_stat_t`, `vdev_rebuild_stat_t`, `pool_removal_stat_t`, `pool_checkpoint_stat_t`, `pool_raidz_expand_stat_t`, `vdev_stat_t`, `ddt_object_t`, `ddt_stat_t`, and `ddt_histogram_t`.
- Upgrade state uses `upgrade_cbdata_t` with selected target version, original argv/argc, and first-output tracking. Feature enablement is compared against `spa_feature_table[]`, `SPA_FEATURES`, compatibility-set booleans loaded by `zpool_do_load_compat()`, and currently enabled feature nvlists from `zpool_get_features()`.
- History state uses `hist_cbdata_t` to choose long format and internal record printing. Event state uses `ev_opts_t` for verbose/scripted/follow/clear mode and optional pool-name filtering.
- Property get state uses `zprop_get_cbdata_t`, including proplist, columns, JSON object, literal formatting, pool-vs-vdev type, vdev names, and JSON keying by pool GUID. Property set state uses `set_cbdata_t` with property name/value, pool-vs-vdev target type, vdev name data, and success state.
- Wait state uses `wait_data_t`, which contains selected wait activities, formatting options, polling interval, pool name, and a `pthread_mutex_t`/`pthread_cond_t` pair used to stop the status-printing thread.
- Global process state visible here includes `g_zfs`, `history_str`, `log_history`, `current_command`, `command_table`, `timestamp_fmt`, `current_prop_type`, `opterr`, and locale/textdomain settings.

## Control Flow

### Status JSON And Text Rendering

The chunk begins in `scan_status_nvlist()`, finishing JSON export of scrub/resilver counters, optional error-scrub fields, and per-top-vdev rebuild stats. Rebuild stats are nested by vdev name, with `fill_vdev_info()` metadata plus state, timing, byte counters, pass counters, skipped bytes, and errors.

`print_scan_status()` chooses which active or historical scan-like status to print. It detects current resilver/scrub/error-scrub data, checks top-level rebuild state through `check_rebuilding()`, always prints scrub or error-scrub when available, then prints either active/latest resilver or active/latest rebuild depending on end times. It also prints checkpoint warnings after looking up checkpoint stats.

`print_removal_status()` and `print_raidz_expand_status()` both look up the affected top-level child vdev, format finished/canceled/in-progress states, compute progress from copied/reflowed bytes, estimate remaining time from current elapsed wall time, and suppress huge estimates above roughly 30 days. Removal additionally reports mapping memory.

`print_status_reason()` is a large status/action mapping from libzfs health reasons to operator guidance. It handles missing/faulted/removed devices, corrupt labels, active resilver/rebuild, recommended scrub after sequential resilver, corrupt data/pool, old/new pool versions, disabled or incompatible features, unsupported read/write features, MMP suspension, I/O failure, bad log, non-native ashift, hostid mismatch, and OpenZFS errata. It writes JSON fields when `cb_json` is active and otherwise prints colored text.

`status_callback_json()` builds a pool object under `"pools"`, optionally keyed by pool GUID. It fills pool info, status/action/msgid, load info, scan/removal/checkpoint/raidz-expand status, vdev stats, class vdevs, L2ARC/cache and spares, dedup stats, and errors. `status_callback()` performs the corresponding text report, including state coloring, status/action text, scan/removal/checkpoint/expand sections, config table headers, recursive vdev layout, class vdevs, L2ARC/cache/spares, data-error log summary, and optional DDT dump.

`zpool_do_status()` parses `-c`, `-d`, `-D`, `-e`, `-g`, `-i`, `-j`, `-L`, `-p`, `-P`, `-s`, `-t`, `-T`, `-v`, `-x`, `--power`, `--json-int`, `--json-flat-vdevs`, and `--json-pool-key-guid`. It validates JSON-only options, optionally runs configured per-vdev scripts, repeatedly invokes `for_each_pool()` for interval/count mode, emits timestamps, prints JSON documents per iteration, and handles "no pools" / "all pools are healthy" messages.

### Pool Upgrade

`upgrade_version()` refuses upgrade if any filesystem version exceeds `ZPL_VERSION`, refuses legacy compatibility mode, then calls `zpool_upgrade()` and prints old-to-new version or feature-flag success. `check_unsupp_fs()` recursively walks filesystems using `zfs_iter_filesystems_v2()`.

`upgrade_enable_all()` loads the pool compatibility set and enables every supported, requested, not-yet-enabled feature that is not flagged `ZFEATURE_FLAG_NO_UPGRADE`. It sets properties named `feature@<name>` to `ZFS_FEATURE_ENABLED` and prints the enabled list.

The upgrade callbacks handle `zpool upgrade -a`, list legacy pools, list disabled supported features, and upgrade a single pool. `upgrade_one()` rejects the reserved pool name `log`, handles already-newer/already-target-version cases, upgrades legacy versions, enables feature flags when appropriate, and calls `after_zpool_upgrade()` after modifications.

`zpool_do_upgrade()` parses `-a`, `-v`, and `-V version`, validates incompatible combinations, prints supported feature flags and legacy versions in show-version mode, upgrades all pools, lists upgradeable pools and disabled features when no pools are supplied, or applies upgrades to specified pools.

### History And Events

`print_history_records()` iterates `ZPOOL_HIST_RECORD` arrays. It formats timestamps, optional elapsed milliseconds, user commands, legacy internal event records, internal name records with dataset details, ioctl records with input/output nvlists or omitted sizes, errno values, and unrecognized records. Long format appends UID/user, host, and zone.

`get_history_one()` pages through history with `zpool_get_history()` using offset/eof state and prints all records for one pool. `zpool_do_history()` parses `-l` and `-i`, then delegates through `for_each_pool()`.

`zpool_do_events_short()` prints event time and class. `zpool_do_events_nvprint()` recursively dumps arbitrary event nvlists and adds readable annotations for ZIO stage/pipeline/type/priority/flags and vdev state fields. `zpool_do_events_next()` opens `ZFS_DEV`, repeatedly calls `zpool_events_next()` in blocking or nonblocking mode, reports dropped events, filters by pool name, prints short and optional verbose forms, and frees each event nvlist. `zpool_do_events_clear()` clears queued events. `zpool_do_events()` parses `-v`, `-H`, `-f`, `-c`, validates pool-name and clear-mode combinations, and dispatches.

### Pool And Vdev Properties

`get_callback_vdev()` collects requested vdev properties via `zpool_get_vdev_prop()`, either printing through `zprop_collect_property()` or accumulating JSON under `"vdevs"`. It skips the synthetic leading pool-name placeholder in the proplist.

`get_callback_vdev_cb()` adapts `for_each_vdev()` traversal to property retrieval. It special-cases the root vdev as `root-0`, because display naming would otherwise transform it to the pool name, expands the vdev proplist, and calls `get_callback_vdev()`.

`get_callback()` handles either vdev or pool property retrieval. Pool properties include user properties, feature/unsupported properties, and normal pool properties via `zpool_get_prop()`. JSON pool objects include `fill_pool_info()` and can be keyed by GUID.

`zpool_do_get()` parses output columns, scripted/literal/JSON modes, pool-GUID keying, and JSON integer mode. It distinguishes these argument shapes: no pool arguments, all pool names, one pool followed by vdev names, `all-vdevs`, and `root`. It validates unresolved vdevs, builds a proplist with a fake leading `name` property for display, initializes JSON `"pools"` or `"vdevs"`, invokes `for_each_pool()`, prints/frees JSON, frees property lists, and releases a duplicated root-vdev name.

`set_pool_callback()` validates compatibility-property changes and feature enablement. When setting `compatibility`, it warns if already-enabled pool features are outside the new set. When enabling a feature, it rejects enablement if the current compatibility set does not request that feature. `set_callback()` applies either `zpool_set_vdev_prop()` or `set_pool_callback()`.

`zpool_do_set()` accepts `property=value pool [vdev]`, rejects option-like arguments, validates pool existence, optionally maps `root` to `root-0`, validates the vdev, switches target type to `ZFS_TYPE_VDEV`, and applies the change through `for_each_pool()`.

### Wait And DDT Prune

`vdev_activity_remaining()` recursively sums initialize or trim remaining bytes over a vdev tree. `vdev_activity_top_remaining()` sums active rebuild remaining bytes over top-level children only. `vdev_any_spare_replacing()` recursively detects spare/replacing/dRAID-spare vdevs for replace-progress heuristics.

`print_wait_status_row()` computes remaining work for checkpoint discard, freeing, initialize, replace, remove, resilver, scrub, trim, and raidz expansion. It refreshes data from pool properties and config stats, treats rebuild as resilver if no active scan is present, uses a documented heuristic for replace progress based on spare/replacing vdev presence, and prints either exact integer or human-readable columns with optional timestamps and periodic headers.

`wait_status_thread()` owns a separate pool handle, refreshes stats/properties, prints rows at the requested interval, and exits when signaled by the main thread or on refresh/condition-variable errors. `zpool_do_wait()` parses `-H`, `-p`, `-T`, and `-t activity[,activity...]`; note that the switch includes a `case 'n'` for one-time headers but the getopt string in this chunk is `"HpT:t:"`, so `-n` is not actually accepted here. It rejects a count argument, opens the pool, optionally starts the status thread, loops over enabled `zpool_wait_status()` activities until none were waited, then signals and joins the thread and destroys synchronization primitives.

`zpool_do_ddt_prune()` parses exactly one of `-d days` or `-p percent`, validates positive days or 1-100 percent, converts days to seconds, opens the pool, calls `zpool_ddt_prune()`, and closes the pool.

### Process Dispatch

`find_command_idx()` searches `command_table` by name. `zpool_do_version()` prints plain or JSON version information. `zpool_do_help()` maps help topics to `zpool`, `zpoolconcepts`, `zpoolprops`, or `zpool-<subcmd>` man pages and `execlp()`s `man`. `zpool_do_load_compat()` wraps `zpool_load_compat()` and converts warning-token status into success after printing a warning.

`main()` sets locale/textdomain, disables getopt's own errors, handles top-level help/version/help-subcommand shortcuts, initializes libzfs, records arguments for history, duplicates `argv` because subcommands mutate strings, dispatches through `command_table`, treats `property=value` as implicit `zpool set`, includes a special `freeze` debug ioctl path, frees duplicated arguments, logs history on successful commands when enabled, finalizes libzfs, and honors `ZFS_ABORT` by aborting after cleanup.

## Dependencies

- libzfs/libzfs_core pool APIs: `libzfs_init()`, `libzfs_fini()`, `zpool_open()`, `zpool_close()`, `zpool_get_config()`, `zpool_get_status()`, `zpool_get_state_str()`, `zpool_get_prop()`, `zpool_get_prop_int()`, `zpool_props_refresh()`, `zpool_refresh_stats()`, `zpool_set_prop()`, `zpool_set_vdev_prop()`, `zpool_get_vdev_prop()`, `zpool_get_userprop()`, `zpool_get_features()`, `zpool_prop_get_feature()`, `zpool_upgrade()`, `zpool_wait_status()`, `zpool_ddt_prune()`, `zpool_get_history()`, `zpool_events_next()`, `zpool_events_clear()`, and `zpool_log_history()`.
- ZFS command and ioctl support: `zfs_save_arguments()`, `zfs_ioctl()` with `ZFS_IOC_POOL_FREEZE`, `zfs_version_print()`, `zfs_version_nvlist()`, `zpool_json_schema()`, `zcmd_print_json()`, `zfs_iter_root()`, `zfs_iter_filesystems_v2()`, and dataset property reads through `zfs_prop_get_int()`.
- Nvlist/fnvlist primitives: lookup/add/free/iteration helpers for strings, uint64 arrays, nested nvlists, nvlist arrays, and JSON-like output trees.
- Vdev and status helpers defined earlier in this file or adjacent OpenZFS code: `fill_pool_info()`, `fill_vdev_info()`, `vdev_stats_nvlist()`, `class_vdevs_nvlist()`, `l2cache_nvlist()`, `spares_nvlist()`, `dedup_stats_nvlist()`, `errors_nvlist()`, `print_status_config()`, `print_class_vdevs()`, `check_rebuilding()`, `print_scan_scrub_resilver_status()`, `print_err_scrub_status()`, `print_rebuild_status()`, `print_checkpoint_scan_warning()`, `max_width()`, `zpool_vdev_name()`, `for_each_pool()`, `for_each_vdev()`, `all_pools_for_each_vdev_run()`, and vdev-name validation helpers.
- Feature/compatibility definitions: `spa_feature_table[]`, `SPA_FEATURES`, `SPA_VERSION`, `SPA_VERSION_FEATURES`, `SPA_VERSION_IS_SUPPORTED()`, `ZPL_VERSION`, `zpool_load_compat()`, `zfeature_lookup_name()`, `ZFEATURE_FLAG_NO_UPGRADE`, and `ZFEATURE_FLAG_READONLY_COMPAT`.
- Event and fault-management schema constants: `FM_EREPORT_TIME`, `FM_CLASS`, `FM_FMRI_ZFS_POOL`, `FM_EREPORT_PAYLOAD_ZFS_*`, plus formatting helpers `zfs_valstr_zio_stage()`, `zfs_valstr_zio_type()`, `zfs_valstr_zio_priority()`, `zfs_valstr_zio_flag()`, and `zpool_state_to_name()`.
- POSIX/runtime dependencies: `getopt()`/`getopt_long()`, `pthread_create()`/mutex/cond timed waits, `clock_gettime()`, `open()`/`close()`, `ctime()`/`ctime_r()`, `localtime_r()`, `strftime()`, `getpwuid()`, `execlp()`, locale/gettext, `time()`, `srand()`, `abort()`, `errno`, and UID checks for status scripts.

## Risks And Edge Cases

- This chunk begins inside `scan_status_nvlist()`, so the report's JSON scan-status coverage depends on prior-chunk setup of the `scan` nvlist and earlier scan counters.
- Several status/progress calculations subtract unsigned or signed byte counters from kernel stats. If stats race or are inconsistent during refresh, remaining bytes can underflow or become negative before formatting.
- Removal and raidz-expansion progress divide by `total` without explicitly forcing `prs_to_copy` or `pres_to_reflow` nonzero. The kernel is expected to supply valid totals for active operations.
- `print_removal_status()` uses the numeric vdev id in the finished message but the resolved vdev name in canceled/in-progress messages, which may surprise parsers comparing human output across states.
- `print_status_reason()` relies on fixed-size `status` and `action` buffers. Most cases use `snprintf()`, but unsupported-feature collection appends into `status` with a hard-coded `1024` argument rather than the full `ST_SIZE`, so output shape depends on helper behavior.
- `status_callback_json()` initializes `pool_guid` only inside the `config != NULL` block but uses it later when `cb_json_pool_key_guid` is set. A missing config for a JSON GUID-keyed status report would risk using an uninitialized key.
- `zpool_do_status -c` intentionally refuses scripts when disabled by environment or when running with root privileges unless `ZPOOL_SCRIPTS_AS_ROOT` is set. This is important because per-vdev scripts run during status reporting and can materially change command safety.
- `upgrade_list_disabled_cb()` logs history inside the loop over every feature, even while only listing disabled features. That means a non-mutating list path can call `zpool_log_history()` repeatedly and disable normal history logging.
- Compatibility enforcement in `set_pool_callback()` prevents explicit feature enablement outside the compatibility set, but setting a stricter compatibility property only warns about already-enabled out-of-set features; it cannot disable on-disk features.
- `zpool_do_events_next()` leaks the current `nvl` if a pool-name filter skips with `continue`, because that branch bypasses `nvlist_free(nvl)`.
- `zpool_do_wait()` has a `case 'n'` but its getopt string lacks `n`, making the header-once option unreachable in this code as shown.
- `print_wait_status_row()` scripted output uses `i == 0` to choose whether to print the first column without a leading tab. If activity 0 is disabled and a later activity is first enabled, scripted output will start with a leading tab.
- The replace wait-progress value is explicitly heuristic: any spare/replacing/dRAID-spare vdev causes replace remaining bytes to mirror resilver remaining bytes, even if the resilver is unrelated.
- `main()` duplicates argv because subcommands mutate strings. Any future command added outside this pattern must not retain pointers into `newargv` past command return.
- The special `freeze` command bypasses normal `command_table` dispatch and disables history logging. It is a debug-only ioctl path and should not be treated like normal user-facing subcommands.

## Cross-Chunk References

- Earlier chunks define the command table, usage data, global variables, most vdev/status formatting helpers, JSON construction helpers, import/export/create/destroy paths, and the start of `scan_status_nvlist()`. This chunk depends directly on those earlier definitions.
- The first lines in this chunk continue `scan_status_nvlist()` from the previous chunk, adding later scan fields, error-scrub fields, and rebuild stats before closing the function at line 10087.
- `status_callback_json()` calls `removal_status_nvlist()`, `checkpoint_status_nvlist()`, `raidz_expand_status_nvlist()`, `vdev_stats_nvlist()`, `class_vdevs_nvlist()`, `l2cache_nvlist()`, `spares_nvlist()`, `dedup_stats_nvlist()`, and `errors_nvlist()`, all of which are defined before or around the chunk boundary.
- `status_callback()` relies on earlier `print_status_config()`, `print_class_vdevs()`, `max_width()`, color helpers, vdev command-column helpers, and health color mapping.
- `zpool_do_get()` and `zpool_do_set()` rely on earlier pool/vdev argument validators such as `are_all_pools()`, `is_pool()`, `are_vdevs_in_pool()`, `error_list_unresolved_vdevs()`, and property expansion helpers.
- `main()` closes the whole file by connecting all subcommands declared and mostly implemented across previous chunks to `command_table` dispatch, implicit `set`, and debug `freeze`.
