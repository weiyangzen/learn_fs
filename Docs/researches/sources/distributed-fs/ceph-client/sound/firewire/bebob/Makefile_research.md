# sources/distributed-fs/ceph-client/sound/firewire/bebob/Makefile

Purpose: builds the BeBoB ALSA FireWire driver object `snd-bebob.o` from common command, stream, proc, MIDI, PCM, hwdep, vendor quirk, and probe modules.

Important APIs/types/functions: no C API, but the object list defines integration order for `bebob_command.o`, `bebob_stream.o`, `bebob_proc.o`, `bebob_midi.o`, `bebob_pcm.o`, `bebob_hwdep.o`, `bebob_terratec.o`, `bebob_yamaha_terratec.o`, `bebob_focusrite.o`, `bebob_maudio.o`, and `bebob.o`.

Control flow and state: Kbuild links these compilation units into a single module enabled by `CONFIG_SND_BEBOB`. There is no persistence or runtime state here.

Dependencies/integration: integrates with the kernel sound/firewire build and depends on symbols supplied by the listed files plus common FireWire audio modules. Risks are build coverage risks: missing a new source file here would omit vendor support or driver entry points. Test signals are successful kernel build with `CONFIG_SND_BEBOB=m/y` and module symbol resolution.
