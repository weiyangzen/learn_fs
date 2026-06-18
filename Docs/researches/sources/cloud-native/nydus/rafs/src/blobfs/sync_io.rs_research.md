<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/blobfs/sync_io.rs -->
# sources/cloud-native/nydus/rafs/src/blobfs/sync_io.rs

## Purpose

This module implements synchronous FUSE operations for `BlobFs`, turning reads and DAX mappings into on-demand RAFS blob range fetches before delegating to the passthrough filesystem.

## Important APIs, Types, and Functions

`MAPPING_UNIT_SIZE` is 2 MiB. `BlobfsState::fetch_range_sync` calls `Rafs::fetch_range_synchronous`. `BlobFs::load_chunks_on_demand` computes a bounded `BlobPrefetchRequest`. The `FileSystem for BlobFs` implementation delegates read-only operations to `PassthroughFs`, denies mutating operations with `EACCES`, and intercepts `read` and `setupmapping`.

## Control Flow

`init` ensures the RAFS handle is ready before delegating to passthrough init. `read` validates/fetches the requested byte range, then calls `pfs.read`. `setupmapping` rejects writable mappings, rounds file offsets to 2 MiB boundaries, fetches the expanded range, then delegates mapping setup. All write/create/link/xattr mutation operations fail immediately.

## State and Persistence Behavior

The module does not persist new state beyond cache data fetched by the underlying `BlobDevice`. It reads cached inode-to-blob metadata and may cause backend/cache population through synchronous prefetch requests.

## Dependencies and Integration Points

It integrates with FUSE backend traits, virtio-fs fscache mapping requests, RAFS blob device prefetch, passthrough file operations, and Nydus error macros.

## Risks and Test Signals

Range validation rejects offsets beyond blob size and overflow, but `setupmapping` delegates with the rounded `len` while original `foffset` is passed, making careful compatibility with passthrough expectations important. Mutating operations are intentionally blocked. There are no focused tests for blobfs FUSE operations in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/blobfs/sync_io.rs -->
