# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank_work.c

## Purpose
Implements `drm_vblank_work`, a delayed work facility that queues work until a target vblank count and then runs it on a per-CRTC realtime-priority kthread worker.

## Important APIs, Types, and Functions
Internal vblank hooks are `drm_handle_vblank_works`, `drm_vblank_cancel_pending_works`, `drm_vblank_worker_init`, `drm_vblank_destroy_worker`, and `drm_vblank_flush_worker`. Exported APIs are `drm_vblank_work_schedule`, `drm_vblank_work_cancel_sync`, `drm_vblank_work_flush`, `drm_vblank_work_flush_all`, and `drm_vblank_work_init`. State resides in each `struct drm_vblank_work` and `struct drm_vblank_crtc` pending list, waitqueue, and kthread worker.

## Control Flow
Scheduling takes `event_lock`, rejects cancelling or modeset-disabled work, acquires a vblank ref for newly pending work, and either queues immediately if the target passed and `nextonmiss` is false or links the work onto `pending_work`. Each vblank calls `drm_handle_vblank_works()` under `event_lock`, moves due items to the kthread worker, drops their vblank refs, and wakes flush waiters. Cancellation removes pending list entries, drops refs, sets a cancellation guard, and synchronously cancels running kthread work.

## State and Persistence
All state is in-memory. Pending list membership tracks whether a vblank ref is held. `cancelling` prevents self-rearming races while cancellation is in progress. Worker lifetime is tied to per-CRTC vblank initialization and cleanup.

## Dependencies and Integration Points
Depends on DRM vblank count/ref APIs, `event_lock`, `vbl_lock`, kernel kthread workers, FIFO scheduler priority, and vblank off cleanup in `drm_vblank.c`.

## Risks
Primary risks are leaked vblank refs if pending list transitions are wrong, rearming races during cancellation, scheduling work while a CRTC is in modeset, and realtime worker latency failing strict scanout deadlines.

## Test Signals
Stress self-rearming work, cancel/flush while vblank interrupts are disabled, vblank-off cleanup, lockdep around event/vblank locks, and refcount WARNs in the vblank core.
