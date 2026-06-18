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
