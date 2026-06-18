# sources/distributed-fs/ceph-client/drivers/media/cec/platform/s5p/Makefile

## Purpose
This Makefile builds the Samsung S5P/Exynos HDMI CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_SAMSUNG_S5P` to the composite object `s5p-cec.o`, with `s5p-cec-y` made from `s5p_cec.o` and `exynos_hdmi_cecctrl.o`.

## Control Flow
Kbuild compiles the framework-facing driver and low-level register-control helper into one module or built-in object depending on the Kconfig setting.

## State and Persistence
No runtime state is present. The file defines build composition only.

## Dependencies and Integration Points
It depends on the surrounding Kconfig selecting `CONFIG_CEC_SAMSUNG_S5P`. The split confirms that `s5p_cec.c` can call helper functions implemented in `exynos_hdmi_cecctrl.c`.

## Risks and Test Signals
Build tests should verify both objects are linked and exported helper prototypes match. A missing helper object would produce unresolved symbols for reset, divider, interrupt-mask, TX, RX, and status routines.
