## sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/zcrypt.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/zcrypt.h` is a s390 tracepoint
definitions in the s390 ceph-client Linux source snapshot. It has 127 lines and 4394 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
zcrypt request/CPRB tracepoints that classify CCA, EP11, and HWRNG request types
Important macros/constants: `TRACE_SYSTEM`, `_TRACE_S390_ZCRYPT_H`, `TP_ICARSAMODEXPO`, `TP_ICARSACRT`, `TB_ZSECSENDCPRB`, `TP_ZSENDEP11CPRB`, `TP_HWRNGCPRB`, `show_zcrypt_tp_type(type)`, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.
Trace events declared: `s390_zcrypt_req`, `s390_zcrypt_rep`.

### Control Flow
Trace control flow is declarative: each TRACE_EVENT expands into tracepoint registration, fast-path
enable checks, and format metadata at build time. This file contributes events `s390_zcrypt_req`,
`s390_zcrypt_rep`, and the runtime path is driven by subsystem callers invoking the generated trace
hooks.

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
