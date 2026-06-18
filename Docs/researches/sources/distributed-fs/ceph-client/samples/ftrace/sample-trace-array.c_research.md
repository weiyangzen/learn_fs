# sources/distributed-fs/ceph-client/samples/ftrace/sample-trace-array.c

Purpose: sample module showing kernel access to a named ftrace instance (`trace_array`) and custom trace events.

Important APIs/functions: `trace_array_get_by_name`, `trace_array_put`, `trace_array_set_clr_event`, `trace_array_printk`, `trace_array_init_printk`, `DECLARE_WORK`, `DEFINE_TIMER`, `kthread_run`, and tracepoints from `sample-trace-array.h`.

Control flow: init gets/creates a trace instance, enables the sample event, initializes trace-array printk, starts a periodic timer and worker/thread activity. The worker writes trace-array printk messages; the kthread emits custom trace events in a loop. Exit stops the thread, deletes the timer, disables the event, and puts the trace array.

State and persistence: global `struct trace_array *tr`, timer, work item, and thread. Trace buffer contents persist in the tracing instance until cleared or removed by tracing infrastructure.

Dependencies and integration: depends on ftrace instances, trace events, and local header definitions.

Risks: trace instance lifetime must be balanced. Timers/work must be stopped before releasing `tr`. Trace output can be noisy.

Test signals: load module, inspect `/sys/kernel/tracing/instances/sample-instance`, check event records and trace_printk output, unload and verify event disabled.
