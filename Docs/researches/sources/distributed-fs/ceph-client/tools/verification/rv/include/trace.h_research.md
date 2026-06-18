# sources/distributed-fs/ceph-client/tools/verification/rv/include/trace.h

Purpose: `trace.h` declares tracefs/libtraceevent helper state and functions used when `rv mon --trace` is enabled.

Important types and APIs: `struct trace_instance` combines a `tracefs_instance`, a local `tep_handle`, and a `trace_seq` buffer. `trace_instance_init()`, `trace_instance_start()`, and `trace_instance_destroy()` manage that state. `collect_registered_events()` is the callback passed to raw event iteration.

Control flow and integration: `in_kernel.c` creates a per-monitor trace instance, enables RV events, registers event handlers, and iterates raw events through `collect_registered_events()`.

State, dependencies, risks, and tests: the header depends on libtracefs/libtraceevent headers. Risks include trace instance lifecycle leaks if callers skip destroy, and callback behavior tied to event handlers registered in TEP. Test signals are trace instance creation/destruction and formatted event/error output from `rv mon MONITOR -t`.
