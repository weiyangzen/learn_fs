# File Research: sources/block-storage/thin-provisioning-tools/src/era/restore.rs

This file restores era metadata from the visitor/XML intermediate representation into on-disk metadata.

`Restorer` implements `MetadataVisitor` and builds writeset arrays, the writeset B-tree, the era array, metadata space map, and final era superblock.

Important behavior:
- Enforces section ordering with `Section::{None, Superblock, Writeset, EraArray, Finalized}`.
- Allocates superblock location during `superblock_b()` and fails if it is already occupied.
- Builds each writeset as an `ArrayBuilder<u64>` bitset.
- `writeset_blocks()` converts marked block ranges into u64 bitset entries.
- Builds the era array with `ArrayBuilder<u32>`.
- `finalize()` completes all structures, builds metadata space map, and writes a clean-shutdown superblock.
- `eof()` requires finalization to have occurred.

Public entry point:
- `restore(EraRestoreOptions)`

Integration points:
- Reads XML via `era::xml::read()`.
- Uses `WriteBatcher`, `ArrayBuilder`, `BTreeBuilder`, metadata space-map code, and superblock writer.

Risks and notes:
- Assumes writeset marked ranges arrive in usable order for buffered bitset emission.
- Some internal paths use `unwrap()` where prior section-state checks are expected to guarantee presence.
