# sources/compression/zstd/lib/common/debug.c

Purpose: owns the process-global debug verbosity variable used by `DEBUGLOG` and `RAWLOG` when runtime tracing is enabled.

Important symbol: `int g_debuglevel = DEBUGLEVEL`, conditionally emitted when not building a Linux kernel empty translation unit or when `DEBUGLEVEL >= 2`.

Control flow: there is no executable logic beyond global initialization. The conditional compilation avoids pedantic warnings from an empty translation unit in some kernel builds.

State and persistence: `g_debuglevel` is mutable global process state and controls debug output dynamically. It is not thread-safe.

Dependencies/integration: includes `debug.h`; macros in that header declare `extern int g_debuglevel` when `DEBUGLEVEL >= 2` and read it before printing.

Risks: global mutable verbosity can create data races if changed while other threads log. When `DEBUGLEVEL < 2`, logging macros compile away and the symbol may not exist, so external code must not depend on it unconditionally.

Test signals: build with `DEBUGLEVEL=0`, `1`, and `2+`; ensure no empty-TU warnings in kernel mode; adjust `g_debuglevel` at runtime in a debug build and verify logs appear/disappear.
