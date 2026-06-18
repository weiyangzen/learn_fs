# sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemHandler.cc

Purpose: implements cached and streaming access to QuarkDB filesystem file-id sets for regular, unlinked, and no-replica lists.

Important APIs/types/functions: constructors set target and dense hash sentinels. `ensureContentsLoaded`, `ensureContentsLoadedAsync`, `getRedisKey`, `triggerCacheLoad`, `insert`, `erase`, `size`, `getFileList`, `getStreamingFileList`, `nuke`, `getApproximatelyRandomFile`, `hasFileId`, and `clearCache` form the API.

Control flow: first load transitions cache from `kNotLoaded` to `kInFlight`, creates a `FutureSplitter` around `folly::via(pExecutor).then(triggerCacheLoad)`, and returns futures to all waiters. `triggerCacheLoad` synchronizes the flusher, streams the QDB set into a temporary dense hash set, then swaps it into `mContents` under lock and applies any concurrent `SetChangeList` operations. `insert`/`erase` update in-memory cache or change list depending on cache state, then enqueue `SADD`/`SREM` through the flusher. `size` uses cached size when loaded or direct `SCARD` otherwise. Cache clearing drops loaded contents after inactivity if it can acquire the mutex quickly.

State and persistence: in-memory cache status, target, location, qclient/flusher/executor pointers, shared timed mutex, dense hash file-id set, change list, future splitter, last-load timestamp, and steady clock. Persistent state is the QuarkDB set selected by `getRedisKey`.

Dependencies and integration: used by `QuarkFileSystemView`. Depends on `RequestBuilder`, `MetadataFlusher`, qclient `QSet`, folly futures/executor, `SetChangeList`, `FileListRandomPicker`, and filesystem-view constants.

Risks: `ensureContentsLoadedAsync` returns `mSplitter.getFuture()` even when status is `kLoaded`; correctness depends on the splitter retaining the completed future. Streaming iterators are weakly consistent and can race flusher state. `nuke` calls flusher while holding the mutex. `clearCache` uses a short timed lock and may skip cleanup under contention.

Test signals: `sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileSystemViewTest.cc` has direct `FileSystemHandler` and `FileSystemHandlerCache` tests covering loading, mutation, and cache clearing.
