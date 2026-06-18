# subset-b-006123 research

Grouped research for CMA, compaction, and DAMON memory-management sources under `sources/distributed-fs/ceph-client/mm`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/cma_debug.c -->
# sources/distributed-fs/ceph-client/mm/cma_debug.c

Purpose: Implements the debugfs interface for Contiguous Memory Allocator areas. It exposes `/sys/kernel/debug/cma/<area>/` controls and counters that let developers inspect CMA capacity, bitmap state, used pages, maximum clear bitmap chunk, and manually allocate or free CMA pages for testing.

Important APIs, types, and functions: `struct cma_mem` tracks debugfs-triggered allocations in an hlist. `cma_debugfs_get()`, `cma_used_get()`, and `cma_maxchunk_get()` back read-only debugfs files. `cma_alloc_mem()` calls `cma_alloc()`, records the allocation, and `cma_free_mem()` releases tracked allocations through `cma_release()`. `cma_debugfs_add_one()` creates the per-CMA directory, files, per-range bitmap directories, and backward-compatible symlinks. `cma_debugfs_init()` installs the root debugfs tree at `late_initcall`.

Control flow: initialization walks global `cma_areas[]`; each area gets `alloc`, `free`, `count`, `order_per_bit`, `used`, `maxchunk`, and `ranges/<n>/` entries. Writes to `alloc` allocate the requested page count and push a `cma_mem` entry onto `cma->mem_head`. Writes to `free` pop tracked entries until the requested count is released. Partial frees are supported only when `order_per_bit == 0`.

State and persistence: The debug-only allocation ledger lives in memory under each `struct cma` and is protected by `mem_head_lock`. CMA availability and bitmap reads use `cma->lock`. State is not persistent across boot and is meant for diagnostics.

Dependencies and integration: Depends on `linux/debugfs.h`, CMA internals from `cma.h`, CMA globals (`cma_area_count`, `cma_areas`), bitmap helpers, and debugfs u32 array support.

Risks: Debugfs write interfaces can intentionally consume CMA memory; misuse can perturb production memory behavior. Partial-release behavior is constrained by bitmap granularity. Debugfs creation errors are mostly ignored, matching debugfs convention but reducing observability of setup failures.

Test signals: Enable CMA and debugfs, verify each CMA area appears, compare `used`/`maxchunk` against allocations, write counts to `alloc` and `free`, and inspect `ranges/*/bitmap`. Stress with multiple writers to exercise `mem_head_lock` and CMA locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/cma_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/cma_sysfs.c -->
# sources/distributed-fs/ceph-client/mm/cma_sysfs.c

Purpose: Provides the sysfs interface for CMA statistics under `mm_kobj/cma/<area>/`. It exposes stable read-only counters for successful allocations, failed allocations, successful releases, total pages, and currently available pages.

Important APIs, types, and functions: `cma_sysfs_account_success_pages()`, `cma_sysfs_account_fail_pages()`, and `cma_sysfs_account_release_pages()` are accounting hooks used by CMA allocation/release paths. `cma_from_kobj()` maps each kobject back to its `struct cma`. The `*_show()` functions format atomic64 counters and page counts via `sysfs_emit()`. `cma_kobj_release()` releases `struct cma_kobject`. `cma_sysfs_init()` creates the root `cma` kobject and per-area kobjects at `subsys_initcall`.

Control flow: initialization creates `mm/cma`, allocates a `cma_kobject` for each global CMA area, links it back to `struct cma`, and calls `kobject_init_and_add()` with `cma_ktype`. Read handlers dereference the owning CMA area and emit current values. On setup failure, already-added kobjects and the root are put.

State and persistence: Statistics are in atomic64 fields inside `struct cma`, while `available_pages` and `total_pages` read live CMA state. The kobject pointer is stored in `cma->cma_kobj` and cleared on release. Values reset on boot and are not persisted.

Dependencies and integration: Integrates with the core CMA allocator through exported accounting functions and `struct cma` fields declared in `cma.h`; integrates with global mm sysfs through `mm_kobj`.

Risks: `available_pages_show()` reads `cma->available_count` without the explicit spinlock used by debugfs; this is acceptable for sysfs statistics but can be momentarily stale. Initialization failure handling assumes previous areas have valid `cma_kobj`. Counter correctness depends on all CMA paths calling the accounting helpers consistently.

