<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_uprobe.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_uprobe.c

Purpose: implements dynamic tracefs and perf events backed by uprobes and uretprobes. It parses user commands from `uprobe_events`, registers probes on executable file offsets, fetches arguments from user register/stack/memory contexts, emits ftrace events, and supports perf/BPF consumers.

Important APIs and types: `struct trace_uprobe` combines a dynamic event, `struct uprobe_consumer`, file path, offsets, hit counters, and a `struct trace_probe`. `trace_uprobe_ops` wires dynamic event create/show/free/match. `trace_uprobe_create()` and `__trace_uprobe_create()` parse `p:`/`r:` commands. `create_local_trace_uprobe()` supports perf-local uprobe events. Dispatcher callbacks are `uprobe_dispatcher()` and `uretprobe_dispatcher()`.

Control flow: command parsing validates probe type, path syntax, regular-file target, offset, optional `%return`, optional ref-counter offset, event name, and fetch arguments. Registration either appends compatible siblings to an existing event or creates a new trace event call. Enabling an event allocates per-CPU page buffers, registers uprobes, and sets trace/profile flags. On a hit, dispatchers set per-task uprobe dispatch context, prepare a per-CPU buffer with fetched args, and fan out to ftrace links and/or perf. Return probes include both function and return instruction addresses.

State and persistence: dynamic events persist while registered in tracefs. Per-probe hit counters are percpu. `uprobe_cpu_buffer` is refcounted under `event_mutex` and stores temporary formatted data. Perf target filtering is stored in `trace_uprobe_filter` with an rwlock, supporting system-wide and per-mm consumers.

Dependencies and integration: relies on uprobes core, trace dynamic events, trace probe argument parser, tracefs files, security lockdown checks, perf, BPF, RCU list traversal, and user memory access helpers.

Risks: command parsing and ref-counter consistency are policy-sensitive. Per-CPU buffer sizing is capped at one page and can truncate/warn if argument data grows. Probe removal must synchronize with uprobe core and event-file links. Perf filters must keep breakpoints applied only to intended mm targets. Test signals include tracefs create/delete, sibling probes with same name, ref-counter mismatch rejection, return probes, fetchargs from stack/registers/file offsets, perf per-task filters, BPF uprobe info, and lockdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_uprobe.c -->
