# sources/distributed-fs/ceph-client/sound/usb/caiaq/Makefile

## Purpose
Defines Kbuild composition for the Native Instruments/CAIAQ USB audio driver.

## Important APIs, Types, and Functions
`snd-usb-caiaq-y` includes `device.o`, `audio.o`, `midi.o`, and `control.o`; `snd-usb-caiaq-$(CONFIG_SND_USB_CAIAQ_INPUT)` conditionally adds `input.o`. `obj-$(CONFIG_SND_USB_CAIAQ)` builds `snd-usb-caiaq.o`.

## Control Flow
Kbuild conditionally includes Linux input support in the same module when enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Driven by `SND_USB_CAIAQ` and `SND_USB_CAIAQ_INPUT` Kconfig symbols.

## Risks
Input support is compile-time optional; code paths in `device.c` are guarded by `CONFIG_SND_USB_CAIAQ_INPUT`, so object selection must match those guards.

## Test Signals
Build CAIAQ with input enabled and disabled.
