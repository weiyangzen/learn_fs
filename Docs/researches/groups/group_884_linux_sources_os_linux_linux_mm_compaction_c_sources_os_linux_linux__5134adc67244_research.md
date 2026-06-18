# Group Research: group_884_linux_sources_os_linux_linux_mm_compaction_c_sources_os_linux_linux__5134adc67244

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/compaction.c -->
# File Research: sources/os/linux/linux/mm/compaction.c

Linux memory compaction implementation for reducing external fragmentation by migrating movable pages out of lower PFN pageblocks and freeing higher PFN pageblocks for high-order allocations, CMA, huge pages, and proactive background compaction.

Key responsibilities:
- Maintains per-zone compaction deferral state (`compact_considered`, `compact_defer_shift`, `compact_order_failed`) to avoid repeated expensive attempts after failures.
- Tracks pageblock skip hints and cached scanner PFNs so future compaction can avoid recently unsuitable pageblocks.
- Implements free-page isolation (`isolate_freepages_block()`, `isolate_freepages_range()`) and migration-source isolation (`isolate_migratepages_block()`, `isolate_migratepages_range()`).
- Runs the main two-ended scanner in `compact_zone()`: migration scanner moves upward, free scanner moves downward, with completion when scanners meet or allocation success is predicted.
- Provides direct allocation path entry point `try_to_compact_pages()` and node-wide/manual paths through `compact_node()` / `compact_nodes()`.
- Implements `/proc/sys/vm/compact_memory`, `compaction_proactiveness`, `extfrag_threshold`, and `compact_unevictable_allowed` sysctls.
- Implements NUMA node sysfs compaction hook and background `kcompactd` worker lifecycle.

Important flows:
- `compact_zone_order()` builds a `compact_control`, installs `current->capture_control`, runs `compact_zone()`, then reports captured pages.
- `compact_finished()` checks scanner convergence, proactive fragmentation thresholds, pageblock alignment, free-area availability, fallback suitability, and contention.
- `compaction_suitable()` combines watermark checks with fragmentation index heuristics to decide whether compaction is worth attempting.
- `kcompactd()` sleeps on node waitqueues, handles allocation-triggered work via `kcompactd_do_work()`, and periodically performs proactive compaction based on weighted node fragmentation scores.
- `wakeup_kcompactd()` records the highest requested order and highest zone index, then wakes the daemon only if the node is currently suitable.

Concurrency and correctness notes:
- Uses zone locks, lruvec locks, RCU read sections, fatal-signal checks, and periodic `cond_resched()` to balance correctness and latency.
- Async compaction uses trylock-style contention detection and aborts more readily than sync/light sync paths.
- Strict free isolation is used by contiguous allocation/CMA-style callers and rolls back if any PFN in the requested range is invalid or non-free.
- Compound, THP, hugetlb, buddy, LRU, movable-ops, dirty/writeback, pinned, unevictable, and inaccessible mapping cases are handled separately during isolation.
- PCP/LRU drain points are used after migration to let freed pages merge before allocation success is tested.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/compaction.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/Kconfig -->
# File Research: sources/os/linux/linux/mm/damon/Kconfig

Kconfig menu for DAMON, the Data Access Monitoring framework.

Defines:
- `DAMON`: core data access monitoring framework.
- `DAMON_DEBUG_SANITY`: optional extra internal sanity checks for development/testing.
- `DAMON_KUNIT_TEST`: KUnit tests for core DAMON.
- `DAMON_VADDR`: virtual address-space monitoring operations, depends on `DAMON && MMU`, selects `PAGE_IDLE_FLAG`.
- `DAMON_PADDR`: physical address-space monitoring operations, depends on `DAMON && MMU`, selects `PAGE_IDLE_FLAG`.
- `DAMON_VADDR_KUNIT_TEST` and `DAMON_SYSFS_KUNIT_TEST`: KUnit tests for operations/sysfs pieces.
- `DAMON_SYSFS`: sysfs interface for configuring DAMON from userspace.
- `DAMON_RECLAIM`: DAMON-based proactive reclaim on physical memory.
- `DAMON_LRU_SORT`: DAMON-based LRU prioritization/deprioritization.
- `DAMON_STAT`: DAMON-based access statistics.
- `DAMON_STAT_ENABLED_DEFAULT`: default-enable knob for `DAMON_STAT`.

The file wires optional DAMON consumers to the physical-address backend where appropriate, making `DAMON_PADDR` the dependency for reclaim, LRU sorting, and stats.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/Makefile -->
# File Research: sources/os/linux/linux/mm/damon/Makefile

Build rules for DAMON objects.

