# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_getparam.c

## Purpose
`i915_getparam.c` implements the legacy `DRM_IOCTL_I915_GETPARAM` UAPI. It reports chipset IDs, engine availability, memory/cache capabilities, reset and scheduler capabilities, firmware/PXP status, mmap/perf versions, topology fields, and timestamp frequencies.

## Important APIs, Types, and Functions
The exported entry point is `i915_getparam_ioctl()`. It consumes `drm_i915_getparam_t`, writes to `param->value`, and switches on `I915_PARAM_*` constants. It calls helpers such as `intel_engine_lookup_user()`, `intel_overlay_available()`, `i915_cmd_parser_get_version()`, `intel_sseu_subslice_total()`, `intel_huc_check_status()`, `intel_pxp_get_readiness_status()`, `i915_gem_mmap_gtt_version()`, `intel_engines_has_context_isolation()`, and i915 perf timestamp/version helpers.

## Control Flow
The ioctl rejects old UMS/DRI parameters with ENODEV, returns PCI device/revision and fence counts directly, checks UABI engine lookup for BSD/BLT/VEBOX/BSD2, returns feature macros for LLC/WT/PPGTT/secure batches, gates secure batches on `CAP_SYS_ADMIN`, reports scheduler bits, GuC-dependent context frequency hints, context isolation, and topology masks. Xe_HP and newer reject legacy slice/subslice masks in favor of topology queries. Unknown parameters log a debug message and return EINVAL. The final value is copied to userspace with `put_user()`.

## State and Persistence Behavior
The function reads current immutable or semi-persistent device state: PCI IDs, GGTT fences, engine registry, runtime SSEU topology, scheduler caps, module params, firmware readiness, PXP readiness, GT clock frequency, coherent GGTT flag, and perf timestamp frequency. It does not mutate driver state.

## Dependencies and Integration Points
It integrates legacy i915 UAPI, PCI, display overlay, engine UABI registry, command parser, SSEU topology, GuC/HuC/PXP, GEM mmap versioning, scheduler caps, perf OA, and capability macros from `i915_drv.h`.

## Risks
This is user-visible ABI. Values must remain compatible even when newer query ioctls exist. Returning true for always-supported features is intentional for historical UAPI, but unsupported hardware exceptions must be explicit. Topology deprecation boundaries such as Xe_HP must remain correct. Firmware/PXP helpers can return negative errors that propagate to userspace.

## Test Signals
IGT `getparam` coverage for every parameter, unknown-param EINVAL, invalid userspace pointer EFAULT, capability values on platforms with/without engines and GuC/PXP/HuC, topology mask behavior before and after Xe_HP, and perf timestamp frequency sanity.
