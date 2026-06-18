# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/Kconfig

## Purpose
This Kconfig file declares Marvell media platform driver options for two camera controller integrations built on the shared MCAM core: the PCI-based Marvell 88ALP01 Cafe CCIC controller and the platform-device Armada 610/MMP camera controller.

## Important APIs, Types, And Functions
There are no C APIs. `VIDEO_CAFE_CCIC` is a tristate for the 88ALP01 Cafe controller and depends on media platform drivers, PCI, I2C, `VIDEO_DEV`, and `COMMON_CLK`. It selects V4L2 async support, optional OV7670 autoselection, and vb2 vmalloc, DMA-contig, and DMA-SG backends. `VIDEO_MMP_CAMERA` is a tristate for Marvell Armada 610/MMP camera controllers and depends on I2C, `VIDEO_DEV`, `ARCH_MMP || COMPILE_TEST`, and `COMMON_CLK`. It selects OV7670 autoselection, `I2C_GPIO`, V4L2 async, and the same vb2 memory backends.

## Control Flow And State
The file controls build inclusion only. The selected memory backends are important because `mcam-core.c` conditionally compiles support for vmalloc, contiguous DMA, and scatter-gather modes based on vb2 backend symbols.

## Dependencies And Integration Points
The adjacent Makefile uses `CONFIG_VIDEO_CAFE_CCIC` to build `cafe_ccic.o` plus `mcam-core.o`, and `CONFIG_VIDEO_MMP_CAMERA` to build `mmp_camera.o` plus `mcam-core.o`. Both drivers integrate with external OV7670 sensor support when media subdevice autoselection is enabled.

## Risks
Because the shared MCAM core conditionally compiles buffer modes from selected vb2 backends, changing selected symbols can remove runtime buffer modes. The Cafe driver is PCI/I2C-specific while MMP is platform/OF-specific, so dependency broadening under `COMPILE_TEST` must retain the support APIs they include. Selecting all three vb2 backends increases build coverage but also exposes code paths that platform defaults may not normally use.

## Test Signals
Build `VIDEO_CAFE_CCIC=m` and `VIDEO_MMP_CAMERA=m`, including `COMPILE_TEST` for MMP on non-MMP architectures. Check that `mcam-core.o` links correctly into each module and that OV7670 autoselection behaves as expected under media subdriver autoselect configurations.
