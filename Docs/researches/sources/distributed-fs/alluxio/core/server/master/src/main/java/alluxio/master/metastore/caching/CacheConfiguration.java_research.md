# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/CacheConfiguration.java

## Purpose
`CacheConfiguration` is an immutable configuration object for metastore caches. It packages max size, high/low eviction watermarks, and eviction batch size.

## Important APIs and Types
- Fields: max size, high watermark, low watermark, eviction batch size.
- Static `newBuilder()` returns `Builder`.
- Builder setters configure each integer and `build()` creates the configuration.

## Control Flow
`CachingInodeStore` computes values from Alluxio configuration and builds one shared `CacheConfiguration` for inode, edge, and listing caches.

## State and Persistence
No persistence. Values are immutable after construction.

## Dependencies and Integration Points
Consumed by `Cache` and `CachingInodeStore.ListingCache`.

## Risks and Edge Cases
The class itself does not validate ratios or ordering; callers such as `CachingInodeStore` must ensure positive max size and low <= high.

## Test Signals
Tests should cover builder defaults if any, setters, getter values, and validation at the caller level.
