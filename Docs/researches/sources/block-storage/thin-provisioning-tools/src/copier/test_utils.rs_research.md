# File Research: sources/block-storage/thin-provisioning-tools/src/copier/test_utils.rs

This file provides reusable copier test helpers.

`BlockVisitor` abstracts visiting sequential logical blocks. `visit_blocks()` calls a visitor for every block number from zero to `nr_blocks - 1`. `Stamper<T: FileExt>` writes deterministic generated data to each block of a device using a seed XORed with the block number.

Important behavior:
- Uses page-aligned `Buffer` allocation.
- `Stamper::offset()` supports byte-offset stamping.
- `visit()` fills the buffer with `Generator::fill_buffer()` and writes it with `write_all_at()`.

Integration points:
- Used by copier tests to stamp source/destination fixtures.
- Depends on `random::Generator`, `io_engine::buffer::Buffer`, and `FileExt`.

Risks and notes:
- Intended for tests; no production error recovery beyond returning `anyhow::Result`.
