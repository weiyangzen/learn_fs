# Chunk Research: sources/cow-pools/openzfs/cmd/zpool/zpool_main.c lines 9957-13962

## Scope

This report covers chunk 2 of `sources/cow-pools/openzfs/cmd/zpool/zpool_main.c`, lines 9957-13962, within `Docs/research_subset_a.md` COW pool/OpenZFS scope. The chunk is the tail of the `zpool` CLI implementation. It covers status JSON/text rendering, pool upgrade, history, event display, pool/vdev property get/set, wait/progress reporting, DDT pruning, version/help compatibility helpers, and the program `main()` dispatcher. The line range starts inside `scan_status_nvlist()` and ends at process exit.

## Primary APIs In This Chunk

- Status report APIs: `scan_status_nvlist()`, `print_scan_status()`, removal/raidz/checkpoint/error-log/dedup renderers, `print_status_reason()`, `status_callback_json()`, and `status_callback()`.
- Command entry points: `zpool_do_status()`, `zpool_do_upgrade()`, `zpool_do_history()`, `zpool_do_events()`, `zpool_do_get()`, `zpool_do_set()`, `zpool_do_wait()`, `zpool_do_ddt_prune()`, `zpool_do_version()`, and `zpool_do_help()`.
- Upgrade helpers: `check_unsupp_fs()`, `upgrade_version()`, `upgrade_enable_all()`, `upgrade_cb()`, list callbacks, and `upgrade_one()`.
- History/event helpers: `print_history_records()`, `get_history_one()`, `zpool_do_events_short()`, `zpool_do_events_nvprint()`, `zpool_do_events_next()`, and `zpool_do_events_clear()`.
- Property helpers: `get_callback_vdev()`, `get_callback_vdev_cb()`, `get_callback()`, `set_pool_callback()`, and `set_callback()`.
- Wait helpers: `vdev_activity_remaining()`, `vdev_activity_top_remaining()`, `vdev_any_spare_replacing()`, `print_wait_status_row()`, and `wait_status_thread()`.
- Dispatch/support helpers: `find_command_idx()`, `zpool_do_load_compat()`, and `main()`.

## Core Data And State

- `status_cbdata_t` carries status rendering mode, JSON flags, literal/integer formatting, health-only filtering, vdev name flags, dedup stats, command-column output, flat JSON vdev layout, and optional columns.
- Pool configuration and stats flow through nvlists under `ZPOOL_CONFIG_VDEV_TREE`, including scan, rebuild, removal, checkpoint, raidz expansion, L2ARC/cache, spares, DDT, and error-count fields.
- Status rendering consumes `pool_scan_stat_t`, `vdev_rebuild_stat_t`, `pool_removal_stat_t`, `pool_checkpoint_stat_t`, `pool_raidz_expand_stat_t`, `vdev_stat_t`, and DDT structs.
- Upgrade state is held in `upgrade_cbdata_t`; feature decisions compare `spa_feature_table[]`, compatibility-set booleans, and `zpool_get_features()`.
- History/event/property/wait commands use dedicated callback structs: `hist_cbdata_t`, `ev_opts_t`, `zprop_get_cbdata_t`, `set_cbdata_t`, and `wait_data_t`.
- Global state visible here includes `g_zfs`, `history_str`, `log_history`, `current_command`, `command_table`, `timestamp_fmt`, and `current_prop_type`.

## Control Flow

### Status Rendering

The chunk completes `scan_status_nvlist()`, adding scrub/resilver counters, error-scrub fields, and per-top-vdev rebuild stats to JSON. `print_scan_status()` chooses scrub, error-scrub, resilver, or rebuild output based on active state and end times.

`print_removal_status()` and `print_raidz_expand_status()` resolve the affected top-level vdev, format finished/canceled/in-progress states, compute progress and rates, and suppress very large time estimates. `print_status_reason()` maps libzfs pool health reasons and errata to status/action text or JSON fields.

`status_callback_json()` builds one JSON pool object with pool info, status/action/msgid, load info, scan/removal/checkpoint/expand status, vdev stats, class vdevs, cache/spares, dedup stats, and errors. `status_callback()` renders the equivalent text output.

`zpool_do_status()` parses status options, validates JSON-only options, optionally runs vdev scripts, iterates pools, prints JSON or text, supports timestamps and interval/count mode, and handles no-pool/healthy-pool messages.

### Upgrade

`upgrade_version()` rejects unsupported filesystem versions and legacy compatibility mode, then calls `zpool_upgrade()`. `upgrade_enable_all()` loads the compatibility set and enables every supported requested feature not flagged `ZFEATURE_FLAG_NO_UPGRADE`.

