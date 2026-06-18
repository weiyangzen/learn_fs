<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.h

## Purpose
`omap_device.h` declares the OMAP device wrapper that connects platform devices to hwmod metadata and exposes the small driver-facing enable/idle/reset interface.

## Important APIs, Types, and Functions
It defines device states `OMAP_DEVICE_STATE_UNKNOWN`, `ENABLED`, `IDLE`, and `SHUTDOWN`, flag `OMAP_DEVICE_SUSPENDED`, and `struct omap_device` with platform device, hwmod list, driver status, state, and flags. It declares `omap_device_enable()`, `omap_device_idle()`, hardreset assert/deassert helpers, and inline `to_omap_device()`.

## Control Flow
The header has no runtime control flow. The inline helper returns `pdev->archdata.od` when the platform device pointer is non-null.

## State and Persistence Behavior
The struct fields are runtime state owned by `omap_device.c`. No persistent data is defined.

## Dependencies and Integration Points
It depends on platform-device and OMAP hwmod definitions. It is consumed by OMAP platform drivers, reset helpers, and PM integration code.

## Risks
Changing state values, struct layout assumptions, or `to_omap_device()` semantics affects all hwmod-backed platform devices. The comment notes this should ideally be a proper bus, so legacy platform-data coupling is a maintenance risk.

## Test Signals
Compile all OMAP hwmod users. Runtime validation is successful `to_omap_device()` lookup, runtime PM enable/idle, hardreset calls, and no invalid-state warnings for correctly written drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.h -->
