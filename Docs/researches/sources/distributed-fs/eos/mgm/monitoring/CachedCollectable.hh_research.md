# sources/distributed-fs/eos/mgm/monitoring/CachedCollectable.hh

Purpose: declares the cached Prometheus collectable wrapper used by MGM monitoring to limit scrape-time work.

Important APIs and types: `CachedCollectable` derives from `prometheus::Collectable`, accepts an inner collectable and TTL in its constructor, and overrides `Collect`. Private `CacheIsFresh` centralizes TTL validation. State includes the wrapped collectable, TTL, a cache mutex, a refresh mutex, cache-existence flag, timestamp, and cached metric families.

Control flow and state behavior: the two-lock design separates short cache reads from long refresh ownership. Members are mutable because Prometheus collection is a logically const API but cache refresh mutates internal state. No persistent state is involved.

Dependencies and integration points: includes Prometheus C++ client headers, chrono, memory, mutex, and vector. Used by `PrometheusExporter.cc` when building the MGM metrics endpoint.

Risks and test signals: because `Collect` is const and internally synchronized, tests should treat it as thread-safe under concurrent Prometheus scrapes. The TTL unit is milliseconds in the wrapper even though configuration is seconds elsewhere, so integration tests should verify conversion at the exporter boundary.
