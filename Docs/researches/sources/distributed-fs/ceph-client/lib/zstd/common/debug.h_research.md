# sources/distributed-fs/ceph-client/lib/zstd/common/debug.h

Purpose: Defines zstd debug/assertion macros: compile-time assertions, optional runtime assertions, and optional debug/raw logging.

Important APIs/macros:
- `DEBUG_STATIC_ASSERT(c)` for compile-time checks inside functions.
- `DEBUGLEVEL` defaulting to 0.
- `assert(condition)` integration through `zstd_deps.h` when `DEBUGLEVEL >= 1`; otherwise disabled if not already defined.
- `RAWLOG(l, ...)` and `DEBUGLOG(l, ...)` when `DEBUGLEVEL >= 2`, backed by global `g_debuglevel`.

Control flow:
- Preprocessor selects no-op or active assertion/logging behavior.
- Active logging routes to `ZSTD_DEBUG_PRINT`, which the kernel dependency layer maps to `pr_debug`.

State and persistence:
- Header itself has no state; for debug level >=2 it declares external `g_debuglevel`.

Dependencies and integration:
- Includes `zstd_deps.h` only for enabled assert/logging support.
- Used throughout zstd/FSE/HUF code.

Risks:
- Assertions are compiled out at default level, so correctness cannot depend on them.
- Variadic logging macros must remain syntactically valid when disabled.
- High debug levels in kernel can be costly and noisy.

Test signals:
- Build with `DEBUGLEVEL=0`, `1`, and `2+`.
- Trigger a debug log path and verify `pr_debug` formatting.
