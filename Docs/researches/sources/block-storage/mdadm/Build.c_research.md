# File Research: sources/block-storage/mdadm/Build.c

## Purpose
`Build.c` implements mdadm’s build mode for creating non-persistent linear or RAID0-style arrays without writing member superblocks.

## Major Entry Point
- `Build(struct mddev_ident *ident, struct mddev_dev *devlist, struct shape *s, struct context *c)`

## Behavior
The function requires an explicit RAID level, validates that all listed real devices are block devices, counts `missing` placeholders, and verifies that the number of listed devices equals `s->raiddisks`. If no layout is provided, it uses `default_layout()`.

It creates an md device, updates the mdadm map with a zero UUID and `STR_COMMON_NONE` metadata, and fills `mdu_array_info_t` directly. The array is marked `not_persistent = 1`, active/working/failed counts are derived from missing devices, and RAID0/linear chunk defaults are applied when needed. RAID0 with unset layout is forced to `RAID0_ORIG_LAYOUT`.

For each non-missing member, it opens the block device exclusively, records device size, updates `s->size` to the smallest usable size when size is unspecified or too large, sets active/sync disk state plus optional write-mostly, and adds the disk through `ADD_NEW_DISK`. Finally it starts the array with `RUN_ARRAY`, waits for the md device, and reports success.

## Dependencies and Integration Points
This code uses shared mdadm helpers for block-device validation, md device creation, map updates, size probing, md ioctl wrappers, and waiting for device readiness. It does not use metadata supertype handlers because build mode is intentionally non-persistent.

## Safety and Risk Notes
Failure paths stop the array with `STOP_ARRAY` and close the md fd. Because no superblocks are written, mdadm cannot later auto-discover the array from member metadata; callers must understand this mode is for explicit, non-persistent construction.
