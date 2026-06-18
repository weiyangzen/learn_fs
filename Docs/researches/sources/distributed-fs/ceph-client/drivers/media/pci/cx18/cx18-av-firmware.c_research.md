# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-firmware.c

## Purpose
This file loads and verifies the digital firmware for the cx23418 integrated A/V decoder 8051 core. It also programs post-load decoder audio routing, I2S timing, standard detection defaults, and the host audio mux.

## Important APIs, Types, and Functions
`cx18_av_loadfw()` is the exported entry point called through the A/V subdev core `load_fw` path. `cx18_av_verifyfw()` re-enters decoder firmware upload mode and reads back the firmware image byte-by-byte through `CXADEC_DL_CTL`. Constants include firmware name `v4l-cx23418-dig.fw`, `CX18_AUDIO_ENABLE`, AI1 mux bit masks, and decoder registers from `cx18-av-core.h`.

## Control Flow
`cx18_av_loadfw()` requests firmware from the PCI device, retries full image upload up to five times, and retries each byte write up to `CX18_MAX_MMIO_WR_RETRIES`. It resets the Mako core, enables 8051 upload mode, writes each byte through `CXADEC_DL_CTL`, starts firmware execution, optionally verifies the load, then writes decoder pin, I2S, standard-detection, MiniMe, and audio mux registers. It releases firmware before returning.

## State and Persistence
The firmware image is transient. Hardware state persists until reset or power management changes: the 8051 program RAM, decoder pins, I2S controls, standard-detection settings, and host `CX18_AUDIO_ENABLE` mux. There is no on-disk persistence.

## Dependencies and Integration Points
This code depends on Linux firmware loading, `cx18_av_read/write` helpers from the A/V core, main MMIO helpers for host registers, and `struct cx18_av_state` for logging through the decoder subdev. It is part of first-open initialization after CPU/APU firmware loading.

## Risks and Edge Cases
Firmware writes are known to have byte errors, so retry logic is central. Verification reuses upload-mode side effects and must leave the decoder in a runnable state afterward. If firmware is missing, analog capture cannot initialize. The AI1 mux toggle is hardware-specific; incorrect masks can mute or misroute audio. Verification failure is logged but the code still attempts to start firmware only if verification succeeded.

## Test Signals
Test by booting with and without `v4l-cx23418-dig.fw`, observing load and verify messages, checking analog audio after first capture, switching standards, and ensuring repeated first-open firmware reloads do not leave the mux in an invalid state.
