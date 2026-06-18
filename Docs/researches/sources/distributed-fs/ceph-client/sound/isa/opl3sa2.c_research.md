# sources/distributed-fs/ceph-client/sound/isa/opl3sa2.c

## Purpose
`opl3sa2.c` is the ALSA ISA/PnP driver for Yamaha OPL3-SA2/SA3-family sound cards. It configures the card control port, registers a WSS PCM codec, mixer, timer, optional OPL3 synth, optional MPU401 MIDI, shared IRQ handler, and suspend/resume support.

## Important APIs, Types, and Functions
- `struct snd_opl3sa2` stores control-port resource, version, IRQ, WSS/OPL/rawmidi handles, cached control registers, and master-control pointers.
- Detection and register helpers: `snd_opl3sa2_detect`, `snd_opl3sa2_read`, `snd_opl3sa2_write`.
- IRQ path: `snd_opl3sa2_interrupt` dispatches OPL3, MPU401, WSS, and hardware-volume notifications from `OPL3SA2_IRQ_STATUS`.
- Mixer path: `snd_opl3sa2_mixer` renames WSS controls, adds OPL3SA controls, and registers SA3 tone/3D controls when available.
- Bus paths: ISA match/probe and both PnP BIOS and PnP card drivers call `snd_opl3sa2_probe`.

## Control Flow
Module arrays provide resources for legacy ISA; PnP fills them from active PnP devices. Card creation initializes register locking and card names. Probe detects the chip by validating `MISC` and `MIC` register behavior, powers the device to D0, programs IRQ/DMA routing, creates a WSS codec at `wss_port + 4`, attaches PCM/mixer/timer, adds Yamaha-specific mixer controls, optionally creates OPL3 and MPU401 devices, builds `longname`, and registers the card.

## State and Persistence
The driver caches control-register values in `ctlregs` so mixer gets can avoid hardware reads and resume can restore registers. Power management writes D3 on suspend, saves state in memory, resumes by powering D0, replaying cached registers, and resuming the WSS codec. There is no persistent storage.

## Dependencies and Integration Points
It integrates Linux ISA and PnP subsystems with ALSA WSS, OPL3, MPU401, control, and power APIs. Hardware-volume IRQs notify ALSA controls by ID to keep userspace mixers in sync.

## Risks and Test Signals
Risks include shared IRQ demultiplexing, hardware-volume notification correctness, resource arrays being mutated by PnP, and resume replay ordering. Test signals include PnP BIOS and PnP-card probe, legacy parameter probe, WSS playback/capture, OPL3 timer/hwdep creation, MPU IRQ behavior, hardware volume button notification, and suspend/resume preserving mixer settings.
