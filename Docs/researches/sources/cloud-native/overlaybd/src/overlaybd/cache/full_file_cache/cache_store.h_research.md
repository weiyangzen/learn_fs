<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.h

Purpose: Declares the concrete `FileCacheStore` used by the full-file cache pool.

APIs and types: Overrides `try_preadv2`, `do_preadv2`, `do_pwritev2`, `set_quota`, `stat`, `evict`, `queryRefillRange`, and `fstat`. Internal helpers cover cache-full checks, merged extents, hole calculation, and raw writes.

State and persistence: Holds pool pointer, owned local media file, refill unit, LRU file iterator, and range lock.

Dependencies and integration: Constructed by `FileCachePool::do_open`; implements `ICacheStore`.

Risks and test signals: Several admin APIs return ENOSYS. Unit tests should focus on read/write/query/evict behavior rather than unsupported quota/stat.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.h -->
