# sources/distributed-fs/ceph/src/rgw/rgw_kms_cache.cc

Purpose: Implements an RGW KMS secret cache that stores fetched KMS secrets in a Ceph keyring-backed secret store and uses `WebCache` for TTL and capacity management.

Important APIs and functions: `KMSCache::KMSCache()` configures cache size and positive TTL from Ceph config and disables the cache if the keyring is unsupported. `initialize_ttl_reaper()` starts either a dedicated `std::jthread` or an async Boost.Asio reaper. `stop_ttl_reaper()` cancels/stops that reaper. `do_cache()` performs lookup, stampede-protected fetch, keyring insertion, TTL adjustment, and final secret readback.

Control flow: `do_cache()` constructs a namespaced cache key from `rgw_sse_`, a caller prefix, and key id. It obtains a shared `once_result` from `WebCache::lookup_or()`, then calls `ceph::async::call_once()` so concurrent readers of the same key share one fetch. Fetch result `-ENOENT` is treated as permanent and assigned the negative TTL; other errors are transient and assigned the transient error TTL. Successful fetches are inserted into `Keyring` with a UUID-suffixed keyring key so racing fetches never share a physical secret entry.

State and persistence: Cache entries hold `shared_ptr<KeyringSecret>` references rather than raw strings. Secrets are zeroized after keyring insertion, and `actual_key` is populated only when read back from the keyring. Reaper state is a variant containing no reaper, a service thread, or async state with strand/cancellation/future.

Dependencies and integration points: Depends on `common/web_cache.h`, `common/keyring.h`, `common/async/call_once.h`, Boost.Asio, RGW perf counters, and Ceph config keys under `rgw_crypt_s3_kms_cache_*`. It is invoked through `maybe_cache_kms_fetch()` in `rgw_kms.cc`.

Risks: If keyring add/read fails, the implementation removes the cache entry, disables cache globally in config, and returns internal error. The async reaper waits on a future after dispatching cancellation; executor shutdown ordering must ensure the cancellation is serviced. TTL minimum is computed from positive, negative, and transient TTLs, so zero or very small config values can make reaping aggressive.

Test signals: Tests should exercise concurrent fetch coalescing, positive/negative/transient TTL assignment, keyring failure disablement, clear-cache behavior, thread and async reaper lifecycle, and perf counter increments for permanent, transient, and secret-store errors.
