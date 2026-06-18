<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.cpp

Purpose: Implements per-file media operations for full-file cache stores.

APIs and control flow: Reads take an LRU entry read lock, update LRU, and read from local media. Writes check pool fullness, truncate media to actual size after eviction, range-lock the target, write, fstat disk blocks, update LRU and usage, and trigger recycle on ENOSPC. `queryRefillRange` uses fiemap over aligned 4 KiB range to find the first/last hole and expands to `refillUnit_`. `evict` truncates or punches holes.

State and persistence: Owns local media file; updates shared pool entry size/open count and sparse extents.

Dependencies and integration: Called by `CachedFile` for cache hit/miss handling.

Risks and test signals: Fiemap extent cap of 1000 can fail large fragmented reads. Tests should cover fragmented files, truncation after eviction, and concurrent refills.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_store.cpp -->
