# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoiox.c

## Purpose

`indigoiox.c` wraps the Echo Indigo IOx ExpressCard variant. It combines Indigo IO-style stereo input/output topology with Indigo Express rate programming.

## Important APIs, Types, and Functions

The topology has 8 playback pipes, 2 analog input pipes, 2 output busses, and 2 input busses. Feature macros enable monitor, super-interleave, vmixer, and stereo 32-bit big-endian. Firmware entries are `loader_dsp.fw` and `indigo_iox_dsp.fw`; PCI subsystem is `00D0`. PCM caps add 64 kHz to the Indigo IO fixed-rate set.

## Control Flow

The file includes `indigoiox_dsp.c`, `indigo_express_dsp.c`, shared DSP, and common Echoaudio code. Identity/init comes from IOx, while rate/vmixer operations come from the Express helper.

## State and Persistence Behavior

Runtime state is common Echoaudio state sized by this topology. Static state is firmware, PCI IDs, and PCM caps.

## Dependencies and Integration Points

It depends on Express clock constants, ALSA PCM/capture, monitor/vmixer controls, and firmware lookup under `ea/`.

## Risks and Test Signals

Risks include omitting Express 64 kHz support or using the non-Express IO firmware. Test signals are successful IOx probe, stereo capture and playback, 64 kHz operation, and monitor/vmixer controls.
