# sources/distributed-fs/ceph-client/sound/core/ump.c

## Purpose

This file implements ALSA Universal MIDI Packet endpoint support on top of rawmidi. It creates UMP rawmidi devices, parses UMP stream messages, maintains endpoint and function-block metadata, forwards packets to userspace and the sequencer, and optionally exposes legacy MIDI 1.0 rawmidi devices backed by UMP conversion.

## Important APIs, Types, and Functions

The exported APIs are `snd_ump_endpoint_new()`, `snd_ump_receive_ump_val()`, `snd_ump_receive()`, `snd_ump_transmit()`, `snd_ump_block_new()`, `snd_ump_update_group_attrs()`, `snd_ump_switch_protocol()`, `snd_ump_parse_endpoint()`, and, with legacy support, `snd_ump_attach_legacy_rawmidi()`. Important state includes `struct snd_ump_endpoint`, `struct snd_ump_block`, `struct snd_ump_group`, rawmidi substream arrays, stream-discovery wait state, sequencer device hooks, and legacy mapping/converter arrays.

## Control Flow

Endpoint creation allocates an `snd_ump_endpoint`, initializes rawmidi with the UMP info flag, assigns UMP-specific global and stream ops, and initializes lists and locks. Device registration optionally creates a sequencer device. Receive flow accumulates 32-bit words with `snd_ump_receive_ump_val()`, handles complete stream messages, forwards to sequencer input hooks, converts to legacy input streams if enabled, then copies raw UMP data to the UMP input substream. Transmit flow reads UMP bytes from the UMP output substream and, when no UMP data is available, can synthesize UMP from opened legacy output streams. Endpoint parsing opens an internal rawmidi output stream, sends discovery requests, waits for matching stream-message replies, fills endpoint/device/name/product/protocol fields, creates function blocks, updates group attributes, then closes the internal stream.

## State and Persistence Behavior

Endpoint metadata persists in `ump->info`, block list entries, per-group attributes, and rawmidi names. Stream discovery uses `stream_wait_for`, `stream_finished`, `input_buf`, and a wait queue with a 500 ms timeout per request. Function block updates after initial parsing may refresh group attributes, legacy substream names, and sequencer clients, except static-block endpoints suppress updates. Legacy rawmidi support persists group-to-substream mapping, output converter state per group, open counts, and tied rawmidi devices.

## Dependencies and Integration Points

The file depends on ALSA rawmidi, UMP protocol definitions, UMP conversion helpers, ALSA sequencer device hooks, procfs info, kernel list/mutex/spinlock/wait primitives, and card/device registration. Hardware-specific UMP drivers supply `ump->ops` for open/close/trigger/drain and call `snd_ump_receive()` and `snd_ump_transmit()`.

## Risks

Risks include malformed or partial UMP packets leaving stale input state, stream-discovery timeouts, deadlocks around internal rawmidi open/write during parsing, incorrect static function-block update handling, bounds errors in group ranges, legacy conversion mismatches, and race-prone name/substream updates while legacy devices are open. The fallback behavior when devices do not respond to optional discovery messages needs to remain tolerant.

## Test Signals

Use UMP-capable virtual or USB MIDI devices to verify endpoint parse, stream config, function-block creation, dynamic function-block update, procfs output, UMP rawmidi read/write, sequencer notifications, and legacy rawmidi group mapping. Include malformed stream messages, timeout-only devices, MIDI 1.0 function blocks under MIDI 2 protocol, and concurrent UMP plus legacy opens.
