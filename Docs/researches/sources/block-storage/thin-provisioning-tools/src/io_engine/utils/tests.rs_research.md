# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/utils/tests.rs

This file tests `VectoredBlockIo` and `SimpleBlockIo` under injected ramdisk faults.

Important components:
- `TestContext` creates a `Ramdisk`, block size, offset, and expected faulty block bitmap.
- `ReadWriteTest` runs read/write operations over block ranges.
- `VectoredIoValidator` models vectored behavior where a failing block can cause earlier batch results to fail up to the last fault.
- `SimpleIoValidator` expects only individually faulty blocks to fail.

Test coverage:
- Reads and writes starting at a faulty block.
- Reads and writes overlapping a faulty block.
- Faults at the end of the device.
- Operations before a fault that should succeed.
- Both vectored and simple block-I/O adapters.

Integration points:
- Validates semantics consumed by `SyncCopier` and `SyncIoEngine`.

Risks and notes:
- Tests use fixed 8 KiB logical blocks on a 64 KiB ramdisk.
