# sources/control-plane/mayastor/io-engine/tests/malloc_bdev.rs

Purpose: verifies malloc bdev creation using both `size_mb` and `num_blocks` produces equivalent capacity and supports basic read/write.

Important APIs/types/functions: `bdev_create`, `bdev_destroy`, `UntypedBdev::open_by_name`, `DmaBuf`, `write_at`, `read_at`.

Control flow: creates `malloc0` with `size_mb=100` and `malloc1` with equivalent `num_blocks`, opens both, compares size/block count and UUID inequality, writes the same pattern to each, reads back into DMA buffers, compares bytes, then destroys both.

State and persistence: malloc bdevs only; no durable state.

Dependencies and integration points: malloc URI parser, bdev registry, bdev handle I/O, DMA buffer allocation.

Risks and edge cases: destroy URI for `malloc1` uses `size_mb=100` although it was created with `num_blocks`; this intentionally relies on name matching rather than exact URI option matching.

Test signals: basic malloc bdev capacity and data-path sanity.
