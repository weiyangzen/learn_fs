<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cache.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/cache.cpp

Purpose: Implements common cache factory wiring and the base `ICachePool` store object cache.

APIs and control flow: `new_full_file_cached_fs` validates refill alignment and power-of-two constraints, creates `FileCachePool`, initializes it, and wraps it with `new_cached_fs`. `ICachePool` owns an `ObjectCache` of stores, optional thread pool, and source-name translation. `open` transforms names, creates or acquires cache stores, initializes metadata and pool linkage, tracks refcounts, and records size from `fstat`. `stores_clear`, `set_trans_func`, and `store_release` manage lifecycle.

State and persistence: Store cache keys map to persistent cache files managed by concrete pools.

Dependencies and integration: Used by full-file and gzip cache factories.

Risks and test signals: Refcount/ObjectCache interaction is subtle. Tests should open the same path concurrently and ensure release, eviction, and metadata remain consistent.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cache.cpp -->
