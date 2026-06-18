<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.c

Purpose: tracepoint instantiation unit for Intel IOMMU tracing.

Important APIs/types/functions: defines `CREATE_TRACE_POINTS` and includes `trace.h`, causing the trace events declared there to be emitted exactly once.

Control flow: compile-time only; no runtime functions are implemented here. Including this translation unit links tracepoint definitions for queued invalidation, PRQ reporting, and cache-tag assignment/flush events.

State and persistence: tracepoint state is owned by the kernel tracing subsystem; this file has no persistent private data.

Dependencies and integration: depends on `trace.h`, Linux tracepoint infrastructure, and any helpers referenced by trace print functions such as PRQ descriptor decoding.

Risks: this file must remain the only `CREATE_TRACE_POINTS` inclusion for the Intel IOMMU trace system. Missing it causes unresolved trace symbols; duplicating it causes duplicate definitions.

Test signals: kernel build/link, tracefs event presence under `intel_iommu`, and enabling each Intel IOMMU tracepoint during invalidation/PRQ/cache-tag activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.c -->
