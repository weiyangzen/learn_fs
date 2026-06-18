# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/async_.rs

This file implements an optional `io_uring`-backed `AsyncIoEngine`.

Important components:
- `AsyncReader` streams sorted logical block requests through larger pooled IO blocks.
- `IoData` owns submitted iovecs and borrowed `IOBlock`s until completion.
- `AsyncIoEngine` wraps a direct-I/O file, block count, and `RingPool`.

Important behavior:
- Uses 16 rings and queue depth 256.
- Validates IO block sizes between 4 KiB and 16 MiB.
- Batches up to 64 contiguous IO blocks per readv request.
- On completion, calls the read handler for each requested logical block and returns buffers to the pool.
- Implements `IoEngine::{read, read_many, write, write_many, read_blocks}` with `io_uring`.

Integration points:
- Feature-gated under `io_uring` in `io_engine/mod.rs`.
- Shares logical-block mapping helpers with the sync engine.

Risks and notes:
- Uses raw pointers in submitted user data and buffer-pool memory; correctness depends on completion processing returning every block.
- `unsafe impl Send/Sync` is used for `AsyncIoEngine`.
- Some submission errors are converted to generic I/O errors.
