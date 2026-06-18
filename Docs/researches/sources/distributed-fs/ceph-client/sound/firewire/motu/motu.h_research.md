# sources/distributed-fs/ceph-client/sound/firewire/motu/motu.h

## Purpose

This header defines the shared MOTU driver model: central device state, packet format descriptions, cache state, model specs, clock/protocol enums, submodule prototypes, and inline dispatchers from generic protocol calls to version-specific implementations.

## Important APIs, types, and functions

Key types are `struct snd_motu`, `struct snd_motu_packet_format`, `struct amdtp_motu_cache`, and `struct snd_motu_spec`. Flags describe MIDI byte positions and DSP parser style. `enum snd_motu_clock_source` normalizes clock source variants across models. Inline helpers `snd_motu_protocol_get_clock_rate/set_clock_rate/get_clock_source/switch_fetching_mode/cache_packet_formats()` dispatch on `spec->protocol_version`.

## Control flow

The inline dispatchers route v2 first, v3 second, and otherwise v1. This makes `spec->protocol_version` the controlling switch for PCM, stream, and proc users. The header also declares external spec objects for all supported models so the FireWire ID table can bind devices to behavior.

## State and persistence behavior

`struct snd_motu` stores all runtime state: ALSA card/unit references, locks, stream resources, substream count, async handler, hwdep lock state, AMDTP domain, cache ring, and DSP parser pointer. No static persistent state is created here.

## Dependencies and integration points

It includes Linux FireWire, ALSA core/control/PCM/rawmidi/hwdep/info, and common FireWire AMDTP/iso-resource helpers. All MOTU `.c` files include this header as their internal contract.

## Risks and test signals

Risks include ABI drift with UAPI DSP structures, incorrect dispatch defaults, and field lifetime assumptions across modules. Compile coverage is important because this header wires many submodules; runtime signals include lock state transitions, stream counter correctness, and protocol dispatch per model.
