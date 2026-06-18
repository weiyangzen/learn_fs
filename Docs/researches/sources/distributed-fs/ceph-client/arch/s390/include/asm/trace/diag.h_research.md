## sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/diag.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/diag.h` is a s390 tracepoint
definitions in the s390 ceph-client Linux source snapshot. It has 44 lines and 950 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
diagnose-instruction tracepoints with a norecursion wrapper for low-level diagnostic calls
Important macros/constants: `TRACE_SYSTEM`, `_TRACE_S390_DIAG_H`, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`.
Important types/layouts: none detected.
Important declarations or inline helpers: `trace_s390_diagnose_norecursion`.
Trace events declared: `s390_diagnose`.

### Control Flow
Trace control flow is declarative: each TRACE_EVENT expands into tracepoint registration, fast-path
enable checks, and format metadata at build time. This file contributes events `s390_diagnose`, and
the runtime path is driven by subsystem callers invoking the generated trace hooks.

### State And Persistence
Tracepoint enable state, ring-buffer records, and format metadata are managed by the tracing core;
this header contributes event schemas but keeps no private persistent state.

### Dependencies
Linux tracepoint generation, ftrace/perf, subsystem drivers, and trace/define_trace.h. Direct
include dependencies detected here: `linux/tracepoint.h`, `trace/define_trace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/trace`
source-tree area and feeds the s390 architecture boundary for Linux tracepoint generation,
ftrace/perf, subsystem drivers, and trace/define_trace.h. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
trace format drift can break tooling that parses field names or event payloads

### Test Signals
tracefs format inspection, perf/ftrace event enablement, and subsystem event generation
