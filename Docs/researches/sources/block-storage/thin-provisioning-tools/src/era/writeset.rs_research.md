# File Research: sources/block-storage/thin-provisioning-tools/src/era/writeset.rs

This file defines the on-disk writeset value type.

`Writeset` contains:
- `nr_bits: u32`
- `root: u64`

It implements:
- `Unpack` with disk size 12 bytes.
- `Pack` as little-endian `u32` followed by little-endian `u64`.

Integration points:
- Stored in era writeset B-trees.
- Used by era superblock current-writeset field, dump, check, invalidate, and restore paths.

Risks and notes:
- It is a compact POD-style metadata value with no validation beyond parse/pack structure.
