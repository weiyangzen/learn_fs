# sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/Makefile

## Purpose

This Makefile builds the Apple I2S soundbus implementation module.

## Important APIs, types, and functions

It adds `snd-aoa-i2sbus.o` under `CONFIG_SND_AOA_SOUNDBUS_I2S` and composes it from `core.o`, `pcm.o`, and `control.o`.

## Control Flow

Kbuild conditionally links the I2S bus core, PCM, and control routines.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It consumes the I2S soundbus Kconfig symbol and builds code used by the layout fabric through generic soundbus devices.

## Risks and Test Signals

Risks are build-wiring issues. Build tests should compile I2S support built-in and modular.
