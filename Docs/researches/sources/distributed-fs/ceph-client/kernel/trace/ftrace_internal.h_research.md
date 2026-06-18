# sources/distributed-fs/ceph-client/kernel/trace/ftrace_internal.h

## Purpose

`ftrace_internal.h` is the private interface shared by function tracing implementation files. It declares registration helpers, dynamic ftrace lifecycle hooks, subops APIs, the global ftrace mutex and global ops object, and graph-tracer state hooks while hiding configuration differences behind small inline fallbacks.

## Important APIs, Types, and Functions

- Always-declared internal registration helpers: `__register_ftrace_function()` and `__unregister_ftrace_function()`.
- Under `CONFIG_FUNCTION_TRACER`, shared globals `ftrace_lock` and `global_ops`.
- Under `CONFIG_DYNAMIC_FTRACE`, prototypes for `ftrace_startup()`, `ftrace_shutdown()`, `ftrace_ops_test()`, `ftrace_startup_subops()`, and `ftrace_shutdown_subops()`.
- Without dynamic ftrace, macro fallbacks call the low-level register/unregister helpers directly, set or clear `FTRACE_OPS_FL_ENABLED`, make `ftrace_ops_test()` always succeed, and reject subops with `-EINVAL`.
- Under `CONFIG_FUNCTION_GRAPH_TRACER`, it exposes `ftrace_graph_active` and, for dynamic ftrace, `fgraph_update_pid_func()`. Without graph tracing, these collapse to zero/no-op definitions.

## Control Flow

The header selects the correct ftrace lifecycle contract at compile time. Dynamic builds call into the full record-patching engine in `ftrace.c`, where ops registration updates filter hashes and machine code. Non-dynamic builds skip callsite patching and directly insert/remove callbacks from the ftrace ops list via `__register_ftrace_function()` and `__unregister_ftrace_function()`. Graph PID integration is similarly conditional: dynamic graph builds update graph callbacks when PID filtering changes; non-graph builds avoid any graph dependency.

## State and Persistence Behavior

This header owns no storage except extern declarations. Its effect on state is indirect: the non-dynamic macros mutate `ops->flags`, while dynamic prototypes route callers to the full state machine in `ftrace.c`. The header's configuration gates make callers compile against a stable API even when underlying state such as `dyn_ftrace` records, graph activity, or subops lists does not exist.

## Dependencies and Integration Points

It depends on definitions from ftrace public/internal kernel headers that provide `struct ftrace_ops`, flags, and graph state. It is included by tracing internals that need ftrace startup/shutdown without depending on all dynamic implementation details. Its prototypes are implemented primarily in `ftrace.c` and consumed by function graph and trace-array setup paths.

## Risks and Edge Cases

- The non-dynamic `ftrace_startup()`/`ftrace_shutdown()` macros deliberately bypass dynamic record filtering, so callers must not assume filter hashes or subops behavior exists in non-dynamic builds.
- Subops callers must handle `-EINVAL` when `CONFIG_DYNAMIC_FTRACE` is off.
- `ftrace_ops_test()` always returns true without dynamic ftrace, so any caller that expects hash-based filtering must be configuration-aware.

## Test Signals

Compile coverage across `CONFIG_FUNCTION_TRACER`, `CONFIG_DYNAMIC_FTRACE`, and `CONFIG_FUNCTION_GRAPH_TRACER` combinations is the main signal. Runtime checks include successful register/unregister paths in non-dynamic builds and graph PID updates becoming no-ops when graph tracing is disabled.
