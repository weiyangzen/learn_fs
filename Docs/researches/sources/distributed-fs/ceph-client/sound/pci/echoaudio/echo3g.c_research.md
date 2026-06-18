# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echo3g.c

## Purpose

This wrapper specializes the shared Echoaudio driver for Echo3G-family PCI cards with external Gina3G/Layla3G boxes.

## Important APIs, types, and functions

It defines Echo3G feature macros for ASIC, monitor, nominal levels, super interleave, digital I/O, digital mode switch, ADAT, external clock, stereo big-endian 32-bit support, MIDI, and phantom power. Pipe and bus indexes are dynamic `chip->px_*`/`chip->bx_*` fields populated after box detection. Firmware entries are loader DSP, Echo3G DSP, and 3G ASIC. PCI ID matches device `0x3410`, subsystem `0x0100`. `pcm_hardware_skel` supports 32 kHz through continuous up to 100 kHz.

## Control flow

The file includes `echo3g_dsp.c`, generic DSP helpers, `echoaudio_3g.c`, shared `echoaudio.c`, and MIDI support. During probe, `init_hw()` loads firmware/ASIC, detects the external box type, and sets dynamic channel counts before shared PCM/control registration.

## State and persistence behavior

The wrapper enables dynamic runtime state for box-dependent pipe/bus layout, digital modes, MIDI, phantom power availability, and clock sources. Shared `struct echoaudio` stores those values.

## Dependencies and integration points

It depends on firmware files under `ea/`, ALSA rawmidi, PCI, firmware, and the generic Echoaudio include-based architecture. Kbuild maps `CONFIG_SND_ECHO3G` to this unit.

## Risks and test signals

Risks include missing firmware, failed ASIC load, wrong external box detection, dynamic channel counts set too late, and feature controls shown for unsupported boxes. Tests should probe Gina3G and Layla3G boxes, validate analog/digital PCM counts, ADAT/SPDIF modes, MIDI, phantom power only on Gina3G, firmware cache behavior, and suspend/resume.
