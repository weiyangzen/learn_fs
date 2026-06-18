# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_voice.h

## Purpose
Provides local cross-file declarations for the OPL3 FM synth implementation. It binds the sequencer, MIDI event, internal drum, OSS emulation, register map, and shared MIDI operation table together without exposing those internals outside the OPL3 driver directory.

## Important APIs, Types, And Functions
Declares synth lifecycle functions from `opl3_seq.c`, MIDI callbacks and helpers from `opl3_midi.c`, drum helpers from `opl3_drums.c`, optional OSS initialization/free hooks from `opl3_oss.c`, and external data `snd_opl3_regmap`, `use_internal_drums`, and `opl3_ops`.

## Control Flow
The header has no executable control flow. Its preprocessor branch maps OSS functions to no-ops when `CONFIG_SND_SEQUENCER_OSS` is disabled, allowing core sequencer code to call the hooks unconditionally.

## State And Persistence
No state is stored in the header. It declares shared runtime state owned by other compilation units.

## Dependencies And Integration
Includes `<sound/opl3.h>` for `struct snd_opl3`, MIDI channel types, and OPL constants. It is the internal integration surface for the OPL3 sequencer object built by the Makefile.

## Risks And Test Signals
Prototype drift would break cross-file builds. The no-op OSS macros are important for configuration coverage. Build tests with OSS enabled and disabled are the main signal; sparse/compiler warnings catch signature mismatches.
