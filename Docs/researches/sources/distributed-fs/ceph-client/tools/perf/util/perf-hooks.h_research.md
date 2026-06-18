
# sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks.h

Purpose: declares the perf hook descriptor API and generates inline invokers for every hook in `perf-hooks-list.h`.

Important APIs/types/functions: `perf_hook_func_t` is a `void (*)(void *ctx)`. `struct perf_hook_desc` stores hook name, pointer to the installed function pointer, and context. Declares `perf_hooks__invoke`, `perf_hooks__recover`, `perf_hooks__set_hook`, and `perf_hooks__get_hook`. X-macro expansion declares external descriptors and defines `perf_hooks__invoke_record_start`, `perf_hooks__invoke_record_end`, and `perf_hooks__invoke_test`.

Control flow: inline invokers pass the generated descriptor to the generic invoke function.

State and persistence: descriptors/function storage are defined in `perf-hooks.c`; this header exposes references only.

Dependencies: C++ compatibility guards and the hook list header.

Integration points: included by code that invokes or registers hooks. It keeps hook declarations synchronized with the central list.

Risks: public inline functions change when the hook list changes. `perf_hooks__get_hook` can return `ERR_PTR`, so callers must not blindly call the result. Test signals are compile/link coverage and hook registration/invocation tests.
