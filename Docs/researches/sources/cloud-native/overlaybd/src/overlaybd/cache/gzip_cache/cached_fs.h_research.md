<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.h

Purpose: Public interface for gzip target-file cache.

APIs and types: Abstract `GzipCachedFs` declares `open_cached_gzip_file(IFile*, const char*)`. Factory `new_gzip_cached_fs` accepts media fs, refill unit, capacity, timer period, disk availability target, and allocator.

State and persistence: Implementations own a cache pool and persist cached data under the media filesystem.

Dependencies and integration: Held in `GlobalFs::gzcache_fs` and used by `ImageFile`.

Risks and test signals: Caller transfers source file ownership into the returned cached file. Tests should verify cleanup on error and successful cached reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.h -->
