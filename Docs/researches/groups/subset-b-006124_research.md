# subset-b-006124 Research

Grouped code research for DAMON sysfs, DAMON virtual-address operations, DAMON KUnit tests, and MM debug helpers. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/sysfs-schemes.c -->
# sources/distributed-fs/ceph-client/mm/damon/sysfs-schemes.c

## Purpose
This file implements the DAMON sysfs subtree for DAMOS schemes. It owns creation and removal of per-scheme kobjects under a DAMON context, exposes writable policy inputs such as action, access pattern, quotas, watermarks, filters, migration destinations, and exposes read-mostly runtime outputs such as scheme statistics, effective quotas, and tried regions.

It also translates sysfs scheme objects into runtime `struct damos` instances for `damon_ctx`, commits quota-goal updates into a running scheme, and mirrors runtime counters back into sysfs-visible fields.

## Important APIs, Types, And Functions
The main sysfs object graph is:

- `struct damon_sysfs_schemes`: top-level schemes directory, containing `schemes_arr` and `nr`.
- `struct damon_sysfs_scheme`: one scheme with `action`, `apply_interval_us`, `target_nid`, plus child directories for `access_pattern`, `dests`, `quotas`, `watermarks`, `filters`, `core_filters`, `ops_filters`, `stats`, and `tried_regions`.
- `struct damon_sysfs_access_pattern`: size, access-count, and age `damon_sysfs_ul_range` children.
- `struct damon_sysfs_quotas`, `struct damon_sysfs_weights`, `struct damos_sysfs_quota_goals`, and `struct damos_sysfs_quota_goal`: quota limits, scoring weights, goal tuner, and per-goal metric/current-value configuration.
- `struct damon_sysfs_scheme_filter` and `struct damon_sysfs_scheme_filters`: filter directories with type, matching, allow, memcg path, address range, hugepage-size range, and target index.
- `struct damos_sysfs_dests`: weighted migration destinations for migrate-hot/cold actions.
- `struct damon_sysfs_stats` and `struct damon_sysfs_scheme_regions`: runtime statistics and tried-region snapshots.

Externally important functions are `damon_sysfs_schemes_alloc()`, `damon_sysfs_schemes_rm_dirs()`, exported `damon_sysfs_schemes_ktype`, `damon_sysfs_add_schemes()`, `damos_sysfs_set_quota_scores()`, `damos_sysfs_update_effective_quotas()`, `damon_sysfs_schemes_update_stats()`, `damos_sysfs_populate_region_dir()`, and `damon_sysfs_schemes_clear_regions()`. These are called from `sysfs.c` when building or updating a DAMON context.

Name mapping tables translate sysfs strings into enums: DAMOS filter types (`anon`, `active`, `memcg`, `young`, `hugepage_size`, `unmapped`, `addr`, `target`), watermark metrics (`none`, `free_mem_rate`), quota-goal metrics, quota goal tuners (`consist`, `temporal`), and actions (`willneed`, `cold`, `pageout`, `hugepage`, `nohugepage`, `lru_prio`, `lru_deprio`, `migrate_hot`, `migrate_cold`, `stat`).

## Control Flow
Users grow or shrink directories by writing `nr_schemes`, `nr_filters`, `nr_goals`, or `nr_dests`. The store functions parse integers, reject negatives, try to take `damon_sysfs_lock`, remove existing child kobjects, allocate an array, and create numbered child directories with `kobject_init_and_add()`. Nested setup uses explicit rollback labels to put already-created kobjects on failure.

When a context is built, `damon_sysfs_add_schemes()` iterates sysfs schemes and calls `damon_sysfs_mk_scheme()`. That function gathers access-pattern ranges, action, apply interval, quota fields, weights, watermarks, target NUMA node, filters, quota goals, migration destinations, and max snapshot count; then creates a runtime `struct damos` with `damon_new_scheme()`. It appends quota goals with `damos_sysfs_add_quota_score()`, adds filters from all three filter directories with `damon_sysfs_add_scheme_filters()`, adds migration destinations, and returns the initialized scheme for `damon_add_scheme()`.

Runtime update commands flow in reverse. `damon_sysfs_schemes_update_stats()` copies `scheme->stat` into sysfs stats fields. `damos_sysfs_update_effective_quotas()` copies `scheme->quota.esz`. `damos_sysfs_populate_region_dir()` is called by a DAMOS walk callback to clear and repopulate tried-region kobjects or only total bytes.

## State And Persistence
All state is in kernel memory behind sysfs kobjects. User writes persist while the kobject hierarchy exists; they are not persisted across module/kernel lifecycle. Runtime scheme objects are separate copies created from sysfs inputs; modifying sysfs files does not affect a running context until the DAMON sysfs command path commits/rebuilds inputs or commits quota goals.

Kobject lifetimes are reference-counted via `.release` callbacks. Array-owning directories clear children before replacing arrays. String fields (`memcg_path`, quota-goal `path`) are replaced under `damon_sysfs_lock` and freed in release handlers.

