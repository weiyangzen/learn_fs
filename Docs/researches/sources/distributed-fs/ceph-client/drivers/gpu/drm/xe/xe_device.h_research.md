<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.h

## Purpose
`xe_device.h` is the public convenience and lifecycle header for the Xe DRM device object. It provides casts from DRM, PCI, kernel device, and TTM handles to `struct xe_device`, declares device create/probe/remove/shutdown entry points, and centralizes helpers for GT/tile lookup, memory access, address canonicalization, flushing, wedged state, and per-file references.

## Important APIs, types, and functions
The most used helpers are `to_xe_device()`, `kdev_to_xe_device()`, `pdev_to_xe_device()`, `ttm_to_xe_device()`, `to_xe_file()`, `xe_device_get_root_tile()`, `xe_device_get_gt()`, `xe_root_mmio_gt()`, and `xe_root_tile_mmio()`. Iteration macros cover tiles, remote tiles, all GTs, typed GTs, and GTs on a tile. Capability helpers expose UC submission, flat CCS, SR-IOV, MSI-X, memory IRQ, LMTT, and MERT. Declared operations include memory barriers, memory-access assertion, CCS byte sizing, device snapshot printing, canonical/uncanonical address conversion, TD/L2 flushing, wedged-state control, file refcounting, fault-injection status, file identity, and ASID-to-VM lookup.

## Control flow and integration points
Most control flow is inline dispatch around `xe->info.tile_count` and `xe->info.max_gt_per_tile`. `xe_device_get_gt()` maps a global GT id to tile primary/media GT, validates initialized GT identity, and returns NULL for out-of-range or missing GTs. These helpers are used throughout submission, memory management, sysfs, fdinfo, and PM code.

## State and persistence behavior
The header does not allocate state, but it exposes persistent device state in `struct xe_device`: tile arrays, capability flags, IRQ mode, wedged atomics, and per-file objects. `LNL_FLUSH_WORKQUEUE()` and `LNL_FLUSH_WORK()` intentionally map to workqueue flushes as a platform latency workaround.

## Dependencies, risks, and test signals
Dependencies are DRM core, TTM, Xe device types, GT types, and SR-IOV helpers. Risks are incorrect GT id mapping on multi-tile/media platforms, stale capability helpers, or wedged-state misuse. Test signals include probe/remove, multi-tile GT enumeration, SR-IOV PF/VF paths, memory IRQ enablement, ASID lookup, runtime suspend/resume, wedged uevents, and build coverage for all inline consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.h -->
