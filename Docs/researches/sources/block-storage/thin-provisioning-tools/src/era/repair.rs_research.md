# File Research: sources/block-storage/thin-provisioning-tools/src/era/repair.rs

This file implements era metadata repair by dump-and-restore.

`repair()` opens an input metadata device and an output metadata device, reads the input superblock, creates a fresh metadata space map and `WriteBatcher` for output, and streams repaired dump output into a `Restorer`.

Important behavior:
- Input is opened read-only through `EngineBuilder`.
- Output is opened writable through `EngineBuilder`.
- Calls `dump_metadata(..., repair = true)` so lower-level dump readers use repair/permissive mode.
- Uses `Restorer` to build new era metadata structures on the output device.

Integration points:
- Bridges `era::dump` and `era::restore`.
- Uses `core_metadata_sm`, `WriteBatcher`, and superblock reading.

Risks and notes:
- Repair behavior depends heavily on dump readers' ability to tolerate damaged structures.
- It does not use the `Report` beyond storing it in context.
