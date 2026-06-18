# File Research: sources/block-storage/lvm2/libdm/libdm-stats.c

## Summary
Implements libdevmapper's userspace interface for device-mapper statistics regions, counters, metrics, histograms, groups, and file-extent mapping. It builds and parses `@stats_*` target messages, maintains cached region/group tables, aggregates counters over regions and groups, formats histogram data, and optionally maps regular-file extents into stats regions via FIEMAP.

## Main Responsibilities
- Creates, binds, lists, populates, clears, deletes, and destroys `struct dm_stats` handles and statistics regions.
- Parses kernel `@stats_list` and `@stats_print` responses into `dm_stats_region`, `dm_stats_group`, `dm_stats_counters`, and `dm_histogram` structures.
- Implements stats walking over areas, regions, and groups using cursor state plus `DM_STATS_WALK_*` flags.
- Computes named counters and derived metrics such as reads/sec, writes/sec, request size, wait time, throughput, service time, and utilization.
- Creates and parses histogram bounds, formats histogram bin strings, and caches aggregate histograms.
- Persists group membership in region `aux_data` as `DMS_GROUP="alias:members"` descriptors.
- Maps file extents to stats regions using `FS_IOC_FIEMAP`, groups those regions, updates mappings, and can spawn `dmfilemapd` when enabled.
- Provides GNU symbol-version compatibility wrappers for older `dm_stats_create_region()` ABIs.

## Key APIs
- Handle/binding: `dm_stats_create()`, `dm_stats_destroy()`, `dm_stats_bind_devno()`, `dm_stats_bind_name()`, `dm_stats_bind_uuid()`, `dm_stats_bind_from_fd()`.
- Region lifecycle: `dm_stats_create_region()`, `dm_stats_delete_region()`, `dm_stats_clear_region()`, `dm_stats_list()`, `dm_stats_populate()`, `dm_stats_print_region()`.
- Walking/introspection: `dm_stats_walk_init()`, `dm_stats_walk_start()`, `dm_stats_walk_next()`, `dm_stats_walk_end()`, `dm_stats_object_type()`.
- Counters/metrics: `dm_stats_get_counter()`, generated `dm_stats_get_*` counter functions, `dm_stats_get_metric()`, generated metric functions, `dm_stats_get_utilization()`.
- Histogram helpers: `dm_histogram_bounds_from_string()`, `dm_histogram_bounds_from_uint64()`, `dm_histogram_to_string()`, `dm_stats_get_histogram()`.
- Groups: `dm_stats_create_group()`, `dm_stats_delete_group()`, `dm_stats_set_alias()`, `dm_stats_get_group_descriptor()`, `dm_stats_get_group_id()`.
- File mappings: `dm_stats_create_regions_from_fd()`, `dm_stats_update_regions_from_fd()`, `dm_stats_start_filemapd()`.

## Important Behavior
`dm_stats_create()` owns three pools: a main region/counter pool, a histogram pool, and a group pool. Region and group tables are pool-allocated arrays indexed by region ID, with holes represented by sentinel IDs. Rebinding a handle clears existing binding, regions, and groups.

Region creation formats `@stats_create` messages with optional range, area step, `precise_timestamps`, histogram bounds, program ID, and escaped aux data. Histogram bounds below millisecond precision automatically force precise timestamps if the driver supports them.

`@stats_list` parsing handles sparse region IDs, extracts program ID and aux data, parses optional `precise_timestamps` and `histogram:` arguments, and converts embedded group descriptors into group table entries while stripping the internal group tag from user-visible aux data.

`@stats_print` parsing reads one row per area, scales millisecond counters to nanoseconds when needed, and parses area histogram counts through a separate histogram pool to avoid interleaving growing objects in the main pool.

The walk engine can visit areas first, then aggregate regions, then groups, depending on flags. Group IDs are encoded in region IDs using `DM_STATS_WALK_GROUP`; current cursors are decoded by accessor functions.

Counter aggregation is centralized in `dm_stats_get_counter()`: group aggregation iterates all member regions and optionally all areas; region aggregation sums all areas; plain access reads a single area's counters. Derived metrics are calculated from these aggregate counters and the configured sampling interval.

File mapping rejects unsupported cases such as non-regular files, non-device-mapper backing devices, and btrfs physical FIEMAP data. It merges contiguous physical extents, creates one stats region per extent, rolls back newly created regions on partial failure, and can update a previous group by deleting missing extents and creating regions for new extents.

## State and Lifetime
`dm_stats_region` owns malloc-allocated `program_id` and `aux_data`, while counters and histogram bounds are pool-owned. Histograms created for parsed area data and aggregate caches live in `hist_mem`. Group aliases and bitsets are explicitly freed by group destruction.

Pool allocation order matters: region and group destruction walks backward so pool frees can unwind safely. Histogram objects for area counters are freed back to the first histogram in a region.

File mapping uses a temporary `extent_mem` pool so transient FIEMAP extents do not disturb the handle's region-table pool.

## Risks
The API relies heavily on sentinel values, encoded flag bits in IDs, and current-cursor substitution. Callers that pass invalid region IDs or mix group/region flags incorrectly can reach unchecked array indexing in some accessors.

Group metadata is persisted by rewriting aux data on the group leader. Failures during aux-data updates, group deletion, or mapped-file updates can leave kernel-side stats regions partly changed, though rollback paths cover many creation failures.

Parsing is tightly coupled to kernel message formats and fixed 4096-byte row buffers. Any kernel format drift or unexpectedly long string data can cause parse failures.

FIEMAP mapping assumes physical extent data is meaningful and excludes btrfs explicitly; other filesystems with unusual FIEMAP semantics may still produce surprising mappings.
