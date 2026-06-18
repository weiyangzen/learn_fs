<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Kconfig

## Purpose
This Kconfig file defines optional, deprecated device-specific reset handlers for VFIO platform devices. These handlers let `vfio_platform_common.c` discover and call reset functions for compatible strings.

## Important APIs, types, and functions
The symbols are `VFIO_PLATFORM_CALXEDAXGMAC_RESET`, `VFIO_PLATFORM_AMDXGBE_RESET`, and `VFIO_PLATFORM_BCMFLEXRM_RESET`. All are tristate and visible only under `if VFIO_PLATFORM`. The Broadcom FlexRM option depends on `ARCH_BCM_IPROC || COMPILE_TEST` and defaults to `ARCH_BCM_IPROC`.

## Control flow
When the generic platform driver is enabled, users may select one or more reset handler modules. Those modules register compat-string callbacks through `module_vfio_reset_handler()` in their C files. The generic platform open/close/reset ioctl path then finds callbacks by device `compatible` string.

## State and persistence behavior
There is no runtime state here. Kconfig choices persist in the kernel build configuration and decide whether reset handlers are available for autoloading via `MODULE_ALIAS("vfio-reset:<compat>")`.

## Dependencies and integration points
This file integrates with the reset Makefile and the reset-handler registry in `vfio_platform_common.c`. The deprecation notices indicate these platform-specific resets are legacy maintenance points.

## Risks and test signals
The major risk is a platform device being assigned without a reset callback when `reset_required` is true, causing open or init failure. Test signals include module autoload by alias, compile coverage for each symbol, Broadcom dependency gating, and platform open/close reset behavior with and without selected handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Kconfig -->