Test signals: Boot with CMA enabled, inspect `/sys/kernel/mm/cma/*`, force successful and failed CMA allocations, verify atomic counters advance, and test hot error paths with allocation failures in kobject creation if fault injection is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/cma_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/compaction.c -->
# sources/distributed-fs/ceph-client/mm/compaction.c

Purpose: Implements Linux memory compaction: isolating movable pages and free pages, migrating data to coalesce higher-order free blocks, supporting direct allocation slow paths, CMA contiguous allocation, proactive background compaction, sysctl/sysfs triggers, and per-node `kcompactd`.

Important APIs, types, and functions: Public entry points include `try_to_compact_pages()`, `compaction_suitable()`, `compaction_zonelist_suitable()`, `isolate_freepages_range()`, `isolate_migratepages_range()`, `wakeup_kcompactd()`, `kcompactd_run()`, and `kcompactd_stop()`. Central internals are `compact_zone()`, `compact_zone_order()`, `isolate_migratepages_block()`, `isolate_freepages_block()`, `compaction_alloc()`, `compaction_free()`, defer/reset helpers, fragmentation scoring helpers, and sysctl handlers.

Control flow: Direct compaction checks GFP eligibility, iterates allocation zones, observes deferral, builds a `compact_control`, and runs `compact_zone()`. `compact_zone()` initializes scanners from zone cached PFNs, isolates migration pages from low PFNs, isolates destination free pages from high PFNs, migrates with `migrate_pages()`, drains LRU/pcp state where useful, and stops on success, contention, scanner meeting, or unsuitability. Background `kcompactd` sleeps on per-node wait queues, runs requested compaction for high-order allocation pressure, and periodically performs proactive compaction based on fragmentation score thresholds.

State and persistence: Per-zone compaction state includes cached migrate/free PFNs, defer counters, failed order, and skip hints in pageblocks. Per-node state includes `kcompactd` task, requested max order/highest zone, and proactive trigger. Sysctls configure proactiveness, external fragmentation threshold, compact-memory trigger, and unevictable isolation policy. State is runtime only.

Dependencies and integration: Relies on page migration, LRU isolation, buddy allocator free areas, pageblock migratetypes, NUMA node devices, cpusets, PSI, freezer/kthreads, tracepoints, and CMA paths. It is a core bridge between allocation failure handling and reclaim/migration machinery.

Risks: Race-prone lockless page checks are intentionally tolerated but require careful rechecks under locks. Incorrect skip-hint or cached-PFN updates can cause missed opportunities or excessive scanning. Migration under filesystem, unevictable, huge page, and RT constraints has many policy branches. Proactive compaction can burn CPU if thresholds are poorly tuned.

Test signals: Use high-order allocation stress, THP allocation behavior, CMA `alloc_contig_range()` paths, `/proc/sys/vm/compact_memory`, node sysfs `compact`, and vmstat/tracepoints such as `COMPACT*`, `KCOMPACTD_*`, and `trace/events/compaction`. Validate under NUMA, memory hotplug, sparsemem holes, hugetlb/THP, cpuset restrictions, and PREEMPT_RT sysctl warning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/compaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/Kconfig -->
# sources/distributed-fs/ceph-client/mm/damon/Kconfig

Purpose: Declares build-time configuration for DAMON, its operation backends, user interfaces, optional modules, and KUnit tests.

Important symbols: `DAMON` enables the framework. `DAMON_DEBUG_SANITY` adds runtime sanity checks. `DAMON_KUNIT_TEST`, `DAMON_VADDR_KUNIT_TEST`, and `DAMON_SYSFS_KUNIT_TEST` gate test inclusion. `DAMON_VADDR` and `DAMON_PADDR` select virtual and physical address monitoring operations and select `PAGE_IDLE_FLAG`. `DAMON_SYSFS` enables sysfs control. `DAMON_RECLAIM`, `DAMON_LRU_SORT`, and `DAMON_STAT` enable policy modules. `DAMON_STAT_ENABLED_DEFAULT` controls default stat startup.

Control flow: Kconfig dependencies shape which objects the Makefile builds and which runtime module parameters become available. Core DAMON can exist alone; paddr/vaddr ops depend on `DAMON && MMU`; sysfs depends on `SYSFS`; policy modules depend on paddr ops.

