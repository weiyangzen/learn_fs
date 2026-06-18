# sources/distributed-fs/ceph-client/sound/synth/emux/emux_effect.c

## Purpose
This file implements optional raw EMUX effect handling when `SNDRV_EMUX_USE_RAW_EFFECT` is enabled. It maps AWE/EMUX effect slots to soundfont voice parameter fields, stores per-channel effect overrides, applies them to new voices, and updates selected parameters on currently playing voices.

## Important APIs, types, and functions
`parm_defs` maps each effect type to byte/word layout, limits, soundfont parameter offset, and real-time update mask. `effect_set_byte`, `effect_set_word`, and `effect_get_offset` apply set/add/off effect semantics and sample/loop offsets. Public functions include `snd_emux_send_effect`, optional `snd_emux_send_effect_oss`, `snd_emux_setup_effect`, `snd_emux_create_effect`, `snd_emux_delete_effect`, and `snd_emux_clear_effect`.

## Control flow
Each EMUX port gets an effect table per MIDI channel. Incoming effect commands store value and mode in `chan->private`. If the effect has a real-time update mask and a valid parameter offset, `snd_emux_send_effect` walks active voices for that channel under `voice_lock`, restores the original zone parameter byte/word, applies the effect value, then calls `snd_emux_update_channel`. When a new voice is prepared, `snd_emux_setup_effect` applies all active channel effects and adjusts start/loop offsets before the hardware voice is triggered.

## State and persistence behavior
Effect state persists per port/channel in `struct snd_emux_effect_table` until reset/clear/delete. It is not written to disk. Per-voice register copies are modified from the original zone data; soundfont zone data remains the baseline.

## Dependencies and integration points
It depends on `soundfont_voice_parm`, MIDI channel private storage, EMUX update masks, and the synth voice setup path. OSS compatibility can translate OSS effect encodings into the same raw effect API.

## Risks and edge cases
The code is compiled only under a feature macro, so call sites must remain guard-aligned. In `snd_emux_send_effect`, the real-time loop checks `parm_defs[i].type` instead of `parm_defs[type].type`, which is suspicious because `i` is a voice index, not an effect type. Endianness-sensitive byte offsets must match soundfont parameter layout. Sample and loop offset effects can push addresses outside intended sample ranges if not constrained elsewhere.

## Test signals
Exercise AWE/OSS raw effects, real-time cutoff/Q/LFO/pitch updates on sustained notes, new note setup with active effects, sample-start and loop offset effects, port reset clearing effects, and builds with the raw-effect macro disabled.
