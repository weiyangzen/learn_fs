# File Research: sources/block-storage/thin-provisioning-tools/src/copier/rescue_copier/tests.rs

This file tests `RescueCopier` with an injectable-error `Ramdisk`.

The test harness stamps deterministic page contents into source and destination devices, invalidates page ranges to simulate read/write failures, runs randomized `CopyOp` batches, and verifies destination pages after the copy.

Important components:
- `mk_random_ops()` creates randomized source-to-destination block mappings.
- `CopySourceIndicator` maps destination pages back to source pages.
- `CopyVerifier` validates every destination page against the expected deterministic seed.
- `CopierTest` owns source/destination ramdisks, fault sets, stamping, invalidation, copy, and verification helpers.

Test coverage:
- Complete successful block copy.
- Partial copy with unreadable source pages.
- Partial copy with unwritable destination pages.
- Combined unreadable source and unwritable destination pages.

Integration points:
- Uses `Ramdisk` error injection and `Generator` deterministic buffers.
- Uses `Stamper` and `visit_blocks()` from copier test utilities.
- Exercises `RescueCopier<Ramdisk>` through the public `Copier` trait.

Risks and notes:
- Random operation order increases coverage variety but means exact operation ordering is not deterministic.
- Assertions check expected failing source/destination block numbers for fixed invalidated ranges.
