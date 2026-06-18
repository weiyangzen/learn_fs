# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/Makefile

## Purpose
`zoran/Makefile` defines how the Zoran MJPEG driver object is assembled. It maps Kconfig symbols to the core object list and optional codec implementation objects.

## Important APIs, Types, And Functions
There are no runtime APIs. `zr36067-objs` always includes `zoran_device.o`, `zoran_driver.o`, `zoran_card.o`, and `videocodec.o`. `obj-$(CONFIG_VIDEO_ZORAN) += zr36067.o` emits the module/built-in object. Conditional object additions are `zr36067-$(CONFIG_VIDEO_ZORAN_DC30) += zr36050.o zr36016.o` and `zr36067-$(CONFIG_VIDEO_ZORAN_ZR36060) += zr36060.o`.

## Control Flow
Build flow follows Kbuild aggregation. The core driver is linked whenever `VIDEO_ZORAN` is enabled. Codec source files are compiled into the same final object only when their corresponding Kconfig symbols are enabled, matching the `#ifdef CONFIG_VIDEO_ZORAN_*` guards in `zoran_card.c`.

## State And Persistence
The file contributes build-time state only. Its choices persist in the generated kernel build artifacts and determine which `zr36016_init_module()`, `zr36050_init_module()`, or `zr36060_init_module()` symbols are available to the core code.

## Dependencies And Integration Points
It integrates with Linux Kbuild and `Kconfig`. The object composition matches logical layers: card/probe, V4L2/vb2 driver, hardware register engine, videocodec registry, and optional codec chips.

## Risks
If Kconfig and Makefile conditions drift, probe can compile references that are unavailable or omit codec implementations that board configuration expects. Since codec "modules" are linked into `zr36067.o` rather than separate loadable modules here, initialization/cleanup naming is internal and called manually by `zoran_card.c`.

## Test Signals
`make M=drivers/media/pci/zoran` or equivalent kernel builds should be checked for core-only, DC30, and ZR36060-enabled configurations. Link errors around codec init/cleanup functions would indicate Kconfig/Makefile mismatch.
