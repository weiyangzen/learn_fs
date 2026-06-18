# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/trace.h

Defines bcachefs tracepoint events for persistent counters, non-counter debug events, and optional btree path tracing.

Key elements:
- `TRACE_SYSTEM bcachefs` sets the Linux trace subsystem name.
- `DECLARE_EVENT_CLASS(fs_str)` defines common trace payload: filesystem name and string message.
- `BCH_NOCOUNTER_TRACEPOINTS()` lists debug-only tracepoints such as accounting insert, journal close, extent trim, and iterator/path events.
- `__BCH_PATH_TRACEPOINTS()` lists detailed path lifecycle/locking tracepoints.
- `BCH_PATH_TRACEPOINTS()` expands only when `CONFIG_BCACHEFS_PATH_TRACEPOINTS` is enabled.
- For disabled path tracepoints, inline no-op `trace_*()` and `trace_*_enabled()` stubs are provided.
- `BCH_PERSISTENT_COUNTERS()` also becomes trace events using the shared `fs_str` event class.

Important invariants:
- The trace include path/file block must remain outside the include guard per Linux tracepoint conventions.
- Disabled path tracepoints must compile away while preserving call-site availability.

Filesystem relevance:
- This header is bcachefs’s lightweight observability hook set for counters, journal/btree activity, and optional path-level btree tracing.
