# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-register-dsp-message-parser.c

## Purpose

This file parses register-DSP status messages embedded in MOTU isochronous packets. It maintains cached meter/parameter state and queues change events for hwdep clients for models whose DSP controls are exposed through asynchronous register access.

## Important APIs, types, and functions

`snd_motu_register_dsp_message_parser_new()` allocates parser state and records 4pre/Audio Express meter-position quirks. `snd_motu_register_dsp_message_parser_init()` resets sequencing state at stream start. `snd_motu_register_dsp_message_parser_parse()` scans packet descriptors and updates mixer, output, line input, input, and meter caches. Copy/count/event functions expose snapshots and queued events to other MOTU UAPI code.

## Control flow

The parser locks its private spinlock, iterates packets then data blocks, derives `msg_type` and `val` from fixed byte offsets, and uses previous-message state to infer channel indexes for message series. When a cached parameter changes, `queue_event()` pushes a compact 32-bit event and wakes `hwdep_wait`. Meter messages update meter bytes but intentionally do not alter previous-message sequencing.

## State and persistence behavior

`struct msg_parser` persists meter data, parameter snapshots, inferred channel cursors, previous message type, and a 16-entry circular event queue. The queue is explicitly described as rough and has no overrun check, so old events can be overwritten.

## Dependencies and integration points

It depends on MOTU AMDTP packet layout, `struct pkt_desc`, model flags, and UAPI structures under `sound/firewire.h`. It is initialized from `motu-stream.c` before domain start and consumed by hwdep paths elsewhere in the MOTU driver.

## Risks and test signals

Risks include queue overrun, byte-offset quirks, inferred channel desynchronization after packet loss, and event loss when no hwdep client is open. Useful tests are high-rate meter streams, rapid mixer-control changes, 4pre/Audio Express layout validation, and concurrent snapshot/event reads while streaming.
