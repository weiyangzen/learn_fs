# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam.h

## Purpose

This header defines the shared TASCAM FireWire driver state, register map, model specification, MIDI transaction state, stream API, and submodule prototypes.

## Important APIs, types, and functions

`struct snd_tscm_spec` records model capabilities. `struct snd_fw_async_midi_port` stores outbound async MIDI transaction state. `struct snd_tscm` centralizes ALSA card/unit refs, locks, stream resources, async MIDI handler, MIDI substreams, status cache, hwdep queue, AMDTP domain, and skip-cycle state. The header defines all `TSCM_OFFSET_*` register constants and `enum snd_tscm_clock`.

## Control flow

Inline helpers `snd_fw_async_midi_port_run()` and `finish()` start and stop outbound MIDI work by setting the active substream and scheduling or canceling work. Other behavior is declared for implementation in TASCAM source files.

## State and persistence behavior

The header describes all runtime state. Hardware state lives in registers under `TSCM_ADDR_BASE`, while kernel state persists only for the card lifetime.

## Dependencies and integration points

It includes ALSA core/info/PCM/rawmidi/hwdep, Linux FireWire, and common AMDTP/iso-resource helpers. It is included by every TASCAM implementation file.

## Risks and test signals

Risks include register-map uncertainty, queue-size limitations, port-count maxima, and lifetime coupling between work items and card removal. Compile tests catch prototype drift; runtime tests should stress MIDI work cancellation, hwdep queue wrap, and stream state transitions.
