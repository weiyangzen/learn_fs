# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/Kconfig

Purpose: defines the Kconfig symbol for the Raspberry Pi PiSP Back End ISP driver.

Important APIs/types/functions: `config VIDEO_RASPBERRYPI_PISP_BE` is tristate, depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, `ARCH_BCM2835 || COMPILE_TEST`, and `PM`; selects `VIDEO_V4L2_SUBDEV_API`, `MEDIA_CONTROLLER`, and `VIDEOBUF2_DMA_CONTIG`.

Control flow: selecting the symbol controls whether `pisp-be.o` is built and registered as a module/built-in.

State and persistence: kernel config state only.

Dependencies and integration: the selects match `pisp_be.c` usage of V4L2 subdevices, media controller entities/links, runtime PM, and dma-contig vb2 queues.

Risks: missing dependencies would surface as link/build errors or runtime unavailable subsystems. The `ARCH_BCM2835 || COMPILE_TEST` gate limits production visibility to Raspberry Pi platforms but keeps build testing broad.

Test signals: build with `m`, `y`, and disabled; compile-test on non-BCM platforms; modinfo should report module name `pisp-be`.
