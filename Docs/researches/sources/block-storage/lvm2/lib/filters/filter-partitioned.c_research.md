# File Research: sources/block-storage/lvm2/lib/filters/filter-partitioned.c

This filter rejects devices that contain a partition table signature. `_passes_partitioned_filter` skips data reads during nodata-only scans, clears `DEV_FILTERED_PARTITIONED`, then calls `dev_is_partitioned`. Detected partitioned devices are rejected and flagged.

The filter is used to avoid accidentally treating whole disks with partition tables as LVM PV candidates. `partitioned_filter_create` allocates a filter named `partitioned`; the `dev_types` argument is unused in this implementation.
