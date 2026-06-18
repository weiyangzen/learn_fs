<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode_types.h

## Purpose

`xe_survivability_mode_types.h` defines the scratch-register identifiers and persistent survivability state.

## Important APIs, Types, and Functions

`enum scratch_reg` names capability, postcode trace, overflow, and auxiliary info registers. `enum xe_survivability_type` distinguishes boot and runtime. `struct xe_survivability` stores telemetry, scratch count, boot status, enabled flag, type, FDO mode, and breadcrumb version.

## Control Flow

The implementation reads PCODE scratch registers into `info[]`, sets `boot_status`, derives version/FDO bits, and uses `type` for sysfs display.

## State and Persistence Behavior

The struct persists in `struct xe_device` and represents current survivability state for sysfs and recovery flows.

## Dependencies and Integration Points

The header uses Linux integer limits/types and is included by survivability implementation and device state.

## Risks and Test Signals

The sysfs visibility code assumes `survivability_info_attrs[]` order matches `enum scratch_reg`. Tests should catch enum/order changes and version-gated FDO visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode_types.h -->
