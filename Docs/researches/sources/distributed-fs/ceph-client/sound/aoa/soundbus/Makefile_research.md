# sources/distributed-fs/ceph-client/sound/aoa/soundbus/Makefile

## Purpose

This Makefile builds the generic AOA soundbus core and optionally recurses into the I2S bus implementation.

## Important APIs, types, and functions

It defines `obj-$(CONFIG_SND_AOA_SOUNDBUS) += snd-aoa-soundbus.o`, composes it from `core.o sysfs.o`, and adds `i2sbus/` under `CONFIG_SND_AOA_SOUNDBUS_I2S`.

## Control Flow

Kbuild includes generic bus code and sysfs support when soundbus is enabled, then recurses into I2S when selected.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It consumes soundbus Kconfig symbols and builds the bus exported to fabrics and I2S devices.

## Risks and Test Signals

Risks include omitting sysfs support or failing to recurse into I2S. Build tests should cover both symbols independently where dependencies allow.
