# sources/distributed-fs/ceph-client/sound/usb/bcd2000/Makefile

## Purpose
Defines the Behringer BCD2000 ALSA module build.

## Important APIs, Types, and Functions
Builds `snd-bcd2000.o` from `bcd2000.o` under `obj-$(CONFIG_SND_BCD2000)`.

## Control Flow
Kbuild includes the module only when `SND_BCD2000` is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Driven by `sound/usb/Kconfig`; the source depends on ALSA rawmidi and USB core.

## Risks
Low risk; a missing object means the module has no implementation.

## Test Signals
Build as module and built-in.
