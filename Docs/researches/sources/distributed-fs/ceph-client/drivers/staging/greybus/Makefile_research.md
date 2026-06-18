# sources/distributed-fs/ceph-client/drivers/staging/greybus/Makefile

## Purpose

The Greybus `Makefile` maps Kconfig symbols to module objects and composes multi-object Greybus drivers.

## Important APIs, Types, and Functions

It defines object groups such as `gb-bootrom-y`, `gb-firmware-y`, `gb-audio-module-y`, `gb-audio-codec-y`, `gb-audio-gb-y`, `gb-audio-apbridgea-y`, `gb-audio-manager-y`, bridged PHY groups, and `gb-arche-y`. `ccflags-y += -I$(src)` supports local trace/event includes.

## Control Flow

Kbuild includes objects through `obj-$(CONFIG_...)`. Enabling firmware builds `gb-firmware.o` plus `gb-spilib.o`; enabling audio builds several separate Greybus/ASoC modules; enabling APBridge codec builds both codec and audio-module objects; enabling bridged PHY builds the shared `gbphy.o` plus selected bus drivers.

## State and Persistence Behavior

No runtime state exists. The file controls build artifacts and module composition.

## Dependencies and Integration Points

The Makefile aligns with `Kconfig` and Linux kbuild. It also contains a commented optional path to include `audio_manager_sysfs.o` and define `GB_AUDIO_MANAGER_SYSFS` for debugging.

## Risks and Edge Cases

The optional audio manager sysfs debug support is commented out, so `audio_manager_sysfs.c` may not build unless manually enabled. `gb-audio-module.o` is tied to `GREYBUS_AUDIO_APB_CODEC`, while `gb-audio-gb`, `gb-audio-apbridgea`, and manager are tied to `GREYBUS_AUDIO`, creating a cross-module dependency surface. Module naming in Kconfig should be checked against the produced objects.

## Test Signals

Build each Kconfig symbol as built-in and module where possible. Verify optional audio sysfs compilation when uncommented, `gb-spilib.o` sharing between firmware/SPI, and no unresolved exports among split audio modules.
