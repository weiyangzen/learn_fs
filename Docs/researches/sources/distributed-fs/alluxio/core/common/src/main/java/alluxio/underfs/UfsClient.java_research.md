## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsClient.java

### Purpose
`UfsClient` defines the asynchronous metadata-listing client contract used by Alluxio metadata sync and exposes the per-UFS rate limiter.

### Important APIs, Types, And Functions
`performListingAsync` accepts a path, continuation token, start-after marker, `DescendantType`, `checkStatus`, completion callback, and error callback. Returned `UfsStatus` names are expected to be full paths from the UFS root, excluding object-store bucket names. `getRateLimiter` returns the UFS rate limiter.

### Control Flow
The interface does not implement behavior. `BaseUnderFileSystem` provides a default executor-backed implementation, while `UnderFileSystemWithLogging` wraps and forwards calls.

### State And Persistence
No state is declared here. Implementations may hold async executors, pagination tokens, and limiter state.

### Dependencies And Integration Points
The method uses `UfsLoadResult`, `UfsStatus`, `DescendantType`, `RateLimiter`, and Java `Consumer` callbacks. It is integrated into metadata sync v2 and listing pipelines that need async, bounded UFS work.

### Risks
Callback contracts are important: implementations must call exactly one completion or error path, produce full child names, and correctly use continuation/start-after semantics. Misreporting `firstIsFile`, truncation, or last item can break incremental sync.

### Test Signals
`UnderFileSystemTestUtil.performListingAsyncAndGetResult` converts this callback API into synchronous test flow. `ObjectUnderFileSystemTest` checks one object-store listing case.
