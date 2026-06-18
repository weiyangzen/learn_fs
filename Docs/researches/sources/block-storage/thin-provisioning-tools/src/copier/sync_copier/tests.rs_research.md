# File Research: sources/block-storage/thin-provisioning-tools/src/copier/sync_copier/tests.rs

This file tests `SyncCopier` across ordered, reversed, random, partial, and failure-heavy copy workloads.

The harness stamps deterministic block contents, invalidates block-aligned byte ranges in `Ramdisk`, copies through `SyncCopier<SimpleBlockIo<Ramdisk>>`, and validates destination contents with source-to-destination reverse mappings.

Important components:
- `mk_ops()` creates direct mappings from arbitrary source and destination sequences.
- `mk_random_ops()` creates randomized subsets.
- `CopySourceIndicator` maps destination blocks to source blocks.
- `CopyVerifier` checks copied blocks, untouched blocks, and skipped failed blocks.
- `CopierTest` centralizes device setup, stamping, invalidation, copy, and verification.

Test coverage:
- Full mirroring.
- Source-sorted, destination-sorted, and random copy order.
- Skipping read-failed blocks.
- Skipping write-failed blocks.
- All reads failing and all writes failing.
- Copy lengths smaller than the buffer and not a multiple of buffer capacity.

Integration points:
- Uses the same copier traits and test utilities as production copier code.
- Validates `CopyStats` counts and error-vector content.

Risks and notes:
- The tests use `SimpleBlockIo`, so they verify copier batching logic against per-block I/O semantics, not all vectored-I/O edge cases.
