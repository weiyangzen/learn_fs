# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_trace.h

## Purpose
Defines Panthor tracepoints for GPU power-status transitions and job IRQ latency/event visibility.

## Important APIs, Types, and Functions
Trace system is `panthor`. `TRACE_EVENT_FN(gpu_power_status, ...)` records device name and shader/tiler/L2 power bitmaps and registers callbacks via `panthor_hw_power_status_register/unregister`. `TRACE_EVENT(gpu_job_irq, ...)` records firmware job IRQ event mask and handler duration in nanoseconds.

## Control Flow
When tracing is enabled, registration hooks can subscribe to hardware power-status updates. Job IRQ instrumentation emits a compact event after the IRQ handler has queued firmware events, letting developers distinguish interrupt dispatch latency from later workqueue processing.

## State and Persistence
Tracepoints persist only in the kernel tracing subsystem. They do not mutate driver state. Captured state is a snapshot of bitmaps, event masks, duration, and device name.

## Dependencies and Integration Points
Depends on Linux tracepoint infrastructure and `panthor_hw.h` callback hooks. Uses standard `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` pattern so exactly one translation unit can instantiate trace definitions.

## Risks and Edge Cases
Tracepoint field definitions must remain stable enough for tooling. The power tracepoint has registration side effects, so callback correctness matters. Job IRQ duration only covers the IRQ queuing path, not full firmware event processing.

## Test Signals
Build with tracing enabled, inspect generated trace events, enable `panthor:gpu_power_status` and `panthor:gpu_job_irq`, verify power bitmap updates and job IRQ duration/event masks during workload and runtime PM transitions.
