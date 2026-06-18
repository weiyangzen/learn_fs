# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log.h

## Purpose
Declares GuC log APIs and compile-time log buffer sizing for debug, crash dump, and state capture data.

## Important APIs, Types, And Functions
Defines per-build buffer sizes, aggregate `GUC_LOG_SIZE`, offsets for event/crash/state capture areas, log-level conversion macros, and public init/print/snapshot/overflow APIs. It also provides inline `xe_guc_log_get_level`.

## Control Flow
Callers initialize the log object, use print or snapshot APIs to inspect it, and call overflow checking when GuC reports buffer-full counters. Log level macros translate between driver log levels and GuC verbosity fields.

## State And Persistence
State is in `struct xe_guc_log` from the types header. Buffer size choices persist for the compiled kernel configuration.

## Dependencies And Integration Points
Includes GuC log ABI and log type definitions. Used by GuC load parameter construction, debugfs, devcoredump, and overflow monitoring.

## Risks And Test Signals
Size and offset constants must match firmware expectations and control dword encoding. Build variants change memory footprint substantially. Tests should cover log-level conversions and ensure offsets remain contiguous within `GUC_LOG_SIZE`.
