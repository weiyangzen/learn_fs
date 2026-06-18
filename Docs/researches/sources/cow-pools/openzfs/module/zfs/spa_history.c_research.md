# File Research: sources/cow-pools/openzfs/module/zfs/spa_history.c

## Summary
Manages the on-disk SPA history log. The log stores packed nvlist records with little-endian length prefixes in a ring buffer while preserving the original pool creation record.

## Main Responsibilities
- Creates the history object and bonus-buffer offset metadata.
- Writes packed history records into a bounded ring buffer.
- Advances BOF when old records must be overwritten.
- Posts sysevents for internal history records.
- Logs command, ioctl, internal, dataset, dsl-dir, and version events.
- Reads history chunks for userland consumers.

## Key APIs
- `spa_history_create_obj()`.
- `spa_history_log()`, `spa_history_log_nvl()`.
- `spa_history_get()`.
- `spa_history_log_internal()`, `spa_history_log_internal_ds()`, `spa_history_log_internal_dd()`.
- `spa_history_log_version()`.
- `spa_history_zone()` outside kernel builds.

## Important Behavior
The physical log size is set to 0.1 percent of normal-class space, capped at 1 GiB and floored at 128 KiB. Logical offsets monotonically advance; `spa_history_log_to_phys()` maps logical offsets into the ring region after the preserved create record.

`spa_history_log_sync()` creates the history object for older pools, adds host info, emits debug messages, packs the nvlist, writes length and record bytes, and sets `sh_pool_create_len` after the first command record. `spa_history_get()` syncs pending async history on first read for writable pools.

## Risks
History writes are asynchronous for most callers, so record time can precede durable pool changes. Consumers must handle ring wrap and overwritten logical offsets. Hidden input nvlist arguments are stripped before logging, but callers still control what history metadata is submitted.
