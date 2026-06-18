# sources/control-plane/longhorn-engine/integration/common/frontend.py

## Purpose
Provides low-level block device access utilities for integration tests, including direct IO read/write helpers and a small `blockdev` wrapper.

## Important APIs, Types, and Functions
- `readat_direct(dev, offset, length)` and `writeat_direct(dev, offset, data)` perform page-aligned direct IO.
- `get_socket_path(volume)` and `get_block_device_path(volume)` build frontend paths.
- `blockdev` class exposes `readat`, `writeat`, and `ready`.

## Control Flow
Direct reads/writes align offsets to `PAGE_SIZE`, use `os.O_DIRECT`, `os.lseek`, and `directio`. `writeat_direct` reads the full page first, overlays encoded data into an mmap buffer, and writes a full page. `blockdev.ready` checks existence and block-device mode before IO.

## State and Persistence Behavior
Writes mutate Longhorn block devices. Reads observe data persisted by controller/replica IO. Socket and device paths are deterministic from constants.

## Dependencies and Integration Points
Used by `common.core.get_blockdev`, data tests, and frontend tests. Depends on Linux block devices, `directio`, `mmap`, and Longhorn device/socket directories.

## Risks and Edge Cases
Direct write helper does not support writes crossing page boundaries except full-page writes. It encodes strings as UTF-8, so arbitrary binary test data would need adaptation. `blockdev.readat` currently uses normal file IO, not direct IO, which may affect cache-sensitive tests.

## Test Signals
`integration/data/test_basic_ops.py`, `test_frontend.py`, and backup tests use these helpers for data integrity assertions.
