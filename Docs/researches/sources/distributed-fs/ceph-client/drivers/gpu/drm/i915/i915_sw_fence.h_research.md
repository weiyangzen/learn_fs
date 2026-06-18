<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.h

## Purpose
Declares the i915 software fence primitive and its APIs for internal asynchronous dependency tracking.

## Important APIs, types, and functions
- `enum i915_sw_fence_notify` distinguishes `FENCE_COMPLETE` and `FENCE_FREE`.
- `i915_sw_fence_notify_t` is the owner callback type.
- `struct i915_sw_fence` stores waitqueue, callback, optional DAG flags, pending count, and error.
- `struct i915_sw_dma_fence_cb` embeds a dma-fence callback plus target software fence.
- Public APIs initialize, reinitialize, commit, await software fences, await dma fences, await reservations, increment pending, complete, test signaled/done, wait synchronously, and set an error once.

## Control flow
The lockdep-aware `i915_sw_fence_init()` macro assigns a static lock class per call site. Inline tests interpret `pending <= 0` as signaled and `pending < 0` as fully done. `i915_sw_fence_wait()` blocks on the waitqueue until done.

## State and persistence
The software fence state is embedded in owner objects such as requests or fenced work. The error field persists until reinit and is copied from signalers or dma fences.

## Dependencies and integration points
Depends on dma-fence, gfp/kref/notifier/waitqueue APIs, and optional lockdep. Included by request, scheduler-related work, and fenced work modules.

## Risks
Owners must supply a non-NULL callback and must not reinitialize while waiters remain. `i915_sw_fence_set_error_once()` ignores later errors, so caller ordering determines the reported failure. Stack-allocated wait entries require the signaler to complete before the storage is invalidated.

## Test signals
Compile-time lockdep macro coverage, software-fence selftests, dma-fence callback tests, request submit/semaphore behavior, and debug-object reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.h -->
