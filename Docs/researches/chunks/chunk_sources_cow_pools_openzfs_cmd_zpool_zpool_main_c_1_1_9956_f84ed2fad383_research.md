# Chunk Research: sources/cow-pools/openzfs/cmd/zpool/zpool_main.c lines 1-9956

## Scope

This chunk covers command registration and usage, pool/vdev creation and mutation commands, import/export, list/iostat output, parts of status output, scan/scrub/trim commands, and the beginning of the JSON status emitter. The chunk ends inside `scan_status_nvlist()`, so the complete `zpool status` JSON and CLI status command flow continue in the next chunk.

## Command Dispatch and State

- `g_zfs` is the shared `libzfs_handle_t`; `mount_tp_nthr`, `current_command`, `current_prop_type`, `history_str`, `log_history`, and `timestamp_fmt` coordinate mounting, usage/property help, history, and timestamps.
- `command_table[]` maps subcommands such as `create`, `import`, `status`, `iostat`, `trim`, `wait`, and `ddtprune` to implementation functions.
- `usage()` exits directly, prints command/global help, and can list pool/vdev properties for `get`, `set`, and `list`.

## Major APIs and Helpers

- Uses libzfs/libzutil heavily: `zpool_open*`, `zpool_create`, `zpool_add`, `zpool_destroy`, `zpool_export*`, `zpool_import_props`, `zpool_search_import`, `zpool_enable_datasets`, `zpool_disable_datasets`, `zpool_wait`, `zpool_vdev_*`, `zpool_power*`, `zpool_clear`, `zpool_scan_range`, and `zpool_trim`.
- Nvlist/fnvlist objects are the main exchange format for pool configs, vdev trees, properties, and JSON output.
- Shared helpers handle property validation, dry-run vdev tree printing, vdev class detection, JSON schema generation, formatted numeric fields, spare ownership, and slot power control.
- Output string tables map scan, vdev, checkpoint, rebuild, initialize, and trim enum values to CLI/JSON strings.

## Control Flow Covered

- Creation/mutation: `zpool_do_create`, `add`, `remove`, `attach`, `replace`, `detach`, `split`, `labelclear`, `destroy`, `checkpoint`, `prefetch`, `online`, `offline`, `clear`, `reguid`, and `reopen`.
- Import/export: parallel `export -a`, import discovery, cachefile fallback, hostid/MMP force checks, rewind policy, destroyed-pool filtering, optional key loading, and dataset mounting.
- Listing/iostat: repeated `zpool list` and `zpool iostat` loops, pool refresh, interval/count parsing, timestamps, JSON output, vdev recursion, class/L2ARC/spare handling, extended latency/queue/histogram stats, and custom `-c` script columns.
- Scrub/resilver/trim: option validation, pool iteration, date parsing, wait handling, checkpoint warnings, and per-vdev/full-pool trim dispatch.

## Status Output

- This chunk includes much of the status support but not the final command implementation.
- Text status helpers print live/import vdev trees, health coloring, read/write/checksum/slow I/O columns, power state, DIO verify errors, aux fault descriptions, ashift warnings, removal/noalloc markers, resilver/rebuild notes, and init/trim leaf state.
- JSON status helpers begin near the end: vdev stats, class vdevs, L2ARC, spares, errlog conversion, DDT/dedup stats, raidz expansion, checkpoint, and removal stats.
- `scan_status_nvlist()` starts at line 9932 and is incomplete at line 9956.

## Risks and Edge Cases

- Several arrays are indexed directly by kernel/libzfs enum values; enum drift could cause invalid reads.
- Many config lookups use `verify()` or `fnvlist_lookup_*`, so malformed/incomplete nvlists can abort the process.
- `usage()` exits, so cleanup often depends on termination rather than local unwinding.
- Parallel import/export workers update shared aggregate error state without explicit locking.
- `zpool_do_online()` can return on power-on failure before closing the opened pool handle.
- `zpool_do_offline()` has user-facing conflict text referring to `-0` for `--power`.
- Some `nvlist_exists(props, ...)` calls occur when `props` may be `NULL`; behavior depends on nvlist API tolerance.

## Cross-Chunk References

- Next chunk must finish `scan_status_nvlist()` and cover the actual `zpool_do_status()` flow.
- Later functions referenced but not implemented in this chunk include `zpool_do_upgrade`, `history`, `events`, `get`, `set`, `version`, `wait`, `ddtprune`, `help`, `zpool_do_load_compat`, and likely `main()`.
- External helpers from other files include `make_root_vdev`, `split_mirror_vdev`, `for_each_pool`, `pool_list_*`, `zpool_sync_one`, `zpool_reopen_one`, `zpool_initialize_one`, `zpool_trim_one`, and command script execution.