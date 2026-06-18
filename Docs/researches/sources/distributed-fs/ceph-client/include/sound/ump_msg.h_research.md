<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ump_msg.h -->
# sources/distributed-fs/ceph-client/include/sound/ump_msg.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/ump_msg.h` is Universal MIDI Packet wire-layout
header for MIDI 1.0 channel voice, MIDI 2.0 channel voice, system, endpoint stream, device info,
stream config, and function block messages. The source was read as a complete 765-line header for
this report.

## Important APIs, Types, and Functions

types: `snd_ump_midi1_msg_note`, `snd_ump_midi1_msg_paf`, `snd_ump_midi1_msg_cc`,
`snd_ump_midi1_msg_program`, `snd_ump_midi1_msg_caf`, `snd_ump_midi1_msg_pitchbend`,
`snd_ump_system_msg`, `snd_ump_midi2_msg_note`, `snd_ump_midi2_msg_paf`,
`snd_ump_midi2_msg_pernote_cc`, `snd_ump_midi2_msg_pernote_mgmt`, `snd_ump_midi2_msg_cc`,
`snd_ump_midi2_msg_rpn`, `snd_ump_midi2_msg_program`, and 10 more; unions: `snd_ump_midi1_msg`,
`snd_ump_midi2_msg`, `snd_ump_stream_msg`; enums: `anonymous enum`; macros/constants:
`__SOUND_UMP_MSG_H`

## Control Flow

Callers map raw 32-bit UMP words into the appropriate union view based on message type, group,
status, and stream status. MIDI 1.0 messages occupy one word, MIDI 2.0 channel voice messages occupy
two words, and stream messages occupy four words.

## State and Persistence Behavior

State is only the packet payload supplied by caller buffers. The packed structs define endian-
sensitive views over UMP words and do not allocate or retain data.

## Dependencies and Integration Points

Direct includes: none. Integrates with ALSA core, ASoC codec/card drivers, rawmidi/seq, firmware
loading, or legacy card drivers depending on the matching subsystem.

## Risks and Edge Cases

Risks include bitfield order differences across endian modes, packed layout assumptions, invalid
status/type combinations, stream name byte-order FIXME handling, and callers using a union view
before checking packet length and message type.

## Test Signals

Test raw word round-trips for big- and little-endian layouts, every MIDI 1.0 and MIDI 2.0 status
family, stream endpoint discovery/info/config/function-block messages, malformed packet lengths, and
UMP parser interoperability with USB MIDI 2.0 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ump_msg.h -->
