# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-midi.c

## Purpose

This file creates ALSA RawMIDI ports for TASCAM FireWire models and connects them to the driver's asynchronous MIDI transaction layer.

## Important APIs, types, and functions

`snd_tscm_create_midi_devices()` creates a duplex RawMIDI device sized by model spec port counts and names hardware ports. Capture trigger stores active input substreams in `tx_midi_substreams`. Playback open initializes the corresponding `snd_fw_async_midi_port`; playback trigger starts its workqueue; drain finishes/cancels it.

## Control flow

Capture open/close are no-ops because inbound MIDI arrives through the async address handler. Playback open resets per-port transaction state. Trigger-up starts or records substreams under the driver spinlock; trigger-down clears capture substreams, while playback cleanup happens through drain/finish.

## State and persistence behavior

This file mutates active capture substream pointers and per-output async MIDI port state. RawMIDI device and substream names persist for the card lifetime.

## Dependencies and integration points

It depends on transaction helpers in `tascam-transaction.c`, model port counts from `tascam.c`, and ALSA RawMIDI core.

## Risks and test signals

Risks include output work continuing after close without drain, capture pointer races with async callbacks, and unsupported virtual ports. Tests should cover all model port counts, capture trigger toggles during incoming MIDI, playback running status/SysEx, drain behavior, and bus reset while output work is active.
