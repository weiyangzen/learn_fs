# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_utils.c

## Purpose
This file provides small environment-detection helpers for display code, currently focused on virtualization and IOMMU/VT-d assumptions.

## Important APIs, Types, and Functions
`intel_display_run_as_guest()` returns whether the system is running under a non-native x86 hypervisor when `CONFIG_X86` is enabled, and false otherwise. `intel_display_vtd_active()` returns true if the display device is IOMMU-mapped or, as a fallback, if it is running as a guest.

## Control Flow
The guest check is compile-time gated by `IS_ENABLED(CONFIG_X86)`. VT-d detection first calls `device_iommu_mapped(display->drm->dev)`. If that is false, it assumes host-enforced VT-d for virtualized guests by calling `intel_display_run_as_guest()`.

## State and Persistence Behavior
No state is stored. Results are derived from current kernel device/IOMMU and hypervisor state.

## Dependencies and Integration Points
Dependencies include Linux device APIs, DRM device, optional x86 hypervisor APIs, `intel_display_core.h`, and the public utils header. These helpers can influence display paths sensitive to DMA remapping, guard pages, or guest behavior.

## Risks
The guest fallback is intentionally conservative and may report VT-d active even without direct guest visibility into host remapping. Non-x86 always returns not guest, so architectures without implementation may miss equivalent virtualization handling. Callers must treat these as policy helpers, not proof of a specific IOMMU configuration.

## Test Signals
Signals include builds with and without `CONFIG_X86`, bare-metal versus VM behavior, IOMMU-on/off boot tests, and display memory/DMA paths that branch on VT-d activity.
