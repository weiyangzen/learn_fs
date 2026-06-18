# sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla20.c

## Purpose

`layla20.c` is the Echo Layla20 wrapper. It defines an Echogals card with ASIC firmware, MIDI, monitor controls, analog input gain, output nominal levels, external clocks, and output clock switching.

## Important APIs, Types, and Functions

The topology exposes 10 analog outputs, 2 digital outputs, 8 analog inputs, and 2 digital inputs. Firmware entries are `layla20_dsp.fw` and `layla20_asic.fw`; PCI subsystems include revisions `0030` and `0031`. PCM caps support U8/S16/S24_3LE/S32_LE/S32_BE, continuous 8 to 50 kHz rates, up to 10 channels, and standard Echo buffer limits. It includes `midi.c` because `ECHOCARD_HAS_MIDI` is set.

## Control Flow

The module includes `layla20_dsp.c`, shared DSP, common Echoaudio code, and MIDI support. Common probe registers PCM, mixer, and rawmidi interfaces according to these macros.

## State and Persistence Behavior

Static firmware, topology, and PCM caps are local. Runtime ASIC, clock, MIDI, monitor, nominal-level, and gain state is held in `struct echoaudio` and the comm page.

## Dependencies and Integration Points

It integrates with ALSA PCM, controls, and rawmidi; firmware loading for both DSP and ASIC; and external clock/output clock controls.

## Risks and Test Signals

Risks include ASIC firmware failure when the external box is absent, incorrect continuous-rate handling, and MIDI timer/IRQ regressions. Test signals are probe with both revisions, ASIC status success or clear error, 8-channel capture, 10-channel playback, rawmidi I/O, and word/super/S/PDIF clock controls.
