<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.h

## Purpose

`xe_psmi.h` declares the PSMI capture-buffer initialization and debugfs registration hooks.

## Important APIs

`xe_psmi_init(struct xe_device *xe)` registers cleanup when PSMI is enabled. `xe_psmi_debugfs_register(struct xe_device *xe)` creates the debugfs files used by the PSMI userspace tool.

## Control Flow and State

The header has no state. The implementation uses `xe->psmi` fields to store selected memory regions and capture BOs.

## Dependencies and Integration Points

It forward-declares `struct xe_device` and is used by device init/debugfs setup.

## Risks and Test Signals

Call ordering matters: debugfs registration should happen after the DRM minor debugfs root exists and init should register cleanup before buffers can be allocated. Tests should cover disabled configfs behavior and cleanup after debugfs-driven allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_psmi.h -->
