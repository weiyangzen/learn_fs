<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Makefile

## Purpose
This Makefile builds the optional VFIO platform reset handler modules selected by reset Kconfig.

## Important APIs, types, and functions
It maps `VFIO_PLATFORM_CALXEDAXGMAC_RESET` to `vfio-platform-calxedaxgmac.o`, `VFIO_PLATFORM_AMDXGBE_RESET` to `vfio-platform-amdxgbe.o`, and `VFIO_PLATFORM_BCMFLEXRM_RESET` to `vfio_platform_bcmflexrm.o`. The first two use `*-y` variables that point at C object names.

## Control flow
Kbuild emits each reset handler only when its Kconfig symbol is enabled. At module load time, each handler registers a compat callback with the VFIO platform reset registry.

## State and persistence behavior
No runtime state exists in the Makefile. Its persistent output is module/object availability.

## Dependencies and integration points
The build artifacts depend on `vfio_platform_private.h` for registration macros and on exported reset registry functions from the platform base module.

## Risks and test signals
Risk is mostly naming mismatch: two modules use hyphenated output module names while the Broadcom object keeps an underscore object path. Test signals are clean module builds, `modinfo` aliases, and successful reset handler registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/Makefile -->
