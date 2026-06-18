# sources/distributed-fs/ceph-client/drivers/md/bcache/stats.h

Purpose: defines the in-memory accounting structures and public stat update/lifecycle APIs for bcache request accounting.

Important APIs/types: `struct cache_stat_collector` is a set of atomic fast-path counters for hits, misses, bypass hits/misses, cache-miss collisions, and sectors bypassed. `struct cache_stats` is a sysfs-visible snapshot with a kobject, shifted counters, and rescale counter. `struct cache_accounting` owns a closure, timer, closing flag, collector, and four exported stat windows: total, five-minute, hour, and day. Public functions initialize, add kobjects, clear totals, destroy, and mark accounting events.

Control flow: users call `bch_cache_accounting_init()` during object setup, add the kobjects once sysfs parentage exists, mark events from request paths, and call destroy during teardown. The implementation handles periodic rollup from collector to snapshots.

State and persistence: all fields are volatile kernel memory. The structures provide observability rather than recovery-critical state.

Dependencies/integration: forward-declares `cache_set`, `cached_dev`, and `bcache_device` to avoid including the full bcache type graph. Implementation integrates with sysfs and timers in `stats.c`.

Risks/test signals: every accounting instance owns timer and kobject lifecycle, so initialization/add/destroy order must be consistent. Tests should verify per-device and aggregate cache-set updates, teardown without timer leaks, sysfs object names, and clear behavior limited to totals.
