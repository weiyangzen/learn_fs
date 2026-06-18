# sources/distributed-fs/ceph-client/sound/firewire/dice/Makefile

Purpose: builds the DICE ALSA FireWire driver object `snd-dice.o` from transaction, stream, proc, MIDI, PCM, hwdep, core probe, and vendor detector modules.

Important APIs/types/functions: no C API, but the object list wires `dice-transaction.o`, `dice-stream.o`, `dice-proc.o`, `dice-midi.o`, `dice-pcm.o`, `dice-hwdep.o`, `dice.o`, and detector files for TC Electronic, Alesis, extension, Mytek, PreSonus, Harman, Focusrite, Weiss, and TEAC.

Control flow and state: Kbuild links all components when `CONFIG_SND_DICE` is enabled. It stores no runtime state.

Dependencies/integration: integrates with kernel sound/firewire build and all common DICE helpers. Risks are omission of detector objects from the module when adding device support. Test signals are successful module build and resolution of all detector symbols referenced from `dice.c`.
