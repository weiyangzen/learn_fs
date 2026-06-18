<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ump.h -->
# sources/distributed-fs/ceph-client/include/sound/ump.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/ump.h` is ALSA Universal MIDI Packet core API
header for UMP endpoints, blocks, conversion state, sequence integration, rawmidi attachment, packet
helpers, and MIDI 1.0/2.0 protocol switching. The source was read as a complete 282-line header for
this report.

## Important APIs, Types, and Functions

types: `snd_ump_endpoint`, `snd_ump_block`, `snd_ump_ops`, `ump_cvt_to_ump`, `snd_seq_ump_ops`,
`snd_ump_group`; enums: `anonymous enum`; functions/prototypes: `snd_ump_endpoint_new`,
`snd_ump_parse_endpoint`, `snd_ump_block_new`, `snd_ump_receive`, `snd_ump_transmit`,
`snd_ump_attach_legacy_rawmidi`, `snd_ump_receive_ump_val`, `snd_ump_switch_protocol`,
`snd_ump_update_group_attrs`; inline helpers: `snd_ump_attach_legacy_rawmidi`, `ump_message_type`,
`ump_message_group`, `ump_message_status_code`, `ump_message_channel`, `ump_message_status_channel`,
`ump_compose`, `ump_sysex_message_status`, `ump_sysex_message_length`, `ump_stream_message_format`,
`ump_stream_message_status`, `ump_stream_compose`; macros/constants: `__SOUND_UMP_H`,
`rawmidi_to_ump`, `ump_is_groupless_msg`

## Control Flow

A driver creates a UMP endpoint, adds function blocks, receives or transmits raw UMP words through
ALSA rawmidi, and optionally attaches legacy rawmidi devices or sequence operations. Conversion
helpers translate between byte-stream MIDI and UMP packets while tracking bank/RPN/NRPN state.

## State and Persistence Behavior

Endpoint state includes rawmidi handles, block lists, protocol flags, group metadata, sequence
client data, conversion accumulators, and private driver data. Conversion state is resettable and
caller-owned.

## Dependencies and Integration Points

Direct includes: `sound/rawmidi.h`. Integrates with ALSA core, ASoC codec/card drivers, rawmidi/seq,
firmware loading, or legacy card drivers depending on the matching subsystem.

## Risks and Edge Cases

Risks include packet length/type mismatches, group indexing errors, protocol switch races, stale
conversion state for RPN/NRPN/bank messages, and legacy rawmidi attachment behavior when
`CONFIG_SND_UMP_LEGACY_RAWMIDI` is disabled.

## Test Signals

Test endpoint/block creation, packet helper extraction, receive/transmit paths, protocol switching,
conversion of running MIDI streams, legacy rawmidi attach stubs, sequence integration, and malformed
UMP packet handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ump.h -->
