# sources/distributed-fs/ceph-client/drivers/cxl/core/trace.c

Purpose: instantiates the CXL tracepoints declared in `trace.h` by defining `CREATE_TRACE_POINTS` in exactly one translation unit.

Important APIs and control flow: the file includes `<cxl.h>`, `core.h`, defines `CREATE_TRACE_POINTS`, and includes `trace.h`. It exports no callable functions; build/link side effects create the tracepoint definitions for all `TRACE_EVENT()` declarations in the header.

State and persistence behavior: tracepoint state is managed by the kernel tracing subsystem. This file owns no runtime data structures beyond the generated tracepoint objects.

Dependencies and integration points: depends on the trace event declarations in `trace.h` and on all types referenced by those declarations being visible from the included headers. RAS, event, poison, and mailbox paths call the generated `trace_cxl_*()` functions.

Risks and test signals: if another file defines `CREATE_TRACE_POINTS` for the same header, duplicate definitions result; if this file is omitted, users get unresolved trace symbols. Build tests with tracing enabled and disabled, plus runtime checks under `/sys/kernel/tracing/events/cxl/`, are the main signals.
