# sources/distributed-fs/ceph-client/sound/firewire/dice/dice.h

Purpose: central DICE internal header defining driver state, stream limits, rate modes, transaction wrappers, stream/PCM/MIDI/hwdep/proc prototypes, and detector prototypes.

Important APIs/types: `MAX_STREAMS`, `enum snd_dice_rate_mode`, `struct snd_dice`, `enum snd_dice_addr_type`, transaction inline wrappers for global/TX/RX/sync sections, `snd_dice_rates`, stream management prototypes, and detector function declarations.

Control flow and state: `struct snd_dice` persists card/unit references, register section offsets, clock capabilities, per-stream channel/MIDI maps, notification handler/generation/bits, hwdep lock state, ISO resources, AM824 streams, global enable flag, high-rate quirk flag, clock completion, substream counter, and AMDTP domain. It is allocated as ALSA card private data and freed through card private cleanup.

Dependencies/integration: includes ALSA, FireWire, AM824, ISO resources, common lib, and `dice-interface.h`. Risks are tight cross-file coupling and fixed `MAX_STREAMS` support despite some ASICs documenting more RX streams. Test signals are successful build across all DICE components and runtime consistency of channel arrays, resources, and streams.
