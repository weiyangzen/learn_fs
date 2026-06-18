# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/sb/mod.rs

- Superblock module exposing typed fields, member views, generated state/counter metadata, and bitmask accessors.
- Includes generated `SbField` implementations, member-state names, and persistent counter table.
- Provides typed superblock field get/get_mut/resize/get-minsize APIs, using mutable handle borrows to prevent stale references after resize.
- Implements bounds-checked read-only and mutable views for members v2 and read-only view for members v1, accounting for variable `member_bytes`.
- Generates little-endian bitmask accessors for superblock and member flags such as clean, csum type, targets, member state/group, data allowed, and resize/freespace flags.
