# sources/distributed-fs/ceph-client/kernel/trace/trace_probe.h

## Purpose

`trace_probe.h` defines common contracts for probe-based dynamic events: fetch operations, fetch types, probe arguments, probe event structures, parser context, parser flags, error codes, and helper prototypes. The complete 596-line header was read.

## Important APIs, Types, and Functions

Key types are `enum fetch_op`, `struct fetch_insn`, `struct fetch_type`, `struct probe_arg`, `struct probe_entry_arg`, `struct trace_probe_event`, `struct trace_probe`, `struct event_file_link`, and `struct traceprobe_parse_context`. Inline helpers cover `__data_loc` encoding, event flags, event-call conversion, sibling/file-list checks, and parser flag checks. Prototypes expose parse, register, field, print, file-link, and cleanup operations.

## Control Flow

The header defines the lifecycle: initialize a `trace_probe`, parse arguments into fetch programs, register a `trace_event_call`, add event files when enabled, fetch/store runtime arguments, print fields, remove files, and clean up allocations.

## State and Persistence Behavior

`struct trace_probe_event` owns the trace event class, call, files list, probes list, and optional uprobe filter. Multiple `trace_probe` instances can share one event. `event->flags` records trace/profile enablement. `probe_arg` state persists names, command text, type, array count, offsets, and formats.

## Dependencies and Integration Points

The header includes tracing internals, trace output, tracefs, kprobes, BTF, perf, ptrace, uaccess, and architecture bit-width definitions. It is included by probe implementations and fetch templates.

## Risks and Edge Cases

Changing enum order, struct ownership, flag semantics, or max sizes can break dynamic probes. Data-location helpers assume `u32` `__data_loc` layout. Parser flags have mutually exclusive combinations. Some APIs compile to no-ops when config options are disabled.

## Test Signals

Compile across config matrices; runtime coverage should include enable flags, sibling probes, file add/remove, parser flag combinations, max argument limits, dynamic strings, and return-probe entry data.