State and persistence: No runtime state. It persists selected build capabilities into the kernel configuration and therefore constrains the runtime API surface.

Dependencies and integration: Feeds `mm/damon/Makefile`, module initialization, and tests. The selected symbols govern whether `core.c`, ops backends, sysfs files, and modules such as reclaim/lru_sort/stat are compiled.

Risks: Build combinations need to preserve object dependencies, especially shared `ops-common.o` for vaddr/paddr and `modules-common.o` for modules. Enabling debug sanity checks may add overhead. Default-enabling `DAMON_STAT` changes boot-time monitoring behavior.

Test signals: Build matrices should cover minimal `DAMON`, paddr/vaddr, sysfs, KUnit, and each module. Kconfig dependency checks should reject modules without required ops and ensure `PAGE_IDLE_FLAG` is selected for monitoring backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/Makefile -->
# sources/distributed-fs/ceph-client/mm/damon/Makefile

Purpose: Maps DAMON Kconfig symbols to compiled objects.

Important entries: `obj-y := core.o` always builds the DAMON core when the directory is selected. `CONFIG_DAMON_VADDR` builds `ops-common.o vaddr.o`; `CONFIG_DAMON_PADDR` builds `ops-common.o paddr.o`; `CONFIG_DAMON_SYSFS` builds `sysfs-common.o sysfs-schemes.o sysfs.o`; module policies add `modules-common.o` plus `reclaim.o`, `lru_sort.o`, or `stat.o`.

Control flow: The build system includes common objects only when their consumers are enabled. Both address backends share `ops-common.o`; all policy modules share `modules-common.o`.

State and persistence: No runtime state; it is build metadata.

Dependencies and integration: Integrates with `mm/Makefile` and Kconfig. Object inclusion must match symbol dependencies to avoid unresolved symbols such as paddr helpers or module parameter macros.

Risks: If multiple enabled symbols add the same object, Kbuild de-duplicates in practice, but dependency changes should be checked. Moving shared APIs between files requires updating this map.

Test signals: Compile each Kconfig combination, especially `DAMON_PADDR` with each policy module, sysfs-only builds, and vaddr+paddr together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/core.c -->
# sources/distributed-fs/ceph-client/mm/damon/core.c

Purpose: Provides the core Data Access Monitoring framework: operation registration, context/target/region/scheme lifecycle, monitoring threads, adaptive region splitting/merging, DAMOS policy application, quotas, filters, watermarks, online parameter commit, and helper APIs exported to DAMON users.

Important APIs, types, and functions: Core APIs include `damon_register_ops()`, `damon_select_ops()`, `damon_new_ctx()`, `damon_destroy_ctx()`, `damon_new_target()`, `damon_set_regions()`, `damon_new_scheme()`, `damon_set_schemes()`, `damon_set_attrs()`, `damon_commit_ctx()`, `damon_start()`, `damon_stop()`, `damon_call()`, `damos_walk()`, `damon_update_region_access_rate()`, `damon_set_region_biggest_system_ram_default()`, and `damon_initialized()`. `kdamond_fn()` is the monitoring worker loop.

Control flow: API users create a context, select registered ops, add targets/regions and schemes, set attributes, and start `kdamond`. Each loop waits for DAMOS watermarks, asks ops to prepare access checks, sleeps for the sample interval, checks accesses, merges/splits regions at aggregation boundaries, handles queued `damon_call()` callbacks, applies DAMOS schemes, tunes intervals if enabled, and invokes ops update callbacks. Stop tears down targets, cancels calls/walks, releases histograms, and updates global running-context counters.

State and persistence: State is in `struct damon_ctx`, targets, regions, schemes, filters, quota goals, watermark activation flags, and runtime counters. Global mutexes protect registered ops and running-context accounting. State is in-memory only; sysfs/module layers rebuild or commit contexts when parameters change.

Dependencies and integration: Depends on operation backends such as paddr/vaddr, tracepoints, kthreads, memcg, PSI, sysinfo, and slab caches. DAMON modules use `damon_call()` for safe online updates and repeated stats collection. KUnit coverage is included via `tests/core-kunit.h`.

Risks: Online commits set `maybe_corrupted` during partial updates; allocation failure during migration destination commit can leave a scheme only safe for destruction. Region splitting during filters and quota charging requires iteration discipline. Division by interval values is guarded in setters and conversion paths; callers must use `damon_set_attrs()`. Exclusive context logic can block unrelated DAMON users.

