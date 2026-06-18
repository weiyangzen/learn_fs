# sources/distributed-fs/ceph-client/sound/usb/usx2y/Makefile

## Purpose

This Makefile defines the ALSA USB usx2y-family kernel module objects. It maps Kconfig symbols to composite object targets for the legacy TASCAM US-X2Y, US-122L, and US-144MKII drivers.

## Important Targets

- `snd-usb-usx2y-y := usbusx2y.o usX2Yhwdep.o usx2yhwdeppcm.o` builds the original US-X2Y module.
- `snd-usb-us122l-y := us122l.o` builds the US-122L/US-144/US-122MKII driver module from one source object.
- `snd-usb-us144mkii-y := ...` builds the US-144MKII module from core, PCM, MIDI, playback, capture, and controls objects.
- `obj-$(CONFIG_SND_USB_USX2Y)`, `obj-$(CONFIG_SND_USB_US122L)`, and `obj-$(CONFIG_SND_USB_US144MKII)` include modules conditionally by Kconfig.

## Control Flow And State

There is no runtime control flow or state. The file affects build graph composition only.

## Dependencies And Integration Points

The object lists depend on source files in the same directory and Kconfig symbols defined elsewhere in the ALSA USB build. `us122l.o` includes `usb_stream.c` directly from `us122l.c`, so this Makefile only lists `us122l.o` for that module.

## Risks

- Missing an object in a composite target causes link failures or missing driver functionality.
- Renaming source files without updating this Makefile breaks module builds.
- Because `us122l.c` includes implementation code directly, adding `usb_stream.o` separately here would likely create duplicate definitions.

## Test Signals

- Kernel build with each `CONFIG_SND_USB_*` option enabled as module and built-in.
- Module load tests for `snd-usb-us122l`, `snd-usb-usx2y`, and `snd-usb-us144mkii`.
