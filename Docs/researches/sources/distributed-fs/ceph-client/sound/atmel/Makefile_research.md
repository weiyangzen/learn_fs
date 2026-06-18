# sources/distributed-fs/ceph-client/sound/atmel/Makefile

## Purpose
This Makefile maps `CONFIG_SND_ATMEL_AC97C` to the Atmel AC97C ALSA driver object.

## Important APIs, Types, And Functions
It builds `snd-atmel-ac97c.o` from `ac97c.o` when the Kconfig symbol is enabled.

## Control Flow
There is no runtime flow. Kbuild expands the object rule according to configuration.

## State And Persistence
No runtime state exists. The file persists build composition.

## Dependencies And Integration Points
It connects the Atmel sound directory to kbuild and mirrors `sound/atmel/Kconfig`.

## Risks And Test Signals
Compile and link tests for `CONFIG_SND_ATMEL_AC97C=m/y` are the primary signals.
