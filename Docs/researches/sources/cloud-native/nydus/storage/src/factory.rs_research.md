# sources/cloud-native/nydus/storage/src/factory.rs

Purpose: central factory for constructing and caching blob cache managers and storage backends. It selects backend implementations by config, selects cache manager type (`FileCacheMgr`, Linux `FsCacheMgr`, or `DummyCacheMgr`), owns the shared async runtime, and garbage-collects unused managers.

Important APIs and control flow: `ASYNC_RUNTIME` is a global Tokio runtime with one worker thread, up to eight blocking threads, and cache-flusher thread naming. `BlobCacheMgrKey` hashes selected config fields (`id`, backend type, cache type, prefetch config) while deriving equality over the whole `Arc<ConfigV2>`. `BLOB_FACTORY` is the global `BlobFactory`. `start_mgr_checker` starts a single periodic task that calls `BLOB_FACTORY.check_cache_stat()` every five seconds. `new_blob_cache` reads backend/cache/rafs config, reuses an existing manager under a mutex if the key matches, otherwise constructs a backend and cache manager, initializes it, inserts it, and returns `mgr.get_blob_cache(blob_info)`. `gc` asks managers to drop a target blob or unused entries and removes empty managers after a second check. `new_backend` and `new_backend_from_json` dispatch to feature-gated backend constructors.

State and persistence behavior: factory state is an in-memory mutex-protected manager map plus an atomic flag for the checker task. Cache/backend persistence is delegated to selected managers and backend implementations.

Dependencies and integration points: depends on `nydus_api` config accessors, feature-gated backend modules (`oss`, `s3`, `registry`, `localfs`, `localdisk`, `http_proxy`), cache managers, `BlobInfo`, and Tokio.

Risks and test signals: the custom hash covers fewer fields than derived equality, which is valid for `HashMap` but may reduce cache reuse if semantically identical configs differ in un-hashed fields. Holding the factory mutex while manager initialization runs can serialize slow backend setup. Tests cover default factory state, supported backend list uniqueness, and rejection of unknown backend types for config and JSON constructors.
