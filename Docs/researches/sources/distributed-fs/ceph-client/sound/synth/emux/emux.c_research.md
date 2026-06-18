# sources/distributed-fs/ceph-client/sound/synth/emux/emux.c

## Purpose
This file provides the lifecycle entry points for the shared EMUX wavetable synthesizer layer used by EMU8000/EMU10K1-style drivers. It allocates the core `snd_emux` object, registers soundfont/hwdep/sequencer/virtual-MIDI/proc interfaces, and tears them down.

## Important APIs, types, and functions
Exported APIs are `snd_emux_new`, `snd_emux_register`, and `snd_emux_free`. Soundfont callbacks `sf_sample_new`, `sf_sample_free`, and `sf_sample_reset` bridge the generic soundfont loader to hardware-specific `emu->ops` methods. `snd_emux_register` validates hardware and voice counts, duplicates the device name, allocates the voice array, creates `snd_sf_list`, initializes hwdep, voices, sequencer ports, optional OSS sequencer support, virtual MIDI, and proc entries.

## Control flow
Hardware drivers call `snd_emux_new`, fill `emu->hw`, `emu->ops`, `max_voices`, memory header, and port counts, then call `snd_emux_register`. Registration creates all user-facing interfaces in dependency order: soundfont list first, hwdep patch loading, voice initialization, ALSA sequencer client/ports, optional OSS facade, virtual raw MIDI, and proc diagnostics. `snd_emux_free` shuts down the pending note-off timer, removes proc/virmidi/OSS/sequencer/hwdep, frees soundfonts, voices, name, and the object.

## State and persistence behavior
State is in-memory only: locks, timer state, use counter, soundfont list, voice table, sequencer clients/ports, optional OSS and virmidi devices, and hardware operation callbacks. Loaded soundfonts and samples live in kernel memory or hardware memory through `memhdr`/hardware ops.

## Dependencies and integration points
The file integrates ALSA core, ALSA soundfont support, hwdep, sequencer, optional OSS sequencer, virtual raw MIDI, procfs, timers, and hardware-specific EMUX operation callbacks. It exports symbols for lower-level sound card drivers.

## Risks and edge cases
Several registration failure paths return directly without unwinding previously allocated pieces, relying on caller cleanup or leaking until free is invoked. Hardware ops must be complete before registration; missing sample callbacks or invalid `max_voices` fail or crash later. `snd_emux_init_seq` return is not checked, so later interfaces may initialize with no valid client if sequencer creation fails.

## Test signals
Test signals include successful registration by an EMUX consumer, hwdep node creation, sequencer ports, virmidi devices when configured, proc entry, soundfont load/reset/free callbacks, and clean `snd_emux_free` after partial registration failures.
