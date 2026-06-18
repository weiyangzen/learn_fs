# sources/distributed-fs/ceph-client/include/trace/define_trace.h

## Purpose
`define_trace.h` is the tracepoint definition pass coordinator. Event headers include it outside their include guards so a translation unit that defines `CREATE_TRACE_POINTS` can instantiate storage and callback wiring for the tracepoints declared in the same event header.

## Important APIs, types, and functions
This header rewrites `TRACE_EVENT`, `TRACE_EVENT_FN`, `TRACE_EVENT_SYSCALL`, `DEFINE_EVENT`, `DEFINE_EVENT_FN`, `DEFINE_EVENT_PRINT`, `DECLARE_TRACE`, and related condition/nop forms into `DEFINE_TRACE*()` invocations. It also optionally maps `DEFINE_RUST_DO_TRACE()` to `__DEFINE_RUST_DO_TRACE()` when `CREATE_RUST_TRACE_POINTS` is set.

## Control flow
When `CREATE_TRACE_POINTS` is absent, the header emits nothing. When present, it undefines the flag to prevent recursive definition, includes the target event header again under `TRACE_HEADER_MULTI_READ`, then includes trace-event, perf, and BPF probe generation headers if `TRACEPOINTS_ENABLED` is defined. Finally it restores macro state and redefines `CREATE_TRACE_POINTS` so later trace headers can be processed.

## State and persistence behavior
The persistent result is compiled tracepoint symbols and generated metadata. It has no runtime state of its own; it controls C preprocessor state and linker-visible tracepoint objects.

## Dependencies and integration points
The include target is derived from `TRACE_SYSTEM`, optionally overridden by `TRACE_INCLUDE_FILE` and `TRACE_INCLUDE_PATH`. The header integrates with `<linux/stringify.h>`, `tracepoint.h` declarations, `trace/trace_events.h`, `trace/perf.h`, `trace/bpf_probe.h`, and the kernel build convention that exactly one C file defines `CREATE_TRACE_POINTS`.

## Risks and test signals
Risks include recursive inclusion if the guard protocol is broken, wrong `TRACE_INCLUDE_PATH` relative semantics, duplicate symbol definitions from multiple `CREATE_TRACE_POINTS` users, and ABI changes in tracepoint macro signatures. Test signals are successful module/kernel builds, exactly one exported tracepoint definition per event, generated format files under tracingfs, and perf/BPF attachment tests.
