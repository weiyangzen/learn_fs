<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cached_fs.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/cached_fs.cpp

Purpose: Generic cached filesystem and cached file implementation over an `ICachePool`.

APIs and control flow: `CachedFs::open` opens a cache store, binds source filesystem, page size, allocator, and returns `CachedFile`. It proxies many filesystem metadata/xattr operations to the source and evicts cache on unlink. `CachedFile` routes preads/pwrites to the cache store, `fstat` uses actual size or source fstat, `query` asks for refill ranges, `fallocate` evicts aligned ranges, and `fadvise(WILLNEED)` prefetches in chunks up to 32 MiB.

State and persistence: Cache contents live in stores; read/write offsets support sequential APIs.

Dependencies and integration: Backing implementation for full-file and gzip cache wrappers.

Risks and test signals: Source ownership is external while pool ownership is internal, so deletion ordering matters. Tests should cover partial misses, xattrs, unlink eviction, and prefetch EOF.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cached_fs.cpp -->
