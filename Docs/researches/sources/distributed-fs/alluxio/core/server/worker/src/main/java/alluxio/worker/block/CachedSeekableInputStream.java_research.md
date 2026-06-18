## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/CachedSeekableInputStream.java

### Purpose
`CachedSeekableInputStream` wraps a `SeekableUnderFileInputStream` with cache bookkeeping metadata so `UfsInputStreamCache` can associate reusable UFS streams with a resource id, file id, and file path.

### Important APIs and Types
- Package-private constructor takes an existing seekable stream, resource id, file id, and file path.
- `getResourceId`, `getFilePath`, and `getFileId` expose metadata to the cache.

### Control Flow
Construction delegates all stream behavior to the superclass wrapper, validates the resource id is non-negative, and stores identifiers. All actual read/seek/close behavior comes from `SeekableUnderFileInputStream`.

### State and Persistence
State is per-stream metadata only. It does not persist data and does not own cache membership; `UfsInputStreamCache` does.

### Dependencies and Integration Points
Used only by `UfsInputStreamCache` for Guava-cache values and removal bookkeeping.

### Risks
- The validation message says positive but accepts zero (`>= 0`).
- Package-private getters keep use local, but any incorrect file id/resource id assignment can break cache tracking.

### Test Signals
Covered indirectly by `UfsInputStreamCache` use in `UnderFileSystemBlockReaderTest` and UFS read paths.
