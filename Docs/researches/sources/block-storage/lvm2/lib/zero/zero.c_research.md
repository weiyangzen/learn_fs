# File Research: sources/block-storage/lvm2/lib/zero/zero.c

## Purpose
Implements the LVM2 `zero` virtual segment type, backed by the device-mapper `zero` target.

## Main Responsibilities
- Merge adjacent zero segments by increasing length and area length.
- Emit a dm-zero target line during activation.
- Probe for zero target availability.
- Report the needed kernel module name.
- Register a virtual, splittable, non-zeroable segment type.

## Key Functions
- `_zero_merge_segments()` combines two zero segments.
- `_zero_add_target_line()` calls `dm_tree_node_add_zero_target()`.
- `_zero_target_present()` caches `target_present(cmd, TARGET_NAME_ZERO, 1)`.
- `_zero_modules_needed()` adds `MODULE_NAME_ZERO`.
- `init_zero_segtype()` registers `SEG_TYPE_NAME_ZERO` with `SEG_CAN_SPLIT | SEG_VIRTUAL | SEG_CANNOT_BE_ZEROED`.

## Edge Cases and Invariants
- Target presence returns false when activation support is disabled.
- The cached target probe is process-local and avoids repeated target checks.
