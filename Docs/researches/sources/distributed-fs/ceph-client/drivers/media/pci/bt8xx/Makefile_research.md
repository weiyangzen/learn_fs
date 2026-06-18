# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/Makefile

## Purpose
The Makefile defines how the bt8xx media PCI drivers are assembled. It groups the many analog bttv implementation files into one `bttv.o` module and conditionally adds the DVB/ATSC-related bt878 modules.

## Important APIs, Types, and Functions
There are no runtime APIs. Important build variables are `bttv-objs`, `obj-$(CONFIG_VIDEO_BT848)`, `obj-$(CONFIG_DVB_BT8XX)`, and `ccflags-y`. `bttv-objs` pulls in driver, card, interface, RISC, VBI, I2C, GPIO, input, audio-hook, and shared RISC memory code.

## Control Flow
Kbuild links `bttv.o` when `CONFIG_VIDEO_BT848` is enabled. When `CONFIG_DVB_BT8XX` is enabled, it builds `bt878.o`, `dvb-bt8xx.o`, `dst.o`, and `dst_ca.o`. Additional include paths expose DVB frontend and tuner headers to these source files.

## State and Persistence
Build state is controlled by kernel configuration and Kbuild dependency tracking. No runtime state exists in this file.

## Dependencies and Integration Points
The file integrates the bt8xx directory with Linux media Kbuild, the DVB frontend include tree, and the media tuner include tree. It also ensures `btcx-risc.o` is linked into the analog bttv module where shared RISC memory helpers are used.

## Risks and Edge Cases
Adding code that uses DVB or tuner internals without matching include paths would break the build. Moving `btcx-risc.o` affects both compile and symbol availability for bttv internals. The DVB object list assumes `CONFIG_DVB_BT8XX` users need the DST support objects as part of the same family.

## Test Signals
Run targeted kernel builds for `CONFIG_VIDEO_BT848=m/y` and `CONFIG_DVB_BT8XX=m/y`, confirm `bttv.o` contains all listed objects, and check that frontend/tuner headers resolve without extra include path changes.
