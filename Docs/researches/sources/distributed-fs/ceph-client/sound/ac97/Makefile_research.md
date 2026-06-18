# sources/distributed-fs/ceph-client/sound/ac97/Makefile

## Purpose

This Makefile builds the new AC97 bus module and optionally includes the compatibility layer.

## Important APIs, types, and functions

It defines `obj-$(CONFIG_AC97_BUS_NEW) += ac97.o`, `ac97-y += bus.o codec.o`, and `ac97-$(CONFIG_AC97_BUS_COMPAT) += snd_ac97_compat.o`.

## Control Flow

Kbuild composes `ac97.o` from the core bus and codec compilation units, adding `snd_ac97_compat.o` only when enabled.

## State and Persistence

No runtime state exists here. It controls object composition.

## Dependencies and Integration Points

It consumes `AC97_BUS_NEW` and `AC97_BUS_COMPAT` from Kconfig and builds the files that export new AC97 controller and codec-driver APIs.

## Risks and Test Signals

Risks are build-level: missing compat object when needed or duplicate reset symbols when legacy AC97 is enabled. Test by compiling all intended AC97 config combinations.
