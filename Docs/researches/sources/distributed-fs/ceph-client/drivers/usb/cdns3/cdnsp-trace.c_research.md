# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-trace.c

Purpose: tracepoint definition translation unit for CDNSP. The complete 12-line file was read. It defines `CREATE_TRACE_POINTS` and includes `cdnsp-trace.h`, causing trace event declarations in that header to emit storage and registration code exactly once.

Important APIs/types/functions: no direct functions or structs. The key API is the kernel tracepoint pattern `#define CREATE_TRACE_POINTS` followed by `#include "cdnsp-trace.h"`.

Control flow: no runtime control flow of its own; generated tracepoint registration and call-site behavior comes from `cdnsp-trace.h`.

State and persistence: owns generated tracepoint definitions at link time. Runtime trace buffers and enable state are managed by the Linux tracing subsystem.

Dependencies/integration: depends entirely on `cdnsp-trace.h` and the kernel tracepoint framework. Integrated with all CDNSP files that include the trace header without defining `CREATE_TRACE_POINTS`.

Risks: must remain the sole CDNSP translation unit defining `CREATE_TRACE_POINTS`; duplicating it causes multiple definitions, removing it causes unresolved tracepoint definitions.

Test signals: build/link with tracing enabled and enable CDNSP ftrace events during enumeration and transfers to verify tracepoints register and emit records.
