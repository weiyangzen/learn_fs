# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pci.c

## Purpose
Defines i915 PCI device matching, platform/device-info tables from gen2 through Meteor Lake/Arrow Lake-era IDs, force-probe policy, PCI resource validation, driver probe/remove/shutdown, and PCI driver registration.

## Important APIs, types, and functions
Public APIs are `i915_pci_register_driver()`, `i915_pci_unregister_driver()`, and `i915_pci_resource_valid()`. Key data includes many `struct intel_device_info` instances, feature macros (`GEN*_FEATURES`, `DGFX_FEATURES`, `XE_HP_FEATURES`), `pciidlist[]`, and `i915_pci_driver`. Probe helpers include `device_id_in_list()`, `id_forced()`, `id_blocked()`, `intel_mmio_bar_valid()`, `i915_pci_probe()`, `i915_pci_remove()`, and `i915_pci_shutdown()`.

## Control flow
PCI matching selects a device-info struct from `pciidlist`, ordered from specific to general. Probe enforces `require_force_probe`, honors negative force-probe block lists, taints the kernel when forcing unsupported IDs, rejects non-zero PCI functions, validates the MMIO BAR for the platform graphics IP, defers to display-driver probe dependency checks, calls `i915_driver_probe()`, then runs live and perf selftests with cleanup on failure. Remove calls `i915_driver_remove()` and clears drvdata. Shutdown delegates to `i915_driver_shutdown()`.

## State and persistence
Static device-info tables persist for the module lifetime and seed runtime platform state during probe. PCI driver registration persists with the kernel PCI core until unregister. Force-probe strings come from `i915_modparams`.

## Dependencies and integration points
Depends on DRM PCI ID macros, platform/device info structures, display probe defer logic, i915 driver probe/remove/shutdown, selftests, PCI resource APIs, force_probe module parameter, and PM ops.

## Risks
Device-info flags are foundational; wrong engine masks, memory regions, PAT/cache mappings, PPGTT sizes, or force-probe flags can break entire platforms. ID ordering matters for subsystem-specific matches. BAR validation must use the correct MMIO BAR by IP version. Force-probing unsupported hardware intentionally taints the kernel.

## Test signals
PCI ID binding across supported platforms, force_probe allow/block strings including `*` and `!*`, non-function-0 rejection, invalid BAR handling, probe defer, live/perf selftest failure cleanup, suspend/shutdown callbacks, and module unload unregister.
