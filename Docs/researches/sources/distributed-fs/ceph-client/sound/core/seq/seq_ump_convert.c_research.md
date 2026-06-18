# sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_convert.c

## Purpose
`seq_ump_convert.c` converts events between UMP sequencer clients and legacy ALSA sequencer clients, and between MIDI 1.0 and MIDI 2.0 UMP channel voice formats. It handles value scaling, group filtering/rewriting, sysex7 packetization, bank-select carry state, and RPN/NRPN aggregation.

## Important APIs, Types, and Functions
- `snd_seq_deliver_from_ump()` receives a UMP event and delivers it to a UMP or legacy destination, converting protocol/format as needed.
- `snd_seq_deliver_to_ump()` converts a legacy sequencer event to UMP MIDI 1.0, UMP MIDI 2.0, or sysex7 UMP packets for a UMP destination.
- `snd_seq_ump_group_port()` returns the 1-based UMP group port for a UMP event or `-1`.
- Scaling helpers convert 7/14/16/32-bit MIDI value ranges.
- `cvt_ump_midi1_to_event()`, `cvt_ump_midi2_to_event()`, and `cvt_ump_system_to_event()` produce legacy events from UMP packets.
- `cvt_ump_midi1_to_midi2()` and `cvt_ump_midi2_to_midi1()` adapt raw UMP channel voice packets between MIDI versions.
- `cvt_sysex_to_ump()` and `cvt_ump_sysex7_to_event()` convert sysex byte streams and UMP data packets.

## Control Flow
For UMP-source delivery, variable events are skipped, destination group filters are applied, and the UMP message type determines the conversion. UMP destinations receive packet copies, protocol-adapted MIDI1/MIDI2 packets, or group-rewritten packets when a destination port is tied to a specific group. Legacy destinations receive converted sequencer events; MIDI 2 program-with-bank can emit two legacy events.

For legacy-to-UMP delivery, destination group filters are applied first. Sysex events are expanded chunk by chunk into UMP sysex7 packets, stripping start/end markers and setting single/start/continue/end status. Non-sysex events are looked up in `seq_ev_ump_encoders[]` and converted to MIDI 1.0 or MIDI 2.0 UMP depending on destination client protocol and port MIDI1 flag.

MIDI 2 conversion keeps per-port/per-channel state in `dest_port->midi2_bank[]` to combine bank select and RPN/NRPN controller sequences into richer MIDI 2 messages.

## State and Persistence
The file's own state is static tables only. Persistent conversion carry state is stored in destination port `midi2_bank[]` fields for bank select, RPN/NRPN selection, and data entry until flushed or consumed.

## Dependencies and Integration Points
Depends on UMP message helpers from `<sound/ump.h>` and `<sound/ump_msg.h>`, sequencer client/port internals, and `__snd_seq_deliver_single_event()`. It is used by the client manager delivery path when UMP and non-UMP clients interoperate.

## Risks
Protocol conversion is lossy when downscaling MIDI 2.0 high-resolution values to legacy/MIDI1 ranges. Sysex7 conversion currently handles 7-bit sysex packets, not arbitrary UMP data formats. Bank/RPN carry state can be affected by interleaved controller streams on the same destination port/channel. Group filter bit semantics are 1-based for groups plus a groupless bit, so off-by-one errors are easy.

## Test Signals
Test every event mapping in `seq_ev_ump_encoders[]`, value scaling boundaries, MIDI2 note-on velocity zero correction, MIDI2 program bank-valid splitting, MIDI1 bank-select-to-MIDI2 program carry, RPN/NRPN aggregation and reset, sysex start/continue/end/single packetization, group rewriting, group filtering, and UMP-to-legacy multi-event delivery.
