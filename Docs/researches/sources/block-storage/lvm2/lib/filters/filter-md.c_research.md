# File Research: sources/block-storage/lvm2/lib/filters/filter-md.c

This Linux-only filter rejects md RAID component devices so LVM scans the md aggregate device rather than its member devices. The file documents three md detection modes: checking superblocks at the start, checking both start and end, and relying on udev. Full checking is used for formatting commands and when older md metadata placement may exist.

`_passes_md_filter` skips work for nodata scans, clears `DEV_FILTERED_MD_COMPONENT`, honors the global `md_filtering()` setting, then calls `dev_is_md_component(cmd, dev, NULL, cmd->use_full_md_check)`. A return of 1 means the device is a component and should be rejected; a negative detection error is also rejected to avoid unsafe scanning.

`md_filter_create` allocates a filter named `md`, stores `dev_types` in `private`, and returns `NULL` on non-Linux builds. The filter is defensive: detection errors produce a skip rather than a pass, preventing component devices from being treated as PVs.
