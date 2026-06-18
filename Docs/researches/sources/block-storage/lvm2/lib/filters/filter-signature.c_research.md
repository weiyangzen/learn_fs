# File Research: sources/block-storage/lvm2/lib/filters/filter-signature.c

This Linux-only filter rejects devices with legacy signatures that LVM should not treat as normal PV candidates. `_ignore_signature` reads the first 4096 bytes, rejects on read failure, rejects LVM1 devices detected by `dev_is_lvm1`, and rejects old GFS pool devices detected by `dev_is_pool`.

It skips data reads when `cmd->filter_nodata_only` is set. Rejections set `DEV_FILTERED_SIGNATURE`; successful signature checks pass. `signature_filter_create` allocates a filter named `signature` and stores `dev_types` in `private`; non-Linux builds return `NULL`.
