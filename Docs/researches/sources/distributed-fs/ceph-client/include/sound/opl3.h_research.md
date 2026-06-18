# sources/distributed-fs/ceph-client/include/sound/opl3.h

Source read summary: 375 lines, Yamaha OPL2/OPL3/OPL4 FM synthesizer interface.

Purpose: declares FM synthesis register constants, instrument/patch formats, hardware voice state, OPL3 device state, hwdep file operations, sequencer integration, timer setup, and patch management.

Important APIs, types, and functions: register macros cover operator, envelope, wave, F-number, key-on/block, feedback/connection, stereo, rhythm, and OPL3 mode registers. `struct fm_operator`, `fm_instrument`, and `fm_patch` describe patch data. `struct snd_opl3_voice` tracks allocation state, note, key-on shadow, MIDI channel, and note-off timing. `struct snd_opl3` stores ports/resources, hardware type, command callback, timers, hwdep, card, mode/rhythm/max voices, optional sequencer clients/channel sets, patch hash table, voices, connection/drum shadows, and locks. APIs include create/init/timer/hwdep setup, open/ioctl/release/write, reset, patch load/find/clear.

Control flow: a legacy card creates the OPL3 object, initializes registers, exposes hwdep and optionally sequencer devices, then note/patch writes allocate voices and program operator/key registers. Timer interrupts and system timers handle note-offs and effects.

State and persistence behavior: state is per-card in-memory synth state plus shadow registers and loaded patch table. Hardware FM registers persist until reset; patches are not persisted across driver unload.

Dependencies and integration points: depends on ALSA hwdep, timer, sequencer, MIDI channel, resource/I/O, and legacy sound card drivers such as SB/OPL4.

Risks and edge cases: voice allocation races, patch hash lifetime, timer locking, OPL2 vs OPL3 register-bank differences, and 4-operator connection programming are fragile.

Test signals: OPL2/OPL3 create/reset, hwdep ioctl/write, patch load/find/clear, sequencer note on/off, timer interrupts, stereo/4-op modes, and builds without sequencer support.