Test signals: KUnit core tests, start/stop races, repeated `damon_call()` cancellation, sysfs/module online commits, quota goal tuning, filter splitting, watermark activation, ops registration failure, interval auto-tuning, and tracepoint validation for aggregated regions and DAMOS application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/lru_sort.c -->
# sources/distributed-fs/ceph-client/mm/damon/lru_sort.c

Purpose: Implements the `DAMON_LRU_SORT` policy module, which uses physical-address DAMON monitoring to prioritize hot pages on LRUs and deprioritize cold pages so reclaim prefers cold memory under pressure.

Important APIs, types, and functions: Module parameters include `enabled`, `commit_inputs`, `active_mem_bp`, `autotune_monitoring_intervals`, `filter_young_pages`, `hot_thres_access_freq`, `cold_min_age`, quotas, watermarks, monitoring attrs, monitor region bounds, `addr_unit`, stats, and `kdamond_pid`. `damon_lru_sort_apply_parameters()` builds a temporary paddr context and commits it to the live context. `damon_lru_sort_new_hot_scheme()` creates a `DAMOS_LRU_PRIO` scheme; `damon_lru_sort_new_cold_scheme()` creates `DAMOS_LRU_DEPRIO`. `damon_lru_sort_turn()` starts/stops DAMON.

Control flow: Init creates a paddr context/target and starts if `enabled` was set early. Enabling applies parameters, starts the context exclusively, and installs a repeating `damon_call()` that refreshes stats and handles `commit_inputs`. Parameter application builds hot/cold schemes with half quota each, optional active/inactive memory quota goals, optional young-page filters, default or explicit monitoring region, and commits through `damon_commit_ctx()`.

State and persistence: Runtime state is held in static module parameters plus global `ctx` and `target`. DAMOS stats are exported as read-only module params. Parameter changes are not applied to a running context until `commit_inputs` is set.

Dependencies and integration: Requires `DAMON_PADDR`, shared `modules-common`, DAMON core, paddr ops handling of `DAMOS_LRU_PRIO`/`DAMOS_LRU_DEPRIO`, and module parameter plumbing.

Risks: Invalid `addr_unit`, zero sample interval, allocation failure while adding filters/goals, or invalid monitor regions disable parameter application. Exclusive DAMON start can fail if another exclusive/noncompatible context is running. Filter semantics can alter effectiveness if young-page checks are too expensive or stale.

Test signals: Enable/disable through module params, change knobs plus `commit_inputs`, observe `kdamond_pid`, hot/cold tried/applied/quota stats, LRU behavior under pressure, active-memory autotune goals, and watermarks that activate only in the configured free-memory band.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/lru_sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/modules-common.c -->
# sources/distributed-fs/ceph-client/mm/damon/modules-common.c

Purpose: Provides shared helper code for DAMON policy modules.

Important APIs, types, and functions: `damon_modules_new_paddr_ctx_target()` allocates a `damon_ctx`, selects `DAMON_OPS_PADDR`, allocates a target, attaches it to the context, and returns both via output pointers.

Control flow: The helper creates a context, fails cleanly if allocation or paddr ops selection fails, creates a target, adds it to the context, then returns ownership to the caller. On target allocation failure it destroys the context.

State and persistence: No static state. It creates transient heap state that modules later own, commit, start, or destroy.

Dependencies and integration: Depends on DAMON core APIs and the physical-address operations backend having registered `DAMON_OPS_PADDR`. Used by reclaim, LRU sort, and similar modules to avoid duplicate context setup.

Risks: Returns `-EINVAL` when paddr ops are unavailable; modules must surface this as disabled/unavailable. Callers must destroy the returned context on subsequent failures to avoid leaks.

Test signals: Build modules with `DAMON_PADDR`, force allocation failures, and verify callers clean up both success and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/modules-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/modules-common.h -->
# sources/distributed-fs/ceph-client/mm/damon/modules-common.h

Purpose: Declares shared module helpers and macro families for defining DAMON module parameters consistently.

