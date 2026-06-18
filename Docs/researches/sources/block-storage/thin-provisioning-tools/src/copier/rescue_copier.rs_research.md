# File Research: sources/block-storage/thin-provisioning-tools/src/copier/rescue_copier.rs

This file implements `RescueCopier`, a page-level salvage copier for damaged devices or files.

`RescueCopier<T: FileExt>` copies one logical block at a time, but reads and writes the block page by page. This lets the copier preserve readable pages even when some pages within a block fail. It records a block-level read error if any page read fails and a block-level write error if any selected page write fails.

Important behavior:
- Requires `block_size`, source offset, and destination offset to be page aligned.
- `from_path()` opens source and destination with `O_EXCL | O_DIRECT`.
- `do_read()` reads each 4096-byte page and records successful page indexes in a `FixedBitSet`.
- `do_write()` writes only pages that were successfully read.
- A block counts as copied only if all page reads and writes succeeded.

Integration points:
- Implements the shared `Copier` trait.
- Uses `io_engine::buffer::Buffer` for aligned direct-I/O memory.
- Uses `CopyOp`, `CopyStats`, and `CopyProgress` from the copier module.
- Used when partial recovery is more important than all-or-nothing block copying.

Risks and notes:
- Read failures do not zero unread pages; they are simply skipped on write.
- A partial read plus successful writes still reports a read error and does not increment `nr_copied`.
- It uses one reusable buffer, so it is single-copy-loop stateful rather than internally parallel.
