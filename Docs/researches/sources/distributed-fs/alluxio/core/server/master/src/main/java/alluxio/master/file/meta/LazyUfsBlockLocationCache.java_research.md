# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LazyUfsBlockLocationCache.java

## Purpose
`LazyUfsBlockLocationCache` lazily caches UFS block location host lists for Alluxio file blocks. It avoids paying UFS location lookup cost until callers need locations and bounds memory by configured cache capacity.

## Important APIs, Types, and Functions
The class implements `UfsBlockLocationCache`. `invalidate(long)` removes a block id, `get(long)` returns a cached value only, and `get(long, AlluxioURI, long)` resolves the file through the mount table, asks the underlying UFS for file locations at an offset, caches non-null results, and returns them.

## Control Flow, State, and Persistence
State is an in-memory Guava cache keyed by block id and a reference to `MountTable`. There is no checkpoint or journal state. A cache miss with file URI and offset resolves the Alluxio path to UFS, acquires a closeable UFS resource, calls `getFileLocations()` with `FileLocationOptions.defaults().setOffset(offset)`, and stores the list if UFS returns one. Invalid path and I/O errors are logged as warnings and return null.

## Dependencies and Integration Points
The class integrates with `MountTable.Resolution`, `UnderFileSystem`, UFS file-location APIs, and master configuration `MASTER_UFS_BLOCK_LOCATION_CACHE_CAPACITY`. It is used by file master/block location code that needs UFS locality for blocks not yet materialized in Alluxio workers.

## Risks
The cache key is only block id, not `(block id, file uri, offset)`, so correctness assumes block ids are globally unique and stable for their file/offset. Null results are not cached, so repeated UFS failures or unsupported location lookups can be retried frequently. Returning the cached `List<String>` directly allows caller-side mutation unless all callers treat it as read-only.

## Test Signals
Tests should cover cache hit/miss behavior, invalidation, mount resolution and UFS resource closing, null UFS results, exception logging/return-null behavior, and capacity eviction. Integration tests can mock UFS `getFileLocations()` and verify one UFS call for repeated block id lookups.
