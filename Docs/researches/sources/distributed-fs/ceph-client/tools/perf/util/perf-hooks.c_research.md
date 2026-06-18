
# sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks.c

Purpose: implements a lightweight runtime hook registry for selected perf lifecycle points, with recovery from hook-triggered segmentation faults.

Important APIs/types/functions: `perf_hooks__invoke` calls a hook descriptor's function pointer with context if installed. `perf_hooks__recover` longjmps out of a crashing hook when signal handling routes there. X-macro expansion creates `__perf_hook_func_<name>` storage and `__perf_hook_desc_<name>` descriptors. `perf_hooks__set_hook` installs or overwrites a hook by name; `perf_hooks__get_hook` retrieves it or returns `ERR_PTR(-ENOENT)`.

Control flow: invoke uses `sigsetjmp`; normal path sets `current_perf_hook`, calls the function, then clears it. Recovery path logs a warning and disables the current hook by storing NULL. Set/get linearly scan the descriptor array generated from `perf-hooks-list.h`.

State and persistence: module globals are `jmpbuf`, `current_perf_hook`, per-hook function pointers, descriptor contexts, and the descriptor array. State persists for the process lifetime.

Dependencies: setjmp/signal recovery machinery, Linux `ERR_PTR`, array-size helpers, debug logging, and the hook list header.

Integration points: external scripts/plugins or tests can set hooks for `record_start`, `record_end`, and `test`; callers use inline `perf_hooks__invoke_<name>` wrappers from the header.

Risks: global state is not thread-safe; concurrent hook invocation/set could race. Recovery only helps when signal handling calls `perf_hooks__recover`. Longjmp from signal context is delicate. Test signals include hook install/get/invoke tests, overwrite warning checks, test hook coverage, and fault-injection recovery where supported.
