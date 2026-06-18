# sources/distributed-fs/ceph-client/drivers/s390/cio/trace.c

Purpose: instantiates and exports s390 CIO tracepoints declared in `trace.h`.

Important APIs/types/functions: defines `CREATE_TRACE_POINTS`, includes `trace.h`, and exports tracepoint symbols for STSCH, MSCH, TSCH, TPI, SSCH, CSCH, HSCH, XSCH, RSCH, and CHSC.

Control flow: no runtime control flow beyond tracepoint instantiation. The wrappers in `ioasm.c` invoke the tracepoints after low-level instructions.

State and persistence behavior: tracepoint state is managed by the kernel tracing subsystem; this file owns no runtime data.

Dependencies and integration points: depends on `asm/crw.h`, `cio.h`, and `trace.h`. Consumers are ftrace/perf/BPF and in-kernel modules that need exported CIO tracepoint symbols.

Risks and test signals: exported symbol list must match declared and used tracepoints. Test with s390 build, enabled trace events for CIO instructions, and module users resolving exported tracepoint symbols.
