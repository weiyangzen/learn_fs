# sources/distributed-fs/ceph-client/kernel/trace/trace_probe.c

## Purpose

`trace_probe.c` is the shared implementation for dynamic probe events used by kprobes, uprobes, fprobes, and event probes. It parses user probe arguments into a compact fetch-instruction program, resolves symbols and BTF arguments, defines trace event fields, builds print formats, manages shared `trace_probe_event` lifetime, and logs parser errors through the tracing error log. The complete 2284-line file was read.

## Important APIs, Types, and Functions

Important exported or shared functions include `trace_probe_log_init()`, `traceprobe_parse_event_name()`, `traceprobe_parse_probe_arg()`, `traceprobe_expand_meta_args()`, `traceprobe_expand_dentry_args()`, `traceprobe_update_arg()`, `traceprobe_set_print_fmt()`, `traceprobe_define_arg_fields()`, `trace_probe_init()`, `trace_probe_cleanup()`, `trace_probe_append()`, `trace_probe_register_event_call()`, `trace_probe_add_file()`, `trace_probe_remove_file()`, `trace_probe_create()`, and `trace_probe_print_args()`. Config-gated BTF helpers map function prototypes, parameters, structure fields, and bitfields onto probe fetch types. Config-gated entry-data helpers store function-entry arguments for return probes.

## Control Flow

Probe creation splits a raw command into argv, parses group/event names, expands `$arg*` and dentry shortcuts, then parses each argument body. Argument parsing recognizes `$` variables, registers, immediates, memory references, nested dereferences, BTF variable names, arrays, explicit types, bitfields, strings, user strings, and symbol strings. The result is a bounded `FETCH_INSN_MAX` program ending in `FETCH_OP_END`. Registration creates the trace event call and fields; runtime printing walks argument metadata and type-specific print functions.

## State and Persistence Behavior

Dynamic state is attached to `struct trace_probe`, `struct trace_probe_event`, and per-argument `struct fetch_insn` arrays. Event flags use acquire/release helpers. File links are RCU-delayed on removal. Parser error state is global under `dyn_event_ops_mutex`. BTF references live in the parse context and are released by `traceprobe_finish_parse()`.

## Dependencies and Integration Points

The file depends on trace event registration, tracefs dynamic event locking, BTF lookup, kallsyms, ftrace field definitions, perf-local probe declarations, and architecture register/function-argument helpers. It is the common parser and event-lifetime layer beneath kprobe, uprobe, eprobe, and fprobe consumers.

## Risks and Edge Cases

Risks include parser offset drift, cleanup of symbol/immediate-string allocations on parse failure, `MAX_PROBE_EVENT_SIZE` overflow, BTF reference leaks, bad return-probe entry offsets, field-name collisions, and symbol resolution changing between parse and registration. Dynamic string size calculation must match runtime storage.

## Test Signals

Use dynamic event selftests for kprobe/uprobe/eprobe syntax, BTF `$arg*`, dentry `%p[dD]`, invalid diagnostics, duplicate events, return-probe entry arguments, symbol updates, tracefs enable/disable, and perf local probe creation.
