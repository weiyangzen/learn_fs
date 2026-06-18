# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gmch.c

## Purpose
`i915_gmch.c` manages legacy GMCH bridge discovery and MCHBAR enablement/resource allocation. It ensures memory-controller registers are accessible during early i915 MMIO/runtime-info probing.

## Important APIs, Types, and Functions
Public functions are `i915_gmch_bridge_setup()`, `i915_gmch_bar_setup()`, and `i915_gmch_bar_teardown()`. Internal helpers are `i915_gmch_bridge_release()`, `mchbar_reg()`, and `intel_alloc_mchbar_resource()`.

## Control Flow
Bridge setup locates bus 0 device/function 0 in the same PCI domain as the graphics device and registers a DRM-managed `pci_dev_put()` action. MCHBAR setup skips Valleyview/Cherryview, checks whether MCHBAR is already enabled via `DEVEN` on i915G/GM or the MCHBAR register on later chips, allocates a resource if ACPI/PNP did not reserve the current address, writes high/low address dwords as needed, marks that disable is required, and sets the enable bit. Teardown disables MCHBAR only if this driver enabled it and releases any allocated resource.

## State and Persistence Behavior
Persistent state lives in `i915->gmch`: bridge `pdev`, resource `mch_res`, and `mchbar_need_disable`. DRM-managed action releases the bridge reference with the DRM device. MCHBAR may remain enabled if firmware had already enabled it; the driver only disables self-enabled instances.

## Dependencies and Integration Points
The file depends on PCI config access, PNP reserved range checks, DRM managed actions, PCI resource allocation, platform predicates, and Intel PCI config register definitions. It is called from `i915_driver_mmio_probe()` before runtime device info reads and torn down in MMIO release.

## Risks
Incorrect resource allocation or enable bits can conflict with firmware/ACPI reservations or leave MCHBAR inaccessible. Teardown must not disable firmware-enabled MCHBAR. Legacy platform differences between i915G/GM and gen4+ are encoded in separate register paths. Missing bridge device aborts probe.

## Test Signals
Boot legacy GMCH systems with and without firmware-enabled MCHBAR, verify no resource conflicts, confirm runtime info reads dependent on MCHBAR, check teardown on probe failure, and inspect PCI config before/after driver unload.