Behavior:
- Always builds `core.o` into `obj-y`.
- Adds `ops-common.o` plus `vaddr.o` when `CONFIG_DAMON_VADDR` is enabled.
- Adds `ops-common.o` plus `paddr.o` when `CONFIG_DAMON_PADDR` is enabled.
- Adds sysfs pieces for `CONFIG_DAMON_SYSFS`.
- Adds `modules-common.o` plus `reclaim.o`, `lru_sort.o`, or `stat.o` for the corresponding DAMON modules.

Notable detail: both virtual and physical address operations share `ops-common.o`, and module-style DAMON consumers share `modules-common.o`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/core.c -->
# File Research: sources/os/linux/linux/mm/damon/core.c

Core implementation of the DAMON framework: operation registration, context/target/region/scheme lifecycle, worker-thread management, adaptive region splitting/merging, DAMOS action scheduling, quota enforcement, and live parameter commits.

Key responsibilities:
- Registers/selects monitoring operation sets through `damon_register_ops()` and `damon_select_ops()`.
- Allocates and manages `damon_ctx`, `damon_target`, `damon_region`, `damos`, `damos_filter`, and `damos_quota_goal` objects.
- Provides `damon_set_regions()`, `damon_set_attrs()`, `damon_set_schemes()`, and `damon_commit_ctx()` for initial and live configuration.
- Starts/stops one `kdamond` thread per context through `damon_start()` and `damon_stop()`, with exclusive/non-exclusive group semantics.
- Supports in-thread callbacks via `damon_call()` and region-walk callbacks via `damos_walk()`.
- Applies DAMOS schemes with access-pattern matching, core/ops filters, watermarks, quotas, quota goals, and action statistics.
- Dynamically adapts monitored regions by merging similar adjacent regions and splitting regions when region count falls low.
- Auto-tunes monitoring intervals using an access-rate feedback loop when `intervals_goal` is configured.

Important flows:
- `kdamond_fn()` initializes context state, waits for watermark activation, prepares access checks, sleeps for the sample interval, checks accesses, merges/splits regions, handles calls, applies schemes, resets aggregation, and invokes ops updates.
- `damos_apply_scheme()` bounds application by quota, splits oversized regions if needed, applies core filters, calls the backend `apply_scheme`, records charged time/size, updates stats, and resets region age for non-stat actions.
- `damos_adjust_quota()` computes effective quota from size/time caps and feedback goals, then uses backend scores to set `quota->min_score`.
- `damon_commit_ctx()` updates schemes, targets, attributes, ops, address unit, and minimum region size while marking the destination context as temporarily possibly corrupted so kdamond can stop on unsafe updates.
- `damon_set_region_biggest_system_ram_default()` finds the largest System RAM resource when a physical-monitoring module does not specify an explicit range.

Concurrency and lifecycle notes:
- Global `damon_lock` tracks running contexts and exclusive runs.
- Per-context locks protect kdamond pointer, call-control list, and walk-control state.
- `kdamond_call()` cancels pending callbacks on shutdown and can stop processing when a callback corrupts context state.
- `kdamond_fn()` destroys targets on exit, cancels pending calls/walks, clears `ctx->kdamond`, and decrements global running count.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/lru_sort.c -->
# File Research: sources/os/linux/linux/mm/damon/lru_sort.c

Module-style DAMON consumer that sorts LRU lists by prioritizing hot regions and deprioritizing cold regions in physical memory.

Key responsibilities:
- Exposes module parameters under `damon_lru_sort.*` for enabling, committing runtime inputs, active/inactive memory target ratio, interval autotuning, young-page filtering, hot/cold thresholds, quotas, watermarks, monitoring attributes, monitored physical range, address unit, kdamond PID, and stats.
- Builds two DAMOS schemes: `DAMOS_LRU_PRIO` for hot regions and `DAMOS_LRU_DEPRIO` for cold regions.
- Splits the configured time quota in half between hot and cold sorting schemes.
- Optionally adds quota goals for active/inactive memory ratios.
- Optionally adds young-page filters to avoid prioritizing not-young pages and avoid deprioritizing young pages.
- Selects the physical-address DAMON backend via `damon_modules_new_paddr_ctx_target()`.
- Uses `damon_set_region_biggest_system_ram_default()` when no explicit region is provided.

Runtime flow:
- `damon_lru_sort_enabled_store()` toggles the running context after DAMON initialization.
- `damon_lru_sort_apply_parameters()` builds a temporary context/schemes/target, validates parameters, then commits them into the live context with `damon_commit_ctx()`.
- Reconfiguration is handled by setting `commit_inputs`, after which the repeated `damon_call()` callback updates stats and commits new inputs inside kdamond context.
- `module_init(damon_lru_sort_init)` allocates the base paddr context and starts immediately if enabled via boot/module parameter.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/lru_sort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/modules-common.c -->
# File Research: sources/os/linux/linux/mm/damon/modules-common.c

