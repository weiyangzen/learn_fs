# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoio.c

## Purpose

`indigoio.c` is the wrapper for Echo Indigo IO, an Indigo-family card with stereo analog input, stereo analog output, monitor controls, and vmixer playback.

## Important APIs, Types, and Functions

The topology defines 8 playback pipes, 2 analog input pipes, 2 output busses, and 2 input busses. Feature macros enable monitor, super-interleave, vmixer, and stereo 32-bit big-endian samples. Firmware entries are `loader_dsp.fw` and `indigo_io_dsp.fw`; PCI subsystem is `00A0`. PCM caps advertise 32, 44.1, 48, 88.2, and 96 kHz, up to 8 channels.

## Control Flow

The file includes `indigoio_dsp.c`, shared DSP, and common Echoaudio code. The common layer creates PCM and controls according to the topology and feature macros.

## State and Persistence Behavior

Runtime state includes monitor and vmixer matrices plus line levels, persisted in `struct echoaudio` and replayed by common restore logic. Static state is firmware, PCI, and PCM capability data.

## Dependencies and Integration Points

It integrates with ALSA PCM capture/playback, monitor and vmixer controls, and the Indigo IO DSP firmware.

## Risks and Test Signals

Risks include mismatching input bus counts and monitor matrix dimensions. Test signals include stereo capture, playback, monitor controls, vmixer routing, and fixed-rate switching.
