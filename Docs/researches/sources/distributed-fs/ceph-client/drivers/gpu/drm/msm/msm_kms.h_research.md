# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_kms.h

## Purpose
Defines the common MSM KMS abstraction and helper structures used by MDP/DPU display backends. It describes backend operations, shared KMS state, commit timers, event threads, and top-level init/uninit entry points.

## Important APIs, Types, and Functions
- `struct msm_kms_funcs` is the backend vtable for hardware init, IRQ setup/handling, vblank, atomic commit lifecycle, format/pixel-clock helpers, destroy, snapshot, and debugfs.
- `struct msm_pending_timer` models per-CRTC async commit flush timers backed by `msm_hrtimer_work`.
- `struct msm_drm_thread` wraps per-CRTC kthread workers.
- `struct msm_kms` stores backend funcs, DRM device, connector/controller pointers, IRQ state, display VM, snapshot worker/mutex, commit locks, pending timers, workqueue, and event threads.
- `msm_kms_init()` initializes commit locks, backend funcs, ordered workqueue, and pending timers.
- `msm_kms_destroy()` destroys pending timers and workqueue.
- `for_each_crtc_mask` helpers iterate CRTCs by mask.

## Control Flow
The header mostly defines contracts. Backend implementations call `msm_kms_init()` during construction and `msm_kms_destroy()` during destruction. Top-level code in `msm_kms.c` calls the function-table hooks in specific init, IRQ, vblank, and atomic-commit phases. Stub functions return `-ENODEV` or no-op when `CONFIG_DRM_MSM_KMS` is disabled.

## State and Persistence
The `struct msm_kms` layout is the persistent in-memory display state across probe/runtime. It tracks commit synchronization, pending async work, IRQ ownership, display VM, attached interfaces, and snapshot state. No disk persistence.

## Dependencies and Integration Points
Depends on Linux clocks/regulators, DRM core types, MSM driver declarations, DSI/DP/HDMI forward declarations, atomic commit helpers, and hrtimer-work utilities. It is consumed by common KMS, DPU, MDP, and display interface code.

## Risks
Because backend hooks are broad, incompatible changes can break multiple display generations. Async commit semantics require careful balance between prepare/flush/wait/complete hooks, especially when multiple async updates accumulate before a vblank. Workqueue and timer lifetimes must match backend teardown.

## Test Signals
Build both with and without `CONFIG_DRM_MSM_KMS`. Runtime checks include backend init/destroy, async commit timer cleanup, CRTC-mask iteration correctness, vblank operations, and suspend/shutdown paths.
