## sources/cloud-native/soci-snapshotter/cache/cache.go

Purpose: generic blob cache implementations backed by a directory or memory, used for cached byte blobs with `ReaderAt` access.

Important APIs/types/functions: `BlobCache`, `Reader`, `Writer`, `DirectoryCacheConfig`, `NewDirectoryCache`, `NewMemoryCache`, `Direct`, `directoryCache.Get/Add/Close`, and `MemoryCache.Get/Add`.

Control flow: directory cache validates absolute path, creates root and `wip`, initializes LRU buffers and file descriptor caches, writes via temp files, and commits by rename. Reads prefer memory, then open-file cache, then disk. Memory cache stores committed buffers in a mutex-protected map.

State and persistence: directory cache persists blobs under the cache directory until `Close`, with temp work in `wip`; memory cache is process-local only. Async `Add` commits to disk unless `SyncAdd` is true.

Dependencies and integration: uses local `lrucache` and `namedmutex` utilities, OS filesystem primitives, and standard `io.ReaderAt` contracts.

Risks and test signals: async commit can report success before disk write failure; duplicate keys keep the first memory entry but still write through cached bytes. `wipLock` is allocated but unused. Tests cover hit/miss and eviction-size scenarios.