## Dependencies And Integration Points
The file depends on `sysfs-common.h` for shared sysfs structures, allocation helpers such as `kmalloc_obj()`/`kmalloc_objs()`, `damon_sysfs_lock`, `damon_sysfs_ul_range`, and DAMON/DAMOS declarations. It integrates with cgroup memory accounting for memcg filters and quota goals through `mem_cgroup_iter()`, `mem_cgroup_online()`, `cgroup_path()`, and `mem_cgroup_id()`. NUMA support is used for default `NUMA_NO_NODE` and migration destinations.

The runtime integration points are DAMON core APIs such as `damon_new_scheme()`, `damon_destroy_scheme()`, `damon_add_scheme()`, `damos_new_filter()`, `damos_add_filter()`, `damos_new_quota_goal()`, `damos_add_quota_goal()`, `damos_commit_quota_goals()`, and scheme iteration macros.

## Risks And Edge Cases
Input validation is uneven by attribute: directory counts reject negatives, ranges validate only when translated to runtime schemes, and many quota/weight/watermark values accept any parseable unsigned value. Misordered address ranges, hugepage size ranges, missing memcg paths, or stale/offline memcg paths fail scheme creation or quota-goal commit later.

`damon_sysfs_add_schemes()` returns `-ENOMEM` for any `damon_sysfs_mk_scheme()` failure even when the underlying failure was `-EINVAL` from an invalid filter or memcg path; callers lose specificity.

`damos_sysfs_add_migrate_dest()` allocates `node_id_arr`, then `weight_arr`; on second allocation failure it relies on scheme destruction to free the first allocation. That is intentional but fragile if future callers reuse partially initialized schemes.

`damos_sysfs_populate_region_dir()` increments `nr_regions`, then uses `sysfs_regions->nr_regions++` again while naming the new kobject. This can make count values and directory numbers skip or drift. If downstream tooling assumes dense tried-region numbering, this deserves focused validation.

The sysfs show/store paths frequently use `mutex_trylock()` and return `-EBUSY` rather than sleeping. User space must handle transient busy errors.

## Test Signals
This file is included with `tests/sysfs-kunit.h` when `CONFIG_DAMON_SYSFS_KUNIT_TEST` is enabled, but that test only checks adding sysfs targets through `damon_sysfs_add_targets()` in `sysfs.c`. DAMOS scheme translation, filters, quota goals, migration destinations, tried-region population, and stats mirroring are indirectly covered by DAMON core KUnit tests for DAMOS commit/filter primitives in `tests/core-kunit.h`; the sysfs-specific scheme object graph is not directly exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/sysfs-schemes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/sysfs.c -->
# sources/distributed-fs/ceph-client/mm/damon/sysfs.c

## Purpose
This file builds the top-level DAMON sysfs administration interface under `mm_kobj` as `/sys/kernel/mm/damon/admin`. It lets user space create `kdamond` entries, configure contexts, monitoring operations, targets, initial regions, monitoring attributes, schemes, and then issue commands through a `state` file to start, stop, commit, refresh, or query runtime DAMON state.

It is the orchestration layer between the sysfs object tree and live `struct damon_ctx` instances. Scheme-specific subtree construction and translation are delegated to `sysfs-schemes.c`.

## Important APIs, Types, And Functions
The object hierarchy is:

- `struct damon_sysfs_ui_dir`: `admin` directory with `kdamonds`.
- `struct damon_sysfs_kdamonds`: numbered kdamond directories controlled by `nr_kdamonds`.
- `struct damon_sysfs_kdamond`: one daemon wrapper with child `contexts`, optional live `damon_ctx`, `state`, `pid`, and `refresh_ms`.
- `struct damon_sysfs_contexts`: currently limited to at most one context per kdamond.
- `struct damon_sysfs_context`: operations ID, address unit, and child directories `monitoring_attrs`, `targets`, and `schemes`.
- `struct damon_sysfs_targets`, `struct damon_sysfs_target`, `struct damon_sysfs_regions`, `struct damon_sysfs_region`: target PIDs, obsolete flag, and optional initial regions.
- `struct damon_sysfs_attrs`, `struct damon_sysfs_intervals`, and `struct damon_sysfs_intervals_goal`: sampling, aggregation, update intervals, auto-tuning goal, and min/max region count.

Critical functions include `damon_sysfs_init()`, `damon_sysfs_build_ctx()`, `damon_sysfs_apply_inputs()`, `damon_sysfs_set_attrs()`, `damon_sysfs_add_targets()`, `damon_sysfs_set_regions()`, `damon_sysfs_turn_damon_on()`, `damon_sysfs_turn_damon_off()`, `damon_sysfs_commit_input()`, `damon_sysfs_handle_cmd()`, and `state_store()`.

The command enum maps to sysfs `state` strings: `on`, `off`, `commit`, `commit_schemes_quota_goals`, `update_schemes_stats`, `update_schemes_tried_bytes`, `update_schemes_tried_regions`, `clear_schemes_tried_regions`, `update_schemes_effective_quotas`, and `update_tuned_intervals`.

## Control Flow
Initialization runs at `subsys_initcall(damon_sysfs_init)`. It creates the root `damon` kobject under `mm_kobj`, adds `admin`, and adds `kdamonds`.

