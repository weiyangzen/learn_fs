
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/Makefile

## Purpose
`hibmc/Makefile` defines the object composition for the Hisilicon HIBMC DRM driver.

## Important APIs, Types, And Functions
`hibmc-drm-y` links `hibmc_drm_drv.o`, `hibmc_drm_de.o`, `hibmc_drm_vdac.o`, `hibmc_drm_i2c.o`, DisplayPort objects `dp/dp_aux.o`, `dp/dp_link.o`, `dp/dp_hw.o`, `dp/dp_serdes.o`, the wrapper `hibmc_drm_dp.o`, and `hibmc_drm_debugfs.o`. `obj-$(CONFIG_DRM_HISI_HIBMC)` emits `hibmc-drm.o`.

## Control Flow
There is no runtime control flow. Kbuild links the display engine, analog output, I2C, DP AUX/link/hardware/serdes, top-level DP integration, debugfs, and PCI/DRM core into one module or built-in object.

## State And Persistence
The file owns build graph state only.

## Dependencies And Integration Points
It ties the DP AUX file in this work item to the rest of the HIBMC DP implementation and the main HIBMC DRM driver. Any new HIBMC source file must be added here to participate in the final driver.

## Risks
Missing an object can produce unresolved symbols or disable an output path. Since DP files are linked into the main HIBMC module, DP build failures prevent the whole driver from building.

## Test Signals
Build `CONFIG_DRM_HISI_HIBMC=m` and verify `hibmc-drm.ko` contains the listed DP, display engine, VDAC, I2C, and debugfs units with no unresolved symbols.
