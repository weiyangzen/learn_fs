# sources/distributed-fs/ceph-client/kernel/trace/trace_selftest.c

## Purpose

`trace_selftest.c` is included into `trace.c` and provides selftests for ftrace and tracer implementations. It validates trace buffer entries, dynamic ftrace filters, recursion protection, saved regs, function graph tracing, graph private storage, irq/preempt latency tracers, wakeup tracers, nop tracer, and branch tracer. The complete 1567-line file was read.

## Important APIs, Types, and Functions

Major entry points are `trace_selftest_startup_function()`, `trace_selftest_startup_function_graph()`, `trace_selftest_startup_irqsoff()`, `trace_selftest_startup_preemptoff()`, `trace_selftest_startup_preemptirqsoff()`, `trace_selftest_startup_nop()`, `trace_selftest_startup_wakeup()`, and `trace_selftest_startup_branch()`. Helpers cover buffer validation, dynamic probe counters, recursion tests, regs tests, fgraph storage fixtures, and graph hang watchdogs.

## Control Flow

Tests initialize a tracer, generate activity, stop tracing, consume buffers to validate entry types/counts, reset, and restart tracing. Dynamic ftrace tests apply filters to known functions and verify exact callback counts. Graph tests register a watchdog graph callback and validate graph storage. Latency tests disable IRQs or preemption. Wakeup tests create and wake a deadline kthread.

## State and Persistence Behavior

State is static test counters, fixture arrays, temporary ftrace ops, and saved globals such as `ftrace_enabled` and `max_latency`. Tests consume ring buffer data. Severe failures can kill function tracing or stop graph tracing.

## Dependencies and Integration Points

The file depends on config-gated ftrace features, dynamic filtering, graph tracing, direct calls, tracer methods, ring buffers, scheduler deadline support, kthreads, completions, and known noinline targets from `trace_selftest_dynamic.c`.

## Risks and Edge Cases

Selftests must restore global tracing state. Count expectations vary with architecture features, recursion transitions, command-line filters, and ftrace availability. Buffer validation disables tracing to avoid infinite loops. The graph watchdog protects against runaway graph tracing. Wakeup timing is handled with completions where possible.

## Test Signals

Boot logs should show PASS/FAIL for enabled configs. Additional signals are no ftrace kill, no graph watchdog trigger, expected buffer counts, graph storage retrieval for 1/2/4/8 byte data, and no residual callbacks after unregister.
