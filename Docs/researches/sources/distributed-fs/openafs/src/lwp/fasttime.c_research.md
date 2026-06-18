## sources/distributed-fs/openafs/src/lwp/fasttime.c

Purpose: Compatibility time API for LWP-era code. Historical comments describe memory-mapped kernel time, but the current implementation falls back to `gettimeofday`.

Important APIs and functions: `FT_Init`, `FT_GetTimeOfDay`, `TM_GetTimeOfDay`, `FT_AGetTimeOfDay`, and `FT_ApproxTime`. Global `FT_LastTime` stores the last successful time value, and `ft_debug` is available for diagnostics.

Control flow: `FT_Init` tracks an enum init state and returns failure for real initialization because mmap support is not implemented. `FT_GetTimeOfDay` calls `gettimeofday`, clamps microseconds into select-compatible range, and updates `FT_LastTime`. `FT_AGetTimeOfDay` returns cached time if available. `FT_ApproxTime` returns `time(0)` under pthread builds and cached seconds under LWP builds, initializing cache if needed.

State and persistence: Process-local `initState` and `FT_LastTime`. No durable state.

Dependencies and integration: Used by LWP timer and I/O manager code for timeouts and approximate time. Provides compatibility alias `TM_GetTimeOfDay`.

Risks: Cached approximate time can be stale in non-pthread builds until another exact time call occurs. `FT_Init(notReally=1)` returns success while leaving state as tried. Timezone requests are passed through to `gettimeofday`.

Test signals: Microsecond clamping, first approximate call, cached approximate call, pthread vs LWP behavior, explicit init before and after use, and error path if `gettimeofday` fails.
