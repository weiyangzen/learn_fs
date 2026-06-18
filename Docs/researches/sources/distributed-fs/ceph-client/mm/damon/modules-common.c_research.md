# sources/distributed-fs/ceph-client/mm/damon/modules-common.c

Purpose: Provides shared helper code for DAMON policy modules.

Important APIs, types, and functions: `damon_modules_new_paddr_ctx_target()` allocates a `damon_ctx`, selects `DAMON_OPS_PADDR`, allocates a target, attaches it to the context, and returns both via output pointers.

Control flow: The helper creates a context, fails cleanly if allocation or paddr ops selection fails, creates a target, adds it to the context, then returns ownership to the caller. On target allocation failure it destroys the context.

State and persistence: No static state. It creates transient heap state that modules later own, commit, start, or destroy.

Dependencies and integration: Depends on DAMON core APIs and the physical-address operations backend having registered `DAMON_OPS_PADDR`. Used by reclaim, LRU sort, and similar modules to avoid duplicate context setup.

Risks: Returns `-EINVAL` when paddr ops are unavailable; modules must surface this as disabled/unavailable. Callers must destroy the returned context on subsequent failures to avoid leaks.

Test signals: Build modules with `DAMON_PADDR`, force allocation failures, and verify callers clean up both success and failure paths.
