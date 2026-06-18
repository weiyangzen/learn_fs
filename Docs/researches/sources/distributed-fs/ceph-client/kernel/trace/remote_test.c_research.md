# sources/distributed-fs/ceph-client/kernel/trace/remote_test.c

## Purpose
`remote_test.c` is a test module for the trace remote interface. It registers a remote tracing producer named `test`, backs the remote trace buffer with per-CPU `simple_ring_buffer` instances, and exposes a tracefs write hook that injects a synthetic remote event.

## Important APIs, types, and functions
Important state is `remote_test_buffer_desc`, per-CPU `simple_rbs`, and `simple_rbs_lock`. Main callbacks are `remote_test_load()`, `remote_test_unload()`, `remote_test_enable_tracing()`, `remote_test_swap_reader_page()`, `remote_test_reset()`, `remote_test_enable_event()`, and `remote_test_init_tracefs()`. The event write path is `write_event_write()`, which reserves `struct remote_event_format_selftest` and commits it to the current CPU simple ring buffer.

## Control flow
`remote_test_init()` calls `trace_remote_register("test", ...)` with the generated `remote_event_selftest` descriptor. When trace remote requests a buffer, `remote_test_load()` allocates a `trace_buffer_desc`, calls `trace_remote_alloc_buffer()`, and builds one `simple_ring_buffer` per descriptor CPU. Unload tears down the simple buffers, frees the remote descriptor, and clears the global pointer. A user write to tracefs `write_event` parses an integer, checks that the selftest event is enabled, disables preemption, reserves space in the current CPU simple ring buffer, fills the remote event id and payload id, then commits.

## State and persistence
The loaded buffer descriptor and per-CPU simple buffers are runtime-only. `simple_rbs_lock` serializes test writes against load/unload, while trace remote serializes its own callbacks. Event enablement uses the generated remote event's `enabled` field and is explicitly noted as racy but sufficient for this test module.

## Dependencies and integration points
The file depends on `trace_remote`, `tracefs`, `simple_ring_buffer`, generated remote event definitions, per-CPU storage, and `trace_clock_global()`. It integrates with the trace remote control plane via `struct trace_remote_callbacks` and with user tests through a tracefs file that writes synthetic events.

## Risks and test signals
Risks include races between write paths and module unload, incomplete cleanup after partial per-CPU allocation failure, rejecting writes when the event or CPU buffer is not enabled, and misuse of this intentionally simple enable-event implementation as production policy. Test signals include successful remote buffer load/unload cycles, per-CPU simple ring buffer creation, `write_event` producing decodable `selftest` records, reset/swap callbacks changing reader state, and clean failure on disabled event or missing buffer.
