# sources/distributed-fs/ceph-client/fs/nilfs2/direct.h

## Purpose
`direct.h` declares constants and APIs for the fixed-size direct block-map backend.

## Important APIs and constants
- `NILFS_DIRECT_NBLOCKS` derives the number of direct pointers that fit in `NILFS_BMAP_SIZE`.
- `NILFS_DIRECT_KEY_MIN` and `NILFS_DIRECT_KEY_MAX` define the valid direct-key range.
- `nilfs_direct_init()` installs direct bmap operations.
- `nilfs_direct_delete_and_convert()` deletes a key and rebuilds direct pointer storage from gathered key/pointer arrays during conversion.

## Control flow and state behavior
The header defines the threshold where direct maps stop being usable and B-tree conversion becomes necessary. Direct state is embedded in the bmap area and therefore persisted with inode/bmap serialization rather than through separate node buffers.

## Dependencies and integration points
It includes `bmap.h` and is used by the bmap conversion layer and direct implementation. `btree.c` and higher bmap code rely on these declarations for conversion between direct and B-tree forms.

## Risks and test signals
Capacity calculations are format-sensitive. Tests should validate boundary keys, conversion at `NILFS_DIRECT_KEY_MAX + 1`, and consistency between direct and B-tree gathered data.
