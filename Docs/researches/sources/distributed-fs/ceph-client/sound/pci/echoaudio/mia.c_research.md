# sources/distributed-fs/ceph-client/sound/pci/echoaudio/mia.c

## Purpose

`mia.c` wraps Echo Mia and Mia MIDI-capable revisions. It defines Echo24 behavior without ASIC, with stereo analog/digital I/O, vmixer, MIDI, nominal levels, and S/PDIF clock support.

## Important APIs, Types, and Functions

The topology has 8 playback pipes, 2 analog input pipes, 2 digital input pipes, 2 analog output busses, 2 digital output busses, and 2 analog plus 2 digital input busses. Firmware entries are loader and `mia_dsp.fw`; PCI subsystems are `0080` and `0081`. PCM caps advertise 32/44.1/48/88.2/96 kHz, up to 8 channels, and common Echo buffer limits. `ECHOCARD_HAS_MIDI` is set but actual MIDI is detected by revision in the DSP file.

## Control Flow

The file includes `mia_dsp.c`, shared DSP, common Echoaudio, and MIDI support. Common code uses card macros to expose PCM, mixer, nominal level, digital clock, vmixer, and rawmidi functionality.

## State and Persistence Behavior

Runtime state includes optional `has_midi`, S/PDIF professional mode, input clock, vmixer matrix, monitor matrix, nominal levels, and line-out gain. Static state is firmware/PCI/PCM capability data.

## Dependencies and Integration Points

It depends on ALSA PCM/rawmidi/control APIs, firmware loading, and common Echoaudio code.

## Risks and Test Signals

Risks are exposing MIDI on non-MIDI revisions, rate mismatch from `rate_min` versus listed rates, and incorrect digital/analog bus mapping. Test with both revisions, MIDI presence only where expected, internal/S/PDIF clocking, vmixer, and stereo analog/digital I/O.
