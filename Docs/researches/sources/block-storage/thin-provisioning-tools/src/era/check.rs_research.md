# File Research: sources/block-storage/thin-provisioning-tools/src/era/check.rs

This file implements era metadata checking.

`check()` opens an era metadata device, validates the superblock version, optionally stops at superblock-only checking, then verifies writeset bitsets and era-array values.

Important behavior:
- Builds a metadata space map and increments the superblock location as reserved.
- Reads and validates the era superblock.
- Walks the writeset B-tree and checks each writeset bitset with metadata-space-map accounting.
- `EraChecker` validates that no era-array value exceeds `current_era`.
- Reports fatal errors through `Report` and returns an error if any fatal issue is found.

Integration points:
- Uses `EngineBuilder`, `read_superblock`, `btree_to_map`, `read_bitset_checked_with_sm`, and `ArrayWalker`.
- Shares `Writeset` and array validation types with restore/dump code.

Risks and notes:
- Superblock validation only checks version greater than 1.
- Nonfatal handling is delegated to lower-level walkers through `ignore_non_fatal`.
