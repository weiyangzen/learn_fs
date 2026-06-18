# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gpu_error.h

## Purpose
`i915_gpu_error.h` defines the structures and APIs for i915 GPU coredump/error capture. It is the shared contract between reset/hang paths, GT/engine capture code, debugfs/sysfs exposure, and no-op builds when error capture is disabled.

## Important APIs, Types, and Functions
Key structs are `i915_vma_coredump`, `i915_request_coredump`, `intel_engine_coredump`, `intel_ctb_coredump`, `intel_gt_coredump`, `i915_gpu_coredump`, `i915_gpu_error`, and `drm_i915_error_state_buf`. Inlines expose reset counters and increment engine reset counts. APIs include capture allocation for GPU/GT/engine, request/VMA coredump addition, VMA compression prepare/finish, error state store/reset/disable, kref get/put, copy-to-buffer, debugfs/sysfs registration, and optional klog capture. `CORE_DUMP_FLAG_IS_GUC_CAPTURE` marks GuC-sourced register capture.

## Control Flow
When `CONFIG_DRM_I915_CAPTURE_ERROR` is enabled, callers can allocate coredumps, add engine/request/VMA state, store the first error, expose it, and reset it. When disabled, the same APIs compile to stubs that do nothing or return NULL, allowing callers to avoid preprocessor complexity. Reset count inlines always operate on atomics in `i915_gpu_error`.

## State and Persistence Behavior
`i915_gpu_error` persists in `drm_i915_private` and holds `first_error`, global reset count, and per-engine-class reset counts. Coredump structs are snapshot-owned and kref-counted. Engine and GT coredumps are linked lists; VMA coredumps own copied page lists; formatted output may be cached as scatterlists.

## Dependencies and Integration Points
The header depends on atomic/kref/time/sched, DRM MM, Intel engine/GT/uC firmware types, device info, GEM/GTT, params, and scheduler types. It is included by driver core, reset paths, GT code, GEM capture paths, and user-visible debug setup.

## Risks
The structures are large and tightly coupled to register-generation behavior. Adding fields requires updating allocation, printing, and cleanup. Stubs must preserve call-site expectations in non-capture builds. Reset engine count indexes by engine class, so class bounds must remain valid.

## Test Signals
Build with capture enabled/disabled, debug GEM enabled/disabled, GuC capture paths, reset counter updates, first-error lifetime/refcount tests, and userspace error-state reads.