User-space configuration starts by writing counts. `nr_kdamonds_store()`, `nr_contexts_store()`, `nr_targets_store()`, and `nr_regions_store()` parse and validate counts, take `damon_sysfs_lock`, remove existing child directories, allocate arrays, and add numbered children. Contexts default to `DAMON_OPS_VADDR`, `addr_unit` 1, default intervals of sample 5000 us, aggregate 100000 us, update 60000000 us, and region count range 10 to 1000.

Starting DAMON writes `on` to a kdamond `state`. `damon_sysfs_turn_damon_on()` rejects already-running daemons and non-one context count, destroys a stale stopped context, builds a fresh context from sysfs inputs, starts it with `damon_start()`, stores `kdamond->damon_ctx`, and schedules a repeat `damon_call()` callback for periodic stats/effective-quota/tuned-interval refresh.

Commit on a running daemon builds a parameter context from sysfs inputs, clones a test context from the running context, tries the commit into the test context, and only then commits into the running context. Scheme stats and effective quota updates are executed inside the DAMON worker via `damon_call()`. Tried-region updates walk DAMOS regions and populate sysfs tried-region directories via `sysfs-schemes.c`.

Stopping writes `off`, which calls `damon_stop()` but leaves `kdamond->damon_ctx` allocated so final monitoring results remain readable until the next start or kdamond directory reset.

## State And Persistence
The sysfs tree is dynamic kernel memory. Configuration values persist only while their kobjects exist. Live runtime state is stored in `kdamond->damon_ctx`; it is rebuilt on `on`, committed on `commit`, stopped on `off`, and destroyed in the kdamond release path or before the next `on`.

`state_show()` derives `on` or `off` from `damon_is_running(ctx)`. `pid_show()` reports `damon_kdamond_pid(ctx)` or `-1`. `refresh_ms` controls periodic readback only; zero disables periodic refresh.

## Dependencies And Integration Points
This file depends on DAMON core APIs for context allocation, ops selection, attribute validation, target management, region setting, start/stop, worker calls, and kdamond PID lookup. It uses `linux/pid.h` to resolve PID targets with `find_get_pid()` and passes referenced PIDs to DAMON targets, later cleaned up by operation cleanup.

It integrates with `sysfs-schemes.c` through `damon_sysfs_schemes_alloc()`, `damon_sysfs_schemes_ktype`, `damon_sysfs_schemes_rm_dirs()`, `damon_sysfs_add_schemes()`, `damon_sysfs_schemes_update_stats()`, `damos_sysfs_set_quota_scores()`, `damos_sysfs_update_effective_quotas()`, `damos_sysfs_populate_region_dir()`, and `damon_sysfs_schemes_clear_regions()`.

Operation availability is dynamic: `avail_operations_show()` only emits registered operations among `vaddr`, `fvaddr`, and `paddr`.

## Risks And Edge Cases
Most structural changes use `mutex_trylock(&damon_sysfs_lock)` and return `-EBUSY` on contention. User-space tooling must retry.

Only one context per kdamond is supported. `nr_contexts_store()` rejects values greater than one, and command handling rejects non-one context counts for all commands except `off`.

`damon_sysfs_add_target()` adds the new target to the context before resolving PID and setting regions. If PID resolution or region validation fails, callers rely on later context destruction to clean partially added targets.

`damon_sysfs_set_regions()` validates sorted, non-overlapping regions and rejects `start > end`, but zero-length regions where `start == end` pass through to `damon_set_regions()` for deeper handling.

`damon_sysfs_next_update_jiffies` is a single static for all kdamonds, not per kdamond. If multiple kdamonds are later supported concurrently, refresh scheduling would interfere across them.

`damon_sysfs_init()` creates a `damon` root kobject but does not retain a module-global pointer here for cleanup; the built-in subsystem init model likely assumes no module unload path.

## Test Signals
`tests/sysfs-kunit.h` is included when `CONFIG_DAMON_SYSFS_KUNIT_TEST` is enabled. It manually allocates sysfs target structures, resolves available PIDs, calls `damon_sysfs_add_targets()` twice, and checks the DAMON context target count. The test covers target addition, PID lookup success behavior, and appending targets, but it does not cover command parsing, kobject directory creation, locking behavior, context commit, start/stop, refresh callbacks, or scheme translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/tests/core-kunit.h -->
# sources/distributed-fs/ceph-client/mm/damon/tests/core-kunit.h

## Purpose
This header defines KUnit tests for DAMON core data structures, region mutation, operation registration, monitoring attribute validation, DAMOS filters, quotas, migration destinations, context commit, and helper algorithms. It is conditionally compiled under `CONFIG_DAMON_KUNIT_TEST`.

The tests are embedded in DAMON core compilation and validate low-level invariants that the sysfs and operation layers rely on.

## Important APIs, Types, And Functions
The suite is named `damon` and is registered with `kunit_test_suite(damon_test_suite)`. It exercises `struct damon_ctx`, `struct damon_target`, `struct damon_region`, `struct damos`, `struct damos_filter`, `struct damos_quota`, `struct damos_quota_goal`, and `struct damos_migrate_dests`.

