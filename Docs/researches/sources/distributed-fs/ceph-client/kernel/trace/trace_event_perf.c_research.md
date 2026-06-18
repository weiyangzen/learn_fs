# sources/distributed-fs/ceph-client/kernel/trace/trace_event_perf.c

## Purpose
`trace_event_perf.c` bridges trace events to perf events. It handles permission checks, tracepoint event registration for perf, per-CPU perf event lists, temporary raw trace buffers, kprobe/uprobe perf-local events, add/delete hooks, and special handling for function-trace perf events.

## Important APIs, types, and functions
Important globals are `perf_trace_buf[PERF_NR_CONTEXTS]` and `total_ref_count`. Core functions include `perf_trace_event_perm()`, `perf_trace_event_reg()`, `perf_trace_event_unreg()`, `perf_trace_event_open()`, `perf_trace_event_close()`, `perf_trace_event_init()`, `perf_trace_init()`, `perf_trace_destroy()`, `perf_kprobe_init()/destroy()`, `perf_uprobe_init()/destroy()`, `perf_trace_add()`, `perf_trace_del()`, `perf_trace_buf_alloc()`, `perf_trace_buf_update()`, and, with function tracing, `perf_ftrace_event_register()` plus ftrace callback registration helpers.

## Control flow
`perf_trace_init()` looks up a trace event by perf config/event ID under `event_mutex`, takes a trace event reference, checks permissions, allocates per-event and global per-context buffers if needed, calls the event class `reg()` hooks for perf register/open, and stores the trace event on the perf event. `perf_trace_add()` starts sampling period state and either lets the event class handle add or links the perf event into the current CPU's RCU hlist. `perf_trace_del()` mirrors removal. Destroy paths close, unregister, synchronize tracepoint callbacks, free per-CPU lists and global buffers when last user exits, and drop trace event references.

## State and persistence behavior
Perf trace state persists while perf events are open. Each trace event has `perf_refcount` and per-CPU `perf_events` hlist storage. Global raw buffers are allocated only while at least one trace event is registered for perf. `perf_trace_buf_alloc()` uses perf recursion contexts and per-CPU buffers, returning memory valid for the current submission path.

## Dependencies and integration points
The file depends on perf core APIs, trace event classes and registration hooks, event mutex/refcounting, security/perf permission helpers, local kprobe/uprobe trace event creation, ftrace recursion guards, BPF/perf submission helpers declared in trace event headers, and per-CPU allocation.

## Risks
Permission handling is security-critical because raw tracepoint payloads can expose kernel data. Function trace perf events require root-like tracepoint permission and reject user callchains/user stacks for sampling. Buffer size is capped by `PERF_MAX_TRACE_SIZE`; oversize records are warned and dropped. Registration failure paths must unwind partially allocated per-CPU resources without corrupting refcounts.

## Test signals
Open perf tracepoint events with and without raw samples, as root and non-root, including task-attached events with `TRACE_EVENT_FL_CAP_ANY`. Test perf kprobe/uprobe creation, ftrace function sampling restrictions, concurrent add/delete on multiple CPUs, oversized record warnings, and final cleanup of per-CPU buffers after the last event closes.
