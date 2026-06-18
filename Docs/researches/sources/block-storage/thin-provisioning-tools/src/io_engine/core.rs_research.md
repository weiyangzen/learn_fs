# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/core.rs

This test-only file implements an in-memory `CoreIoEngine`.

Important behavior:
- Allocates a contiguous aligned memory area sized by number of 4 KiB blocks.
- `read()` copies a block from memory into a new `Block`.
- `write()` copies from a `Block` into memory.
- `read_many()` and `write_many()` loop over single-block operations.
- `trash_block()` writes a zero block at a location.

Integration points:
- Available only under `#[cfg(test)]` from `io_engine/mod.rs`.
- Useful for unit tests that need an `IoEngine` without filesystem I/O.

Risks and notes:
- `read_blocks()` is unimplemented with `todo!()`.
- Raw memory is exposed through unsafe copy operations.
