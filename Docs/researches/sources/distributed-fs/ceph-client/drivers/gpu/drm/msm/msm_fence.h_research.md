# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fence.h

## Purpose
Declares MSM fence context state, fence lifecycle APIs, and wrap-safe fence comparison helpers.

## Important APIs, types, and functions
- `struct msm_fence_context` documents per-ring timeline state, GPU fence pointer, spinlock, deadline timer, and deadline work.
- Declares `msm_fence_context_alloc/free()`, `msm_fence_completed()`, `msm_update_fence()`, `msm_fence_alloc()`, and `msm_fence_init()`.
- Inline `fence_before()` and `fence_after()` use signed 32-bit subtraction for seqno wraparound.

## Control flow
The header has no complex runtime flow; only inline comparisons execute.

## State and persistence
Defines the persistent fence context layout used by `msm_fence.c` and GPU ring code.

## Dependencies and integration points
Includes `msm_drv.h` for DRM/device types and is consumed by submit, ring, and wait paths.

## Risks
Changing struct fields or comparison semantics affects synchronization correctness across the driver. Deadline fields currently track only one next deadline and are documented as limited for multiple queued deadlines.

## Test signals
Build coverage plus rollover comparison unit-style checks and submit/wait tests.