Shared helper implementation for DAMON module consumers.

Primary function:
- `damon_modules_new_paddr_ctx_target()` allocates a new DAMON context, selects `DAMON_OPS_PADDR`, creates a target, adds the target to the context, and returns both pointers.

Failure handling:
- Destroys the context if selecting physical-address ops fails.
- Destroys the context if target allocation fails.
- Returns `-ENOMEM` for allocation failures and `-EINVAL` for missing/invalid paddr ops.

Used by DAMON_RECLAIM and DAMON_LRU_SORT to avoid duplicating context/target setup.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/modules-common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/modules-common.h -->
# File Research: sources/os/linux/linux/mm/damon/modules-common.h

Shared declarations and module-parameter macros for DAMON module consumers.

Provides macros for:
- Monitoring attributes: `sample_interval`, `aggr_interval`, `min_nr_regions`, `max_nr_regions`.
- DAMOS time quota: `quota_ms`, `quota_reset_interval_ms`.
- DAMOS size/time quotas: adds `quota_sz`.
- Watermarks: `wmarks_interval`, `wmarks_high`, `wmarks_mid`, `wmarks_low`.
- DAMOS stats: tried/applied region counts, tried/applied bytes, and quota-exceed counts.

Also declares:
- `damon_modules_new_paddr_ctx_target()`.

The header centralizes common module parameter naming and permissions, keeping DAMON_RECLAIM and DAMON_LRU_SORT consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/modules-common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/ops-common.c -->
# File Research: sources/os/linux/linux/mm/damon/ops-common.c

Shared low-level helpers for DAMON address-space operation backends.

Key responsibilities:
- Safely obtains LRU folios from PFNs with `damon_get_folio()`.
- Clears young/accessed state for PTEs/PMDs while interacting with MMU notifiers and folio idle state.
- Walks reverse mappings to mark folios old (`damon_folio_mkold()`) or test whether folios are young (`damon_folio_young()`).
- Computes hot and cold DAMOS scores from access frequency and region age.
- Implements folio-level DAMOS ops filters for anon, active, memcg, young, hugepage-size, and unmapped filters.
- Migrates folio lists to a target NUMA node for DAMOS migration actions.
- Provides `damos_ops_has_filter()`.

Important details:
- Device-exclusive/PFN swap entries that map pages are treated as CPU-old, with MMU notifier handling device-side young state.
- Young filter matching can also clear young state by calling `damon_folio_mkold()`.
- Migration uses `MIGRATE_ASYNC`, `MR_DAMON`, `GFP_NOWAIT`, and ignores cpuset/mempolicy constraints.
- Folios that fail migration are put back on the LRU.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/ops-common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/ops-common.h -->
# File Research: sources/os/linux/linux/mm/damon/ops-common.h

Header for shared DAMON operation helpers.

Declares:
- PFN-to-folio helper: `damon_get_folio()`.
- PTE/PMD aging helpers: `damon_ptep_mkold()`, `damon_pmdp_mkold()`.
- Folio aging/access helpers: `damon_folio_mkold()`, `damon_folio_young()`.
- DAMOS scoring helpers: `damon_cold_score()`, `damon_hot_score()`.
- Folio filter helper: `damos_folio_filter_match()`.
- NUMA migration helper: `damon_migrate_pages()`.
- Filter presence helper: `damos_ops_has_filter()`.

This file defines the common interface consumed by `paddr.c` and virtual-address DAMON operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/ops-common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/paddr.c -->
# File Research: sources/os/linux/linux/mm/damon/paddr.c

Physical address-space DAMON operations backend.

Key responsibilities:
- Converts between DAMON core addresses and physical addresses using `ctx->addr_unit`.
- Prepares access checks by selecting a random sampling address per region and marking the corresponding folio old.
- Checks accesses by testing folio young/idle state and updating region access rates.
- Registers `DAMON_OPS_PADDR` at subsys init.
- Applies physical-memory DAMOS actions: pageout, LRU prioritize, LRU deprioritize, hot/cold migration, and stats.
- Scores schemes using hot/cold score helpers from `ops-common.c`.

DAMOS behavior:
- `damon_pa_pageout()` iterates folios in a region, installs a young-page reject filter by default if none exists, isolates reclaimable folios, and calls `reclaim_pages()`.
- `damon_pa_de_activate()` activates or deactivates folios for LRU priority changes.
- `damon_pa_migrate()` isolates folios and migrates them to the scheme’s target node.
- `damon_pa_stat()` only counts bytes passing ops filters.
- `last_applied` avoids repeatedly applying an action to the same folio when regions overlap folio boundaries.

