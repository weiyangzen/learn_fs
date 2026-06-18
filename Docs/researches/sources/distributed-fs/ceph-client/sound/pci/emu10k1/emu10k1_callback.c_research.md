# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_callback.c

## Purpose

`emu10k1_callback.c` implements `snd_emux` wavetable synth callbacks for EMU10K1 hardware voices. It allocates/reclaims hardware voices, prepares sample playback registers, starts and releases envelopes, updates modulation parameters, and frees voices back to the main driver.

## Important APIs, Types, and Functions

`snd_emu10k1_ops_setup()` installs `emu10k1_ops` into an emux instance. `snd_emu10k1_synth_get_voice()` steals an active synth voice for PCM when needed. `lookup_voices()` ranks candidate voices as free, off, released, playing, or ended. `get_voice()` allocates a hardware voice through `snd_emu10k1_voice_alloc()`. `start_voice()` maps sample memory, adjusts loop addresses, programs routing, pitch, envelopes, LFOs, filter, cache, and map registers. `trigger_voice()` enables playback. `release_voice()`, `terminate_voice()`, and `free_voice()` stop/release hardware and sample-map references. `update_voice()` writes live volume, pitch, pan, modulation, tremolo, and filter parameters. `make_fmmod()`, `make_fm2frq2()`, and `get_pitch_shift()` derive register values.

## Control Flow

The synth module registers these callbacks during probe. When emux needs a note, `get_voice()` selects or allocates a channel; `start_voice()` maps sample memory and writes a full register set while the channel is silent; `trigger_voice()` starts the envelope and pitch. MIDI/control changes call `update_voice()`. Note-off calls `release_voice()`, and voice cleanup calls `terminate_voice()`/`free_voice()`. PCM voice pressure can call `snd_emu10k1_synth_get_voice()` to reclaim a synth channel.

## State and Persistence Behavior

State spans `struct snd_emux_voice`, hardware voice registers, `struct snd_emu10k1_memblk` map locks, `hw->voices[]`, and `emux->num_voices`. `start_voice()` mutates sample address fields by adding mapped offsets, so sample mapping and voice lifecycle must stay coordinated.

## Dependencies and Integration Points

It depends on `emu10k1_synth_local.h`, `sound/asoundef.h`, emux core, EMU10K1 register write helpers, voice allocator, and synth memory mapping functions from other EMU10K1 files.

## Risks and Test Signals

Risks include leaked `map_locked` references, voice stealing while still audible, invalid loop unroll/address math, Audigy versus EMU10K1 routing register differences, and the noted `hw == NULL` free path. Test with wavetable playback, heavy polyphony and voice stealing, PCM plus synth concurrency, modulation/pitch/pan updates, and unload/replug cycles.
