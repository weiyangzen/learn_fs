# sources/distributed-fs/ceph-client/tools/verification/rv/src/trace.c

Purpose: `trace.c` provides tracefs/libtraceevent lifecycle and event-collection helpers for `rv mon --trace`.

Important functions: `create_instance()` wraps `tracefs_instance_create()`. `destroy_instance()` destroys and frees a tracefs instance. `collect_registered_events()` checks `should_stop()`, ignores events without handlers, and invokes registered event handlers with the shared `trace_seq`. `trace_instance_init()` allocates a sequence buffer, creates a trace instance, loads local events with `tracefs_local_events()`, and leaves tracing off. `trace_instance_start()` enables tracing; `trace_instance_destroy()` frees all components.

Control flow and integration: `in_kernel.c` initializes a trace instance, enables specific RV events, registers handlers on the `tep_handle`, turns tracing on, and iterates raw events. Cleanup destroys the trace instance and TEP data.

State and dependencies: state is held in `struct trace_instance`. Dependencies are libtracefs, libtraceevent, and tracefs permissions. Risks include `trace_instance_start()` currently being bypassed in favor of direct `tracefs_trace_on()`, no detailed error codes from init, and event handler callbacks relying on mutable `event->handler`. Test signals are creation of a named trace instance, event output, and absence of leftover trace instances after exit.
