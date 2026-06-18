# sources/distributed-fs/orangefs/src/common/gossip/gossip.h

Purpose: Public declarations and macros for OrangeFS logging.

Important APIs/types: Declares global debug state, buffer size, timestamp enum, facility control functions, debug/error functions, and `gossip_backtrace()`. Provides kernel-mode simplified macros and user-mode GCC/non-GCC macro variants. `gossip_debug_enabled()`, `gossip_debug()`, `gossip_perf_log()`, `gossip_ldebug()`, and `gossip_lerr()` are the main call-site APIs.

Control flow contract: Call sites normally use macros, which avoid function-call overhead when debugging is disabled. Error macros always call `gossip_err()` and, on GCC user-mode builds, `gossip_lerr()` also emits a backtrace.

State/persistence: Header exposes global variables for direct reads/writes by macros and possibly callers.

Dependencies/integration: Includes `pvfs2-config.h`, syslog on POSIX user builds, and `wincommon.h` on Windows. Performance logging depends on `GOSSIP_PERFCOUNTER_DEBUG` being defined elsewhere.

Risks: Macro syntax differs by compiler/Windows branch and may hide format-checking differences. Direct global exposure makes it easy to bypass setters. Kernel and user semantics differ significantly.

Test signals: Compile with GCC, non-GCC, Windows, kernel, `GOSSIP_DISABLE_DEBUG`, and performance-counter configurations.
