# sources/distributed-fs/ceph-client/lib/zstd/common/debug.c

Purpose: Provides the optional global zstd debug verbosity variable when runtime debug logging is compiled in.

Important APIs/state:
- Defines `int g_debuglevel = DEBUGLEVEL` when `DEBUGLEVEL >= 2`.

Control flow: No functions. Conditional definition prevents an empty translation unit issue in non-kernel upstream contexts; in this kernel copy it only emits state for debug builds.

State and persistence:
- `g_debuglevel` is global mutable process/kernel state for zstd debug logging and is not thread-safe.

Dependencies and integration:
- Includes `debug.h`, whose `RAWLOG` and `DEBUGLOG` macros reference `g_debuglevel` when enabled.
- Built into `zstd_common.o`.

Risks:
- Runtime modification affects all zstd users globally.
- Debug logging at high levels can be very verbose and expensive.

Test signals:
- Build with default `DEBUGLEVEL=0` and with `DEBUGLEVEL>=2`.
- Confirm `DEBUGLOG` compiles and emits through kernel debug print hooks when enabled.