Major test groups include:

- Region and target lifecycle: `damon_test_regions()`, `damon_test_target()`.
- Aggregation and monitoring-result math: `damon_test_aggregate()`, `damon_test_nr_accesses_to_accesses_bp()`, `damon_test_update_monitoring_result()`, `damon_test_moving_sum()`.
- Region splitting/merging/setting: `damon_test_split_at()`, `damon_test_merge_two()`, `damon_test_merge_regions_of()`, `damon_test_split_regions_of()`, `damon_test_set_regions()`, `damon_test_apply_min_nr_regions()`, `damon_test_is_last_region()`.
- Ops and context configuration: `damon_test_ops_registration()`, `damon_test_set_attrs()`, `damon_test_commit_ctx()`.
- DAMOS object updates: `damos_test_new_filter()`, `damos_test_commit_quota_goal()`, `damos_test_commit_quota_goals()`, `damos_test_commit_quota()`, `damos_test_commit_dests()`, `damos_test_commit_filter()`, `damos_test_commit_pageout()`, `damos_test_commit_migrate_hot()`, `damos_test_filter_out()`, `damon_test_set_filters_default_reject()`.
- Feedback loop: `damon_test_feed_loop_next_input()`.

## Control Flow
Each test allocates minimal DAMON objects, sets fields directly, calls the core API under test, and asserts state with `KUNIT_EXPECT_*`. Allocation failures call `kunit_skip()` after freeing prior allocations. Helper functions construct targets and regions or compare commit results across source/destination structures.

The suite table `damon_test_cases[]` lists all tests and terminates with an empty entry. KUnit discovers and runs them as part of the compiled suite.

## State And Persistence
All state is local to test functions. Tests directly mutate in-memory DAMON structs and free them before returning. Some tests temporarily modify global operation registration state, protected by `damon_ops_lock`, then restore the original registered operation.

The tests intentionally use stack-allocated DAMOS objects in several commit cases and initialize list heads manually to isolate commit logic from allocator behavior.

## Dependencies And Integration Points
The file depends on DAMON core implementation symbols being visible from the including translation unit. It includes `<kunit/test.h>` and assumes DAMON internal list macros and allocation helpers are in scope.

It indirectly validates behavior that `sysfs.c`, `sysfs-schemes.c`, and `vaddr.c` depend on: valid attrs constraints, `damon_set_regions()`, target-region commit semantics, filter default-reject behavior, quota-goal commit behavior, migration destination updates, and action-specific commit fields.

## Risks And Edge Cases
The tests are white-box and compiled into the implementation, so they can reach static/internal helpers. That improves precision but means they are not standalone API consumers.

Several tests use `kunit_skip()` on allocation failure, so low-memory paths may reduce coverage instead of failing. Some helpers build temporary arrays on the stack; future struct layout changes could require updating expected comparisons.

`damon_test_ops_registration()` temporarily clears `damon_registered_ops[DAMON_OPS_VADDR]`; restoration is careful but any added early return path would risk leaking global test state.

The tests cover many core invariants but do not exercise concurrent mutation, live kdamond worker calls, sysfs locking, page-table walking, or actual memory migration.

## Test Signals
This file is itself the test signal. It provides direct coverage for core mutation logic, validation failures, DAMOS commit behavior, filtering splits, and feedback-loop direction. For this subset, it is especially relevant as indirect coverage for sysfs scheme commit behavior and vaddr region adjustment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/tests/core-kunit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/tests/sysfs-kunit.h -->
# sources/distributed-fs/ceph-client/mm/damon/tests/sysfs-kunit.h

## Purpose
This header defines a small KUnit suite for the DAMON sysfs layer, enabled by `CONFIG_DAMON_SYSFS_KUNIT_TEST`. It verifies that sysfs target objects can be converted into DAMON runtime targets and appended to a context.

## Important APIs, Types, And Functions
The suite is named `damon-sysfs`. It defines `nr_damon_targets()` to count runtime targets, `__damon_sysfs_test_get_any_pid()` to find an existing PID in a numeric range, and `damon_sysfs_test_add_targets()` as the sole test case.

The test manually allocates `struct damon_sysfs_targets`, `struct damon_sysfs_target`, `struct damon_sysfs_regions`, and `struct damon_ctx`, then calls `damon_sysfs_add_targets()`.

## Control Flow
`damon_sysfs_test_add_targets()` creates a sysfs target array with one target, assigns a found PID, creates an empty regions object, and builds a new DAMON context. It calls `damon_sysfs_add_targets()` and expects one target. Then it changes the sysfs PID to another live PID, calls `damon_sysfs_add_targets()` again, and expects two targets.

The test frees manually allocated sysfs wrappers and destroys the context at the end.

## State And Persistence
All test state is transient. The PID helper briefly obtains and releases PID references only to find candidate numeric PIDs. The actual `damon_sysfs_add_targets()` call is responsible for acquiring PID references for runtime targets.

## Dependencies And Integration Points
The test depends on `sysfs.c` static helpers being visible through inclusion. It requires KUnit and a running system with at least one PID in the probed ranges. It also relies on DAMON core context allocation and target iteration.

