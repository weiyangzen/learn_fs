# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/Makefile

## Purpose
Builds MMP display hardware controller and optional SPI master objects.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_MMP_DISP_CONTROLLER) += mmp_ctrl.o`.
- `obj-$(CONFIG_MMP_DISP_SPI) += mmp_spi.o`.

## Control Flow
Kbuild includes hardware support objects according to Kconfig selections.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects MMP hardware implementation sources to the kernel build.

## Risks
If `mmp_spi.o` is omitted, panel drivers expecting the LCD SPI bus will not probe unless another SPI controller provides the bus/device.

## Test Signals
Build with both Kconfig options and verify object inclusion.
