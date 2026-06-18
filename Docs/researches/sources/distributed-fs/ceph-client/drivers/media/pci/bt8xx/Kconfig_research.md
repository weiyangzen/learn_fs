# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/Kconfig

## Purpose
This Kconfig file exposes the analog `bttv` driver and the DVB/ATSC `bt878` support under the bt8xx PCI media driver family. It encodes the core build-time dependencies and optional subdevice selections needed for Brooktree/Conexant Bt848/Bt878 cards.

## Important APIs, Types, and Functions
There are no C APIs here. The important symbols are `VIDEO_BT848`, which builds the `bttv` module, and `DVB_BT8XX`, which builds DVB support for Bt878-based cards. `VIDEO_BT848` selects helpers such as `I2C_ALGOBIT`, `VIDEOBUF2_DMA_SG`, `VIDEO_TUNER`, `VIDEO_TVEEPROM`, radio support, and optional audio subdrivers. `DVB_BT8XX` depends on `VIDEO_BT848` and selects supported DVB frontends and simple tuner support when subdriver autoselect is enabled.

## Control Flow
The configuration dependency flow requires PCI, I2C, V4L2 video device support, RC core, and radio support before analog Bt848 support is visible. DVB support then layers on top of `VIDEO_BT848` and `DVB_CORE`, ensuring the base bt8xx capture/card infrastructure is present before the MPEG/DVB path is built.

## State and Persistence
Kconfig choices persist in the kernel configuration, not in runtime driver state. The symbols determine whether object files are compiled in, built as modules, or omitted.

## Dependencies and Integration Points
This file connects bt8xx drivers to the broader media stack, including V4L2, DVB core, I2C tuner/audio subdevices, RC input, videobuf2 DMA scatter-gather support, and radio adapters. The `DVB_BT8XX` entry mirrors the card list in `bttv-cards.c` and the device IDs in `bt878.c`.

## Risks and Edge Cases
Because `DVB_BT8XX` depends on `VIDEO_BT848`, disabling analog support also removes DVB support for these bridge chips. The `MEDIA_SUBDRV_AUTOSELECT` selections affect which frontend and audio modules are available automatically; minimal configs may require manual subdriver selection. `VIDEO_BT848` also depends on `MEDIA_RADIO_SUPPORT`, which can surprise users who only need capture boards.

## Test Signals
Check `oldconfig`/`menuconfig` visibility, module names (`bttv`, `bt878`, `dvb-bt8xx`, `dst`, `dst_ca`), selected frontend modules under `MEDIA_SUBDRV_AUTOSELECT`, and successful builds for built-in and modular combinations.
