# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_debug.h

Purpose: this header centralizes SPL assertion and debugger-break macros for kernel builds. It maps SPL internal invariants to Linux `WARN_ON()` behavior and, when KGDB is configured, can trigger `kgdb_breakpoint()` for critical assertions.

Important macros: `SPL_ASSERT_CRITICAL(expr)` warns on failed expressions and conditionally breaks into KGDB. `SPL_ASSERT(expr)` maps to critical assertions only when `CONFIG_DEBUG_KERNEL_DC` is enabled; otherwise it is a plain `WARN_ON(!(expr))`. `SPL_BREAK_TO_DEBUGGER()` is implemented as `SPL_ASSERT(0)`.

Control flow and state: there is no persistent state. Failed assertions affect control only through warnings and optional debugger breakpoints; most callers continue executing unless the debugger stops the system. Many scaler helpers use these macros for impossible tap counts, overflow checks, and packing validation.

Dependencies and integration: this file assumes Linux warning/debug symbols are available through including contexts; `spl_os_types.h` includes Linux kernel headers and also includes this header. It is used by fixed-point math, custom float packing, and filter selectors.

Risks and tests: because assertions are warnings in non-debug builds, callers must not rely on them for input sanitization. Code paths often return fallback values after `SPL_BREAK_TO_DEBUGGER()`, so invalid inputs can still propagate `NULL` or clamped values. Build tests should cover configurations with and without KGDB and `CONFIG_DEBUG_KERNEL_DC`. Runtime tests should include invalid-input paths only in controlled debug environments to avoid unexpected breakpoints.