## Risks And Edge Cases
The PID range scan may return `-1` if no PID is found; the test does not explicitly skip in that case before assigning it, so behavior depends on `damon_sysfs_add_targets()` failing or finding later PIDs for the second scan.

The test ignores return values from `damon_sysfs_add_targets()` and only checks target counts. It does not validate error handling, PID reference cleanup, region validation, physical address target constraints, or sysfs kobject creation.

## Test Signals
This is narrow positive-path coverage for sysfs-to-runtime target addition. It gives a weak signal that `damon_sysfs_add_targets()` appends targets but does not cover the broader sysfs command or scheme machinery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/tests/sysfs-kunit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/tests/vaddr-kunit.h -->
# sources/distributed-fs/ceph-client/mm/damon/tests/vaddr-kunit.h

## Purpose
This header defines KUnit tests for DAMON virtual-address region derivation and region-set updates, enabled by `CONFIG_DAMON_VADDR_KUNIT_TEST`. It validates the policy that complex VMA layouts are approximated as three monitored regions separated by the two largest unmapped gaps.

## Important APIs, Types, And Functions
The suite is named `damon-operations`. It tests internal `__damon_va_three_regions()` and core `damon_set_regions()` behavior as used by `vaddr.c`.

Key helpers are `__link_vmas()` for populating an `mm_struct` maple tree with synthetic VMAs, `damon_test_three_regions_in_vmas()`, `__nth_region_of()`, and `damon_do_test_apply_three_regions()`.

The main test cases are `damon_test_apply_three_regions1()` through `damon_test_apply_three_regions4()`, covering slight, moderate, and large changes to the three-region abstraction.

## Control Flow
The VMA test initializes a static `mm_struct` maple tree, stores synthetic VMAs, calls `__damon_va_three_regions()`, and checks the three output ranges.

The apply tests build a target with initial regions, call `damon_set_regions(t, three_regions, 3, DAMON_MIN_REGION_SZ)`, then compare the resulting target region list against expected start/end pairs. Each test destroys the target after assertions.

## State And Persistence
All state is local to the KUnit run, except the synthetic static `mm_struct` used by the first test. The test build overrides `DAMON_MIN_REGION_SZ` to `1` in `vaddr.c`, making small numeric region examples valid.

## Dependencies And Integration Points
The tests depend on maple tree VMA storage APIs, KUnit, DAMON target/region helpers, and internal vaddr functions from the including translation unit. They validate initialization and update logic used by `damon_va_init()` and `damon_va_update()`.

## Risks And Edge Cases
The tests cover abstract region math, not actual page tables, PTE aging, MMU notifier state, target PID lifetime, huge pages, migration, or madvise application. The VMA maple tree created by `__link_vmas()` is synthetic and does not model all `mm_struct` lifecycle details.

The tests focus on successful derivation with enough VMAs/gaps; failure cases such as fewer than two gaps, empty maps, or VMA iteration races are not covered.

## Test Signals
These tests are strong signals for the three-region heuristic and `damon_set_regions()` interactions. They are indirect but important coverage for `vaddr.c` initialization/update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/tests/vaddr-kunit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/vaddr.c -->
# sources/distributed-fs/ceph-client/mm/damon/vaddr.c

## Purpose
This file implements DAMON operations for process virtual address spaces. It registers `DAMON_OPS_VADDR` for adaptive virtual address monitoring and `DAMON_OPS_FVADDR` for fixed virtual address ranges. It derives initial monitored regions from a target process's VMAs, samples page-table accessed/idle state, and applies DAMOS actions such as `madvise()`, stat accounting, and NUMA migration.

## Important APIs, Types, And Functions
Target and mm helpers are `damon_get_task_struct()`, `damon_get_mm()`, and `damon_va_target_valid()`. Region initialization/update centers on `__damon_va_three_regions()`, `damon_va_three_regions()`, `__damon_va_init_regions()`, `damon_va_init()`, and `damon_va_update()`.

Access sampling uses page-table walkers:

- `damon_va_prepare_access_checks()` chooses a random sampling address per region and calls `damon_va_mkold()`.
- `damon_mkold_pmd_entry()` and `damon_mkold_hugetlb_entry()` clear young/accessed state and set folio idle state.
- `damon_va_check_accesses()` calls `damon_va_young()` through `damon_young_pmd_entry()` and `damon_young_hugetlb_entry()` and updates region access rates.

DAMOS action support includes `damos_va_filter_young_match()`, `damos_va_filter_out()`, migration helpers `damos_va_migrate_dests_add()`, `damos_va_migrate_pmd_entry()`, `damos_va_migrate()`, stat helpers `damos_va_stat_pmd_entry()` and `damos_va_stat()`, `damos_madvise()`, `damon_va_apply_scheme()`, and `damon_va_scheme_score()`.

`damon_va_initcall()` registers the operation table with DAMON core.

## Control Flow
At subsystem init, `damon_va_initcall()` registers vaddr ops with initialization/update callbacks and then registers fixed-vaddr ops by copying the same operation table but clearing `.init` and `.update`.

