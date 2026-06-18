<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/trace_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/trace_types.h

Purpose: Defines trace-facing Xen multicall flush and extension reason enums plus a callback function type used by Xen tracing and multicall batching.

Important APIs/types/functions: `enum xen_mc_flush_reason`, `enum xen_mc_extend_args`, and `xen_mc_callback_fn_t`.

Control flow: Xen multicall code tags flushes as explicit, batch-space, argument-space, or callback-space exhaustion and tags extend attempts as ok, bad operation, or no space. Trace events consume these values.

State and persistence behavior: No state is stored. Enum values become part of trace output semantics and should remain stable for observability.

Dependencies and integration points: Integrated with Xen multicall batching, tracepoints, and callback queues.

Risks and test signals: Risks are trace decoder drift and missing reason coverage when multicall behavior changes. Test with Xen trace events enabled, multicall-heavy PV MMU workloads, and trace consumers that decode flush reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/trace_types.h -->