Important APIs and macros: `DEFINE_DAMON_MODULES_MON_ATTRS_PARAMS()` exposes monitoring intervals and region limits. `DEFINE_DAMON_MODULES_DAMOS_TIME_QUOTA()` and `DEFINE_DAMON_MODULES_DAMOS_QUOTAS()` expose quota knobs. `DEFINE_DAMON_MODULES_WMARKS_PARAMS()` exposes watermark thresholds. `DEFINE_DAMON_MODULES_DAMOS_STATS_PARAMS()` exposes read-only tried/applied/quota-exceed stats. It declares `damon_modules_new_paddr_ctx_target()`.

Control flow: The macros expand at file scope in modules, binding fields of static DAMON structs to module parameters with appropriate permissions.

State and persistence: No direct runtime state, but macro expansion exposes module state to userspace. Writable params are generally mode `0600`; stats are `0400`.

Dependencies and integration: Depends on `linux/moduleparam.h` and DAMON struct definitions from including C files. Used by reclaim, lru_sort, and stat-style modules.

Risks: Macro users must provide correctly typed lvalues; field renames in DAMON structs require synchronized macro updates. Permissions determine operational safety because writable knobs affect live memory policy after commit.

Test signals: Compile modules using each macro, inspect generated module params, verify permissions, and confirm stats fields map to expected counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/modules-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/ops-common.c -->
# sources/distributed-fs/ceph-client/mm/damon/ops-common.c

Purpose: Supplies shared low-level helpers for DAMON address-operation backends, especially page/folio lookup, access-bit aging, hot/cold scoring, folio filters, and NUMA migration support.

Important APIs, types, and functions: `damon_get_folio()` obtains an online LRU folio for a PFN. `damon_ptep_mkold()`, `damon_pmdp_mkold()`, `damon_folio_mkold()`, and `damon_folio_young()` implement access-bit/idle-state sampling via reverse mapping and MMU notifiers. `damon_hot_score()` and `damon_cold_score()` compute DAMOS score values. `damos_folio_filter_match()` evaluates anon, active, memcg, young, hugepage-size, and unmapped filters. `damon_migrate_pages()` migrates isolated folios to a target NUMA node.

Control flow: Access checks clear young bits and set folio idle state, later query young/idle/MMU notifier state to decide if accessed. Filters call into folio predicates and may mark young pages old after matching. Migration groups folios by source node, locks where possible, calls `migrate_pages()` with async DAMON reason, returns migrated folios, and puts back failed pages to LRU.

State and persistence: No global persistent state. It mutates PTE/PMD young bits, folio idle/young flags, LRU membership during migration, and memcg references while filtering.

Dependencies and integration: Uses rmap walking, page idle, mmu_notifier, memcg, migration, swap/softleaf handling, THP conditionals, and `../internal.h`. Called by paddr and vaddr DAMON ops.

Risks: Rmap walking and nonblocking folio locking can miss accesses or decline sampling under contention. Young filtering has side effects by aging folios. Migration ignores cpuset/mempolicy by design and must avoid reclaim recursion using `memalloc_noreclaim_save()`.

Test signals: Page idle and DAMON access sampling tests, THP and device-exclusive mapping coverage, memcg filter checks, NUMA migration success/failure counts, and KUnit or trace validation of hot/cold scores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/ops-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/ops-common.h -->
# sources/distributed-fs/ceph-client/mm/damon/ops-common.h

Purpose: Declares shared DAMON operations helpers for address backends.

Important APIs: Declares folio lookup and aging helpers (`damon_get_folio()`, `damon_ptep_mkold()`, `damon_pmdp_mkold()`, `damon_folio_mkold()`, `damon_folio_young()`), score helpers (`damon_cold_score()`, `damon_hot_score()`), filter/migration helpers (`damos_folio_filter_match()`, `damon_migrate_pages()`), and `damos_ops_has_filter()`.

Control flow: Header-only control is limited to providing prototypes; consumers include paddr/vaddr operation implementations and rely on `ops-common.o` being built.

State and persistence: No state.

Dependencies and integration: Includes `linux/damon.h`; Kbuild adds `ops-common.o` when vaddr or paddr ops are enabled.

Risks: Prototype drift against implementation or `linux/damon.h` type changes will break backends. Adding helpers requires Kbuild dependency checks for all consumers.

Test signals: Compile paddr/vaddr combinations and run DAMON operation tests that exercise declared helper paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/ops-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/paddr.c -->
# sources/distributed-fs/ceph-client/mm/damon/paddr.c

Purpose: Registers DAMON operations for monitoring and acting on physical address ranges.

