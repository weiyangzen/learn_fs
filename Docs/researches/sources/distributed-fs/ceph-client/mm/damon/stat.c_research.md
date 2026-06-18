# sources/distributed-fs/ceph-client/mm/damon/stat.c

Purpose: Implements `DAMON_STAT`, a monitoring-only module that exposes estimated memory bandwidth and memory idle-time percentiles through module parameters.

Important APIs, types, and functions: Module params include `enabled`, `estimated_memory_bandwidth`, `memory_idle_ms_percentiles`, and `aggr_interval_us`. `damon_stat_build_ctx()` creates a paddr context over all System RAM with interval autotuning. `damon_stat_damon_call_fn()` periodically refreshes exported metrics. `damon_stat_set_estimated_memory_bandwidth()` sums region sizes times access counts. `damon_stat_set_idletime_percentiles()` sorts regions by synthetic idle time and fills 0..100 percentiles.

Control flow: Init starts if default or boot param enables it. Enabling builds the context, starts exclusive DAMON, records last refresh time, and registers a repeating call. The repeating callback rate-limits updates to about every five seconds, copies current aggregation interval, recomputes bandwidth, sorts region pointers, and writes percentile values.

State and persistence: Static exported arrays/counters hold the latest snapshot. `damon_stat_context` owns the running DAMON context. No persistence beyond module/kernel lifetime.

Dependencies and integration: Uses DAMON core/paddr ops, `walk_system_ram_res()`, sorting, module params, and interval auto-tuning in core.

Risks: `damon_stat_sort_regions()` assumes one target and allocates region pointer arrays during callback; allocation failure skips percentile update. Percentile filling depends on nonzero total size. Bandwidth is an estimate based on DAMON sampled access counts, not hardware counters. Exclusive monitoring can conflict with other exclusive DAMON modules.

Test signals: Read module params while enabled, check percentiles monotonic by memory share, validate updates are rate-limited, compare `aggr_interval_us` under auto-tuning, and test enable/disable plus default-enabled Kconfig path.
