# sources/distributed-fs/openafs/src/opr/opr.h

Purpose: main public OPR header aggregating common macros, assertions, string helpers, thread-name API, and cache API.

Important APIs/types/functions: defines `opr_containerof`, stringization macros, `opr_abort`, `opr_min`, `opr_max`, `opr_Assert`, `opr_Verify`, and `opr_StaticAssert`. Declares `opr_AssertionFailed`, case-string helpers, `opr_threadname_set`, `struct opr_cache_opts`, opaque `struct opr_cache`, and cache operations.

Control flow: assertion macros call `opr_AssertionFailed` when expressions fail; `opr_Verify` guarantees expression evaluation. In non-pthread/NT contexts `opr_threadname_set` is inline no-op.

State and persistence: no header-owned state. Cache state is owned by cache implementation.

Dependencies/integration: installed as `afs/opr.h` and included widely across OpenAFS. It bridges OPR implementation files and callers.

Risks and test signals: macros evaluate operands multiple times for `opr_min`/`opr_max`. Assertions may be used in paths where abort behavior matters. Compile coverage across C dialects and platforms is important.
