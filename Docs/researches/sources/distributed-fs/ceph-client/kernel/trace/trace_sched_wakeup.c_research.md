# sources/distributed-fs/ceph-client/kernel/trace/trace_sched_wakeup.c

## Purpose

`trace_sched_wakeup.c` implements the `wakeup`, `wakeup_rt`, and `wakeup_dl` latency tracers. These capture latency from task wakeup to actual scheduling, optionally recording function or function-graph trace context. The complete 830-line file was read.

## Important APIs, Types, and Functions

Key tracer callbacks are `wakeup_tracer_init()`, `wakeup_rt_tracer_init()`, `wakeup_dl_tracer_init()`, `wakeup_tracer_reset()`, `wakeup_tracer_start()`, `wakeup_tracer_stop()`, `wakeup_flag_changed()`, `wakeup_trace_open()`, `wakeup_trace_close()`, `wakeup_print_line()`, and `wakeup_print_header()`. Runtime probes are `probe_wakeup()`, `probe_wakeup_sched_switch()`, and `probe_wakeup_migrate_task()`.

## Control Flow

Initialization saves flags, forces overwrite/latency format, sets the trace array, initializes ftrace ops, registers scheduler tracepoints, resets state, and starts function tracing. Wakeup probes filter candidates by tracer mode and priority, record the wake event, stack, and function call, and store task/CPU/priority/timestamp. The sched-switch probe detects the target task, computes latency, updates max trace if reportable, and resets state.

## State and Persistence Behavior

The tracer uses singleton global state: active trace array, enable flag, task reference, CPUs, priority, RT/DL flags, deadline-in-progress flag, lock, saved trace flags, function enabled flag, and busy flag. `wakeup_task` holds a reference until reset.

## Dependencies and Integration Points

It integrates with scheduler tracepoints, latency snapshot buffers, function and graph tracers, stack tracing, thresholds, command-line recording, trace arrays, and tracer registration via `core_initcall()`.

## Risks and Edge Cases

Races around global task state, migration, and enable ordering are central. Memory barriers guard stale `wakeup_task`. Deadline tasks suppress replacement. Locking runs in scheduler/IRQ-disabled paths. Graph mode toggles require careful unregister/register. Reset must drop the task reference.

## Test Signals

Use ftrace wakeup selftests, deadline wakeup tests, max latency updates, trace output for all three tracers, migration during wakeup, graph display toggles, threshold behavior, and busy-tracer refusal.
