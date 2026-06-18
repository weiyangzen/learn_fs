# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/Makefile

## Purpose
The Makefile maps the Kconfig symbols for the Exynos4 camera subsystem to concrete object lists and loadable module targets.

## Important APIs, Types, and Functions
It builds `s5p-fimc-objs` from FIMC core, register, mem2mem, capture, and media-device code. It builds `exynos-fimc-lite-objs`, `s5p-csis-objs`, and `exynos4-is-common-objs`. `exynos-fimc-is-objs` combines FIMC-IS core, ISP, sensor, register, parameter, error, and ISP-I2C code, with `fimc-isp-video.o` appended when `CONFIG_VIDEO_EXYNOS4_ISP_DMA_CAPTURE=y`.

## Control Flow
There is no runtime control flow. Kbuild expands `obj-$(CONFIG_...)` lines to include or omit each module or built-in object.

## State and Persistence
Build state is produced under the kernel object tree. The file stores no runtime state.

## Dependencies and Integration Points
This file integrates the directory with Kbuild and the Kconfig symbols defined in the sibling `Kconfig`. Object grouping determines module boundaries and therefore symbol visibility and initialization order within each module.

## Risks and Edge Cases
Changing object membership can break module init dependencies, especially FIMC-IS registering its private ISP-I2C driver before the platform driver. Optional ISP DMA capture must remain conditional or references to video capture objects may appear without the corresponding Kconfig support.

## Test Signals
Build tests should check each individual symbol as module and built-in, verify `exynos-fimc-is` links with and without ISP DMA capture, and confirm module names match user-visible Kconfig help text.
