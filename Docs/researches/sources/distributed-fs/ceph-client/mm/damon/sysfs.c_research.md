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
