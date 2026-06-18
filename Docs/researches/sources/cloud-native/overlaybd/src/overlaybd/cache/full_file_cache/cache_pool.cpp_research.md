<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.cpp

Purpose: Implements disk-backed full-file cache pool with LRU eviction.

APIs and control flow: Constructor computes water/risk marks from capacity and free-space targets. `Init` indexes existing media files and starts a periodic Photon timer. `do_open` creates media parent dirs, opens local cache files, inserts/accesses LRU entries, and returns `FileCacheStore`. `updateSpace` tracks disk-block usage and forces recycle near risk mark. `eviction` compares cache usage and filesystem free space, marks full, walks LRU from the back, truncates unopened or open files under locks, unlinks zero-size closed files, and updates total usage.

State and persistence: Maintains `fileIndex_`, LRU entries, total used bytes, and persistent cache files under `mediaFs_`.

Dependencies and integration: Used by generic full-file cache and gzip cache.

Risks and test signals: `afterFtrucate` logs unlink failure even when no error occurred. Eviction with open files and ENOSPC conditions need targeted tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/cache_pool.cpp -->
