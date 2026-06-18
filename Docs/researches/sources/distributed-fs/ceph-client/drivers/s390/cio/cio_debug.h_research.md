# sources/distributed-fs/ceph-client/drivers/s390/cio/cio_debug.h

## Purpose
This header centralizes CIO debug-feature handles and logging macros for message, trace, and channel-report-word diagnostics, and declares the shared CIO debugfs directory.

## Important APIs, Types, and Functions
It declares `cio_debug_msg_id`, `cio_debug_trace_id`, `cio_debug_crw_id`, `cio_debugfs_dir`, and macros `CIO_TRACE_EVENT()`, `CIO_MSG_EVENT()`, `CIO_CRW_EVENT()`, plus inline `CIO_HEX_EVENT()`. These wrap the s390 `debug_*` APIs.

## Control Flow
The macros emit text, sprintf, or hex trace records to debug-feature buffers initialized in `cio.c`. There is no independent control flow in the header.

## State and Persistence
State lives in debug-feature buffers and the debugfs dentry created elsewhere. Logs are in-memory kernel debug data, not persistent storage.

## Dependencies and Integration Points
It depends on `<asm/debug.h>` and is included by most CIO/CHSC/CSS/channel-path files. `cio_debugfs_dir` is used by debugfs feature files such as CRW injection.

## Risks and Test Signals
Risk areas include logging before debug areas are initialized, null debug handles on init failure, and format-string mismatch in variadic macros. Test signals include boot-time debug area creation, trace visibility under `/sys/kernel/debug/s390`, CRW/event logging, and builds with debug feature support.
