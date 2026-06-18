<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.cpp

Purpose: Wraps gzip-decoded target files with the generic cache store.

APIs and control flow: `GzipCachedFsImpl` owns an `ICachePool`. `open_cached_gzip_file` normalizes cache key to an absolute path, opens/creates a store, binds the source gzfile, allocator, and page size, then returns `FileSystem::new_cached_file`.

State and persistence: Stores cached decompressed data in a `FileCachePool` backed by the configured gzip cache directory.

Dependencies and integration: `ImageFile::open_lower_layer` calls this after building `new_gzfile` for remote target data.

Risks and test signals: On cache store open failure the source file is deleted. Tests should verify digest-key naming and repeated opens share cache.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/cached_fs.cpp -->
