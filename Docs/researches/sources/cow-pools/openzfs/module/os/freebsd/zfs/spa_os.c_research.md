# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/spa_os.c

## Scope

FreeBSD SPA OS hooks, primarily root pool import from on-disk GEOM labels. Other import/export/activate/deactivate hooks are no-ops.

## Main Interfaces

- `spa_import_rootpool()` imports or prepares the root pool configuration.
- `spa_generate_rootconf()` reads top-level vdev configs from GEOM labels and constructs a root vdev tree.
- `spa_history_zone()` returns `"freebsd"`.
- `spa_import_os()`, `spa_export_os()`, `spa_activate_os()`, and `spa_deactivate_os()` are empty hooks.

## State And Control Flow

`spa_generate_rootconf()` calls `vdev_geom_read_pool_label()`, selects the highest-TXG config as the base, determines top-level child count and holes, duplicates available child vdev trees by ID, fills holes with `VDEV_TYPE_HOLE`, fills missing children with `VDEV_TYPE_MISSING`, wraps them under a synthetic root vdev with the pool GUID, removes top-level-only GUID fields from the pool config, frees intermediate configs, and returns the assembled config.

`spa_import_rootpool()` uses that config to replace or add namespace state for the root pool, marks it as root, applies import flags including checkpoint rewind, parses the vdev tree under `SCL_ALL`, immediately frees the parsed tree, exits namespace, and frees the temporary config.

## Dependencies

Uses GEOM label reading, SPA namespace/config locks, nvlist helpers, vdev config parsing/freeing, and pool import flags.

## Correctness Notes

Root-pool import must reconstruct a full root vdev tree even when boot labels only contain top-level configs. Missing or hole children are represented explicitly to preserve child IDs. Existing active imports are treated as success.
