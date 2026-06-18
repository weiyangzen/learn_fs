<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.c

## Purpose
Implements small i915 utility functions for CI tainting, VT-d/guest detection, and Meteor Lake direct stolen-memory access policy.

## Important APIs, types, and functions
- `add_taint_for_CI()` logs a CI taint reason and calls `__add_taint_for_CI()`.
- `i915_vtd_active()` returns true when the device is IOMMU mapped or the driver runs as a guest.
- `i915_direct_stolen_access()` implements Wa_22018444074 policy for direct GSM/DSM access on Meteor Lake when firmware permits it and the driver is not in a guest.

## Control flow
VT-d detection first asks the device IOMMU API, then treats guests as protected by the host. Direct stolen access checks platform, guest status, and `MTL_PCODE_STOLEN_ACCESS` register value through uncore.

## State and persistence
No local persistent state is stored. CI taint affects global kernel taint state. Direct-access decisions reflect current platform and firmware register state.

## Dependencies and integration points
Depends on DRM logging, device IOMMU APIs, i915 platform detection, uncore register access, and register definitions from `i915_reg.h`. Used by memory-management and CI/error-handling paths.

## Risks
Guest detection is architecture-limited; non-x86 returns false. Incorrect direct stolen-memory access policy can hang MTL systems or break guests that cannot access GSM/DSM directly. CI tainting intentionally marks the kernel as unreliable for automated testing.

## Test signals
CI taint log/taint-state checks, IOMMU-on/off boot tests, guest VM tests, MTL firmware register validation, and stolen-memory access tests on MTL and non-MTL systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.c -->
