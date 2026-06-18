# File Research: sources/cow-pools/openzfs/module/zfs/dataset_kstats.c

## Scope

This file implements per-dataset kstats for OpenZFS objsets. It creates named kstat rows for dataset identity, read/write byte counters, unlink counters, and embedded ZIL statistics, with helper APIs used by dataset I/O paths to update counters.

The source was read completely, lines 1-261.

## Primary APIs And Entry Points

- `dataset_kstats_create()` creates and installs a virtual named kstat for an objset.
- `dataset_kstats_destroy()` deletes the kstat and frees its string and counter backing storage.
- `dataset_kstats_rename()` updates the exported dataset name string after a dataset rename.
- `dataset_kstats_update_write_kstats()` increments write operation and byte counters.
- `dataset_kstats_update_read_kstats()` increments read operation and byte counters.
- `dataset_kstats_update_nunlinks_kstat()` and `dataset_kstats_update_nunlinked_kstat()` update unlink-related counters.
- `dataset_kstats_update()` is the kstat read callback; writes to this kstat are rejected with `EACCES`.

## Data Model

- `empty_dataset_kstats` is a template `dataset_kstat_values_t` containing named fields for dataset name, read/write counters, unlink counters, and a nested ZIL kstat value set.
- Each live `dataset_kstats_t` owns a `kstat_t`, a group of `wmsum_t` counters, and ZIL sums.
- The exported dataset name is stored as a dynamically allocated fixed-size string buffer attached to `dkv_ds_name`.

## Control Flow

Creation skips snapshots, avoiding memory overhead for potentially numerous snapshot objsets. For non-snapshots it builds a kstat module name of `zfs/<pool>` and a kstat name of `objset-0x<id>`, checking both against `KSTAT_STRLEN`.

After `kstat_create()`, the file allocates a private copy of the template data, allocates a dataset-name buffer, fills it with `dsl_dataset_name()`, points the named-string kstat at that buffer, initializes all `wmsum_t` counters and ZIL sums, sets update/private pointers, and installs the kstat.

The update callback snapshots all `wmsum_t` values with `wmsum_value()` and delegates ZIL field refresh to `zil_kstat_values_update()`.

Destroy reverses creation: delete kstat, free the dataset-name buffer, free the kstat data copy, and finalize all sums.

## Dependencies

- Objset and dataset identity helpers: `dmu_objset_is_snapshot()`, `dmu_objset_id()`, `dmu_objset_spa()`, `dmu_objset_pool()` through included headers, and `dsl_dataset_name()`.
- SPA naming via `spa_name()`.
- Kernel kstats: `kstat_create()`, `kstat_install()`, `kstat_delete()`, `KSTAT_NAMED_STR_PTR`, and `KSTAT_NAMED_STR_BUFLEN`.
- Counter infrastructure: `wmsum_init/add/value/fini`.
- ZIL statistics helpers: `zil_sums_init()`, `zil_sums_fini()`, and `zil_kstat_values_update()`.

## Notable Behavior

- Snapshot objsets return success without creating a kstat.
- Name truncation is treated as an error and logged through `zfs_dbgmsg()`.
- Counter update helpers are no-ops if the kstat was not created.
- Read/write update helpers assert non-negative byte counts.
- The kstat data size is increased by `ZFS_MAX_DATASET_NAME_LEN` because the virtual kstat includes an external string buffer.

## Risks And Correctness Notes

- `dataset_kstats_destroy()` assumes the named string pointer and buffer length are still valid after `kstat_delete()`, so creation and mutation must preserve that storage model.
- `dataset_kstats_rename()` silently truncates to the kstat string buffer length via `strlcpy()`.
- Skipping snapshots is a policy/performance choice; consumers should not assume every objset has dataset kstats.
- The create path initializes sums only after kstat backing memory is allocated. If future changes add failure points after partial initialization, teardown ordering would need matching cleanup.
