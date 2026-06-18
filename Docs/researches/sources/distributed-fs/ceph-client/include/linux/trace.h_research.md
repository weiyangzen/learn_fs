# sources/distributed-fs/ceph-client/include/linux/trace.h

## Purpose
Declares high-level tracing interfaces for exporting ftrace output, writing to trace arrays, creating/destroying trace instances, and controlling osnoise hooks.

## Important APIs, Types, And Functions
`struct trace_export` links export targets and provides a `write()` callback for trace data. Public APIs under `CONFIG_TRACING` include `register_ftrace_export()`, `unregister_ftrace_export()`, `trace_array_puts()`, `trace_array_printk()`, `trace_array_init_printk()`, `trace_array_get_by_name()`, `trace_array_destroy()`, and osnoise registration/IRQ entry/exit hooks.

## Control Flow
When tracing is enabled, producers write constant strings or formatted data into a `trace_array`; export targets can be registered so committed trace records are delivered beyond the ring buffer. When tracing is disabled, inline stubs return neutral failures or no-ops, allowing callers to compile without runtime tracing.

## State, Persistence, And Dependencies
The header defines only interfaces. Runtime state lives in `trace_array`, registered export lists, and trace buffers managed by tracing core. It depends on `BIT()` being available to consumers and forward-declares `struct trace_array`.

## Integration Points
Integrates ftrace, trace instances, trace_printk initialization, and osnoise tracer architecture hooks. Export flags distinguish functions, events, and markers.

## Risks And Test Signals
Risks include export callbacks running in sensitive contexts, stale export registration, trace-array lifetime mistakes, and config-disabled stubs masking missing tracing behavior. Test signals include registration/unregistration races, writing into named trace arrays, disabled-config builds, and osnoise tracer entry/exit accounting.
