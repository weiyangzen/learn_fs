# sources/distributed-fs/ceph-client/samples/trace_events/trace-events-sample.c

## Purpose

This kernel module exercises custom trace events defined in `trace-events-sample.h` by emitting them from kernel threads.

## Important APIs, Types, and Functions

It defines `CREATE_TRACE_POINTS`, includes the sample trace header, uses `kthread_run`, `kthread_stop`, `schedule_timeout`, `trace_foo_bar`, event-template trace functions, `trace_foo_rel_loc`, and registration callbacks `foo_bar_reg()`/`foo_bar_unreg()`.

## Control Flow

Module init starts `event-sample`, which loops once per second building arrays and emitting a variety of tracepoints. Trace events with `_FN` registration callbacks start a second thread `event-sample-fn` only when those tracepoints are enabled; callbacks maintain `simple_thread_cnt` under `thread_mutex`. Module exit stops the base thread and any active function-triggered thread.

## State and Persistence Behavior

Global state includes thread task pointers, `thread_mutex`, and the registration count. Trace ring buffer state is managed by ftrace/perf infrastructure.

## Dependencies and Integration Points

It depends on the kernel tracing subsystem, kthreads, scheduler timeouts, and the generated tracepoint definitions from its header.

## Risks and Edge Cases

Registration callbacks must coordinate with module unload to avoid running threads after removal. Tracepoint format changes affect user-space parsers. The sample intentionally emits frequent events once enabled.

## Test Signals

Load the module, enable events under `/sys/kernel/tracing/events/sample-trace/`, observe emitted records, then disable `_fn` events and verify the auxiliary thread stops.
