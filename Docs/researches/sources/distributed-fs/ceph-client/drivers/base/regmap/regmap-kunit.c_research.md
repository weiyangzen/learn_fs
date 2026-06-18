<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-kunit.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-kunit.c

Purpose: Provides a KUnit suite for regmap core and cache behavior using in-memory RAM and raw-RAM regmap buses as deterministic fixtures.

Important APIs/types/functions: `struct regmap_test_priv` stores the KUnit device and default-callback tracking. `struct regmap_test_param` drives cache type, value endian, base register, and fast I/O. `gen_regmap()` creates `regmap_init_ram()` maps; `gen_raw_regmap()` creates `regmap_init_raw_ram()` maps. The suite registers many `KUNIT_CASE_PARAM()` tests across `REGCACHE_NONE`, `FLAT`, `FLAT_S`, `RBTREE`, and `MAPLE`.

Control flow: Test init creates a KUnit device and stores the test in driver data. Parameter generators cover regular, real-cache-only, sparse-cache, flat-cache, and raw endian cases. Tests fill random RAM buffers, create regmaps, perform regmap API operations, and compare returned values with mock hardware arrays plus `read[]`/`written[]` side effects. Raw tests additionally validate endian conversion and byte-oriented raw buffers. Exit drops the KUnit device reference.

State and persistence behavior: State is test-scoped and freed via `kunit_add_action_or_reset()` invoking `regmap_exit()`. RAM fixture state includes hardware values, read/write tracking, optional no-increment register predicates, and callback invocation flags. Cache state is intentionally manipulated through `regcache_cache_only()`, `regcache_cache_bypass()`, `regcache_mark_dirty()`, `regcache_sync()`, and `regcache_drop_region()`.

Dependencies and integration points: Depends on KUnit, KUnit device helpers, random bytes, internal regmap interfaces, RAM/raw-RAM buses, and all major regcache implementations. It is the strongest local executable specification for regmap cache semantics in this subset.

Risks: Random data can hide deterministic edge cases if no fixed seed is captured, but assertions mostly compare exact in-memory transformations. Some raw tests disable locking for rbtree/maple cache types, so race properties are not exercised. Test coverage focuses on mock memory transports rather than real bus timing/failures.

Test signals: Covers basic read/write, bulk, multi, bypassed reads, volatile/cache-only interplay, readonly/writeonly policy, defaults and default callbacks, patches, stride validation, range windows, stress insertion, cache bypass, dirty sync, cache-only sync, default optimization, readonly sync, patch sync, drop-region behavior with sparse caches, cache presence including zero values, range window cache sync, raw default/raw write/raw sync/no-increment/raw range behavior, and endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-kunit.c -->
