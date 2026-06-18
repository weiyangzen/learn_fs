# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/sync/tests.rs

This file tests `SyncIoEngine::write_many_()` vector layout.

It uses `mockall` to mock the `VectoredIo` trait, stamps synthetic metadata blocks, and verifies that generated iovecs point to the expected buffers at expected offsets.

Important behavior:
- `allocate_test_blocks()` creates zeroed `Block`s and stamps each with its block number plus a valid NODE checksum.
- `test_write_many()` computes expected contiguous runs and configures the mock to validate position, iovec count, base pointers, lengths, and block contents.
- Tests cover empty input, contiguous blocks, gaps, long runs, and splitting beyond `UIO_MAXIOV`.

Integration points:
- Exercises private helper `find_runs_nogap()` and `SyncIoEngine::write_many_()`.

Risks and notes:
- Focuses on write batching, not read gap batching.
