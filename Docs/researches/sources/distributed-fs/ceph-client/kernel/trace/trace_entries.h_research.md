# sources/distributed-fs/ceph-client/kernel/trace/trace_entries.h

## Purpose
`trace_entries.h` is the macro source of truth for built-in ftrace ring-buffer entry layouts and their user-visible print formats. It is repeatedly included with different `FTRACE_ENTRY*` macro definitions to generate C structs, trace event call declarations, and format metadata.

## Important APIs, types, and functions
It defines entries for function calls, function graph entry/return, optional function graph return address/retval fields, context switch and wakeup, kernel and user stacks, trace printk variants (`bprint`, `print`, `bputs`), raw data, MMIO trace records, branch records, hardware latency, function repeats, OS noise, and timer latency. It also defines helper field groups such as `FTRACE_CTX_FIELDS`, `FTRACE_STACK_ENTRIES`, branch field sizes, and `FUNC_REPEATS_GET_DELTA_TS()`.

## Control flow
There is no direct runtime control flow. Instead, the included macros expand into declarations consumed by writer and printer paths. `FTRACE_ENTRY_DUP` creates format metadata for `wakeup` while reusing the context-switch structure. `FTRACE_ENTRY_REG` attaches registration hooks to entries such as function tracing and `trace_print`.

## State and persistence behavior
The file defines binary layouts that become persistent within ring-buffer records and visible through tracefs `format` files. These layouts form an ABI for tooling that reads trace data.

## Dependencies and integration points
It depends on macro definitions supplied by including files, especially `trace.h` and trace event generation code. The entry IDs must align with `enum trace_type`, and field structures must match internal helper structures such as `struct ftrace_graph_ent`, `struct ftrace_graph_ret`, `struct mmiotrace_rw`, and `struct mmiotrace_map`.

## Risks
Layout drift is the main risk. Changing fields, packing, dynamic array use, or print format can break trace tooling. Conditional entries must preserve compatibility across configs; for example, function graph retval and return-address variants change layouts under specific config symbols. Stack entry handling deliberately exposes a fixed historical caller array while using dynamic storage internally.

## Test signals
Compile-time macro expansion catches some structure mismatches. Runtime validation should inspect tracefs format files, emit each built-in event type where possible, parse output with trace-cmd/perf tooling, and compare event IDs against `enum trace_type`.
