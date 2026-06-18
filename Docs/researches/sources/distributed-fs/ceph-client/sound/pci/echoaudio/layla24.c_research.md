# sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla24.c

## Purpose

`layla24.c` wraps the Echo Layla24, a full 32-pipe Echo24/GML card with MIDI, ASIC firmware, digital mode switching, ADAT, and nominal level controls.

## Important APIs, Types, and Functions

The topology defines 8 analog outputs, 8 digital outputs, 8 analog inputs, and 8 digital inputs. Firmware entries include loader, `layla24_dsp.fw`, one PCI-card ASIC, and external S/ADAT ASIC images. PCI subsystem is `0060` on DSP 56361. PCM caps support 8 to 96 kHz nominally with `rate_max` 100 kHz for continuous mode, up to 8 channels, and common Echo limits. It includes GML helpers and MIDI support.

## Control Flow

The inclusion chain is `layla24_dsp.c`, shared DSP, GML helpers, common Echoaudio, and MIDI. Card-specific DSP code loads the base ASIC and switches external ASIC images as digital modes change.

## State and Persistence Behavior

Runtime state includes ASIC code, digital mode, digital auto-mute, professional S/PDIF, MIDI state, nominal levels, clocks, and line/mixer settings. Static state is firmware and capability data.

## Dependencies and Integration Points

It integrates with firmware `ea/layla24_*`, ALSA PCM/control/rawmidi, GML register helpers, and common Echoaudio transport.

## Risks and Test Signals

Risks are wrong external ASIC selection, continuous-rate register mistakes, and ADAT/double-speed conflicts. Test with DSP/ASIC load, S/PDIF and ADAT mode switching, continuous rates around 25 to 100 kHz, MIDI I/O, and full 8-channel capture/playback.
