# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/mod.rs

This module file wires together IO-engine implementations.

Always exported modules:
- `base`
- `buffer`
- `buffer_pool`
- `gaps`
- `spindle`
- `sync`
- `utils`

Always re-exported:
- `base::*`
- `SpindleIoEngine`
- `SyncIoEngine`

Feature/test exports:
- `async_`, `AsyncIoEngine`, and `ring_pool` under `io_uring`.
- `core` and `ramdisk` under tests.

Integration points:
- Central import point for metadata tooling and copier code.
