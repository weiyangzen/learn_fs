# File Research: sources/block-storage/lvm2/lib/device/dev-lvm1-pool.c

## Purpose
Detects legacy LVM1 PV labels and old pool labels from an already-read buffer.

## LVM1 Detection
The file defines a packed `pv_disk` structure for the old LVM1 on-disk format. `dev_is_lvm1()` checks the `"HM"` identifier and little-endian version 1 or 2.

## Pool Detection
The file defines old pool label constants and `struct pool_disk`. `pool_label_in()` converts/copies fields from the input buffer using big-endian conversions. `dev_is_pool()` checks `POOL_MAGIC` and compares the major/minor version bits of `pl_version`, ignoring the update-level byte.

## Integration
Used by device-type probing to reject or classify legacy LVM/pool signatures before writing new metadata.

## Risk Notes
Both functions trust that the caller supplied a buffer large enough for the corresponding disk structure; `buflen` is not used for bounds checks.