`zpool_do_upgrade()` handles show-version mode, upgrade-all mode, list-only mode, and named-pool upgrade mode. It prints supported feature flags and legacy versions, lists old pools and disabled features, or applies upgrades through callbacks.

### History And Events

`print_history_records()` formats command, internal event, internal name, ioctl, and unknown history records, with optional UID/user/host/zone long format. `get_history_one()` pages through pool history via `zpool_get_history()`.

Events are read from `ZFS_DEV` with `zpool_events_next()`. Short mode prints time/class; verbose mode recursively dumps nvlists and annotates ZIO/vdev fields. Clear mode calls `zpool_events_clear()`.

### Properties

`zpool_do_get()` parses output columns, literal/scripted/JSON modes, pool GUID keying, and JSON integer mode. It distinguishes pool-property queries from vdev-property queries, including `all-vdevs` and `root` mapped to `root-0`.

`get_callback()` retrieves user, feature/unsupported, normal pool, or vdev properties and either prints through `zprop_collect_property()` or builds JSON. `zpool_do_set()` accepts `property=value pool [vdev]`; pool sets are guarded by compatibility checks, while vdev sets call `zpool_set_vdev_prop()`.

### Wait And DDT Prune

Wait status computes remaining work for checkpoint discard, freeing, initialize, replace, remove, resilver, scrub, trim, and raidz expansion. It uses recursive vdev stats, scan stats, rebuild stats, and a documented replace heuristic based on spare/replacing vdev presence.

`zpool_do_wait()` optionally starts a status thread, then repeatedly calls `zpool_wait_status()` for enabled activities until none are still in progress. `zpool_do_ddt_prune()` validates `-d days` or `-p percent`, opens the pool, and calls `zpool_ddt_prune()`.

### Dispatch

`main()` handles top-level help/version shortcuts, initializes libzfs, saves arguments for history, duplicates argv because subcommands mutate strings, dispatches through `command_table`, treats `property=value` as implicit `set`, supports debug `freeze`, logs history on success, finalizes libzfs, and honors `ZFS_ABORT`.

## Dependencies

- libzfs/libzfs_core pool APIs for config, status, properties, features, upgrade, wait, DDT prune, history, events, and history logging.
- Nvlist/fnvlist helpers for all JSON/status structures.
- Earlier file helpers for vdev naming, pool iteration, vdev traversal, status table printing, JSON vdev/class/cache/spare/error construction, and validation.
- Feature/compatibility definitions: `spa_feature_table[]`, `SPA_FEATURES`, `SPA_VERSION*`, `ZPL_VERSION`, `zpool_load_compat()`, and `zfeature_lookup_name()`.
- POSIX/runtime APIs: getopt, pthreads, time/ctime/localtime/strftime, open/close, getpwuid, execlp, locale/gettext, and errno.

## Risks And Edge Cases

- The chunk starts mid-`scan_status_nvlist()`, so JSON scan setup is in the prior chunk.
- Progress calculations subtract changing kernel counters; races can produce negative or underflowed remaining values.
- Removal and raidz expansion divide by total work without locally forcing nonzero totals.
- `status_callback_json()` only initializes `pool_guid` when config exists, but may use it later for GUID-keyed JSON.
- `zpool_do_events_next()` skips freeing `nvl` when a pool-name filter `continue`s.
- `zpool_do_wait()` has `case 'n'`, but the getopt string lacks `n`, making that option unreachable in this chunk.
- Scripted wait output uses `i == 0` to decide tab placement, so disabling activity 0 can produce a leading tab.
- Replace wait progress is explicitly heuristic and can report unrelated resilver work as replace work.
- The debug `freeze` command bypasses normal dispatch and disables history logging.

## Cross-Chunk References

- Earlier chunks define `command_table`, usage data, globals, import/export/create/destroy paths, status helpers, JSON helpers, validation helpers, and the start of `scan_status_nvlist()`.
- `status_callback_json()` depends on JSON helpers defined before or around the chunk boundary: removal/checkpoint/raidz-expand/vdev/class/cache/spare/dedup/error nvlist builders.
- `status_callback()` depends on earlier text-format helpers including vdev config printing, class vdev printing, max-width calculation, color helpers, and command-column helpers.
- `zpool_do_get()` and `zpool_do_set()` rely on earlier pool/vdev validators such as `are_all_pools()`, `is_pool()`, `are_vdevs_in_pool()`, and unresolved-vdev reporting.
- `main()` closes the file by wiring all earlier subcommand implementations into the CLI dispatcher.