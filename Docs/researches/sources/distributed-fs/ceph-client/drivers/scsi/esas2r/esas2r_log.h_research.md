<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.h

## Purpose

`esas2r_log.h` is the public logging interface for the ESAS2R driver. It defines the ESAS2R log-level enum, declares checked printf-style logging functions, and provides compile-time debug and trace macros used throughout the driver.

## Important APIs, Types, and Definitions

The level enum defines `ESAS2R_LOG_NONE`, `CRIT`, `WARN`, `INFO`, `DEBG`, and `TRCE`. `ESAS2R_LOG_DFLT` is `TRCE` when `ESAS2R_TRACE` is defined and `WARN` otherwise. Exported declarations are `esas2r_log()`, `esas2r_log_dev()`, and `esas2r_log_hexdump()`.

When `ESAS2R_DEBUG` is enabled, `esas2r_debug()` and `esas2r_hdebug()` call `esas2r_log(ESAS2R_LOG_DEBG, ...)`; otherwise they compile away. When `ESAS2R_TRACE` is enabled, `esas2r_bugon()` logs a trace message, dumps the stack, and calls `BUG()`, while `esas2r_trace_enter()`, `esas2r_trace_exit()`, and `esas2r_trace()` include function, file, and line metadata. Without tracing these macros also compile away.

## Control Flow

This header has no runtime control flow by itself, but it controls instrumentation compiled into other ESAS2R files. Debug builds route extra messages through `esas2r_log.c`; trace builds add function-entry/exit calls and make `esas2r_bugon()` fatal. Normal builds remove these calls at preprocessing time, which keeps fast paths and interrupt paths free of debug logging overhead.

## State and Persistence Behavior

There is no state in the header. The main behavioral state is the build configuration: `ESAS2R_DEBUG` and `ESAS2R_TRACE` determine whether macro call sites exist in the compiled driver, while `event_log_level` in `esas2r_log.c` determines runtime emission for compiled-in calls.

## Dependencies and Integration Points

The header forward declares `struct device` and relies on kernel `__printf` annotations. It is included by `esas2r.h`, which is then included across the ESAS2R driver. This means changes to macro behavior affect ioctl, target discovery, request completion, interrupt, and reset paths.

## Risks and Edge Cases

Trace builds are intentionally intrusive: `esas2r_bugon()` becomes a stack-dumping `BUG()` and trace logging may heavily affect timing. Because debug/trace macros compile away in normal builds, code must not rely on macro arguments having side effects. The default log level changes between trace and non-trace builds, so reproducing log volume requires knowing build flags as well as module parameters.

## Test Signals

Useful checks include building with and without `ESAS2R_DEBUG` and `ESAS2R_TRACE`, verifying no side-effect dependencies in macro arguments, confirming compile-time format checking on logging declarations, checking default log level in each build mode, and validating that trace call sites do not break performance-sensitive request or interrupt paths when enabled for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.h -->
