# sources/distributed-fs/ceph-client/mm/damon/reclaim.c

Purpose: Implements `DAMON_RECLAIM`, a DAMON paddr policy module that proactively reclaims cold physical memory regions under configurable quotas and watermarks.

Important APIs, types, and functions: Module params cover `enabled`, `commit_inputs`, `min_age`, quota size/time/reset, PSI/user-feedback quota goals, watermarks, monitoring attrs, monitor region bounds, `addr_unit`, `skip_anon`, stats, and `kdamond_pid`. `damon_reclaim_new_scheme()` creates a cold `DAMOS_PAGEOUT` scheme. `damon_reclaim_apply_parameters()` builds and commits a paddr context. `damon_reclaim_turn()` starts/stops the exclusive DAMON context.

Control flow: Enabling applies current parameters, starts DAMON, and registers a repeating `damon_call()` that refreshes stats and processes `commit_inputs`. Parameter application validates aggregation interval and address unit, creates a scheme matching zero-access regions older than `min_age`, adds optional quota goals and anon filter, selects either requested monitor range or biggest System RAM, then commits to the live context.

State and persistence: Runtime state is in static module params, `ctx`, `target`, and exported `damos_stat`. Running contexts are updated only via `commit_inputs`; otherwise changed params remain pending. State is runtime only.

Dependencies and integration: Requires DAMON paddr ops, core commit/start/call APIs, shared module helper, reclaim action in paddr ops, PSI for quota tuning, and kernel module parameter infrastructure.

Risks: Bad parameters disable or fail updates. `min_age / aggr_interval` depends on nonzero aggregation interval. Reclaim can compete with regular reclaim if quotas/watermarks are aggressive. Exclusive DAMON start may fail with another exclusive context.

Test signals: Enable/disable module params, verify `kdamond_pid`, change params with `commit_inputs`, inspect reclaimed/tried/quota stats, test `skip_anon`, PSI/user feedback quota goals, and watermark activation under varying free-memory pressure.
