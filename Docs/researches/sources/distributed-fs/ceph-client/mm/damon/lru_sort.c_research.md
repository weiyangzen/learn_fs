# sources/distributed-fs/ceph-client/mm/damon/lru_sort.c

Purpose: Implements the `DAMON_LRU_SORT` policy module, which uses physical-address DAMON monitoring to prioritize hot pages on LRUs and deprioritize cold pages so reclaim prefers cold memory under pressure.

Important APIs, types, and functions: Module parameters include `enabled`, `commit_inputs`, `active_mem_bp`, `autotune_monitoring_intervals`, `filter_young_pages`, `hot_thres_access_freq`, `cold_min_age`, quotas, watermarks, monitoring attrs, monitor region bounds, `addr_unit`, stats, and `kdamond_pid`. `damon_lru_sort_apply_parameters()` builds a temporary paddr context and commits it to the live context. `damon_lru_sort_new_hot_scheme()` creates a `DAMOS_LRU_PRIO` scheme; `damon_lru_sort_new_cold_scheme()` creates `DAMOS_LRU_DEPRIO`. `damon_lru_sort_turn()` starts/stops DAMON.

Control flow: Init creates a paddr context/target and starts if `enabled` was set early. Enabling applies parameters, starts the context exclusively, and installs a repeating `damon_call()` that refreshes stats and handles `commit_inputs`. Parameter application builds hot/cold schemes with half quota each, optional active/inactive memory quota goals, optional young-page filters, default or explicit monitoring region, and commits through `damon_commit_ctx()`.

State and persistence: Runtime state is held in static module parameters plus global `ctx` and `target`. DAMOS stats are exported as read-only module params. Parameter changes are not applied to a running context until `commit_inputs` is set.

Dependencies and integration: Requires `DAMON_PADDR`, shared `modules-common`, DAMON core, paddr ops handling of `DAMOS_LRU_PRIO`/`DAMOS_LRU_DEPRIO`, and module parameter plumbing.

Risks: Invalid `addr_unit`, zero sample interval, allocation failure while adding filters/goals, or invalid monitor regions disable parameter application. Exclusive DAMON start can fail if another exclusive/noncompatible context is running. Filter semantics can alter effectiveness if young-page checks are too expensive or stale.

Test signals: Enable/disable through module params, change knobs plus `commit_inputs`, observe `kdamond_pid`, hot/cold tried/applied/quota stats, LRU behavior under pressure, active-memory autotune goals, and watermarks that activate only in the configured free-memory band.