For adaptive vaddr monitoring, initialization walks each target. If the user did not provide regions, `__damon_va_init_regions()` obtains the target `mm_struct`, finds the two largest unmapped gaps among VMAs, constructs three ranges covering mapped regions outside those gaps, and installs them with `damon_set_regions()`. Periodic update recomputes the three ranges and resets target regions.

For sampling, the prepare phase randomly selects one address inside each region and clears accessed/young state for that address. The check phase later tests whether the same address became young or non-idle, caches the last checked folio result for adjacent regions in the same target, and updates `nr_accesses`/`nr_accesses_bp`.

For DAMOS actions, `damon_va_apply_scheme()` maps actions to `do_madvise()` behaviors, migration, or stat-only walks. Migration walks PTE/PMD entries in the region, filters folios, isolates eligible folios into weighted destination lists, and calls `damon_migrate_pages()`. Stat walks count bytes that pass filters without applying memory advice.

## State And Persistence
The operation stores no global runtime state except the registered ops. It relies on per-context targets, per-region `sampling_addr`, access counters, scheme fields, and target PID references. `damon_va_cleanup_target()` releases target PID references with `put_pid()`.

Sampling functions use static local cache variables in `__damon_va_check_access()` (`last_addr`, `last_folio_sz`, `last_accessed`) to reuse a page lookup for adjacent regions in the same target during a check pass.

## Dependencies And Integration Points
The file depends on Linux MM internals: VMA maple tree iteration, mmap locks, page-table walkers, PTE/PMD/hugetlb helpers, folio idle/young state, MMU notifiers, THP, HugeTLB, `do_madvise()`, LRU isolation, NUMA migration, and scheduler rescheduling.

It integrates with DAMON core via `struct damon_operations`: `.init`, `.update`, `.prepare_access_checks`, `.check_accesses`, `.target_valid`, `.cleanup_target`, `.apply_scheme`, and `.get_scheme_score`. It also uses common DAMON operations helpers for pte/pmd aging, hot/cold scoring, folio filters, and migration.

## Risks And Edge Cases
`__damon_va_three_regions()` requires at least two nonzero unmapped gaps. Processes with too few mappings or insufficient gaps fail initialization/update and are skipped or left unchanged.

Page-table walking races are mitigated with mmap read locks, page-table locks, and walker read locks, but sampling is inherently approximate. Young checks combine PTE/PMD young bits, folio idle state, and MMU notifier young state; architecture-specific behavior can affect accuracy.

The static last-folio cache in `__damon_va_check_access()` is scoped to the function and reused across calls; it is guarded only by the `same_target` boolean and assumes the calling flow is serial per context.

Migration destination selection uses weighted modulo based on VMA offset and folio order. If all destination weights are zero, migration is skipped. If no explicit destinations exist, all isolated folios go to `scheme->target_nid`.

Stat and migration walkers skip duplicate folios using `s->last_applied`; correctness relies on updating this field consistently across THP and PTE paths.

## Test Signals
`tests/vaddr-kunit.h` directly covers three-region derivation and `damon_set_regions()` update behavior. Core KUnit tests cover filter and scoring primitives. The file has no direct KUnit coverage for page-table young/mkold walkers, HugeTLB/THP paths, madvise application, migration isolation, or NUMA destination weighting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/damon/vaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/debug.c -->
# sources/distributed-fs/ceph-client/mm/debug.c

## Purpose
This file provides MM debugging and dump helpers for pages, folios, VMAs, `mm_struct`, and VMA merge state. It also defines trace-print flag name tables and a `vm_debug` boot option for page-struct initialization poisoning.

## Important APIs, Types, And Functions
Exported data includes `migrate_reason_names`, `pageflag_names`, `gfpflag_names`, and `vmaflag_names`. Page type rendering is handled by `page_type_names[]` and `page_type_name()`.

Key dump functions are `dump_page()`, `dump_vma()`, `dump_mm()`, and `dump_vmg()`. Internal helpers `__dump_page()` and `__dump_folio()` snapshot and print folio/page state, including refcount, mapcount, mapping, index, PFN, large-folio details, memcg data, KSM/anon/mapping information, flags, page type, and raw `struct page` bytes.

Debug configuration uses `setup_vm_debug()` through `__setup("vm_debug", ...)`, `page_init_poisoning`, and `page_init_poison()`. `vma_iter_dump_tree()` dumps maple-tree state under `CONFIG_DEBUG_VM_MAPLE_TREE`.

## Control Flow
`dump_page()` detects poisoned pages, otherwise snapshots the page and folio, prints metadata, prints page owner information, and appends a reason string if supplied. `dump_vma()`, `dump_mm()`, and `dump_vmg()` format progressively larger VM state; `dump_vmg()` optionally recurses into `dump_mm()` and `dump_vma()` for related objects and dumps the VMA iterator tree if configured.

The `vm_debug` boot parameter parser treats no argument as enabling supported debug options. With an explicit option string, it currently recognizes `p` for page initialization poisoning; a leading `-` disables all controllable options. Unknown option characters emit errors and are skipped.

