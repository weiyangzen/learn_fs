# sources/distributed-fs/ceph-client/sound/usb/6fire/Makefile

## Purpose
Defines the TerraTec DMX 6Fire USB ALSA module composition.

## Important APIs, Types, and Functions
Build variables are `snd-usb-6fire-y` and `obj-$(CONFIG_SND_USB_6FIRE)`. The module is assembled from `chip.o`, `comm.o`, `midi.o`, `control.o`, `firmware.o`, and `pcm.o`.

## Control Flow
Kbuild compiles the object list into `snd-usb-6fire.o` when `CONFIG_SND_USB_6FIRE` is enabled as built-in or module.

## State and Persistence
No runtime state. It persists the compile-time binding between Kconfig selection and driver objects.

## Dependencies and Integration Points
Depends on `sound/usb/Kconfig` selecting `SND_USB_6FIRE`. The listed objects mutually depend on shared headers under the same directory.

## Risks
Leaving out any object breaks probe, firmware, MIDI, PCM, or mixer functionality. Object order is conventional and does not encode init order; runtime init order is in `chip.c`.

## Test Signals
Build with `CONFIG_SND_USB_6FIRE=m` and `=y`; verify produced module exports one USB driver and includes firmware declarations.
