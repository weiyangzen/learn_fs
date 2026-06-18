# File Research: sources/cow-pools/bcachefs-tools/fs/fs/inode_format.h

## Purpose
Defines the on-disk inode-related bkey value formats and field/flag layouts. This file is the storage-format contract for inode keys, inode generations, inode allocation cursors, inode option ids, and inode flags.

## Main Contents
- Constants `BLOCKDEV_INODE_MAX` and `BCACHEFS_ROOT_INO`, both set to 4096.
- Packed on-disk inode formats:
  - `struct bch_inode` with hash seed, 32-bit flags, mode, and flexible fields.
  - `struct bch_inode_v2` adding journal sequence and 64-bit flags.
  - `struct bch_inode_v3` moving sectors, size, and version into fixed fields and storing mode/field start in packed flag bits.
- `struct bch_inode_generation` for inode generation tracking.
- `BCH_INODE_FIELDS_v2()` and `BCH_INODE_FIELDS_v3()` macro lists, covering timestamps, ids, nlink, generation, device, checksum/compression/replica/target options, project id, backpointer, subvolume fields, nocow, depth, 31-bit dirent offsets, casefold, and an unused EC field.
- `BCH_INODE_OPTS()` and `enum inode_opt_id`, the subset of fields exposed as inheritable inode options.
- `BCH_INODE_FLAGS()` plus bitmask accessors for string hash type, field count, v3 field start, and v3 mode.
- `struct bch_inode_alloc_cursor`, used under logged ops inode cursor namespace.

## Integration Notes
`inode.h` expands the field macros into `struct bch_inode_unpacked` and option accessors. `xattr.c` maps option ids to `bcachefs.*` xattrs. `str_hash.c` reads the packed string hash bits through the unpacked `INODE_STR_HASH` helper. Namespace code depends on the subvolume and backpointer fields defined here.

## Risks and Edge Cases
- Bits 20 and above in inode flags are shared with packed fields; new flags must not collide with hash/type/count/mode encodings.
- v1/v2/v3 formats have different fixed fields and bit widths, so validation and conversion code must keep minimum value sizes and field starts synchronized with this header.
- `bi_subvol` and `bi_parent_subvol` are documented as valid only for subvolume roots.
