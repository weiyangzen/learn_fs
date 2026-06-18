# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/Makefile

## Purpose
This Makefile assembles the ivtv driver objects and optional companion modules.

## Important APIs, Types, And Data
`ivtv-objs` includes routing, card tables, controls, driver core, file ops, firmware, GPIO, I2C, ioctl, IRQ, mailbox, queues, streams, UDMA, VBI, and YUV objects. `ivtv-alsa-objs` includes `ivtv-alsa-main.o` and `ivtv-alsa-pcm.o`. Object inclusion follows `CONFIG_VIDEO_IVTV`, `CONFIG_VIDEO_IVTV_ALSA`, and `CONFIG_VIDEO_FB_IVTV`. Additional include paths point to media tuners and DVB frontends.

## Control Flow
No runtime flow exists; this file controls build composition.

## State And Persistence
No state is represented.

## Dependencies And Integration Points
It maps Kconfig selections to module objects and includes tuner/frontend headers needed by ivtv source files.

## Risks And Test Signals
Build tests should verify that `ivtv-alsa` links only when ALSA support is enabled and that include paths remain valid after media tree moves.
