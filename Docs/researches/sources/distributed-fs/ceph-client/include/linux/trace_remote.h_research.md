# sources/distributed-fs/ceph-client/include/linux/trace_remote.h

## Purpose
Defines the callback interface for registering a remote trace source with tracefs. A remote provider exposes trace buffers and event controls that tracefs can present like local tracing data.

## Important APIs, Types, And Functions
`struct trace_remote_callbacks` provides `init`, `load_trace_buffer`, `unload_trace_buffer`, `enable_tracing`, `swap_reader_page`, `reset`, and `enable_event`. Public APIs are `trace_remote_register()`, `trace_remote_alloc_buffer()`, and `trace_remote_free_buffer()`.

## Control Flow
A remote registers a name, callbacks, private data, and event table. Tracefs calls `init()` to extend its directory, lazily calls `load_trace_buffer()` before first buffer access, toggles writing through `enable_tracing()`, calls `swap_reader_page()` while consuming per-CPU pages, calls `reset()` on trace clear, and calls `enable_event()` for per-event toggles.

## State, Persistence, And Dependencies
Provider state is opaque through `priv`; buffer state is represented by `trace_buffer_desc`. The header depends on dcache, ring buffer, and remote-event definitions.

## Integration Points
Integrates tracefs with off-core or external tracing producers that can provide ring-buffer-compatible pages and event metadata.

## Risks And Test Signals
Risks include callback ordering mistakes, buffer lifetime errors between load/unload, stale event enable state, and per-CPU reader-page swap races. Test signals include remote registration/removal, tracefs open/close buffer lifecycle, event enable toggles, reset behavior, and multi-CPU buffer consumption.
