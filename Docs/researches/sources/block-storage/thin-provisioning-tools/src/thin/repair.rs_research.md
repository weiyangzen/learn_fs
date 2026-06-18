# File Research: sources/block-storage/thin-provisioning-tools/src/thin/repair.rs

This file implements high-level thin metadata repair by reading damaged input metadata and writing repaired output metadata.

Key elements:
- `ThinRepairOptions` carries input path, output path, engine options, report, and superblock overrides.
- `new_context()` opens the input read-only and output writable.
- `repair()`:
  - reads or rebuilds superblock state via `read_or_rebuild_superblock()`
  - builds metadata from input using `build_metadata()`
  - optimizes shared metadata definitions with `optimise_metadata()`
  - creates output metadata space map and `WriteBatcher`
  - creates a `Restorer`
  - calls `dump_metadata()` to replay the rebuilt metadata into the output

Interactions:
- Combines `metadata_repair`, `metadata`, `dump`, and `restore`.
- Uses the same visitor pipeline as dump/restore, but source and destination are metadata devices.

Risks and notes:
- Repair quality depends on `read_or_rebuild_superblock()` root inference if the original superblock is corrupt.
- It writes to a separate output metadata device/file rather than modifying input in place.
