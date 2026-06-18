# Group Research: group_467_illumos_gate_sources_os_illumos_illumos_gate_usr_src_cmd_zpool_zpool_6f4e7d27f62a

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/illumos/illumos-gate`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_main.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_main.c

## Purpose
Primary implementation of the illumos `zpool` command-line utility. It parses subcommands and options, translates CLI requests into libzfs/libzutil operations, renders pool/vdev status and statistics, and records successful administrative actions in ZFS history.

## Main Elements
- Global CLI dispatch: command table, usage text, `main()`, libzfs initialization, history capture, `property=value` shorthand, and debug `freeze`.
- Property/vdev helpers: property nvlist validation, feature/version exclusion, vdev-tree traversal, dry-run output, and leaf collection.
- Pool creation/topology mutation: create/add/remove/attach/replace/detach/split/labelclear flows.
- Import/export/destroy/checkpoint/sync: discovery, duplicate-name handling, rewind/checkpoint policies, MMP/hostid safety, dataset mount/disable, and sync.
- Monitoring/reporting: list, status, iostat, timestamps, scripted/parsable modes, latency/queue/histogram stats, scan/removal/checkpoint progress, error logs, and dedup stats.
- Device maintenance: online/offline/clear/reguid/reopen/scrub/resilver/trim/initialize/wait.
- Upgrade/history/get/set: feature listing/enabling, pool version upgrades, paged history output, and pool property access.

## Dependencies And Integration
- Depends heavily on libzfs/libzutil for real pool, vdev, property, history, import/export, scan, wait, and dataset operations.
- Uses `zpool_util.h` plus companion zpool modules for `make_root_vdev()`, `split_mirror_vdev()`, `for_each_pool()`, `for_each_vdev()`, and `pool_list_*()`.
- Uses nvlists as the main interchange format for pool configs, vdev trees, stats, load policies, and properties.
- Uses ZFS structures/constants such as `vdev_stat_t`, scan/removal/checkpoint stats, DDT stats, and `spa_feature_table`.

## Notable Behaviors
- Rejects dataset-like pool names containing `/` for many pool-only commands.
- `zpool create` enables all supported feature flags unless disabled or an older version is requested.
- `-R` and temporary-name flows default `cachefile=none`.
- `zpool iostat -g` avoids misparsing numeric vdev GUIDs as interval/count.
- Status output separates normal, dedup, special, log, cache, and spare vdev classes.
- `zpool wait` can continue waiting for selected activities that begin while it is running.

## Risk Notes
- Very large CLI surface; option parsing and output formatting are externally observable compatibility contracts.
- Script-facing modes (`-H`, `-p`, `-T`, list/status/iostat columns) are sensitive to spacing and field order.
- Many nvlist accesses use `verify()`/`fnvlist_lookup_*()`, assuming kernel/libzfs invariants.
- `labelclear` directly opens and clears device labels, so force and membership checks are safety-critical.
- Several property parsers mutate `optarg` by replacing `=` with NUL.
- `wait_status_thread()` combines global libzfs state, pthreads, semaphore timing, and refresh/error handling.
- Debug `freeze` copies into a fixed buffer and is intentionally treated as a debugging-only path.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_util.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_util.c

## Purpose
Small shared utility implementation for the illumos `zpool` command sources.

## Main Elements
- `safe_malloc()`: zeroed allocation with process exit on failure.
- `zpool_no_memory()`: ENOMEM assertion, localized error, and exit.
- `num_logs()`: counts immediate child vdevs marked as log devices.
- `array64_max()`: finds the maximum uint64 array element.
- `isnumber()`: permissive digit/dot screening for CLI interval/count parsing.

## Dependencies And Integration
- Includes `zpool_util.h`.
- Uses nvlist APIs and ZFS config keys.
- `safe_malloc()` is used across zpool command code for fail-fast allocation.
- `array64_max()` supports histogram column sizing.
- `isnumber()` supports interval/count parsing in list, status, iostat, and wait flows.

## Risk Notes
- `safe_malloc()` exits instead of returning failure.
- `isnumber()` accepts loose forms like `.` or multiple dots; stricter parsing happens later.
- `num_logs()` is shallow and does not recurse into nested vdevs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_util.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_util.h

## Purpose
Shared header for the illumos `zpool` command implementation. It declares utility helpers, vdev construction/splitting helpers, pool/vdev iteration APIs, pool-list management APIs, and the global libzfs handle.

## Main Elements
- Utility declarations: `safe_malloc()`, `zpool_no_memory()`, `num_logs()`, `array64_max()`, `highbit64()`, `lowbit64()`, and `isnumber()`.
- Vdev construction: `make_root_vdev()` and `split_mirror_vdev()`.
- Pool iteration: `for_each_pool()`.
- Vdev iteration: `pool_vdev_iter_f` and `for_each_vdev()`.
- Pool-list abstraction: `zpool_list_t`, `pool_list_get()`, `pool_list_update()`, `pool_list_iter()`, `pool_list_free()`, `pool_list_count()`, and `pool_list_remove()`.
- Global state: `extern libzfs_handle_t *g_zfs`.

## Dependencies And Integration
- Includes `<libnvpair.h>` and `<libzfs.h>`.
- Provides the shared contract between `zpool_main.c` and companion zpool modules for vdev parsing and pool iteration/list management.
- Exposes bit helper prototypes used by iostat flag handling.

## Risk Notes
- `g_zfs` is process-global and assumes initialization/teardown in `main()`.
- Several APIs accept mutable argv/property nvlist inputs, so ownership and mutation behavior must remain consistent.
- Some standard types rely on included lib headers or prior include order.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_util.h -->