# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring_submission.c

## Purpose
`intel_ring_submission.c` implements legacy pre-execlists i915 ringbuffer submission for Gen2-Gen7 engines. It programs ring registers, status pages, context switches, PPGTT state, request preambles, reset handling, IRQ hooks, and engine setup.

## Important APIs, Types, And Functions
The public entry point is `intel_ring_submission_setup()`. Major internal paths include `xcs_resume()`, `xcs_sanitize()`, `reset_prepare()`, `reset_rewind()`, `reset_cancel()`, `i9xx_submit_request()`, `gen6_bsd_submit_request()`, `ring_context_ops`, `load_pd_dir()`, `mi_set_context()`, `switch_mm()`, `switch_context()`, `ring_request_alloc()`, engine-class setup helpers, and Gen7 render-clear workaround VMA setup.

## Control Flow
Setup installs common engine callbacks, selects render/video/copy/VEBox emitters and interrupt masks, creates one legacy timeline and one global ring, pins both under a ww context, optionally allocates a Gen7 residual-clear batch, and hands cleanup to `ring_release()`. Request allocation reserves a legacy preamble budget, emits invalidate flushes, switches address spaces, emits `MI_SET_CONTEXT` if needed, handles L3 remap state, and clears residual state when mitigations require it. Submission marks the request submitted, drains writes with `wmb()`, and writes `RING_TAIL`; Gen6 BSD wraps tail updates with wake and PSMI workarounds.

## State, Persistence, And Dependencies
Persistent driver state attaches to `engine->legacy.ring`, `engine->legacy.timeline`, `engine->status_page`, `engine->wa_ctx`, context state VMAs, and the scheduler request list. Hardware state is in ring registers, HWS PGA registers, PP_DIR registers, interrupt masks, and MI command streams. Dependencies include generation-specific command emitters, PPGTT, breadcrumbs, reset, engine PM, i915 mitigations, render-clear batches, GEM WW locking, and uncore MMIO helpers.

## Integration Points
It plugs into `intel_engine_cs` callbacks for resume, sanitize, reset, submit, request allocation, context ops, IRQ enable/disable, and release. Timelines and status pages integrate with breadcrumbs and request retirement. PPGTT and context state are shared with GEM contexts.

## Risks
This code is register-ordering sensitive. Resume/reset must disable and empty rings before reprogramming start/head/tail/ctl, and failed head reset can lead to unrecoverable hangs. Context switch command lengths must match emitted dwords. PPGTT loads require flush and invalidate barriers. Residual clear ownership in `wa_ctx.vma->private` must not leak references. The Gen6 BSD wake sequence and Gen7 workarounds are platform-specific fault points.

## Test Signals
Selftests include `selftest_ring_submission.c`. Runtime signals include suspend/resume on Gen2-Gen7, GPU reset recovery, context switch stress, PPGTT aliasing, L3 remap tests, residual-clear mitigation tests, interrupt delivery after reset, and Gen6 BSD media workloads.
