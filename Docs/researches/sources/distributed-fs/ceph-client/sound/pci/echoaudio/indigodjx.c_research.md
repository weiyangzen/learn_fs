# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodjx.c

## Purpose

`indigodjx.c` is the card wrapper for the Echo Indigo DJx ExpressCard variant. It combines DJ-style four-output topology with the Indigo Express DSP clock helper.

## Important APIs, Types, and Functions

Feature macros enable Indigo family, super-interleave, vmixer, and stereo 32-bit big-endian samples. The topology has 8 output pipes and 4 analog output busses. Firmware entries are `loader_dsp.fw` and `indigo_djx_dsp.fw`; PCI subsystem is `00E0`. PCM caps include 32, 44.1, 48, 64, 88.2, and 96 kHz with up to 4 channels.

## Control Flow

The inclusion order is `indigodjx_dsp.c`, `indigo_express_dsp.c`, shared DSP, and common Echoaudio core. The first file supplies identity/init; the Express helper supplies sample-rate and vmixer functions.

## State and Persistence Behavior

Static state is firmware/PCI/PCM capability data. Runtime state is common Echoaudio state, especially `sample_rate`, `control_register`, and vmixer gains.

## Dependencies and Integration Points

It depends on ALSA PCI/PCM infrastructure, `echoaudio.h`, and firmware under `ea/`. It integrates with common Echoaudio probe and vmixer controls.

## Risks and Test Signals

Risks are losing the Express-only 64 kHz rate or mixing DJx identity with the older DJ firmware. Test signals are probe on subsystem `00E0`, `indigo_djx_dsp.fw` load, 64 kHz playback, and four-output vmixer operation.
