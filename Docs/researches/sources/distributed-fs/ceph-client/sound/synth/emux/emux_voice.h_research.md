# sources/distributed-fs/ceph-client/sound/synth/emux/emux_voice.h

## Purpose
This private EMUX header centralizes cross-file prototypes for sequencer, synth voice, raw effects, NRPN/SYSEX, OSS, proc, and hwdep support. It is the internal contract between EMUX implementation files.

## Important APIs, types, and functions
The header declares sequencer functions such as `snd_emux_init_seq`, `snd_emux_create_port`, `snd_emux_event_input`, and virmidi helpers; synth functions such as note on/off, control, update, timer, and sound-off helpers; raw effect functions under `SNDRV_EMUX_USE_RAW_EFFECT`; NRPN/SYSEX functions; OSS attach/detach; proc functions or no-op inlines depending on `CONFIG_SND_PROC_FS`; and hwdep setup/teardown. `STATE_IS_PLAYING` abstracts the voice state test against `SNDRV_EMUX_ST_ON`.

## Control flow
There is no executable flow beyond the proc no-op inline definitions. The declarations define how `emux.c` sequences registration and teardown and how `emux_seq.c` routes MIDI events into `emux_synth.c`, `emux_nrpn.c`, and optional effect/OSS/proc layers.

## State and persistence behavior
The header stores no state. It exposes functions that mutate EMUX in-memory voice, port, soundfont, hwdep, and proc state.

## Dependencies and integration points
It includes Linux wait/sched and ALSA core/EMUX synth public headers. It connects all objects listed in the EMUX Makefile and encodes feature guards for raw effects and procfs.

## Risks and edge cases
Prototype guards must match object inclusion in the Makefile. If `SNDRV_EMUX_USE_RAW_EFFECT`, `CONFIG_SND_PROC_FS`, or OSS build options drift from call sites, builds can fail or no-op unexpectedly. `STATE_IS_PLAYING` treats any state bit overlapping `SNDRV_EMUX_ST_ON` as playing, so state bit definitions must remain compatible.

## Test signals
Compile every EMUX configuration combination, especially procfs on/off, OSS on/off, and raw effects on/off. Runtime signals include successful registration and teardown paths that call the declared interfaces in order.
