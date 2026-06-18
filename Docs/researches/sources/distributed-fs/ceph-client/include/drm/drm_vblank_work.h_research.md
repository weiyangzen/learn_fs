# sources/distributed-fs/ceph-client/include/drm/drm_vblank_work.h

## Purpose
`drm_vblank_work.h` declares a delayed work abstraction that runs a `kthread_work` item after a target vblank at realtime priority, outside IRQ context.

## Important APIs, types, and functions
`struct drm_vblank_work` embeds a `kthread_work`, points to its `drm_vblank_crtc`, records target vblank count, tracks active cancel calls, and links into the per-CRTC pending work list. `to_drm_vblank_work()` converts from embedded work. APIs are `drm_vblank_work_schedule`, `drm_vblank_work_init`, `drm_vblank_work_cancel_sync`, `drm_vblank_work_flush`, and `drm_vblank_work_flush_all`.

## Control flow
Drivers initialize a vblank work item for a CRTC and callback, schedule it for a target count, and optionally request next-vblank execution if the target was missed. The vblank core queues it to the CRTC worker when the count is reached. Cancellation and flush APIs synchronize with pending or running work.

## State and persistence
State is runtime per work item plus per-CRTC pending lists and worker. Work items persist while owned by their driver and must not be rescheduled during active synchronous cancellation.

## Dependencies and integration points
It depends on kthread work and the vblank core. It integrates with `drm_vblank_crtc.worker`, `pending_work`, and `work_wait_queue` fields from `drm_vblank.h`.

## Risks and test signals
Risks include scheduling after CRTC teardown, target count races, missed-vblank policy mistakes, cancel/reschedule races, work running after resources are freed, and realtime worker starvation. Test signals include schedule for future/past vblanks, `nextonmiss` behavior, cancel while pending and running, flush all on CRTC shutdown, and concurrent scheduling from multiple contexts.
