# sources/distributed-fs/ceph-client/include/linux/fscache-cache.h

Purpose: declares the FS-Cache backend interface used by cache implementations to register caches and service netfs cookies, volumes, operations, invalidations, resizing, withdrawal, and accounting. It is paired with backend documentation and complements the netfs-facing `fscache.h`.

Important APIs and types: `enum fscache_cache_state` tracks cache lifecycle from not-present through preparing, active, I/O error, and withdrawn. `struct fscache_cache` stores operation vectors, list linkage, provider-private state, refcount, active volume/access/object counters, debug id, state, and name. `struct fscache_cache_ops` supplies cache-provider callbacks for volume acquisition/free, cookie lookup/withdraw, cookie resize, invalidation, operation start, and write preparation. Public functions include `fscache_acquire_cache()`, `fscache_add_cache()`, `fscache_withdraw_cache()`, `fscache_withdraw_volume()`, `fscache_withdraw_cookie()`, `fscache_io_error()`, reference helpers for volumes/cookies, and `fscache_wait_for_operation()`. Inline helpers expose cookie state, key storage, cache-resource cookie, object count accounting, and optional stats counters.

Control flow: a backend acquires and adds a cache, implements callbacks, counts objects while live, starts operations on requested cookies, and withdraws volumes/cookies during shutdown or error. Access counters and waitqueues coordinate teardown so cache structures are not freed while objects or operations remain.

State and persistence: backend-private persistent cache contents are outside this header, but `fscache_cache` owns in-memory lifecycle and accounting state for those contents. `fscache_cookie_state()` uses acquire semantics to order cookie state reads against cookie contents.

Dependencies and integration points: integrates with `fscache.h`, netfs cache resources, workqueues, waitqueues, trace enums, cachefiles-like providers, `/proc/fs/fscache`, and optional stats.

Risks and test signals: risks include object-count leaks that block withdrawal, cache state races after I/O error, callback implementations that ignore access counts, and memory ordering bugs around cookie state. Tests should cover cache add/remove, backend I/O error, concurrent cookie lookup/invalidate/withdraw, resize during active operations, stats-enabled/disabled builds, and teardown waiting for objects.
