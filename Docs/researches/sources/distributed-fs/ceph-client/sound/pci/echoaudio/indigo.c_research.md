# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo.c

## Purpose

`indigo.c` is the Echo Indigo playback-card wrapper. It defines an Indigo-family module with virtual mixer support and no physical inputs or digital I/O.

## Important APIs, Types, and Functions

The topology defines 8 playback pipes feeding 2 analog output busses. Feature macros enable super-interleave, vmixer, and stereo 32-bit big-endian support. Firmware entries are `loader_dsp.fw` and `indigo_dsp.fw`; the PCI table matches subsystem `0090`. PCM caps support 32, 44.1, 48, 88.2, and 96 kHz, 1 to 8 channels, and common Echo buffer constraints.

## Control Flow

The file includes `indigo_dsp.c`, shared DSP, and common Echoaudio core. Common probe uses the static tables here and `indigo_dsp.c` supplies internal-only clocking and vmixer behavior.

## State and Persistence Behavior

Runtime state is held by the common Echoaudio structures, especially vmixer gains and output gains. This wrapper contributes fixed firmware, topology, and PCM capability state.

## Dependencies and Integration Points

It depends on the 56361 loader firmware, ALSA PCM/control headers, and `echoaudio.h`. Integration is through common PCI probe and vmixer controls.

## Risks and Test Signals

Risks are exposing nonexistent inputs or more physical output busses than the two analog outputs. Test signals are successful firmware load, playback-only ALSA devices, vmixer routing from 8 virtual pipes to 2 outputs, and rate switching across the advertised rates.
