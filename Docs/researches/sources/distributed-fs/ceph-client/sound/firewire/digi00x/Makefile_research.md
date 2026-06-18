# sources/distributed-fs/ceph-client/sound/firewire/digi00x/Makefile

Purpose: builds the Digidesign Digi 002/003 family FireWire driver object `snd-firewire-digi00x.o`.

Important APIs/types/functions: no C API, but object composition includes `amdtp-dot.o`, `digi00x-stream.o`, `digi00x-proc.o`, `digi00x-pcm.o`, `digi00x-hwdep.o`, `digi00x-transaction.o`, `digi00x-midi.o`, and `digi00x.o`.

Control flow and state: Kbuild links the protocol-specific AMDTP DOT implementation with stream, ALSA surface, transaction, and probe code when `CONFIG_SND_FIREWIRE_DIGI00X` is enabled. There is no runtime state in this file.

Dependencies/integration: integrates with kernel sound/firewire build. Risks are object list omissions, particularly because `amdtp-dot.o` provides protocol callbacks used by stream code. Test signals are successful module build and symbol resolution for Digi00x stream/PCM/MIDI/hwdep helpers.
