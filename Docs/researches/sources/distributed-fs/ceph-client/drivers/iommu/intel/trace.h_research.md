<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.h

Purpose: Intel IOMMU tracepoint declarations for queued invalidation descriptors, PRQ reports, and cache-tag assignment/flush activity.

Important APIs/types/functions: `TRACE_EVENT(qi_submit)`, `TRACE_EVENT(prq_report)`, `DECLARE_EVENT_CLASS(cache_tag_log)`, `cache_tag_assign`, `cache_tag_unassign`, `DECLARE_EVENT_CLASS(cache_tag_flush)`, `cache_tag_flush_range`, and `cache_tag_flush_range_np`.

Control flow: callers invoke generated trace helpers around queued invalidation submission, PRQ reporting, and cache-tag operations. Print functions decode descriptor type bits and cache-tag types into human-readable strings; PRQ output delegates descriptor formatting to `decode_prq_descriptor()`.

State and persistence: no driver state; trace records snapshot IOMMU name, device name, descriptor qwords, domain IDs, PASIDs, ranges, masks, and sequence numbers into tracing buffers.

Dependencies and integration: includes `iommu.h`, Linux tracepoint macros, and `trace/define_trace.h` with explicit include path/file settings for out-of-tree trace generation.

Risks: tracepoint field layouts are ABI-like for tracing users. `MSG_MAX` limits decoded PRQ text. Cache-tag enum names must stay in sync with actual cache-tag values.

Test signals: build with tracing, tracefs format files, enabled `qi_submit` while invalidating, `prq_report` during PRI faults, and cache-tag tracepoints during SVA/nested attach and invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/trace.h -->
