# sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla20.c

## Purpose

This card wrapper specializes the shared Echoaudio driver for Darla20.

## Important APIs, types, and functions

It defines feature macros `ECHOGALS_FAMILY`, `ECHOCARD_DARLA20`, `ECHOCARD_NAME`, and `ECHOCARD_HAS_MONITOR`; pipe and bus indexes for 8 analog outs and 2 analog ins; `MODULE_FIRMWARE("ea/darla20_dsp.fw")`; firmware table `card_fw`; PCI IDs for subsystem `0x0010`; and `pcm_hardware_skel` for 44.1/48 kHz, up to stereo streams. It includes `darla20_dsp.c`, `echoaudio_dsp.c`, and `echoaudio.c`.

## Control flow

Compilation textually combines card constants, Darla20 DSP policy, generic DSP helpers, and the shared ALSA PCI driver. Probe in `echoaudio.c` uses the local PCI table and calls `init_hw()` from `darla20_dsp.c`.

## State and persistence behavior

Runtime state is the shared `struct echoaudio`; this wrapper fixes channel layout, supported formats/rates, monitor support, and firmware selection.

## Dependencies and integration points

It depends on ALSA, PCI, firmware loading, `echoaudio.h`, and the included shared implementation files. Kbuild creates `snd-darla20.o` from this unit.

## Risks and test signals

Risks include macro layout mismatches, firmware name/path errors, and constraint mismatch with hardware. Test signals include successful probe with Darla20 subsystem ID, firmware load, analog PCM enumeration, monitor controls, and 44.1/48 kHz playback/capture.
