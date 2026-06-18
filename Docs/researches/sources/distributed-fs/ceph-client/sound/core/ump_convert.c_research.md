# sources/distributed-fs/ceph-client/sound/core/ump_convert.c

## Purpose

This file implements conversion helpers between Universal MIDI Packet data and legacy MIDI 1.0 byte streams. It is used by UMP legacy rawmidi bridging to translate incoming UMP packets into MIDI bytes and outgoing legacy MIDI bytes into MIDI 1.0 or MIDI 2.0 UMP packets.

## Important APIs, Types, and Functions

The exported APIs are `snd_ump_convert_from_ump()` and `snd_ump_convert_to_ump()`. Internal helpers scale values between 7-, 14-, 16-, and 32-bit MIDI encodings, convert UMP system/channel/SysEx7 messages to MIDI bytes, convert MIDI byte streams to UMP system/SysEx/channel messages, and track bank/RPN/NRPN state in `struct ump_cvt_to_ump` and `struct ump_cvt_to_ump_bank`.

## Control Flow

UMP-to-legacy conversion dispatches on UMP message type, returns the target group, and emits MIDI bytes for system, MIDI 1 channel voice, MIDI 2 channel voice, and SysEx7 packets. Legacy-to-UMP conversion is byte-stream driven: status bytes establish expected command length, realtime/system messages are emitted when complete, SysEx bytes are packed into 6-byte UMP data chunks, and channel messages are converted according to the requested endpoint protocol. MIDI 2 output expands controller, pressure, pitch bend, notes, program/bank select, and RPN/NRPN sequences into the wider UMP encodings.

## State and Persistence Behavior

`snd_ump_convert_from_ump()` is stateless. `snd_ump_convert_to_ump()` mutates the caller-owned converter context, including partial command bytes, SysEx state, generated packet bytes, per-channel bank select state, and deferred RPN/NRPN data. This persistence is required for running-status-like byte stream assembly and multi-message controller sequences.

## Dependencies and Integration Points

It depends on ALSA UMP protocol macros and structures from `sound/ump.h` and `sound/ump_convert.h`. `sound/core/ump.c` uses it for legacy rawmidi input and output conversion, and any other driver can reuse the exported conversion helpers.

## Risks

Conversion is intentionally lossy when downscaling MIDI 2 values to MIDI 1. Edge cases include note-on with zero velocity, bank select state lifetime, incomplete RPN/NRPN sequences, SysEx chunk boundaries, unsupported UMP message types, realtime bytes interrupting SysEx, and host endianness assumptions around casting UMP words to unions. A zero return means "no complete output" rather than hard failure, so callers must preserve converter state.

## Test Signals

Round-trip tests should cover all channel voice statuses, MIDI 2 value scaling boundaries, program changes with and without bank select, pitch bend extremes, RPN and NRPN complete and partial sequences, SysEx single/start/continue/end packets, realtime/system messages, unsupported data types, and group preservation across conversions.
