# File Research: sources/block-storage/thin-provisioning-tools/src/era/dump.rs

This file implements era metadata dumping to the visitor/XML intermediate representation.

It can emit physical metadata, including writesets and the era array, or logical metadata where pending writesets are folded into effective per-block era values.

Important components:
- `EraEmitter` visits array blocks and emits each block's era.
- `Archive`/`EraArchive<T>` store writeset-derived era deltas compactly.
- `LogicalEraEmitter` overlays archived writeset-era data on top of era-array values.
- `OutputVisitor` wraps downstream visitor calls with `OutputError` context.
- `dump_writeset()` emits contiguous marked-bit ranges.
- `get_writesets_ordered()` combines archived writesets and current writeset, enforcing contiguous era coverage.

Public entry points:
- `dump_metadata()`
- `dump_metadata_logical()`
- `dump(EraDumpOptions)`

Integration points:
- Reads from `IoEngine`, walks B-trees/arrays, reads bitsets, and writes through `era::xml::XmlWriter` or any `MetadataVisitor`.
- Used directly by era dump CLI and by era repair as a source stream for `Restorer`.

Risks and notes:
- Logical dumping requires all writesets to be readable and ordered.
- Duplicate current-era writeset detection is explicit.
- `repair` mode is passed to lower-level readers as the permissive/ignore-nonfatal flag.
