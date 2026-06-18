# sources/distributed-fs/orangefs/src/common/events/pvfs_tau_api.h

Purpose: Public C interface for PVFS/OrangeFS TAU trace instrumentation.

Important APIs/types: Defines limits and `tau_thread_group_info` with group name, max, blocking flag, and buffer size. Declares initialization/finalization, thread start/stop, event definition, and enter/leave state functions including `va_list` variants.

Control flow contract: Call `Ttf_init()`, optionally `Ttf_thread_start()`, define event types, wrap operations with enter/leave calls, then call `Ttf_finalize()`.

State/persistence: The header itself holds no state but its API drives TAU trace file creation and per-thread event state in `pvfs_tau_api.c`.

Dependencies/integration: C++ compatible `extern "C"`, includes `<stdarg.h>` and TAU writer definitions for handle/integer types.

Risks: API names are generic `Ttf_*` and may collide with TAU/trace naming. It exposes varargs functions without compile-time format checking. `tau_thread_group_info.name` is only 20 bytes.

Test signals: Compile C and C++ instrumentation callers, and verify event enter/leave calls produce matching TAU records.
