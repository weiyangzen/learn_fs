## sources/distributed-fs/juicefs/pkg/chunk/cached_store_test.go

Purpose: unit and integration tests for `cachedStore`, writer/reader behavior, cache modes, writeback, delayed upload, cache fill/evict/check APIs, retry behavior, and cache-file tier/checksum parsing.

Important tests and helpers: `testStore` writes sparse/multi-block data, flushes, reads offsets across blocks, and concurrently writes/removes slices. `defaultConf` defines a temp disk cache baseline. Tests cover default disk cache, memory cache, lz4 compression, upload/download limits, low free-space config, small buffer, async writeback scanning staged files, forced direct upload versus writeback, delayed upload, hash-prefix bucket layout, `FillCache`/`EvictCache`/`CheckCache`, cached/uncached read benchmarks, `load` no-retry behavior on direct object errors, and `openCacheFile` handling of data-only, checksum+tier, invalid size, and invalid tier files.

State and persistence: uses in-memory object storage plus temp disk cache directories. Some tests precreate staging files or remove caches to assert upload/recovery behavior.

Dependencies and integration points: depends on `object.CreateStorage("mem")`, `utils.RandRead`, `testify`, local cache constants, and public `ChunkStore` APIs.

Risks and test signals: strong functional coverage for common cache paths. It relies on sleeps for async flush/scan timing, which can flake under slow CI. It validates recent tier-ID behavior in cache files and protects writeback semantics where cache-only data should fail after staged cache removal but direct-upload data should remain readable.
