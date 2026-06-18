# sources/cloud-native/stargz-snapshotter/cache/cache.go

Purpose: Provides blob cache implementations used by lazy pulling: a directory-backed cache with optional memory and fd LRU caches, and a simple in-memory cache.

Important APIs: `BlobCache`, `Reader`, `Writer`, `NewDirectoryCache`, `NewMemoryCache`, `Direct`, and `PassThrough`. `DirectoryCacheConfig` controls LRU sizes, sync behavior, supplied caches/pools, direct mode, and `FADV_DONTNEED`.

Control flow: `Get` checks closed state, applies options, returns memory cache hits, fd cache hits, or opens the cache file. In direct mode it avoids memory/fd caching and optionally drops page cache on close. `Add` writes to a WIP temp file. In normal mode it first writes to a pooled memory buffer, adds that buffer to LRU, then commits to disk synchronously or in a goroutine. Commit creates the final key directory and renames the WIP file.

State and persistence: Directory cache persists files under `<dir>/<first-two-key-bytes>/<key>` and WIP files under `<dir>/wip`; close removes the entire directory. Memory cache stores buffers in a mutex-protected map.

Dependencies and integration: Uses `cacheutil.LRUCache`, `namedmutex`, filesystem operations, and `unix.Fadvise`.

Risks: Asynchronous disk commit can make a memory-hit visible before the disk file exists. Duplicate adds may reuse existing memory cache data. `cachePath` assumes key length >= 2. `PassThrough` is only an option bit here; behavior depends on callers using `GetReaderAt`.

Test signals: `cache_test.go` covers directory and memory caches, hits, misses, duplicate adds, partial `ReadAt`, and LRU eviction behavior.
