# File Research: sources/block-storage/thin-provisioning-tools/src/thin/dump.rs

This file implements metadata dumping to XML or human-readable output.

Key elements:
- `RunBuilder` coalesces adjacent `ir::Map` entries when thin block, data block, and time are contiguous/equal.
- `MappingVisitor` walks mapping leaves and emits coalesced `map` callbacks to a `MetadataVisitor`.
- `OutputVisitor` wraps a metadata visitor and adds output context to visitor errors.
- `OutputFormat` parses `"xml"` and `"human_readable"`.
- `ThinDumpOptions` controls input/output paths, engine options, repair mode, skip mappings, superblock overrides, selected devices, and format.
- `emit_leaf()` verifies a metadata block is a btree node, unpacks a mapping leaf, and emits its mappings.
- `read_for()` reads blocks in engine batch-size chunks.
- `emit_entries()` handles metadata entries as either leaf blocks or shared-definition references.
- `to_superblock_ir()` converts on-disk or rebuilt in-core superblocks into output IR.
- `dump_metadata()` emits full metadata IR: superblock, shared defs, devices, mapping leaves, and EOF.
- `dump_with_formatter()` reads or rebuilds the superblock, builds metadata with or without mappings, optimizes shared definitions, and dumps it.
- `dump()` selects writer target and formatter.

Interactions:
- Uses `metadata.rs` to build and optimize metadata.
- Uses `metadata_repair.rs` when `repair` mode asks for `read_or_rebuild_superblock()`.
- Uses `xml::XmlWriter` or `HumanReadableWriter`.
- Reads mapping leaves through `IoEngine`.

Risks and notes:
- `emit_leaf()` requires leaf blocks; internal blocks in entry lists are treated as errors.
- `skip_mappings` still emits device metadata but no mapping entries.
- Repair mode can dump from rebuilt superblock state, which may be heuristic if original superblock is corrupt.
