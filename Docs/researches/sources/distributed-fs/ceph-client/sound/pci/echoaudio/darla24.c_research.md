# sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla24.c

## Purpose

This card wrapper specializes the shared Echoaudio driver for Darla24.

## Important APIs, types, and functions

It defines Darla24 feature macros for monitor, input/output nominal levels, external ESync clock, and super interleave. Pipe/bus layout is 8 analog outs and 2 analog ins. Firmware is `ea/darla24_dsp.fw`; PCI IDs cover subsystem `0x0040` and `0x0041`; `pcm_hardware_skel` supports 8 kHz through 96 kHz, up to 8 playback channels.

## Control flow

Like other Echoaudio wrappers, this file is a compile unit that includes `darla24_dsp.c`, `echoaudio_dsp.c`, and `echoaudio.c`. The shared probe uses its local firmware table, PCI IDs, PCM skeleton, and feature macros.

## State and persistence behavior

The wrapper fixes static runtime capabilities: no ASIC, monitor mixer, nominal-level controls, ESync external clock list, super-interleaved hardware behavior, and PCM constraints.

## Dependencies and integration points

It depends on ALSA/PCI/firmware APIs and `echoaudio.h`. Kbuild maps `CONFIG_SND_DARLA24` to this module.

## Risks and test signals

Risks include rate/channel constraints that do not match DSP firmware, missing nominal-level controls, and ESync detection drift. Tests should probe both revisions, enumerate analog PCM and controls, switch internal/ESync clock, and run 8/44.1/48/88.2/96 kHz streams.
