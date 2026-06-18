# File Research: sources/block-storage/lvm2/lib/error/errseg.c

This file registers LVM's virtual `error` segment type. The segment type represents logical extents that map to the device-mapper error target, causing I/O to fail predictably.

Core behavior:
- `_errseg_merge_segments` merges adjacent error segments by adding lengths and area lengths.
- Under `DEVMAPPER_SUPPORT`, `_errseg_add_target_line` emits an error target line into the device-mapper tree.
- `_errseg_target_present` lazily checks kernel support for the current and old truncated error target names, caching the result.
- `_errseg_modules_needed` requests the kernel error module in activation dependency lists.
- `_errseg_destroy` frees the allocated segment type.

`init_error_segtype` allocates and initializes the `segment_type` with name `SEG_TYPE_NAME_ERROR`, handler table `_error_ops`, and flags `SEG_CAN_SPLIT`, `SEG_VIRTUAL`, and `SEG_CANNOT_BE_ZEROED`. This makes error areas splittable and virtual while preventing zeroing semantics that would be nonsensical for an error target.