## State And Persistence
The only persistent state is the static `page_init_poisoning` flag, initialized true and changed by the early boot option. Dump functions do not mutate inspected objects except for reading snapshots and printing logs. `page_init_poison()` writes `PAGE_POISON_PATTERN` into page structures when enabled.

## Dependencies And Integration Points
The file depends on core MM structures, trace event flag definitions, migration trace metadata, memcg, page owner, maple tree debugging, and architecture/formatting support for `%pGp`, `%pGg`, and `%pGv`-style flag rendering.

The exported dump helpers are used across the MM subsystem for diagnostics, VM assertions, and fault reporting. `dump_page()` is exported for modules.

## Risks And Edge Cases
Dump output intentionally accepts racing state. Comments note pageblock migratetype may change while printing flags. The snapshot path warns if the page snapshot does not match folio state, but still prints available data.

These functions can emit sensitive kernel pointer-like values depending on kernel pointer formatting policy. They are diagnostic tools and may be noisy under repeated failure paths.

`setup_vm_debug()` mutates global behavior early in boot only. New options must preserve backward behavior of no-argument and `-` parsing.

## Test Signals
There is no direct KUnit suite in this file. Runtime test signal comes from build coverage, boot-time `vm_debug` parsing, and downstream users invoking dump helpers during DEBUG_VM assertions or page diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/debug_page_alloc.c -->
# sources/distributed-fs/ceph-client/mm/debug_page_alloc.c

## Purpose
This file implements early configuration and small helpers for debug page allocation and guard pages. It owns static keys used by page allocator debug paths and supports boot parameters for enabling debug page allocation and choosing the guard-page minimum order.

## Important APIs, Types, And Functions
Global state includes `_debug_guardpage_minorder`, `_debug_pagealloc_enabled_early`, `_debug_pagealloc_enabled`, and `_debug_guardpage_enabled`. `_debug_pagealloc_enabled_early` and `_debug_pagealloc_enabled` are exported.

Boot parameter handlers are `early_debug_pagealloc()` for `debug_pagealloc=` and `debug_guardpage_minorder_setup()` for `debug_guardpage_minorder=`.

Allocator helpers are `__set_page_guard()` and `__clear_page_guard()`.

## Control Flow
`early_debug_pagealloc()` parses a boolean string into `_debug_pagealloc_enabled_early`. `debug_guardpage_minorder_setup()` parses an unsigned long, rejects values greater than `MAX_PAGE_ORDER / 2`, stores `_debug_guardpage_minorder`, and logs the configured value.

When the buddy allocator wants to mark a page as a guard page, `__set_page_guard()` rejects orders greater than or equal to `debug_guardpage_minorder()`, sets the guard flag, initializes `buddy_list`, stores the order in page private data, and returns true. `__clear_page_guard()` clears the guard flag and resets private data.

## State And Persistence
Configuration is global and set during early boot. Static keys allow other MM paths to branch efficiently when debug page allocation or guard pages are enabled.

Guard page state is stored in page flags and page private data until cleared.

## Dependencies And Integration Points
The file depends on core MM page flags, page isolation/list definitions, static keys, and early boot parameter parsing. It is integrated into page allocator debug behavior through externally referenced symbols and `debug_guardpage_minorder()`.

## Risks And Edge Cases
Invalid `debug_guardpage_minorder` values are logged and ignored by returning `0` from the early parameter handler. `__set_page_guard()` does not touch zone accounting directly in this file; callers must handle surrounding allocator state correctly.

The order comparison means only orders strictly below the configured minimum become guard pages. Misunderstanding that threshold can disable more or fewer guard pages than expected.

## Test Signals
No direct tests are present here. Validation is mostly via boot-parameter behavior, allocator debug configurations, and runtime page allocator assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/debug_page_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/debug_page_ref.c -->
# sources/distributed-fs/ceph-client/mm/debug_page_ref.c

## Purpose
This file provides exported wrapper functions for page reference-count tracepoints. It creates tracepoints for `trace/events/page_ref.h` and exposes helper symbols that page reference manipulation code can call when debug page reference tracing is enabled.

## Important APIs, Types, And Functions
`CREATE_TRACE_POINTS` instantiates the page_ref tracepoints. The exported functions are `__page_ref_set()`, `__page_ref_mod()`, `__page_ref_mod_and_test()`, `__page_ref_mod_and_return()`, `__page_ref_mod_unless()`, `__page_ref_freeze()`, and `__page_ref_unfreeze()`.

Each function forwards its arguments to the corresponding `trace_page_ref_*()` event and exports both the function and the tracepoint symbol where applicable.

## Control Flow
There is no branching or stored state. Each wrapper is called by page reference accounting code, emits a trace event with the page and operation values, and returns.

## State And Persistence
The file maintains no private state. Observability is provided through kernel tracing infrastructure; persistence depends on active trace buffers and user-space tracing tools.

## Dependencies And Integration Points
It depends on `linux/mm_types.h`, `linux/tracepoint.h`, and `trace/events/page_ref.h`. It integrates with page reference manipulation instrumentation and kernel tracepoint consumers.

## Risks And Edge Cases
Because these wrappers are instrumentation hooks, their correctness is mostly signature and tracepoint alignment. Adding or changing trace event fields must be reflected in these wrappers. Trace overhead depends on tracing enablement and static-key behavior in the tracing subsystem.

