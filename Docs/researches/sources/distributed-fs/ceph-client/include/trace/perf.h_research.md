# sources/distributed-fs/ceph-client/include/trace/perf.h

Purpose: Adds perf-event probe generation for trace events when `CONFIG_PERF_EVENTS` is enabled.

Important APIs/types/functions: Redefines `__DECLARE_EVENT_CLASS`, `DECLARE_EVENT_CLASS`, `DECLARE_EVENT_SYSCALL_CLASS`, `DEFINE_EVENT`, and `DEFINE_EVENT_PRINT` to emit perf callback wrappers. Supports `__perf_count` and `__perf_task` assignment helpers and includes `stage6_event_callback.h` to populate raw event data.

Control flow: The trace generator includes the target trace header under these macro definitions. For each event class, generated perf functions reserve/populate trace event buffers and submit data to perf consumers.

State/persistence: No persistent state is owned by this header; it creates callback code that writes records into perf ring buffers.

Dependencies/integration: Conditional on `CONFIG_PERF_EVENTS`; relies on trace event call structures, event offsets, raw event structs, and perf tracing internals.

Risks: Macro redefinition order is fragile. Generated function signatures must match event prototypes exactly or trace/perf builds fail.

Test signals: Build with perf events enabled and run `perf trace`/tracepoint recording for representative generated events.
