# File Research: sources/block-storage/lvm2/lib/unknown/unknown.c

## Purpose
Provides a fallback LVM2 segment type for metadata segment types unknown to the running binary. It preserves unrecognized segment metadata so it can be round-tripped instead of discarded.

## Main Responsibilities
- Import all config nodes except generic segment keys: `type`, `start_extent`, `tags`, and `extent_count`.
- Clone unknown config nodes into VG memory and store them in `seg->segtype_private`.
- Export the preserved config subtree unchanged with `out_config_node()`.
- Register a named segment type marked as unknown, virtual, and not zeroable.

## Key Functions
- `_unknown_text_import()` walks sibling config nodes, clones unknown fields, and chains them into a private list.
- `_unknown_text_export()` writes the saved config nodes back out.
- `init_unknown_segtype()` allocates a segment type with caller-provided name and flags `SEG_UNKNOWN | SEG_VIRTUAL | SEG_CANNOT_BE_ZEROED`.

## Edge Cases and Invariants
- Allocation failure during config-node cloning aborts import.
- The segment type name is duplicated and freed by `_unknown_destroy()`.
- This handler has no device-mapper activation behavior; it is metadata-preservation support.
