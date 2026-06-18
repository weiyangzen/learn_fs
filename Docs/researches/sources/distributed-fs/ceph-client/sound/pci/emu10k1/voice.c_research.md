# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/voice.c

## Purpose
`voice.c` implements the EMU10K1 voice allocator. Voices are hardware playback/effect/synth channels; the allocator gives PCM, EFX, and synth code contiguous voice groups with correct stereo alignment and frees them safely.

## Important APIs, Types, and Functions
Public APIs are `snd_emu10k1_voice_alloc()` and `snd_emu10k1_voice_free()`. Internal helpers are `voice_alloc()` and `voice_free()`. Allocation operates on `emu->voices[]`, `emu->next_free_voice`, `struct snd_emu10k1_voice` fields `use`, `epcm`, `last`, `dirty`, `interrupt`, and optional synth reclamation callback `emu->get_synth_voice`.

## Control Flow
Allocation validates arguments, locks `emu->voice_lock`, and repeatedly calls `voice_alloc()` until the requested number of channel groups is obtained. `voice_alloc()` starts at `emu->next_free_voice`, scans round-robin across `NUM_G`, enforces even starting voices for multi-voice/stereo groups, skips used ranges efficiently, marks each voice with the requested type and `epcm`, marks the last voice in the group, and advances `next_free_voice`. If allocation fails for non-synth clients and `get_synth_voice` is available, it reclaims one synth voice and retries. Partial allocations are rolled back on failure. Freeing walks from the first voice until the `last` marker, resets dirty hardware voices through `snd_emu10k1_voice_init()`, and clears software fields.

## State and Persistence
Voice allocation state is runtime-only in `emu->voices[]` and `emu->next_free_voice`. Dirty voices reflect hardware register programming that must be reset before reuse. No persistent storage is used.

## Dependencies and Integration Points
`emupcm.c`, FX, and synth code allocate voices through this file. `irq.c` reads voice `use` and `interrupt` fields while dispatching loop interrupts. Hardware reset on dirty free depends on `snd_emu10k1_voice_init()` from main initialization code. Synth reclamation uses `emu->get_synth_voice`.

## Risks
The allocator returns `-ENOMEM` for busy voice pools, and callers must unwind cleanly. Stereo alignment is essential; changing scan behavior can break hardware assumptions. The `last` marker defines group length during free, so any corruption can over-free adjacent voices. Free must clear interrupt callbacks before reuse to avoid stale IRQ calls.

## Test Signals
Allocate/free mono, stereo, multi-channel EFX, and synth voices until exhaustion. Verify stereo groups start on even voice numbers, round-robin allocation advances, failed multi-group allocations roll back all partial state, dirty voices are reinitialized, and IRQ dispatch never calls freed voice callbacks.
