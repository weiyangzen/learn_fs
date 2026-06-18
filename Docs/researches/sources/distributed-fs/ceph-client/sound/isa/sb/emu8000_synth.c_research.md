# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_synth.c

## Purpose
`emu8000_synth.c` is the ALSA sequencer-driver plugin for EMU8000 hardware. It receives the hardware pointer from the sequencer device created by `snd_emu8000_new`, creates an emux synthesizer instance, allocates sample memory management, registers sequencer ports, optionally creates an EMU8000 PCM device, and frees those resources on removal.

## Important APIs, Types, and Functions
- `snd_emu8000_probe` creates and registers the emux device.
- `snd_emu8000_remove` destroys optional PCM, emux, and memory-header resources.
- `emu8000_driver` is a `struct snd_seq_driver` with ID `SNDRV_SEQ_DEV_ID_EMU8000` and argument size `sizeof(struct snd_emu8000 *)`.

## Control Flow
Probe fetches the `struct snd_emu8000 *` from the seq-device argument, rejects missing or already-bound hardware, allocates `snd_emux`, installs EMU8000 ops, sets voice count and port counts, creates `snd_util_memhdr` sized to detected DRAM, configures MIDI port exposure, registers the emux synth, and creates PCM playback if DRAM size is nonzero. Remove reverses the sequence.

## State and Persistence
The file populates `hw->emu`, `hw->memhdr`, and `dev->driver_data`. Sample memory state is in the memory header and is freed on removal. No disk persistence exists.

## Dependencies and Integration Points
It depends on ALSA sequencer driver helpers, emux APIs, `emu8000_local.h`, callback setup, and PCM creation. It is built as `snd-emu8000-synth`.

## Risks and Test Signals
Risks include partial-registration cleanup, double-probe protection, and ordering between PCM device free and emux/memory teardown. Test signals include seq-driver autoload/probe, emux port availability, SoundFont memory allocation, optional PCM creation only when DRAM exists, and clean module removal.
