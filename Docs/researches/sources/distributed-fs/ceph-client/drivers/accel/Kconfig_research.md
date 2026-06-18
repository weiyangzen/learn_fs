# sources/distributed-fs/ceph-client/drivers/accel/Kconfig

## Purpose
This file defines the compute acceleration driver menu under DRM. It introduces `CONFIG_DRM_ACCEL`, the framework gate for accelerator devices exposed separately from GPUs.

## Important APIs, Types, And Functions
The key symbol is `menuconfig DRM_ACCEL`, a boolean visible only within `if DRM`. Its help text explains `/dev/accel/accel*` device exposure and shared DRM infrastructure. It sources vendor/device submenus including AMD XDNA, Ethos-U, habanalabs, IVPU, QAIC, and Rocket.

## Control Flow
If `CONFIG_DRM` is enabled, users can enable the compute acceleration framework and then select individual accelerator drivers from the sourced submenus. If DRM is disabled, this entire menu is omitted.

## State, Dependencies, Integration, Risks, And Tests
State is Kconfig selection propagated to `drivers/accel/Makefile`. Dependencies include DRM and all sourced vendor Kconfig paths. Risks are hiding accelerator drivers unintentionally behind DRM, missing sourced files, or help text drifting from device-node behavior. Test signals include menu visibility with DRM on/off and build coverage for each sourced driver symbol.