Filtering:
- Core filters are respected before ops filters via `scheme->core_filters_allowed`.
- Ops filters are evaluated with `damos_folio_filter_match()`.
- `sz_filter_passed` is accumulated in core-address units, matching DAMON’s address-unit scaling.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/paddr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/reclaim.c -->
# File Research: sources/os/linux/linux/mm/damon/reclaim.c

Module-style DAMON consumer for proactive reclamation of cold physical memory.

Key responsibilities:
- Exposes `damon_reclaim.*` module parameters for enable/disable, runtime input commit, cold age threshold, quotas, PSI/user-feedback quota goals, watermarks, monitoring intervals, monitored physical range, address unit, anon-skip filter, stats, and kdamond PID.
- Builds a single `DAMOS_PAGEOUT` scheme targeting regions of at least `PAGE_SIZE`, with zero accesses and age at least `min_age / aggr_interval`.
- Defaults quota to 10 ms and 128 MiB per second.
- Uses free-memory watermarks to activate/deactivate reclaim work.
- Optionally adds a PSI-based quota goal and/or user-feedback quota goal.
- Optionally adds an anon-page reject filter when `skip_anon` is true.

Runtime flow:
- `damon_reclaim_apply_parameters()` constructs a temporary paddr context and scheme, validates attributes, sets the monitoring region, then commits to the live context.
- `damon_reclaim_turn()` starts/stops the exclusive DAMON context and installs a repeated `damon_call()` callback.
- Callback updates exported stats and applies committed parameter changes when `commit_inputs` is set.
- Initialization creates the paddr context and starts immediately if enabled by boot/module parameter.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/reclaim.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/stat.c -->
# File Research: sources/os/linux/linux/mm/damon/stat.c

DAMON module that exposes simple system memory access statistics.

Exported module parameters:
- `enabled`: starts/stops the stat context.
- `estimated_memory_bandwidth`: read-only estimated accessed bytes per second.
- `memory_idle_ms_percentiles[101]`: read-only idle-time percentiles.
- `aggr_interval_us`: read-only current aggregation interval.

Key behavior:
- Builds an exclusive physical-address DAMON context over the full System RAM span.
- Uses default 5 ms sampling, 100 ms aggregation, 60 s ops update, 10-1000 regions.
- Enables interval autotuning toward a 4% observed access ratio with sample interval bounded from 5 ms to 10 s.
- Repeated `damon_call()` refreshes stats at most every 5 seconds.
- Bandwidth estimate sums region size multiplied by access count, scaled by aggregation interval.
- Idle percentiles sort regions by signed idleness: accessed regions are represented as negative age and idle regions as positive age.
- `enabled_store()` defers startup if DAMON is not initialized yet, allowing command-line configuration before init.

Lifecycle:
- `damon_stat_start()` destroys stale stopped context, builds a new one, starts DAMON exclusively, and registers the repeated stat callback.
- `damon_stat_stop()` stops DAMON, destroys the context, and clears the global pointer.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/stat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/sysfs-common.c -->
# File Research: sources/os/linux/linux/mm/damon/sysfs-common.c

Common sysfs support code for DAMON.

Implemented object:
- `damon_sysfs_ul_range`, a kobject-backed unsigned long range with `min` and `max` fields.

Key functions:
- `damon_sysfs_ul_range_alloc()` allocates and initializes a range object.
- `min_show()` / `min_store()` expose and update the minimum value.
- `max_show()` / `max_store()` expose and update the maximum value.
- `damon_sysfs_ul_range_release()` frees the containing range object.

Exports:
- Global `damon_sysfs_lock`.
- `damon_sysfs_ul_range_ktype`, with release callback, `kobj_sysfs_ops`, and default `min`/`max` attribute group.

This file provides a small reusable sysfs building block used by larger DAMON sysfs scheme/configuration code.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/sysfs-common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/sysfs-common.h -->
# File Research: sources/os/linux/linux/mm/damon/sysfs-common.h

Common declarations for DAMON sysfs support.

Defines:
- External `damon_sysfs_lock`.
- `struct damon_sysfs_ul_range`, containing a kobject plus unsigned long `min` and `max`.
- Allocation/release declarations and external `damon_sysfs_ul_range_ktype`.

Also declares shared scheme sysfs integration types and functions:
- `struct damon_sysfs_schemes`.
- Allocation/removal helpers for scheme directories.
- `damon_sysfs_add_schemes()`.
- Scheme stat update helpers.
- Region population/clear helpers for scheme results.
- Quota score/effective quota update helpers.

This header connects the simple range object from `sysfs-common.c` with the fuller DAMON sysfs scheme implementation in other files.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/sysfs-common.h -->