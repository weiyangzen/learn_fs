# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/gaps.rs

This file builds run/gap batches from block-number sequences for efficient vectored I/O.

Important components:
- `RunOp::Run(begin, end)` and `RunOp::Gap(begin, end)` represent end-exclusive ranges.
- `find_runs()` groups adjacent requested blocks and optionally includes small gaps.
- `batch_adjacent()` groups adjacent runs/gaps into contiguous batches.
- `split_batches()` limits batch length.
- `generate_runs()` is the public pipeline.
- `count_gaps()` counts total gap blocks.

Integration points:
- Used by `SyncIoEngine::read_many_()` to combine requested reads with small gap buffers into larger `preadv` calls.

Test coverage:
- Single/multiple runs.
- Large and small gaps.
- Unordered input behavior.
- Singleton runs.
- Batching and max-size splitting.

Risks and notes:
- Input is not sorted internally; unordered input produces order-sensitive runs.
- Gap inclusion can read extra blocks into disposable buffers.
