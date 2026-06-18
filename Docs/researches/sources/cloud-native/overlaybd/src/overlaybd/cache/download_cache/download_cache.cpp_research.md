<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/download_cache.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/download_cache.cpp

Purpose: Implements a cache mode that lazily downloads registry data into per-layer local `.download` files as reads occur.

APIs and control flow: `DownloadCacheFs::open` opens the remote source and returns `DownloadCacheFile`. The file waits for `SET_LOCAL_DIR` and `SET_SIZE` ioctls before caching; until then it reads source directly. `preadv` aligns requested ranges, locks local ranges, queries holes with fiemap, reads missing refill ranges from source into an `IOVector`, writes them to local file, then serves from local. `DownloadCacheStore::query_refill_range` computes the missing hole and expands it to `refill_size`. `fallocate` evicts aligned ranges by trimming local sparse extents.

State and persistence: Persistent data is `dir/.download`, pooled by path in `ObjectCache`; range locks protect concurrent refills.

Dependencies and integration: `ImageFile::__open_ro_remote` sends local dir and size through ioctls.

Risks and test signals: `open(const char*,int,mode_t)` recursively calls itself, a likely bug if that overload is used. Tests should cover ioctl ordering, concurrent reads, sparse fiemap, and eviction.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/download_cache.cpp -->