Important APIs, types, and functions: Address conversion helpers map DAMON core addresses through `ctx->addr_unit`. `damon_pa_prepare_access_checks()` samples a random address per region and marks its folio old. `damon_pa_check_accesses()` checks if sampled folios became young and updates access rates. DAMOS action handlers implement `DAMOS_PAGEOUT`, `DAMOS_LRU_PRIO`, `DAMOS_LRU_DEPRIO`, `DAMOS_MIGRATE_HOT`, `DAMOS_MIGRATE_COLD`, and `DAMOS_STAT`. `damon_pa_scheme_score()` selects hot/cold scoring. `damon_pa_initcall()` registers `DAMON_OPS_PADDR`.

Control flow: Monitoring periodically marks sample folios old, sleeps in core, then checks young/idle state. Scheme application iterates physical pages/folios in a region, applies ops filters, then reclaims, activates, deactivates, migrates, or only counts filter-passed size. Pageout automatically installs a young filter unless one already exists.

State and persistence: Uses only runtime DAMON regions and scheme fields. `s->last_applied` avoids reapplying to the same folio during region walks. Paddr ops mutate LRU isolation, folio active state, reference/young bits, and reclaim/migration outcomes.

Dependencies and integration: Depends on `ops-common` folio helpers, reclaim, LRU, migration, memory tiers, page idle, and DAMON core operation registration.

Risks: Physical address iteration must account for large folio sizes and invalid PFNs. The static cache in `__damon_pa_check_access()` reuses last folio results across regions, which improves performance but must remain correct with address-unit conversion. Action handlers can be costly over large regions and depend on filter semantics.

Test signals: DAMON paddr monitoring over system RAM, pageout effects, LRU activation/deactivation stats, NUMA migration actions, young-filter behavior, and registration failure when duplicate ops IDs are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/paddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/reclaim.c -->
# sources/distributed-fs/ceph-client/mm/damon/reclaim.c

Purpose: Implements `DAMON_RECLAIM`, a DAMON paddr policy module that proactively reclaims cold physical memory regions under configurable quotas and watermarks.

Important APIs, types, and functions: Module params cover `enabled`, `commit_inputs`, `min_age`, quota size/time/reset, PSI/user-feedback quota goals, watermarks, monitoring attrs, monitor region bounds, `addr_unit`, `skip_anon`, stats, and `kdamond_pid`. `damon_reclaim_new_scheme()` creates a cold `DAMOS_PAGEOUT` scheme. `damon_reclaim_apply_parameters()` builds and commits a paddr context. `damon_reclaim_turn()` starts/stops the exclusive DAMON context.

Control flow: Enabling applies current parameters, starts DAMON, and registers a repeating `damon_call()` that refreshes stats and processes `commit_inputs`. Parameter application validates aggregation interval and address unit, creates a scheme matching zero-access regions older than `min_age`, adds optional quota goals and anon filter, selects either requested monitor range or biggest System RAM, then commits to the live context.

State and persistence: Runtime state is in static module params, `ctx`, `target`, and exported `damos_stat`. Running contexts are updated only via `commit_inputs`; otherwise changed params remain pending. State is runtime only.

Dependencies and integration: Requires DAMON paddr ops, core commit/start/call APIs, shared module helper, reclaim action in paddr ops, PSI for quota tuning, and kernel module parameter infrastructure.

Risks: Bad parameters disable or fail updates. `min_age / aggr_interval` depends on nonzero aggregation interval. Reclaim can compete with regular reclaim if quotas/watermarks are aggressive. Exclusive DAMON start may fail with another exclusive context.

Test signals: Enable/disable module params, verify `kdamond_pid`, change params with `commit_inputs`, inspect reclaimed/tried/quota stats, test `skip_anon`, PSI/user feedback quota goals, and watermark activation under varying free-memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/reclaim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/stat.c -->
# sources/distributed-fs/ceph-client/mm/damon/stat.c

Purpose: Implements `DAMON_STAT`, a monitoring-only module that exposes estimated memory bandwidth and memory idle-time percentiles through module parameters.

Important APIs, types, and functions: Module params include `enabled`, `estimated_memory_bandwidth`, `memory_idle_ms_percentiles`, and `aggr_interval_us`. `damon_stat_build_ctx()` creates a paddr context over all System RAM with interval autotuning. `damon_stat_damon_call_fn()` periodically refreshes exported metrics. `damon_stat_set_estimated_memory_bandwidth()` sums region sizes times access counts. `damon_stat_set_idletime_percentiles()` sorts regions by synthetic idle time and fills 0..100 percentiles.

