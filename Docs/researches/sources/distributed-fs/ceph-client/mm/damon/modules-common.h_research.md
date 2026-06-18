# sources/distributed-fs/ceph-client/mm/damon/modules-common.h

Purpose: Declares shared module helpers and macro families for defining DAMON module parameters consistently.

Important APIs and macros: `DEFINE_DAMON_MODULES_MON_ATTRS_PARAMS()` exposes monitoring intervals and region limits. `DEFINE_DAMON_MODULES_DAMOS_TIME_QUOTA()` and `DEFINE_DAMON_MODULES_DAMOS_QUOTAS()` expose quota knobs. `DEFINE_DAMON_MODULES_WMARKS_PARAMS()` exposes watermark thresholds. `DEFINE_DAMON_MODULES_DAMOS_STATS_PARAMS()` exposes read-only tried/applied/quota-exceed stats. It declares `damon_modules_new_paddr_ctx_target()`.

Control flow: The macros expand at file scope in modules, binding fields of static DAMON structs to module parameters with appropriate permissions.

State and persistence: No direct runtime state, but macro expansion exposes module state to userspace. Writable params are generally mode `0600`; stats are `0400`.

Dependencies and integration: Depends on `linux/moduleparam.h` and DAMON struct definitions from including C files. Used by reclaim, lru_sort, and stat-style modules.

Risks: Macro users must provide correctly typed lvalues; field renames in DAMON structs require synchronized macro updates. Permissions determine operational safety because writable knobs affect live memory policy after commit.

Test signals: Compile modules using each macro, inspect generated module params, verify permissions, and confirm stats fields map to expected counters.
