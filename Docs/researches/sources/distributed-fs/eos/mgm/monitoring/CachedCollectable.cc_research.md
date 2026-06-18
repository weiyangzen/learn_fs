# sources/distributed-fs/eos/mgm/monitoring/CachedCollectable.cc

Purpose: implements a Prometheus `Collectable` wrapper that caches metric families for a configurable TTL and shields scrapes from expensive collection or collection exceptions.

Important APIs and functions: the constructor stores an inner `std::shared_ptr<prometheus::Collectable>` and TTL. `CacheIsFresh` returns true when cached metrics exist, TTL is positive, and the cache age is less than TTL. `Collect` returns empty for a null inner collectable, bypasses caching for non-positive TTL, returns fresh cached metrics under `mCacheMutex`, serializes refreshes with `mRefreshMutex`, returns stale cached data while another thread refreshes when possible, catches all exceptions from the inner collectable, and updates cache state after successful collection.

Control flow: fast path checks cache freshness under the cache mutex. If stale, a thread tries to acquire the refresh mutex without blocking; losing threads return stale metrics if any exist, otherwise wait for the refresh lock. After acquiring refresh responsibility, the code rechecks freshness to avoid duplicate refreshes. The actual inner `Collect` runs outside `mCacheMutex`, so cached readers are not blocked by the expensive collection except for refresh serialization.

State and persistence behavior: state is in-memory only: cached metric families, cache timestamp, and a flag indicating whether a cache has ever been populated. Exceptions preserve the last successful cache; without a cache, exceptions yield an empty vector.

Dependencies and integration points: depends on `prometheus::Collectable` and `prometheus::MetricFamily`. `PrometheusExporter.cc` wraps its registry/collectable in `CachedCollectable` using `monitoring.prometheus.cache_ttl_seconds`. Logging alias setup maps `CachedCollectable` under the Monitoring fanout.

Risks and test signals: returned vectors are copied, which is safe but can be costly for large metric sets. A TTL of zero intentionally disables caching. Catch-all exception handling prevents scrape failures but can hide repeated collection bugs unless logs are emitted by the inner collectable. Tests should simulate concurrent scrapes, null collectable, zero TTL, stale fallback while another thread refreshes, exception after a successful cache, and exception before any cache exists.
