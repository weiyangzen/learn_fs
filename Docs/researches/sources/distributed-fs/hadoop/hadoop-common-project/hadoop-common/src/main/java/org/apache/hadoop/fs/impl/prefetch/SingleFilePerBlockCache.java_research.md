<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/SingleFilePerBlockCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/SingleFilePerBlockCache.java

## Purpose
Implements `BlockCache` by storing each cached block as a separate temporary local file and evicting entries with an LRU list.

## Important APIs, Types, And Functions
Public methods are `containsBlock`, `blocks`, `size`, `get`, `put`, `close`, `isCacheSpaceAvailable`, and `toString`. The internal `Entry` stores block number, file path, size, checksum, per-entry lock, and linked-list pointers. `readFile`, `writeFile`, `getEntry`, `addToLinkedListAndEvictIfRequired`, `deleteBlockFileAndEvictCache`, `deleteCacheFiles`, `validateEntry`, and `getTempFilePath` provide the core behavior.

## Control Flow
`put` validates duplicates by checksum, creates a temp file through `LocalDirAllocator`, writes the buffer, records size/checksum, updates statistics, moves the entry to the LRU head, and evicts the tail when the count exceeds `maxBlocksCount`. `get` looks up the entry, moves it to the head, reads the file into the caller's buffer, rewinds, and validates size/checksum. Eviction and close attempt timed write locks before deleting files.

## State And Persistence
State includes a concurrent block map, LRU `head`/`tail`, `entryListSize`, `numGets`, closed flag, and temporary files on local disk. Files persist only until eviction or cache close; failed deletion can leave temp files behind.

## Dependencies And Integration Points
Used by `CachingBlockManager`. Integrates Hadoop `LocalDirAllocator`, `Configuration`, stream statistics, `DurationTrackerFactory`, `STREAM_FILE_CACHE_EVICTION`, Guava `ImmutableSet`, Java NIO channels, and POSIX file permissions.

## Risks
LRU list state is separate from the concurrent map and must remain synchronized under `blocksLock`. Duplicate `put` validates against the caller's buffer rather than rewriting. Deletion can fail if locks are held past timeout, leaving cache files and statistic mismatches. `getTempFilePath` assumes POSIX permissions are supported.

## Test Signals
Test put/get checksum validation, duplicate put, LRU eviction order, close deletion, lock-timeout paths, cache-space probing, non-POSIX local FS behavior, and statistic updates for add/remove/evict.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/SingleFilePerBlockCache.java -->
