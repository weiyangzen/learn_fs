# File Research: sources/block-storage/lvm2/lib/filters/filter-type.c

This filter rejects unrecognized block device major types. `_passes_lvm_type_device_filter` looks up the device major in `dev_types->dev_type_array` and requires a nonzero `max_partitions` entry. Unknown majors are marked `DEV_FILTERED_DEVTYPE` and rejected.

`lvm_type_filter_create` allocates a filter named `type` with `dev_types` stored in `private`. It is a low-cost structural filter and does not perform data reads.
