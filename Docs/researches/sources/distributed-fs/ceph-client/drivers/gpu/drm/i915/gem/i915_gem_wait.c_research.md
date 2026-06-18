# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_wait.c

## Purpose
This file implements GEM object wait and wait-priority behavior for dma-reservation fences, including the `DRM_IOCTL_I915_GEM_WAIT` ioctl and migration-fence waiting.

## Important APIs, Types, and Functions
Important functions are `i915_gem_object_wait`, `i915_gem_object_wait_priority`, `i915_gem_fence_wait_priority`, `i915_gem_fence_wait_priority_display`, `i915_gem_wait_ioctl`, and `i915_gem_object_wait_migration`. Internal helpers wait on individual fences, preboost i915 requests, convert nanosecond timeouts to jiffies, and set fence priorities.

## Control Flow
Object wait prescans all relevant reservation fences and boosts unstarted i915 requests, then iterates fences and waits on each with timeout propagation. i915 fences use `i915_request_wait_timeout`, non-i915 fences use generic `dma_fence_wait_timeout`. Priority helpers recurse one level into fence arrays or the first fence in a chain, then call the engine schedule hook under RCU and bottom-half disable/enable.

The wait ioctl validates flags, looks up the object, records start time, waits interruptibly with priority on all fences, subtracts elapsed time from the user timeout, clamps to zero, and returns `-EAGAIN` instead of `-ETIME` when remaining time is above jiffy precision.

## State and Persistence Behavior
This file stores no persistent state. It observes and may reprioritize reservation fences and request scheduling attributes. The ioctl mutates the user argument's `timeout_ns` to report remaining time.

## Dependencies and Integration Points
It depends on dma-resv iterators, dma-fence arrays/chains, i915 requests/engines/RPS boost, GEM object lookup, migration moving fences, and UAPI wait structs.

## Risks
Timeout conversions must avoid overflow and jiffy precision regressions. Waiting without exclusive object locks means the object can become busy again immediately after success. Priority boosting order is subtle because reservation fence order can affect whether a request appears boost-worthy.

## Test Signals
Wait ioctl timeout/remaining-time tests, zero-time busy compatibility, signal interruption, foreign dma-fence waits, array/chain priority tests, RPS boost behavior, and migration fence waits cover the behavior.
