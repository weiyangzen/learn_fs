# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/buffer_pool.rs

This file implements a fixed-size aligned IO buffer pool.

Important structures:
- `IOBlock`: location plus raw data pointer.
- `BufferPool`: contiguous allocation divided into reusable blocks.

Important behavior:
- Allocates `nr_blocks * block_size` bytes aligned to `block_size`.
- Initializes a stack of available `IOBlock`s.
- `get(loc)` pops a block and tags it with the requested location.
- `put(block)` returns the block for reuse.
- Exposes block size, block count, and empty state.

Integration points:
- Used by sync and async stream readers to read larger IO blocks and split them into logical metadata blocks.

Risks and notes:
- `IOBlock` is `Clone`, so callers must avoid returning duplicate handles to the same memory.
- Pool does not check that returned blocks came from the pool.
