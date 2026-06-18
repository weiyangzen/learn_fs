# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_patch.c

## Purpose
`emu8000_patch.c` implements SoundFont sample-memory callbacks for the EMU8000 synth. It allocates sample blocks, converts userspace sample data, writes it into EMU8000 DRAM through hardware DMA registers, expands reverse/bidirectional loops, appends blank loops when needed, frees sample blocks, and terminates voices on sample reset.

## Important APIs, Types, and Functions
- Public callbacks: `snd_emu8000_sample_new`, `snd_emu8000_sample_free`, and `snd_emu8000_sample_reset`.
- DMA helpers: `snd_emu8000_open_dma`, `snd_emu8000_close_dma`, `snd_emu8000_write_wait`, and `write_word`.
- `read_word` handles 8-bit to 16-bit conversion, endian conversion, and unsigned-to-signed conversion.
- Module parameter `emu8000_reset_addr` optionally resets the hardware write address for each word to avoid lost writes.

## Control Flow
On new sample load, the driver computes true size, allocates memory from the emux memory header, validates user memory, translates byte offset to EMU8000 word address, terminates all voices, reserves voices for DMA, sets the write address, streams sample words from userspace, conditionally duplicates reverse-loop data, appends blank loop samples, adjusts sample start/end/loop addresses to DRAM absolute addresses, closes DMA, and reinitializes FM refresh voices.

## State and Persistence
Sample allocation state is stored in `sp->block` and the emux memory header. The sample metadata is mutated in place to include true size and DRAM-based addresses. Data persists only in card DRAM while loaded.

## Dependencies and Integration Points
It depends on `emu8000_local.h`, ALSA soundfont/emux memory APIs, EMU8000 DMA helper functions from `emu8000.c`, and userspace copy/access helpers. It is used through the emux operator table installed by `emu8000_callback.c`.

## Risks and Test Signals
Risks include memory leaks on errors after allocation, slow or interruptible long sample writes, unchecked `get_user` result in `read_word`, and mutation of loop metadata for reverse/bidir loops. Test signals include loading 8-bit, 16-bit, unsigned, single-shot, reverse-loop, and bidirectional-loop SoundFonts; ENOSPC on small DRAM; interrupting large loads; freeing samples; and verifying no voices remain locked after load failure.
