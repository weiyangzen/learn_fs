<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.c

## Purpose

`xe_psmi.c` provides debugfs support for PSMI capture buffers. It allocates physically contiguous pinned VRAM GEM objects for selected memory regions and exposes their physical addresses and size to a userspace PSMI tool, while leaving register programming to userspace.

## Important APIs and Functions

Public functions are `xe_psmi_init()` and `xe_psmi_debugfs_register()`. Private helpers check configfs enablement, allocate/free pinned BOs, clean up all selected capture objects, resize allocation based on debugfs writes, show capture addresses, get/set capture size, and get/set capture region mask. Debugfs files are `psmi_capture_addr`, `psmi_capture_region_mask`, and `psmi_capture_size`.

## Control Flow and State

PSMI is disabled unless configfs enables it. Init registers a devm cleanup action. Debugfs registration creates files under the primary DRM minor. Users first set `psmi_capture_region_mask` to non-system memory regions, then write `psmi_capture_size`, which frees existing buffers, allocates one pinned VRAM BO per selected region, and stores it in `xe->psmi.capture_obj[id]`. Address reads print `region: physical_address` using `__xe_bo_addr()`. Region mask changes are rejected once buffers exist. Size zero frees all current buffers.

## Dependencies and Integration Points

The file depends on debugfs, Xe BO creation/pinning/unpinning, configfs, DRM minor debugfs roots, device-managed cleanup, memory region masks, and dGFX VRAM placement flags.

## Risks and Test Signals

Debugfs setters do not take a dedicated PSMI mutex in this file, so concurrent writes need external serialization guarantees from debugfs usage or additional locking if expanded. Size is documented as power-of-two but not validated here. System memory is explicitly unsupported. Tests should cover disabled mode, debugfs file creation, invalid region masks, SMEM rejection, busy region-mask change, size zero cleanup, allocation failure rollback, multi-tile address reporting, and devm cleanup unpinning all BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.c -->
