# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_throttle.c

## Purpose
This file implements the legacy `DRM_IOCTL_I915_GEM_THROTTLE` behavior. It limits CPU submission lead by waiting for this file's old outstanding requests, roughly preventing userspace from getting more than one frame ahead of the GPU.

## Important APIs, Types, and Functions
The sole exported ioctl handler is `i915_gem_throttle_ioctl`. `DRM_I915_THROTTLE_JIFFIES` is a 20 ms threshold used to choose requests old enough to wait on.

## Control Flow
The ioctl first returns terminal wedge status for ABI compatibility. It walks all contexts in the file private context xarray under RCU, takes a context ref, locks the context engine set, and for each engine timeline scans requests in reverse order. It skips completed requests and requests emitted more recently than the threshold, takes a reference to the first old incomplete request, drops the timeline mutex, waits interruptibly forever for that request, then continues unless interrupted.

## State and Persistence Behavior
No persistent state is stored. The function temporarily references contexts and requests and observes per-timeline request lists. It can cause scheduling latency by blocking the caller until selected requests complete.

## Dependencies and Integration Points
It depends on DRM file private state, GEM contexts and engine iteration, request timelines, terminal wedge reporting, jiffies timekeeping, and `i915_request_wait`.

## Risks
Timeline scanning assumes request list ordering and correct `emitted_jiffies`. The wait is unbounded except for signals. RCU is dropped and reacquired around context processing, so context lifetime must be protected by refs. This is legacy latency policy, not a precise frame pacing mechanism.

## Test Signals
Throttle ioctl ABI tests, wedged-device return tests, multi-context/multi-engine request submission, signal interruption, and frame-latency workloads show whether behavior remains compatible.
