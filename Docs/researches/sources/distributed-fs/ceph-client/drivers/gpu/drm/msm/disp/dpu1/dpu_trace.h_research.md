# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_trace.h

Purpose: defines the DPU tracepoint surface for performance, IRQ, encoder, CRTC, plane, resource-manager, VBIF, and CTL events. It is the main low-overhead observability layer for this DPU driver code.

Important APIs and events: trace events include `dpu_perf_set_qos_luts`, `dpu_perf_set_danger_luts`, `dpu_perf_set_ot`, `dpu_perf_crtc_update`, IRQ callback register/unregister events, encoder enable/disable/kickoff/RC/wait events, command/video physical encoder events, CRTC mixer/vblank/enable events, plane scanout/disable events, RM LM/CTL/INTF reservation events, VBIF halt failures, external TE connection, core perf clock updates, and CTL pending flush events. `DPU_ATRACE_BEGIN`, `DPU_ATRACE_END`, `DPU_ATRACE_FUNC`, and `DPU_ATRACE_INT` provide Android-style trace markers.

Control flow: the file is included by producers, then `trace/define_trace.h` is included outside the guard as required by Linux tracepoint generation. Event classes reduce repeated definitions for similar payloads.

State and persistence: tracepoints record transient runtime state into kernel tracing buffers when enabled. They do not mutate driver state.

Dependencies and integration: depends on Linux tracepoint macros, DRM rect formatting, and DPU private structs. Users include this header where they call generated `trace_*` functions.

Risks: trace event struct fields dereference caller-provided state; callers must pass valid pointers. Trace payload formats become user-visible diagnostics, so changing fields can disrupt tooling. A few printk payloads repeat the wrong field for video IRQ refcnt, which is a diagnostic accuracy risk.

Test signals: kernel build validates trace macro expansion. Runtime validation comes from enabling `dpu:*` trace events during modeset, vblank, kickoff, VBIF, and RM stress tests and checking coherent ids, masks, and dimensions.
