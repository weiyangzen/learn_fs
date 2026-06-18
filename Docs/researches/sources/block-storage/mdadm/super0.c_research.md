# File Research: sources/block-storage/mdadm/super0.c

## Purpose
Implements the `superswitch super0` backend for legacy Linux md metadata format `0.90`, including superblock load/store, creation, examination, update, geometry validation, and internal bitmap placement.

## Main Responsibilities
- Computes and validates legacy superblock checksums with `calc_sb0_csum()`.
- Handles host-endian 0.90 metadata and byte-swapped legacy variants via `super0_swap_endian()`.
- Prints `--examine`, brief, export, and `--detail` views, including UUID/homehost matching and reshape details.
- Converts superblock state into `struct mdinfo` through `getinfo_super0()`.
- Initializes and writes 0.90 metadata through `init_super0()`, `add_to_super0()`, `write_init_super0()`, and `store_super0()`.
- Loads metadata from the reserved tail area of a component device with `load_super0()`.
- Updates metadata for assemble, force, UUID/homehost, super-minor, resync, bitmap removal, linear grow, metadata migration to v1.0, and reshape rollback.
- Supports fixed-location internal bitmap data immediately after the 0.90 superblock.

## Integration
The file exports `struct superswitch super0`, wiring mdadm’s common metadata interface to the legacy implementation. It depends heavily on shared mdadm helpers from `mdadm.h`, `xmalloc.h`, SHA1 homehost hashing, UUID helpers, bitmap structures, and `super1_make_v0()` for metadata conversion.

## Notable Behavior
- 0.90 metadata is limited by `MD_SB_DISKS`, tail-reserved placement, and older kernel size constraints.
- RAID0 creation rejects non-uniform device sizes unless explicit dangerous layout is requested.
- `match_metadata_desc0()` accepts `0`, `0.90`, default old metadata, `0.91` reshape metadata, and swapped `0.swap`/`0.9`.
- Internal bitmap allocation is constrained to the 60 KiB area after the superblock.

## Risks and Edge Cases
- 0.90 is host-endian, so cross-endian handling is special and easy to regress.
- Device size arithmetic is constrained by the legacy layout and can reject large arrays.
- `UOPT_SPEC_WRITEMOSTLY` and `UOPT_SPEC_READWRITE` manipulate `sb->state`; these names suggest per-device flags, so callers must rely on existing legacy semantics carefully.
- Metadata conversion to v1.0 is refused for unclean arrays or arrays with bitmaps.
