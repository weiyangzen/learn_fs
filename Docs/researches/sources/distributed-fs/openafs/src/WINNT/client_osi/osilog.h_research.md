<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osilog.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osilog.h

Purpose: Declares the OSI logging data structures, fd cursor, logging functions, event helpers, debug macros, and convenience macros for 0-to-5 parameter log entries.

Important APIs, types, and functions: `osi_logEntry_t` stores thread id, microsecond timestamp, format pointer, and five `size_t` parameters. `osi_log_t` is a named circular log with queue linkage, counters, critical section, entry storage, rotating string storage, and enabled flag. `osi_logFD_t` snapshots a log for remote iteration. Exports include create/free/add/debug/reset/print/enable/disable, fd operations, panic logging, string saving, trace option init, event logging, and `osi_HexifyString`. `osi_Log0` through `osi_Log5` guard on enabled logs; `osi_Debug0` through `osi_Debug5` always call the debug path.

Control flow and state: Callers create a log, enable it, and use macros to append. String parameters that might not outlive the log call can be stored in the log string pool first. Remote debugging opens the log fd type registered by `osi_LogCreate`.

Persistence and dependencies: In-memory ring by default; printing and Event Log calls are implemented in `osilog.c`. The header depends on aggregate OSI headers for sleep, base locks, stats, fd, queue, and thread handle types.

Integration points: Used throughout Windows client code for debug traces and by stats/panic code for instrumentation. The `DEBUG_EVENT*` macros provide compile-time optional Event Log traces under `DEBUG_VERBOSE`.

Risks: The macro API casts all parameters to `size_t`, so pointer/integer formatting must match the format string and platform width. Debug macros do not check for null logs in the macro itself but the implementation does. `DEBUG_EVENT*` macros use fixed local buffers and `sprintf` under `DEBUG_VERBOSE`.

Test signals: Compile 32/64-bit format cases, verify macro parameter ordering, confirm disabled logs skip `osi_LogAdd`, and test `DEBUG_VERBOSE` builds for Event Log path correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osilog.h -->
