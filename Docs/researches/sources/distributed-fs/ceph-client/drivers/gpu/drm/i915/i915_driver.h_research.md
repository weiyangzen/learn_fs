# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_driver.h

## Purpose
This header is the small public-internal interface for the i915 top-level driver module. It names the driver, exposes power-management operations, declares PCI probe/remove/shutdown entry points, switcheroo suspend/resume helpers, display parent-interface access, and IOMMU status printing.

## Important APIs, Types, and Functions
It defines `DRIVER_NAME` as `"i915"` and `DRIVER_DESC` as `"Intel Graphics"`. Exports are `i915_pm_ops`, `i915_driver_probe()`, `i915_driver_remove()`, `i915_driver_shutdown()`, `i915_driver_resume_switcheroo()`, `i915_driver_suspend_switcheroo()`, `i915_driver_parent_interface()`, and `i915_print_iommu_status()`. Forward declarations keep dependencies light for PCI, DRM private state, DRM printers, and display parent interfaces.

## Control Flow
There is no implementation control flow. The declarations are consumed by PCI driver registration code, switcheroo code, display code, and diagnostic paths. Calls flow from Linux PCI/PM entry points into `i915_driver.c`, while display code calls `i915_driver_parent_interface()` to acquire parent callbacks.

## State and Persistence Behavior
The header stores no state. It defines ABI-like internal linkage for the singleton `i915_pm_ops` and for functions operating on persistent `struct drm_i915_private` instances.

## Dependencies and Integration Points
The header depends only on `linux/pm.h` for `pm_message_t` and forward declarations. It is the integration point between i915 core, PCI binding, runtime/system PM, VGA switcheroo, display parent code, and debug printing.

## Risks
Because this header is widely included, adding heavy includes can increase rebuild scope or create dependency cycles. The function declarations must stay aligned with `i915_driver.c`; changing names or signatures breaks PCI, PM, and display integration. `DRIVER_NAME` is user-visible in DRM registration and logs.

## Test Signals
Build coverage is the primary signal. Runtime signals are successful PCI probe/remove, PM callback registration, switcheroo operation, display parent interface retrieval, and IOMMU status appearing in debug device info dumps.
