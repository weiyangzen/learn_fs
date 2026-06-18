<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.c

## Purpose
Implements Intel GVT-g vGPU detection, capability queries, display-ready notification, and GGTT address-space ballooning/deballooning for guest drivers.

## Important APIs, types, and functions
- `intel_vgpu_detect()` maps the PVINFO MMIO page, validates magic/version, records capabilities, initializes vGPU state, and logs detection.
- `intel_vgpu_register()` writes display-ready state for active vGPUs.
- Capability queries: `intel_vgpu_active()`, `intel_vgpu_has_full_ppgtt()`, `intel_vgpu_has_hwsp_emulation()`, and `intel_vgpu_has_huge_gtt()`.
- Ballooning APIs: `intel_vgt_balloon()` and `intel_vgt_deballoon()`.
- Internal helpers reserve/deallocate unavailable GGTT ranges with `vgt_balloon_space()` and `vgt_deballoon_space()`.

## Control flow
Detection runs early before normal uncore MMIO setup, maps the PCI BAR range containing PVINFO, rejects older graphics versions, checks `VGT_MAGIC` and interface version, reads caps, and marks vGPU active. Ballooning reads mappable and unmappable guest-owned graphics memory ranges from PVINFO registers, validates them against GGTT mappable and total boundaries, then reserves all gaps before, between, and after those ranges. On partial failure it rolls back earlier reservations.

## State and persistence
Persistent state includes `dev_priv->vgpu.active`, capability bits, vGPU lock, and a static `_balloon_info_` containing up to four `drm_mm_node` reservations. Ballooned GGTT nodes reduce `ggtt->vm.reserved` until deballooned.

## Dependencies and integration points
Depends on PCI BAR mapping, DRM logging, PVINFO structures/register macros, i915 GGTT reservation APIs, uncore register access, and display-ready integration after modeset. Used during driver initialization and cleanup in virtualized environments.

## Risks
Balloon configuration from the host must be valid; invalid ranges are rejected. Static balloon info assumes one active relevant vGPU instance in this driver context. Reservation/deballoon accounting must stay balanced or GGTT space can leak. Detection cannot use normal uncore access because it runs before those mappings exist.

## Test signals
GVT-g guest boot detection logs, capability-dependent paths, display-ready notification observed by host, valid/invalid balloon configuration tests, GGTT reservation accounting, unload deballoon cleanup, and non-vGPU bare-metal no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.c -->
