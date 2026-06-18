# sources/distributed-fs/juicefs/pkg/vfs/fill.go

Purpose: implements cache warmup, eviction, and cache-status checking over VFS paths or inode IDs.

Important APIs and types: `_file`, `CacheAction` (`WarmupCache`, `EvictCache`, `CheckCache`), `CacheFiller`, `NewCacheFiller`, `cacheFile`, `Cache`, path `resolve`, `walkDir`, `sliceIterator`, and `newSliceIterator`.

Control flow and state: `Cache` resolves each requested path, recursively walks directories, queues files, and processes them with bounded concurrency. `cacheFile` selects a slice handler: fill cache, evict cache, or check cache and aggregate `CacheResponse` locations/misses. Warmup may briefly open files when metadata open-cache is enabled. `sliceIterator` reads file slices chunk by chunk from metadata, counts slices/bytes, and invokes handlers either directly or in goroutines using the shared token channel.

Persistence and integration: it mutates chunk cache state through `chunk.ChunkStore` methods and reads namespace/slice metadata through `meta.Meta`. It integrates with internal control command `FillCache`.

Risks and test signals: `sliceIterator.err` is written by concurrent goroutines without synchronization. Symbolic link resolution rejects absolute or external targets. `fill_test.go` covers normal paths, directories, symlinks, internal nodes, missing paths, and missing chunks.