## Test Signals
No local tests are present. Build-time tracepoint generation and runtime ftrace/perf/tracefs observation are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/debug_page_ref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/debug_vm_pgtable.c -->
# sources/distributed-fs/ceph-client/mm/debug_vm_pgtable.c

## Purpose
This file is a late-boot self-test for architecture page-table helper semantics. It validates that generic and architecture-specific PTE/PMD/PUD/P4D/PGD helpers satisfy expectations documented in `Documentation/mm/arch_pgtable_helpers.rst`.

It is not a KUnit test; it runs via `late_initcall(debug_vm_pgtable)` and emits `WARN_ON()` failures when helpers violate expected behavior.

## Important APIs, Types, And Functions
`struct pgtable_debug_args` holds a synthetic `mm_struct`, VMA, page-table pointers, allocated lower-level page-table pages, test virtual address, page protections, test PFNs, fixed physical PFNs, swap entries, and allocation bookkeeping.

Test functions cover:

- Basic present entry transforms: `pte_basic_tests()`, `pmd_basic_tests()`, `pud_basic_tests()`, `p4d_basic_tests()`, `pgd_basic_tests()`.
- Advanced set/clear/access operations: `pte_advanced_tests()`, `pmd_advanced_tests()`, `pud_advanced_tests()`.
- Clear/populate operations: `pte_clear_tests()`, `pmd_clear_tests()`, `pmd_populate_tests()`, `pud_clear_tests()`, `pud_populate_tests()`, `p4d_clear_tests()`, `p4d_populate_tests()`, `pgd_clear_tests()`, `pgd_populate_tests()`.
- Huge/leaf/THP/HugeTLB behavior: `pmd_leaf_tests()`, `pud_leaf_tests()`, `pmd_huge_tests()`, `pud_huge_tests()`, `pmd_thp_tests()`, `pud_thp_tests()`, `hugetlb_basic_tests()`.
- Special encodings: `pte_special_tests()`, protnone tests, soft-dirty tests, swap exclusive tests, swap conversion tests, softleaf/THP migration tests, and `swap_migration_tests()`.

Setup and teardown are handled by `init_args()`, `init_fixed_pfns()`, `debug_vm_pgtable_alloc_huge_page()`, `debug_vm_pgtable_free_huge_page()`, `destroy_args()`, `phys_align_check()`, and `get_random_vaddr()`.

## Control Flow
`debug_vm_pgtable()` initializes a synthetic MM/VMA and page-table hierarchy, allocates representative pages where possible, then runs basic tests for all protection flag combinations from `VM_NONE` through `VM_SHARED | VM_EXEC | VM_WRITE | VM_READ`.

It then runs non-iterated tests for upper-level same checks, leaf/huge/protnone/soft-dirty/swap/migration/THP/HugeTLB semantics. Modifying tests are grouped under the proper page-table lock: PTE lock for PTE clear/advanced tests, PMD lock for PMD operations, PUD lock for PUD operations, and `mm->page_table_lock` for P4D/PGD operations. Finally it calls `destroy_args()` to clear entries, free allocated table pages, free huge/normal pages, free VMA, and `mmput()` the synthetic mm.

Many tests are compiled out or return early depending on configuration and runtime support: transparent huge pages, PUD THP, huge vmap, HugeTLB, soft dirty, migration, folded page-table levels, and NUMA balancing.

## State And Persistence
The test uses transient synthetic MM state and allocated pages. It writes test entries into the allocated page tables and clears them before teardown. It also uses a random user virtual address for the test hierarchy and fixed valid PFNs derived from memblock ranges or `start_kernel` physical address for helpers that need existing physical addresses but do not dereference memory.

No persistent state is kept after the late initcall completes, except warnings/logs if failures occur.

## Dependencies And Integration Points
The file depends on a broad set of MM and architecture APIs: pgtable helper macros, pte/pmd/pud/p4d/pgd allocation and locking, THP, HugeTLB, huge vmap, swap encoding, migration entries, memblock ranges, cache/TLB flushing, vmalloc, and folded-level helpers.

It is tightly coupled to architecture page-table definitions and serves as a cross-architecture compliance guard for generic MM assumptions.

## Risks And Edge Cases
Because it runs at late init, failures surface as warnings during boot rather than structured test results. Allocations can fail; some tests silently skip when required pages or features are unavailable, reducing coverage on constrained systems.

The test intentionally uses valid but sometimes not allocated fixed PFNs for helpers that should not touch memory. Architecture helper changes that begin dereferencing these PFNs could turn semantic tests into real memory hazards.

Cache flushing after setting entries is needed for arm64 `PG_arch_1` behavior; future architecture-specific side effects may require similar care. The migration test manually sets and clears `PageLocked` around migration-entry construction; mistakes there can trigger BUG_ON paths.

## Test Signals
The file is itself a boot-time self-test. Passing means no `WARN_ON()` fired during `debug_vm_pgtable()`. It complements KUnit by exercising architecture page-table helper contracts under real compiled configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/debug_vm_pgtable.c -->
