# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw.h

## Purpose

This header is the internal contract for the OXFW driver. It defines device state, quirk flags, stream formation types, AV/C helper prototypes, stream/PCM/MIDI/hwdep/proc entry points, and model-specific extension hooks.

## Important APIs, types, and functions

`enum snd_oxfw_quirk` documents transport and device deviations such as jumbo payload, wrong DBS, blocking transmission, SCS transactions, NO_INFO handling, voluntary recovery, unsupported stream-format info, and unusual DBC semantics. `struct snd_oxfw` stores card/unit refs, locks, quirks, stream-format arrays, CMP connections, AMDTP streams, MIDI port counts, hwdep lock state, private `spec`, and domain.

## Control flow

The header does not execute logic except inline wrappers for single/list stream format queries. It establishes that OXFW code uses AV/C plug direction, format arrays capped at `SND_OXFW_STREAM_FORMAT_ENTRIES`, and a shared duplex stream API consumed by PCM and MIDI users.

## State and persistence behavior

All runtime OXFW state is centralized in `struct snd_oxfw`. Format arrays are devm-managed and persist for card lifetime; CMP and AM824 objects are initialized/destroyed by stream code.

## Dependencies and integration points

It includes ALSA control/core/PCM/info/rawmidi/firewire/hwdep and common FireWire libraries for FCP, packets buffer, iso resources, AM824, and CMP. Every OXFW source includes this header.

## Risks and test signals

Risks include quirk flag overlap, stale prototypes, and lifetime coupling around `spec`. Build tests catch most prototype drift; runtime tests should exercise each quirk family and ensure PCM/MIDI/hwdep modules agree on lock and stream counters.
