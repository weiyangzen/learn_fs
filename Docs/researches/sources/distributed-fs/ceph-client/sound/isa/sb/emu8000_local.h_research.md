# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_local.h

## Purpose
`emu8000_local.h` is the private header shared by the EMU8000 synth plugin files. It includes common kernel and ALSA headers and declares cross-file callbacks for sample memory management, emux operator setup, and PCM device creation.

## Important APIs, Types, and Functions
It declares `snd_emu8000_sample_new`, `snd_emu8000_sample_free`, `snd_emu8000_sample_reset`, `snd_emu8000_ops_setup`, and `snd_emu8000_pcm_new`.

## Control Flow
There is no executable control flow. The declarations connect `emu8000_synth.c` to operator setup in `emu8000_callback.c`, sample loading in `emu8000_patch.c`, and optional PCM creation in `emu8000_pcm.c`.

## State and Persistence
No state is declared here beyond included external structures. Runtime state lives in `struct snd_emu8000`, `struct snd_emux`, and memory-header structures from ALSA.

## Dependencies and Integration Points
It depends on `<sound/emu8000.h>` and `<sound/emu8000_reg.h>`, plus core kernel memory/scheduler headers. It is included by all `snd-emu8000-synth` component files.

## Risks and Test Signals
Risks are mainly interface drift between companion C files. Test signals include successful compilation of all EMU8000 synth objects and correct linkage of patch/callback/PCM functions.
