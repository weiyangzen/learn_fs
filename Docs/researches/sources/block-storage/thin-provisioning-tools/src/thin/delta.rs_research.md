# File Research: sources/block-storage/thin-provisioning-tools/src/thin/delta.rs

This file implements `thin_delta`: comparing mappings from two snapshots/devices/roots and emitting XML delta output.

Key elements:
- Local `RunBuilder` coalesces adjacent mappings where thin blocks and data blocks advance together.
- `MappingRecorder` implements `NodeVisitor<BlockTime>` and records contiguous `DataMapping` runs from a mapping tree.
- `get_mappings(engine, root)` walks a mapping tree and returns coalesced data mappings.
- `MappingStream` wraps a mapping iterator and supports partial consumption of a run.
- `dump_delta_mappings(left, right, visitor)` performs the core merge-style comparison:
  - `LeftOnly`
  - `RightOnly`
  - `Same`
  - `Differ`
- `dump_diff()` resolves `Snap::DeviceId` through the top-level mapping tree or accepts `Snap::RootBlock` directly, builds output superblock IR, emits diff begin/end events, and streams deltas to a `DeltaVisitor`.
- `ThinDeltaOptions` selects input metadata, engine options, report, two snapshots, and verbose XML mode.
- `delta()` opens metadata, reads current or snapshot superblock, validates superblock consistency, selects simple or verbose XML writer, and emits the diff.

Interactions:
- Uses `delta_visitor.rs` for delta model and XML writers.
- Uses `metadata_repair::is_superblock_consistent()` before comparing.
- Uses `btree_to_map::<u64>()` to resolve device IDs to mapping roots.
- Uses `SMRoot` to populate `nr_data_blocks` in output IR.

Risks and notes:
- Mapping timestamps are ignored by design; comparison is based on data block addresses.
- The algorithm assumes mapping vectors are ordered by thin block, as produced by btree walking.
- Errors such as missing roots are reported as command failures.
