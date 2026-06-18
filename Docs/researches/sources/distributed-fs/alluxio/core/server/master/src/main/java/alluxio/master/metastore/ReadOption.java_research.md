# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/ReadOption.java

## Purpose
`ReadOption` carries read modifiers for inode-store operations: whether to bypass caches, where ordered directory listing should start, and what child-name prefix to filter.

## Important APIs and Types
- Immutable fields: `mSkipCache`, `mStartFrom`, `mPrefix`.
- Static `defaults()` returns the default no-skip/no-range option.
- `newBuilder()` creates a builder with setters for skip cache, start-from, and prefix.
- Getters expose nullable start/prefix values.

## Control Flow
Callers build options and pass them into inode store methods. Heap and Rocks implementations use `startFrom`/`prefix` to seek sorted child maps or RocksDB key ranges. Cache implementations use `shouldSkipCache` to bypass population.

## State and Persistence
No persistence; this is an immutable request object once built.

## Dependencies and Integration Points
Used throughout `ReadOnlyInodeStore`, `Cache`, `CachingInodeStore`, `HeapInodeStore`, and `RocksInodeStore`.

## Risks and Edge Cases
- `startFrom` and `prefix` are nullable; implementations must handle all combinations consistently.
- `skipCache` may still return a cached value if it is already present in the generic cache path's skip-cache implementation.

## Test Signals
Tests should cover builder defaults, each setter, nullable fields, and consistent prefix/start behavior across heap and Rocks stores.
