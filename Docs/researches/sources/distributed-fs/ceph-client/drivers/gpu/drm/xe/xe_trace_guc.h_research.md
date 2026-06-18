# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_guc.h

Purpose: Provides tracepoints for GuC CT buffer flow control, H2G/G2H CTB messages, and GuC engine activity accounting snapshots.

Important APIs/types/functions: Event class `xe_guc_ct_flow_control` underlies `xe_guc_ct_h2g_flow_control` and `xe_guc_ct_g2h_flow_control`, recording head, tail, size, space, and message length. Event class `xe_guc_ctb` underlies `xe_guc_ctb_h2g` and `xe_guc_ctb_g2h`, recording GT id, action, length, tail, and head. `xe_guc_engine_activity` records metadata and activity counters from `struct engine_activity`.

Control flow: GuC communication paths emit the CT flow/CTB tracepoints around ring-buffer operations. Engine-activity sampling emits a snapshot including global/change counters, GuC TSC frequency, latency, quanta ratio, active ticks, accumulated active/total/quanta counters, and CPU timestamp.

State and persistence behavior: This header only observes GuC communication/accounting state. It snapshots values without changing queue pointers or activity counters.

Dependencies and integration points: Includes Xe device, GuC exec queue, and GuC engine activity type headers. It is consumed by GuC CT and engine utilization/statistics paths.

Risks: Ring-buffer diagnostics are only as accurate as call-site ordering; tracing before head/tail updates versus after updates changes interpretation. `xe_guc_engine_activity` assumes `struct engine_activity` is populated and stable. New GuC actions or metadata layouts may require trace format updates.

Test signals: Enable tracepoints during GuC submission, CT send/receive stress, and engine activity collection. Verify H2G and G2H events distinguish direction and that activity counters update plausibly under busy/idle engine workloads.
