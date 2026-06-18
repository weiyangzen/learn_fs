<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/bpf_probe.h -->
# sources/distributed-fs/ceph-client/include/trace/bpf_probe.h

## Purpose

`sources/distributed-fs/ceph-client/include/trace/bpf_probe.h` is Linux trace-event BPF probe
generation header. It redefines trace event class and event macros so trace headers emit BPF/raw-
tracepoint probe prototypes, test stubs, BTF typedefs, and writable-buffer size checks during trace
include re-expansion. The source was read as a complete 139-line header for this report.

## Important APIs, Types, and Functions

functions/prototypes: `void`; macros/constants: `__perf_count`, `__perf_task`, `UINTTYPE`,
`__CAST_TO_U64`, `__CAST1`, `__CAST2`, `__CAST3`, `__CAST4`, `__CAST5`, `__CAST6`, `__CAST7`,
`__CAST8`, `__CAST9`, `__CAST10`, and 15 more

## Control Flow

Trace event headers are included after stage6 callback generation; this file maps
`DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `DECLARE_TRACE`, and writable variants into BPF-specific
declarations. Generated test helpers cast trace arguments to u64, call
`check_trace_callback_type_*`, and validate writable buffer sizes where applicable.

## State and Persistence Behavior

The header owns no runtime state. It produces compile-time declarations and static inline test
functions; live state belongs to tracepoints, BPF programs, perf/raw tracepoint registration, and
event callback tables.

## Dependencies and Integration Points

Direct includes: `stages/stage6_event_callback.h`, `linux/args.h`. Integrates with Linux trace-event
code generation, BPF/raw tracepoint attachment, and trace include re-expansion stages.

## Risks and Edge Cases

Risks include macro redefinition order mistakes, argument cast truncation or signedness surprises,
unsupported argument counts, writable-buffer size expressions with side effects, and BTF prototype
drift from generated trace callback types.

## Test Signals

Test trace header regeneration, BPF raw tracepoint attachment, writable trace events, syscall event
classes, sparse/build coverage for argument casts, and compile failures for mismatched callback
prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/bpf_probe.h -->
