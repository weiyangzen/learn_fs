# sources/distributed-fs/ceph-client/sound/synth/emux/emux_oss.c

## Purpose
This file implements OSS sequencer compatibility for the EMUX wavetable synth. It registers an OSS synth device, creates per-open EMUX ports, supports OSS patch loading/ioctls, and translates OSS private/AWE/GUS control events into EMUX MIDI or raw effect operations.

## Important APIs, types, and functions
`snd_emux_init_seq_oss` and `snd_emux_detach_seq_oss` manage the OSS sequencer device. The `oss_callback` table points to open, close, ioctl, patch load, and reset handlers. `snd_emux_open_seq_oss` creates an OSS port and increments module/card use counts; `snd_emux_close_seq_oss` silences and detaches it. `emuspec_control`, `gusspec_control`, and `fake_event` implement private event translation.

## Control flow
Initialization creates a `SNDRV_SEQ_DEV_ID_OSS` device using device number 1 to avoid OPL3 conflicts, marks it as sample/AWE32 compatible, and registers callbacks. On OSS open, the driver creates a writable sequencer port with 32 channels, stores OSS arguments, sets MIDI or synth mode, and resets the port. Raw OSS events with `SEQ_PRIVATE` are parsed: EMUX-specific commands update effects, terminate voices, switch port mode, change drum flags, or call hardware `oss_ioctl`; GUS commands update sample, pan, or sample-start effects. Close stops all sounds, releases soundfont client locks, detaches the port, and decrements module usage.

## State and persistence behavior
State persists per OSS open in a dynamically created `snd_emux_port`, its channel set, drum flags, volume attenuation, and associated soundfont client number. Patch loads mutate the shared EMUX soundfont list. No disk persistence exists.

## Dependencies and integration points
It integrates ALSA OSS sequencer emulation, EMUX sequencer/event APIs, soundfont loaders, Linux ultrasound compatibility constants, MIDI control constants, and optional raw effect support.

## Risks and edge cases
Private event parsing uses unaligned casts from raw byte data to short/int values, which can be architecture-sensitive. Many OSS commands are unsupported no-ops. Port creation failure must correctly unwind module counts. Soundfont client numbers are derived from port numbers and must avoid collisions. Mode switching resets the port and may interrupt active notes.

## Test signals
Test OSS synth registration, open/close cycles, patch loading in GUS and soundfont formats, reset/ioctl memory queries, AWE private effect events, terminate/release commands, MIDI versus synth mode transitions, GUS sample/pan/position commands, and builds without OSS sequencer support.
