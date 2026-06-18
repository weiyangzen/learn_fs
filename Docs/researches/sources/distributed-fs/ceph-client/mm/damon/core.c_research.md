# sources/distributed-fs/ceph-client/mm/damon/core.c

Purpose: Provides the core Data Access Monitoring framework: operation registration, context/target/region/scheme lifecycle, monitoring threads, adaptive region splitting/merging, DAMOS policy application, quotas, filters, watermarks, online parameter commit, and helper APIs exported to DAMON users.

Important APIs, types, and functions: Core APIs include `damon_register_ops()`, `damon_select_ops()`, `damon_new_ctx()`, `damon_destroy_ctx()`, `damon_new_target()`, `damon_set_regions()`, `damon_new_scheme()`, `damon_set_schemes()`, `damon_set_attrs()`, `damon_commit_ctx()`, `damon_start()`, `damon_stop()`, `damon_call()`, `damos_walk()`, `damon_update_region_access_rate()`, `damon_set_region_biggest_system_ram_default()`, and `damon_initialized()`. `kdamond_fn()` is the monitoring worker loop.

Control flow: API users create a context, select registered ops, add targets/regions and schemes, set attributes, and start `kdamond`. Each loop waits for DAMOS watermarks, asks ops to prepare access checks, sleeps for the sample interval, checks accesses, merges/splits regions at aggregation boundaries, handles queued `damon_call()` callbacks, applies DAMOS schemes, tunes intervals if enabled, and invokes ops update callbacks. Stop tears down targets, cancels calls/walks, releases histograms, and updates global running-context counters.

State and persistence: State is in `struct damon_ctx`, targets, regions, schemes, filters, quota goals, watermark activation flags, and runtime counters. Global mutexes protect registered ops and running-context accounting. State is in-memory only; sysfs/module layers rebuild or commit contexts when parameters change.

Dependencies and integration: Depends on operation backends such as paddr/vaddr, tracepoints, kthreads, memcg, PSI, sysinfo, and slab caches. DAMON modules use `damon_call()` for safe online updates and repeated stats collection. KUnit coverage is included via `tests/core-kunit.h`.

Risks: Online commits set `maybe_corrupted` during partial updates; allocation failure during migration destination commit can leave a scheme only safe for destruction. Region splitting during filters and quota charging requires iteration discipline. Division by interval values is guarded in setters and conversion paths; callers must use `damon_set_attrs()`. Exclusive context logic can block unrelated DAMON users.

Test signals: KUnit core tests, start/stop races, repeated `damon_call()` cancellation, sysfs/module online commits, quota goal tuning, filter splitting, watermark activation, ops registration failure, interval auto-tuning, and tracepoint validation for aggregated regions and DAMOS application.
