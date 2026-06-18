# sources/compression/zstd/lib/common/debug.h

Purpose: defines zstd/FSE debug and assertion macros. It centralizes compile-time static assertions, runtime `assert`, and optional trace printing.

Important macros/symbols: `DEBUG_STATIC_ASSERT`, `DEBUGLEVEL`, `assert`, `g_debuglevel`, `RAWLOG`, `DEBUGLOG`, stringification helpers, and dependency flags `ZSTD_DEPS_NEED_ASSERT`/`ZSTD_DEPS_NEED_IO`.

Control flow: at `DEBUGLEVEL >= 1`, real assertions are enabled through `zstd_deps.h`; otherwise `assert` is defined as a no-op if not already present. At `DEBUGLEVEL >= 2`, `g_debuglevel` is declared and `RAWLOG`/`DEBUGLOG` conditionally print through `ZSTD_DEBUG_PRINT`. Below level 2, log macros compile to empty statements.

State and persistence: the header itself has no state, but debug builds rely on the global `g_debuglevel` from `debug.c` for runtime verbosity.

Dependencies/integration: consumed across common, entropy, compression, and decompression code. It deliberately avoids pulling IO/assert dependencies unless the selected debug level requires them.

Risks: default `DEBUGLEVEL=0` removes runtime checks, so invariants must not rely on assert side effects. Global debug level is not thread-safe. Redefining `assert` can interact with prior includes; the guard avoids overriding an existing assert macro.

Test signals: compile with multiple debug levels, verify DEBUGLOG file/line formatting, assert-enabled failures in debug builds, and no extra IO dependency in release builds.
