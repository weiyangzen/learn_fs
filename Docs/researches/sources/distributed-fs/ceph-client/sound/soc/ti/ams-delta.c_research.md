# sources/distributed-fs/ceph-client/sound/soc/ti/ams-delta.c

## Purpose
Machine driver for Amstrad E3/Delta videophone audio. It connects OMAP McBSP to a CX20442 voice codec, controls handset/handsfree GPIO mutes, exposes an `Audio Mode` control, and optionally uses a TTY line discipline for modem/codec control.

## Important APIs/types/functions
Key functions include DAPM GPIO events, `ams_delta_get_audio_mode`, `ams_delta_set_audio_mode`, `cx81801_open/close/receive`, `ams_delta_mute`, `ams_delta_cx20442_init`, and platform probe/remove.

## Control flow
Probe gets mute GPIOs and registers the card. Card init saves the codec for TTY callbacks, creates hook-switch jack GPIOs, gets the modem-codec mux GPIO, installs mute hooks, registers line discipline `N_V253`, and initializes DAPM pins. TTY receive detects modem responses and pulses the mux GPIO through a timer. The audio-mode control maps enum selections to DAPM pins.

## State, dependencies, integration, risks, tests
State is mostly file-static: GPIOs, codec pointer, hook switch, AGC, timer, pending flag, mute flag, spinlock, and mux GPIO. Dependencies are OMAP McBSP naming, CX20442/v253, TTY, GPIO, and ASoC. Risks are single-card static state, timer/mute/TTY races, ldisc lifecycle, and userspace `ldattach` dependency. Test card probe, ldisc lifecycle, hook switch, audio modes, mute, and mux GPIO timing.
