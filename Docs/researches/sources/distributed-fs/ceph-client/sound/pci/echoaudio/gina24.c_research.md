# sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina24.c

## Purpose

`gina24.c` is the card wrapper for Echo Gina24 devices. It selects Echo24/GML behavior, declares firmware for 56301 and 56361 variants, exposes PCI IDs, and sets PCM capabilities for an 8-output/8-digital-capable interface.

## Important APIs, Types, and Functions

Feature macros enable monitor, ASIC loading, nominal input/output levels, super-interleave, digital I/O, digital input auto-mute, digital mode switching, external clocks, ADAT, and stereo 32-bit big-endian samples. Firmware entries include loader, `gina24_301_dsp.fw`, `gina24_361_dsp.fw`, and matching ASIC images. The PCI table matches both 56301 and 56361 revisions. PCM hardware supports standard 8 to 48 kHz rates plus 88.2/96 kHz, 1 to 8 channels, and the common Echo period/buffer limits.

## Control Flow

The module is assembled by including `gina24_dsp.c`, shared DSP, GML helpers, and common Echoaudio code. The card-specific DSP file chooses firmware and digital modes at runtime based on device ID.

## State and Persistence Behavior

Static state consists of firmware, PCI IDs, and PCM caps. Runtime digital mode, ASIC code, clocks, nominal levels, and mixer state are maintained by included code in `struct echoaudio`.

## Dependencies and Integration Points

It integrates with Linux firmware files under `ea/`, ALSA PCM/control surfaces, common `echoaudio.c`, and `echoaudio_gml.c` for GML register control.

## Risks and Test Signals

Risks include mismatching 301/361 firmware or exposing ADAT/digital mode controls inconsistent with hardware revision. Test signals include probe on all listed PCI IDs, firmware load for both DSP families, sample-rate coverage from 8 to 96 kHz, ADAT versus S/PDIF switching, and nominal level controls.
