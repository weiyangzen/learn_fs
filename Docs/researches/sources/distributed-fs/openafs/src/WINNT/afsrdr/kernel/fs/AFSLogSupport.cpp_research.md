# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLogSupport.cpp

## Purpose
`AFSLogSupport.cpp` implements the kernel trace ring buffer, runtime trace configuration, trace-buffer export, trace dump-file writing, and dump support buffer allocation for the fs layer. It provides `AFSDbgLogMsg`, the callback passed to the library driver.

## Important APIs, Control Flow, And State
`AFSDbgLogMsg` filters by `AFSTraceComponent` and `AFSTraceLevel`, serializes on `AFSDbgLogLock`, writes a monotonically numbered prefix into `AFSDbgBuffer`, wraps when space is low or formatting overflows, sets `AFS_DBG_LOG_WRAPPED`, and optionally mirrors to the debugger under `AFS_DBG_TRACE_TO_DEBUGGER`. `AFSInitializeDbgLog` allocates the nonpaged circular buffer when `AFSDbgBufferLength > 0`, installs `AFSDebugTraceFnc`, and tags the initial timestamp entry; `AFSTearDownDbgLog` frees it.

`AFSConfigureTrace` updates level, subsystem, debug flags, and buffer length, persists changes through `AFSUpdateRegistryParameter`, clamps buffer length to `AFS_DBG_LOG_MAXLENGTH`, reallocates the ring buffer, and calls `AFSConfigLibraryDebug` so the library sees the current callback. `AFSGetTraceConfig` reports globals; `AFSGetTraceBuffer` copies wrapped tail then head into a caller buffer. `AFSTagInitialLogEntry` records local time. `AFSDumpTraceFiles` opens `AFSDumpFileLocation`, serializes on `AFSDumpFileEvent`, creates a timestamped log file under that directory, and writes the current trace buffer using `AFSDumpBuffer`. `AFSInitializeDumpFile` allocates the dump filename buffer and a 64 KiB paged dump staging buffer.

## Dependencies And Integration Points
The file depends on resource locking wrappers, pool allocation wrappers, registry helpers, file I/O (`ZwCreateFile`, `ZwWriteFile`), local time conversion, global dump location set during redirector initialization, and the library-debug IOCTL path. It exports trace state to user/service IOCTL paths via `AFSGetTraceConfig` and `AFSGetTraceBuffer`.

## Risks And Test Signals
Trace formatting uses a `va_list` twice on overflow without restarting it, which is a portability/correctness risk. `AFSGetTraceBuffer` requires the caller length to be at least `AFSDbgBufferLength`, not just used length. Dumping reads `AFSDbgBuffer` without holding the lock across the full write, so dumps are best-effort snapshots. Tests should cover trace disabled/enabled, component and level filtering, wrap behavior, dynamic resize, registry persistence failures, library trace callback changes, dump path absence, concurrent dump serialization, and buffer export after wrap.
