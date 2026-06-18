# File Research: sources/block-storage/thin-provisioning-tools/src/thin/delta_visitor.rs

This file defines the delta data model, visitor trait, and XML writers for `thin_delta`.

Key elements:
- `DataMapping` describes a same-side run: thin begin, data begin, length.
- `DiffMapping` describes equal thin range mapped to different left/right data blocks.
- `Delta` variants are `LeftOnly`, `RightOnly`, `Differ`, and `Same`.
- `Snap` identifies either a `DeviceId` or explicit `RootBlock`.
- `DeltaVisitor` defines superblock, diff, and delta callbacks.
- `DeltaRunBuilder` merges adjacent deltas of the same type when thin ranges are adjacent.
- `SimpleXmlWriter` emits compact empty tags such as `<left_only begin=... length=.../>`.
- `VerboseXmlWriter` groups deltas by type tag and emits `<range>` children with data block fields.
- Shared XML helpers emit `<superblock>` and `<diff>` begin/end tags.

Interactions:
- Used by `thin/delta.rs` and its tests.
- Uses `quick_xml::Writer` and repository XML attribute helper `mk_attr()`.
- Consumes `thin::ir::Superblock` for superblock output.

Risks and notes:
- `DeltaRunBuilder` merges by delta type and thin adjacency only; for `Differ` and same-side mappings it does not verify data-address adjacency before extending the run. This matches compact reporting by thin range, but verbose users should note that a merged range may hide internal data discontinuities if upstream emits such deltas.
- XML writers return `Visit::Continue`; stop behavior is not used here.
