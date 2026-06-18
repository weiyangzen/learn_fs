# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/Kconfig

## Purpose
Defines kernel configuration options for the Matrox G200 DRM/KMS driver and its optional write-combine disable mode.

## Important APIs, types, and functions
- `DRM_MGAG200` is a tristate depending on DRM and PCI and selecting client selection, GEM shmem helpers, KMS helpers, I2C, and I2C algobit.
- `DRM_MGAG200_DISABLE_WRITECOMBINE` is a PREEMPT_RT-specific bool that disables write-combine VRAM mappings.

## Control flow
This is build-time configuration only. Enabling `DRM_MGAG200` builds the mgag200 object. The write-combine option changes the VRAM mapping branch in `mgag200_device_preinit()`.

## State and persistence
No runtime state. The selected configuration persists in the kernel build and changes driver mapping behavior.

## Dependencies and integration points
Integrates with the DRM, PCI, KMS helper, GEM shmem, I2C, and I2C algobit subsystems. The write-combine toggle is consumed through `CONFIG_DRM_MGAG200_DISABLE_WRITECOMBINE`.

## Risks
Disabling write-combine can reduce framebuffer update performance but may be needed on real-time systems. Missing I2C selections would break DDC support, so the selects are part of the driver contract.

## Test signals
Configuration tests should cover module and built-in builds, PREEMPT_RT builds with write-combine disabled, and dependency resolution through `make olddefconfig` or similar Kconfig checks.
