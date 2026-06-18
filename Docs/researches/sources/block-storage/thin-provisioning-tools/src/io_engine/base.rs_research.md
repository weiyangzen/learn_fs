# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/base.rs

This file defines core IO-engine traits, constants, aligned `Block` allocation, and vectored file I/O wrappers.

Important definitions:
- `PAGE_SIZE = 4096`, `BLOCK_SIZE = 4096`, `SECTOR_SHIFT = 9`.
- `Block`: page-aligned 4 KiB metadata block with location.
- `ReadHandler`: callback interface for streaming reads.
- `IoEngine`: common metadata block read/write API.
- `VectoredIo`: abstraction over `preadv64`/`pwritev64`.

Important behavior:
- `Block::new()` allocates aligned raw memory.
- `Block::zeroed()` returns a zero-filled block.
- `get_nr_blocks()` derives metadata block count from file/device byte size.
- `VectoredIo` is implemented for `File` and `&File`.

Integration points:
- Foundation for sync, async, spindle, core, and test IO engines.
- Used by metadata code throughout the crate.

Risks and notes:
- `Block::get_data()` returns a mutable slice from `&self`, relying on external alias discipline.
- Raw allocation/deallocation is manual.
