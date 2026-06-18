# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob.h

Purpose: central BeBoB internal header defining driver state, register addresses, stream formation/spec abstractions, AV/C BridgeCo command interfaces, and cross-file prototypes.

Important APIs/types: `struct snd_bebob`, `struct snd_bebob_stream_formation`, `snd_bebob_clock_spec`, `snd_bebob_rate_spec`, `snd_bebob_meter_spec`, `snd_bebob_spec`, `enum snd_bebob_clock_type`, `enum snd_bebob_quirk`, and BridgeCo plug direction/mode/unit/type enums. Inline helpers read BeBoB info registers and fill BridgeCo plug addresses.

Control flow and state: `struct snd_bebob` owns the ALSA card, FireWire unit, mutex/spinlock, selected spec, quirks, MIDI port counts, two AMDTP streams, two CMP connections, per-rate stream formation caches, sync input plug, hwdep lock state, optional M-Audio special context, and an AMDTP domain. State is runtime-only and torn down by ALSA private free.

Dependencies/integration: includes ALSA core/PCM/rawmidi/hwdep, FireWire core/constants, common FireWire helpers, FCP, packets buffers, ISO resources, AM824, and CMP. Risks are ABI-like internal coupling: every BeBoB source assumes these fields and specs remain consistent. Test signals include compile-time coverage of all extern specs and runtime stream discovery filling formation and MIDI fields before PCM/MIDI creation.
