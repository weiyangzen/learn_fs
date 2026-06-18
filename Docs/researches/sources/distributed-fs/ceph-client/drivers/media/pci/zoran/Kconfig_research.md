# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/Kconfig

## Purpose
`zoran/Kconfig` declares configuration options for the deprecated Zoran ZR36057/ZR36067 Video4Linux MJPEG driver and board-specific support variants. It controls whether the core driver and optional codec modules are built into the `zr36067` object.

## Important APIs, Types, And Functions
This is Kconfig metadata, not C code. The primary symbol is `VIDEO_ZORAN`, a tristate depending on `PCI`, `I2C_ALGOBIT`, `VIDEO_DEV`, `DEBUG_FS`, and not `ALPHA`. It selects `VIDEOBUF2_DMA_CONTIG` and conditionally selects I2C decoder/encoder drivers for supported boards. Boolean board symbols include `VIDEO_ZORAN_DC30`, `VIDEO_ZORAN_ZR36060`, `VIDEO_ZORAN_BUZ`, `VIDEO_ZORAN_DC10`, `VIDEO_ZORAN_LML33`, `VIDEO_ZORAN_LML33R10`, and `VIDEO_ZORAN_AVS6EYES`.

## Control Flow
Build-time control flow is dependency driven. Enabling `VIDEO_ZORAN` builds the core driver. Enabling `VIDEO_ZORAN_DC30` includes support for the ZR36050 MJPEG codec and ZR36016 VFE path. Enabling `VIDEO_ZORAN_ZR36060` unlocks boards using the ZR36060 codec; board-specific options under it select the needed I2C subdevice drivers.

## State And Persistence
Kconfig choices persist in the kernel configuration and determine compiled capabilities. They do not create runtime state directly, but they decide whether `codec_init()` in `zoran_card.c` can register codec implementations or returns unsupported errors.

## Dependencies And Integration Points
The file integrates with the Linux media Kconfig tree, PCI, bit-banged I2C, V4L2, videobuf2 DMA-contig, debugfs, and numerous media I2C subdevice drivers. The help text points users to Zoran driver documentation and states the module name as `zr36067`.

## Risks
Missing board options can produce runtime probe failures when `zoran_card.c` attempts to initialize a codec compiled out of the build. The driver is explicitly marked deprecated and depends on `DEBUG_FS`, making it unavailable in configurations that omit debugfs. Conditional `select` usage means board options may pull in legacy I2C components.

## Test Signals
Build tests should cover `VIDEO_ZORAN=m`, `VIDEO_ZORAN_DC30=y`, and `VIDEO_ZORAN_ZR36060=y` combinations, plus individual board selections. Runtime probe should confirm expected codec support messages rather than "support is not enabled" errors for configured boards.
