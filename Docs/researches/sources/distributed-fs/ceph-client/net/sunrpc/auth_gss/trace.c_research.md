# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/trace.c

Purpose: instantiates the RPCSEC_GSS tracepoint definitions by defining `CREATE_TRACE_POINTS` and including `trace/events/rpcgss.h`. The file provides the compilation unit that emits tracepoint storage for GSS client/server authentication events.

Important APIs/types/functions: no callable functions are defined. The important interface is the generated tracepoint set from `<trace/events/rpcgss.h>`, which is used by files such as `svcauth_gss.c` to report MIC, wrap, unwrap, sequence-number, and upcall events.

Control flow: normal compilation includes SUNRPC and GSS headers, defines `CREATE_TRACE_POINTS`, and then includes the trace event header exactly once. At runtime, calls to `trace_rpcgss_*` in other files hit the generated tracepoint code if enabled.

State and persistence behavior: tracepoint state is managed by the kernel tracing subsystem. This file writes no persistent state and owns no runtime objects beyond generated tracepoint metadata.

Dependencies/integration points: depends on SUNRPC client, scheduler, service, transport, auth_gss, and GSS error headers so trace event prototypes can reference the right types. It integrates with ftrace/perf/BPF trace consumers.

Risks: the file must remain the single `CREATE_TRACE_POINTS` owner for `rpcgss.h`; duplicate definitions would break linking, while removing it would leave tracepoint references unresolved. Header dependency drift can break tracepoint type compilation.

Test signals: build with `CONFIG_SUNRPC` and tracing enabled, then verify `rpcgss` events appear under tracing event lists. Runtime RPCSEC_GSS tests should emit expected events when tracepoints are enabled.
