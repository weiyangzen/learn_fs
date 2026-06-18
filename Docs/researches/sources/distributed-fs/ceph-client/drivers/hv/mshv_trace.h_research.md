# sources/distributed-fs/ceph-client/drivers/hv/mshv_trace.h

## Purpose

`mshv_trace.h` declares the Linux tracepoints for the MSHV root driver. The events provide low-overhead observability for partition/VP lifecycle, hypercalls, VP dispatch, IRQ routing, memory mapping, eventfd registration, wait states, and GPA intercept handling.

## Important APIs, Types, and Functions

- Lifecycle events: `mshv_create_partition`, `mshv_partition_release`, `mshv_destroy_partition`, `mshv_create_vp`, `mshv_vp_release`.
- Hypercall events: create/initialize/finalize/delete partition, withdraw memory, map VP state page, dispatch VP.
- Run-loop events: `mshv_run_vp_entry`, `mshv_run_vp_exit`, explicit suspend clear, guest-mode work, wait-for-kick.
- Configuration events: routing table update, user memory map, ioeventfd assign/deassign.
- Fault event: `mshv_handle_gpa_intercept` logs partition, VP, GFN, access type, and handled status.

## Control Flow

Implementation files call generated `trace_mshv_*()` helpers at important transitions. The header sets `TRACE_SYSTEM mshv`, defines include path/file metadata, and ends with `trace/define_trace.h` outside the include guard as required by kernel tracepoint conventions.

## State and Persistence Behavior

Tracepoints do not alter MSHV state. They snapshot scalar fields and pointers into ring buffers when enabled. Pointer fields such as routing table or eventfd addresses are diagnostic only and should not be treated as stable identifiers after object teardown.

## Dependencies and Integration Points

The header depends on `linux/tracepoint.h` and Hyper-V HVDK types. It is included by MSHV implementation files and instantiated by `mshv_trace.c`.

## Risks and Edge Cases

Trace format is a user-visible diagnostics contract; changing field names or print formats can affect tooling. Some events log raw pointers, which may be restricted by kernel pointer formatting policy. The GPA intercept event stores access type as a character in a `u8` field, which is intentional but easy to misread.

## Test Signals

Build with tracing, enable each event, exercise matching code paths, verify field decoding through `trace_pipe` or perf, and ensure tracepoint prototypes remain synchronized with call sites after refactors.
