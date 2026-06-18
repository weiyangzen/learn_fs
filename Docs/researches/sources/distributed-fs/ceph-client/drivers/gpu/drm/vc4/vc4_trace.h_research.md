# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_trace.h

Purpose: Declares Linux tracepoints for VC4 wait/submit/interrupt events, enabling ftrace/perf-style observation of GPU job submission and completion without changing normal driver behavior.

Important APIs/types/functions: `TRACE_SYSTEM vc4` and `TRACE_INCLUDE_FILE vc4_trace` define the trace namespace. Trace events are `vc4_wait_for_seqno_begin`, `vc4_wait_for_seqno_end`, `vc4_submit_cl_ioctl`, `vc4_submit_cl`, `vc4_bcl_end_irq`, and `vc4_rcl_end_irq`. Each event records DRM minor index and event-specific fields such as seqno, timeout, CL sizes, BO count, queue type, and CTN address range.

Control flow: No driver control flow; trace macros expand into static tracepoint definitions. The include guard allows `TRACE_HEADER_MULTI_READ`, and the file ends by setting `TRACE_INCLUDE_PATH` and including `trace/define_trace.h` as required by the kernel tracepoint pattern.

State and persistence: Tracepoints maintain kernel tracing metadata when compiled; event records are transient in tracing buffers. No VC4 state is modified.

Dependencies and integration points: Includes Linux tracepoint headers and expects `struct drm_device` fields such as `primary->index`. Instantiated by `vc4_trace_points.c`; called from wait, submit, and IRQ paths elsewhere in the VC4 driver.

Risks: Tracepoint prototypes must match call sites exactly or builds fail. Dereferencing `dev->primary` assumes a registered DRM device. Changing event fields affects userspace tracing scripts.

Test signals: Build with tracing enabled, enable `vc4:*` trace events, submit workloads, and verify begin/end seqnos, ioctl sizes, BCL/RCL selection, and interrupt completion events appear in order.
