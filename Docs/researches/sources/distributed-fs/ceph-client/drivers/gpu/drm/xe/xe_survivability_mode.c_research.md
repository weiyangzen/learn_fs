<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.c

## Purpose

`xe_survivability_mode.c` implements boot and runtime survivability mode, a reduced driver mode for firmware recovery and telemetry when boot firmware or runtime firmware reaches a failed state.

## Important APIs, Types, and Functions

`xe_survivability_mode_is_requested()` checks platform support, configfs request state, and PCODE scratch boot status. `xe_survivability_mode_boot_enable()` enables boot survivability when requested. `xe_survivability_mode_runtime_enable()` creates survivability sysfs, marks the device wedged with vendor recovery, and tells userspace firmware flash is required. `xe_survivability_mode_is_boot_enabled()` reports active boot mode. Internal helpers populate scratch-register telemetry, expose sysfs attributes, initialize HECI GSC/VSEC/NVM/I2C services, and log critical boot data.

## Control Flow

Requested mode is limited to discrete, non-VF, Battlemage-or-newer devices. Boot enable reads PCODE breadcrumbs, rejects critical failures on breadcrumb versions before v2, sets type to boot, creates sysfs, marks `survivability->mode`, initializes recovery-capable auxiliary services, and optionally NVM when FDO mode is set. Runtime enable populates info, creates sysfs, sets type runtime, declares the device wedged, and returns success after notification.

## State and Persistence Behavior

`xe->survivability` stores scratch info, boot status, enabled mode, type, FDO mode, and breadcrumb version. Sysfs files persist until devm cleanup removes `survivability_mode`; the info group is devm-managed. Boot mode intentionally avoids full DRM card bring-up.

## Dependencies and Integration Points

The file integrates configfs, PCI/sysfs, MMIO PCODE scratch registers, HECI GSC, VSEC, NVM, I2C, pcode API bitfields, and Xe wedging notification.

## Risks and Test Signals

Risks include incorrect scratch linked-list traversal, sysfs creation failure leaving partial state, unsupported platform gating, and FDO/NVM init failure disabling mode. Tests should cover configfs request, PCODE critical/non-critical status, breadcrumb v1/v2 behavior, sysfs attribute visibility, runtime wedge signaling, and FDO mode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.c -->
