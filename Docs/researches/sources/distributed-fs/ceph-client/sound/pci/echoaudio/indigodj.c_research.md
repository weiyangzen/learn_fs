# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodj.c

## Purpose

`indigodj.c` is the card wrapper for Echo Indigo DJ. It is a playback-oriented Indigo-family module with four analog output busses and vmixer support.

## Important APIs, Types, and Functions

The topology defines 8 output pipes and 4 analog output busses, with no inputs. Firmware entries are `loader_dsp.fw` and `indigo_dj_dsp.fw`; the PCI table matches subsystem `00B0`. PCM caps are the same fixed Indigo rates from 32 to 96 kHz, with up to 4 channels.

## Control Flow

The module includes `indigodj_dsp.c`, shared DSP, and common Echoaudio core. Probe and ALSA registration are common; this file supplies compile-time card identity and capability data.

## State and Persistence Behavior

Runtime state is common Echoaudio state, especially vmixer gain and output gain arrays sized by this topology. Static firmware and PCI tables are module-local.

## Dependencies and Integration Points

It integrates with ALSA PCM and mixer controls through `echoaudio.c` and with DSP firmware through `indigodj_dsp.c` and `echoaudio_dsp.c`.

## Risks and Test Signals

Risks are topology mismatches between 8 virtual pipes and 4 output busses, and exposing input controls that should not exist. Test signals include playback on all four analog outputs, vmixer controls, and firmware load for `indigo_dj_dsp.fw`.
