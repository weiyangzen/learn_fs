# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/sputrace.h

Purpose: defines the spufs tracepoint event used to observe context lifecycle and scheduler transitions.

Important APIs: `TRACE_EVENT(spufs_context)` records a string name, owner thread id, and physical SPU number or `-1`. Convenience macros `spu_context_trace(name, ctx, spu)` and `spu_context_nospu_trace(name, ctx)` stringify call-site names and invoke the tracepoint.

Control flow and dependencies: `sched.c` defines `CREATE_TRACE_POINTS` before including this header, while other files include it for declarations. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE sputrace` make the tracing generator find the local header; the Makefile adds `-I$(src)` for `sched.o`.

State and integration: trace data is observational only and depends on `ctx->tid` and optional `spu->number`. Risks include trace include path breakage, using a transient string pointer incorrectly, and missing updates if important paths are not instrumented. Test signals are tracepoint generation during build and runtime events around bind, unbind, activate, fault wake, and destroy paths.
