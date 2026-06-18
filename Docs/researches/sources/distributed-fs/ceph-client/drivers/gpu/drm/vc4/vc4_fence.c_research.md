# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_fence.c

## Purpose
`vc4_fence.c` provides the `dma_fence_ops` implementation used by VC4 GEN_4 GEM job submissions. The fence represents completion of a VC4 V3D job sequence number and allows dma-reservation objects and DRM syncobjs to observe GPU work completion.

## Important APIs, Types, And Functions
- `vc4_fence_get_driver_name()` returns `"vc4"`.
- `vc4_fence_get_timeline_name()` returns `"vc4-v3d"`.
- `vc4_fence_signaled()` converts the generic `dma_fence` to `struct vc4_fence`, retrieves `struct vc4_dev`, and reports signaled when `vc4->finished_seqno >= f->seqno`.
- `vc4_fence_ops` publishes these callbacks to `dma_fence_init()` in `vc4_gem.c`.

## Control Flow
Fences are allocated and initialized in `vc4_queue_submit()` when a job is assigned a seqno. The fence is attached to dma-reservation objects and optionally installed into an output syncobj. Completion is normally signaled explicitly by GEM/IRQ job completion code, while the `signaled` callback provides state-based verification using `finished_seqno`.

## State And Persistence Behavior
This file defines no independent persistent state. Each `struct vc4_fence` stores a DRM device pointer and seqno. The global completion state is `vc4->finished_seqno`, protected/updated by the GEM/IRQ path outside this file. The fence lifetime is managed by dma-fence refcounting and the job cleanup path.

## Dependencies And Integration Points
It depends on `vc4_drv.h` for `struct vc4_fence`, `to_vc4_fence()`, and `to_vc4_dev()`, plus the kernel dma-fence API included through that header. It integrates with `vc4_gem.c` for fence allocation, reservation attachment, syncobj replacement, wait semantics, and job cleanup.

## Risks And Edge Cases
- Correctness depends on monotonic `finished_seqno` updates and proper locking in the GEM/IRQ code.
- If a job is force-completed during reset, GEM must signal and drop the fence; this file only answers the signaled query.
- `get_driver_name` and timeline name are used for debugging and fence introspection; changing them can affect userspace diagnostics.

## Test Signals
- Submit jobs with output syncobjs and wait through dma-fence/syncobj paths.
- Force GPU reset/hang handling and verify fences are signaled to avoid permanent waits.
- Inspect fence debug output to confirm `"vc4"` and `"vc4-v3d"` names.
