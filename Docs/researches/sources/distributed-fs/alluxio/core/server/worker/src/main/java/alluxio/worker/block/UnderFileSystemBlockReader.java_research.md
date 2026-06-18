## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UnderFileSystemBlockReader.java

### Purpose
`UnderFileSystemBlockReader` is a `BlockReader` that reads a block range directly from UFS and opportunistically caches the block into local worker storage when the read starts at offset 0 and proceeds contiguously through the whole block.

### Important APIs and Types
- Static `create(...)` acquires UFS resource, constructs reader, and initializes stream/writer at the requested offset.
- `read(long offset, long length)` performs positional-style UFS reads and writes newly read contiguous bytes to the local temp block when caching.
- `transferTo(ByteBuf)` supports sequential streaming reads and cache writes.
- `close()` finalizes stream/resource and closes block writer after calling `updateBlockWriter(blockSize)`.
- Helpers `updateUnderFileSystemInputStream`, `updateBlockWriter`, and `cancelBlockWriter` manage UFS stream positioning and local cache eligibility.

### Control Flow
Initialization opens/acquires a UFS input stream at block offset plus read offset and creates a local temp block/writer only when offset is zero and caching is allowed. If future reads skip beyond the current writer position, caching is canceled and temp metadata is aborted. On reads/transfers, bytes are read from UFS, metrics are updated, and any contiguous bytes not yet written are appended after requesting space. Close calls `updateBlockWriter` at block size, which aborts incomplete cache writes if the full block was not read, releases the UFS input stream to the cache, closes the writer, closes UFS resource, and increments blocks-read-UFS counter.

### State and Persistence
State includes UFS block metadata, UFS resource, input stream position, optional local block writer, closed flag, initial block size, metrics, and local store reference. Persistent effects occur only when the reader successfully writes and closes a full local temp block for later commit by the UFS block store/worker close flow.

### Dependencies and Integration Points
Created by `UnderFileSystemBlockStore.createBlockReader`, used by `MonoBlockStore.createUfsBlockReader`, cache requests, and client UFS fallback reads. Integrates with `LocalBlockStore`, `UfsInputStreamCache`, UFS manager resources, metrics, and Netty buffers.

### Risks
- Cache correctness depends on contiguous full-block reads; any seek gap aborts caching.
- Exceptions while appending cache data cancel the writer but still let the UFS read continue.
- `read` allocates a byte array sized by requested bytes cast to int, so very large single read requests can stress heap.
- Close behavior can abort temp blocks if called before full read; callers must understand that partial reads are no-cache.

### Test Signals
`UnderFileSystemBlockReaderTest` covers create/read/offset behavior, caching, no-cache paths, transfer, cancellation on errors, and close behavior.
