# sources/distributed-fs/ceph/src/rgw/rgw_kms_cache.h

Purpose: Declares `rgw::kms::KMSCache`, the cache layer for RGW KMS secrets. It combines a bounded web cache, keyring-backed secret storage, TTL reaping, and fetch stampede mitigation.

Important APIs and types: `SharedSecret`, `CacheResult`, `CacheValue`, `KMSSecretCache`, and `FetchFn` describe cached secret storage and fetch callbacks. The constructor takes `CephContext*` and an owned `Keyring`. Public APIs include `initialize_ttl_reaper()`, `stop_ttl_reaper()`, `reaper_initialized()`, `make_ttl_reaper_thread()`, `make_ttl_reaper_async()`, `clear_cache()`, `do_cache()`, and `disable_cache()`.

Control flow: Callers initialize the cache with a keyring, optionally start a TTL reaper on either a supplied Asio executor or an owned thread, then call `do_cache()` for each KMS key. `do_cache()` delegates cache-miss retrieval to a caller-provided `FetchFn`, making the class backend-agnostic.

State and persistence: The class owns a `WebCache<std::string, CacheValue>`, a `Keyring`, and reaper state. Reaper state is intentionally single-instance and non-copyable/non-movable to avoid duplicate reapers over one cache. `disable_cache()` mutates the Ceph config flag `rgw_crypt_s3_kms_cache_enabled`.

Dependencies and integration points: Depends on Boost.Asio executor/cancellation types, Ceph async yield/call-once helpers, keyring, web cache, and expected-style error returns. It integrates with `rgw_kms.cc` but does not know about Barbican, Vault, or KMIP.

Risks: `actual_key` is returned as a string and must be cleared by higher layers. `disable_cache()` changes runtime config globally for the daemon, so secret-store failures can affect all KMS users. Reaper initialization is idempotent but not explicitly synchronized, so callers should initialize from controlled startup code.

Test signals: Header-level consumers should validate non-copyable ownership assumptions, executor and non-executor reaper modes, cache namespace prefixes, and behavior when the configured cache is disabled.
