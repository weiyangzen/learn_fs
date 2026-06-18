# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProviderShard.cc

## Purpose
This file implements one shard of the QuarkDB metadata provider. A shard owns LRU caches for file and container metadata, coalesces concurrent cache misses with `folly::FutureSplitter`, fetches from QDB through `MetadataFetcher`, and turns protobuf/map results into `QuarkFileMD` and `QuarkContainerMD` objects.

## Important APIs, Types, and Functions
The constructor stores non-owning qclient/service/executor pointers and initializes default cache sizes: 312,500 containers and 2,500,000 files per shard. `retrieveContainerMD()` checks the LRU, checks in-flight fetches under `mMutex`, fetches container protobuf, file map, and container map concurrently, combines them with `folly::collect`, processes the result on the executor, and clears in-flight state on errors. `retrieveFileMD()` follows the same pattern for file protobufs and explicitly rejects fid 0. `dropCachedFileID()` and `dropCachedContainerID()` remove LRU entries. `hasFileMD()` delegates existence checks. Insert and cache-size methods update LRU state under the mutex.

`processIncomingContainerMD()` validates id, constructs a `QuarkContainerMD`, initializes it from protobuf plus maps, erases the in-flight splitter, inserts the object into the cache, and returns the pointer. `processIncomingFileMdProto()` does the same for `QuarkFileMD`. Cache-stat methods report enabled state, occupancy, max, request/hit counters, and in-flight size.

## Control Flow
Each retrieve method uses double-checked cache lookup: a fast unlocked LRU get, then a locked in-flight/cache check. Cache hits returning deleted tombstone objects are converted to ENOENT futures. Cache misses insert a `FutureSplitter` before returning so later callers receive the same eventual object. Error continuations remove the in-flight entry and propagate the exception.

## State and Persistence Behavior
The shard stores in-memory LRU caches and in-flight maps. It reads persistent metadata from QuarkDB via `MetadataFetcher` but does not write persistent state. Newly created metadata objects can be inserted directly by services before they are fetched from QDB. Deleted objects may remain as tombstones, causing future retrievals to return ENOENT until dropped or evicted.

## Dependencies and Integration Points
It depends on folly futures/executors, `MetadataFetcher`, `QuarkFileMD`, `QuarkContainerMD`, `MDException`, EOS assertions, `LRU`, qclient, and namespace service interfaces. It is used exclusively by `MetadataProvider`.

## Risks and Test Signals
Race behavior is central. Tests should verify concurrent callers for the same id share one backend fetch, in-flight entries are erased on both success and failure, tombstone cache hits return ENOENT, fid 0 does not contact QDB, cache drops work while objects are in flight, cache stats include in-flight counts, and malformed fetched protobuf ids trip assertions. Object initialization runs under `mMutex`, so expensive initialization could block unrelated ids in the same shard.
