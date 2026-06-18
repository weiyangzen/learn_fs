# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-transaction.c

## Purpose

This file implements TASCAM asynchronous MIDI transaction support and device registration of the host callback address.

## Important APIs, types, and functions

`calculate_message_bytes()` classifies MIDI status lengths. `fill_message()` formats outbound MIDI into a four-byte TASCAM quadlet with port label and up to three MIDI bytes, handling running status and SysEx. `midi_port_work()` schedules and sends outgoing quadlet transactions at MIDI baud timing. `handle_midi_tx()` receives inbound MIDI block writes. Register/reregister/unregister functions manage the device callback address, MIDI TX enable bit, and FireWire LED.

## Control flow

Outbound work peeks RawMIDI bytes, forms a complete message only when enough bytes are available, schedules the next send time based on consumed bytes, sends a FireWire write request, and acknowledges bytes only after a successful callback. Recoverable errors retry immediately; permanent errors stop the port. Inbound handler splits block transactions into messages, selects the hardware port from the label, estimates MIDI length, and delivers bytes to active capture substreams.

## State and persistence behavior

Per-output-port state includes work item, next send time, transaction object, running status, SysEx state, active substream, and error/idling flags. Device state persists callback address and MIDI/LED enable registers until unregister or bus reset.

## Dependencies and integration points

It depends on RawMIDI, FireWire request callbacks, `tascam-midi.c` trigger state, and bus-reset update calling `snd_tscm_transaction_reregister()`.

## Risks and test signals

Risks include MIDI parser edge cases, timing drift, no support for virtual ports, queue starvation when incomplete SysEx bytes are pending, and races with close/reset. Tests should cover running status, SysEx start/end, real-time messages, recoverable/permanent transaction errors, inbound block batches, bus reset, and unregister cleanup.