Control flow: Init starts if default or boot param enables it. Enabling builds the context, starts exclusive DAMON, records last refresh time, and registers a repeating call. The repeating callback rate-limits updates to about every five seconds, copies current aggregation interval, recomputes bandwidth, sorts region pointers, and writes percentile values.

State and persistence: Static exported arrays/counters hold the latest snapshot. `damon_stat_context` owns the running DAMON context. No persistence beyond module/kernel lifetime.

Dependencies and integration: Uses DAMON core/paddr ops, `walk_system_ram_res()`, sorting, module params, and interval auto-tuning in core.

Risks: `damon_stat_sort_regions()` assumes one target and allocates region pointer arrays during callback; allocation failure skips percentile update. Percentile filling depends on nonzero total size. Bandwidth is an estimate based on DAMON sampled access counts, not hardware counters. Exclusive monitoring can conflict with other exclusive DAMON modules.

Test signals: Read module params while enabled, check percentiles monotonic by memory share, validate updates are rate-limited, compare `aggr_interval_us` under auto-tuning, and test enable/disable plus default-enabled Kconfig path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/sysfs-common.c -->
# sources/distributed-fs/ceph-client/mm/damon/sysfs-common.c

Purpose: Provides shared sysfs support for DAMON, currently the reusable unsigned-long range kobject and global DAMON sysfs mutex.

Important APIs, types, and functions: Defines `damon_sysfs_lock`. `damon_sysfs_ul_range_alloc()` allocates and initializes a `struct damon_sysfs_ul_range`. `min_show()/min_store()` and `max_show()/max_store()` expose writable range endpoints. `damon_sysfs_ul_range_release()` frees the object. `damon_sysfs_ul_range_ktype` wires release, sysfs ops, and default attributes.

Control flow: Higher-level sysfs code allocates a range, registers its kobject with `damon_sysfs_ul_range_ktype`, and userspace reads/writes `min` and `max`. Store handlers parse unsigned longs with `kstrtoul()` and update the object directly.

State and persistence: Each range object stores `min` and `max` in memory; values persist only while the sysfs object exists. `damon_sysfs_lock` is global coordination state used across the sysfs DAMON implementation.

Dependencies and integration: Depends on `sysfs-common.h`, kobject/sysfs APIs, and slab allocation. Other DAMON sysfs files reference additional declarations in the header for schemes and stats.

Risks: This common range object does not enforce `min <= max`; callers must validate semantics before committing to DAMON contexts. Store updates are simple assignments and rely on external locking/serialization when needed.

Test signals: Create range kobjects through DAMON sysfs paths, read/write numeric endpoints, verify parse failures return errors, and check object release with kobject lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/sysfs-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/sysfs-common.h -->
# sources/distributed-fs/ceph-client/mm/damon/sysfs-common.h

Purpose: Declares shared types and entry points used by DAMON sysfs implementation files.

Important APIs and types: Declares global `damon_sysfs_lock`, `struct damon_sysfs_ul_range`, allocation/release functions, and `damon_sysfs_ul_range_ktype`. Declares `struct damon_sysfs_schemes` and scheme-management APIs such as `damon_sysfs_schemes_alloc()`, `damon_sysfs_add_schemes()`, stats updates, region population, region clearing, quota-score setting, and effective-quota updates.

Control flow: This header lets `sysfs.c`, `sysfs-schemes.c`, and common helpers share kobject types and convert sysfs model objects into DAMON runtime schemes.

State and persistence: No direct state, but declared structs own sysfs kobjects and arrays of scheme objects while the sysfs tree exists.

Dependencies and integration: Includes `linux/damon.h` and `linux/kobject.h`. Integrates common sysfs pieces with DAMON core contexts and scheme stats.

Risks: The header exposes cross-file contracts for sysfs scheme arrays and kobject lifetime. Mismatched ownership between allocation, directory removal, and kobject release can cause leaks or use-after-free in sysfs code.

Test signals: Compile full `DAMON_SYSFS`, run sysfs KUnit tests, exercise scheme creation/removal, stats update, quota score updates, and region-population paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/sysfs-common.h -->
