<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.h

Purpose: Declares the `FileCachePool` LRU disk cache pool.

APIs and types: Exposes `Init`, `do_open`, `stat`, `evict`, `rename`, `isFull`, `removeOpenFile`, `forceRecycle`, `updateLru`, and `updateSpace`. `LruEntry` stores LRU iterator, open count, size, rwlock, and truncate flag; `FileNameMap` maps cache path to entries.

State and persistence: Owns media filesystem, timer, capacity thresholds, LRU container, file index, and usage counters.

Dependencies and integration: Creates `FileCacheStore` instances for generic cache reads/writes.

Risks and test signals: Iterator validity comments rely on map semantics and destruction order. Tests should simulate open file eviction and pool destruction.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.h -->
