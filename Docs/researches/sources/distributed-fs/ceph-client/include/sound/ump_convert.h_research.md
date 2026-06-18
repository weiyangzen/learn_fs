<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ump_convert.h -->
# sources/distributed-fs/ceph-client/include/sound/ump_convert.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/ump_convert.h` is ALSA Universal MIDI Packet core
API header for UMP endpoints, blocks, conversion state, sequence integration, rawmidi attachment,
packet helpers, and MIDI 1.0/2.0 protocol switching. The source was read as a complete 47-line
header for this report.

## Important APIs, Types, and Functions

types: `ump_cvt_to_ump_bank`, `ump_cvt_to_ump`; functions/prototypes: `snd_ump_convert_from_ump`,
`snd_ump_convert_to_ump`; inline helpers: `snd_ump_convert_reset`; macros/constants:
`__SOUND_UMP_CONVERT_H`

## Control Flow

A driver creates a UMP endpoint, adds function blocks, receives or transmits raw UMP words through
ALSA rawmidi, and optionally attaches legacy rawmidi devices or sequence operations. Conversion
helpers translate between byte-stream MIDI and UMP packets while tracking bank/RPN/NRPN state.

## State and Persistence Behavior

Endpoint state includes rawmidi handles, block lists, protocol flags, group metadata, sequence
client data, conversion accumulators, and private driver data. Conversion state is resettable and
caller-owned.

## Dependencies and Integration Points

Direct includes: `sound/ump_msg.h`. Integrates with ALSA core, ASoC codec/card drivers, rawmidi/seq,
firmware loading, or legacy card drivers depending on the matching subsystem.

## Risks and Edge Cases

Risks include packet length/type mismatches, group indexing errors, protocol switch races, stale
conversion state for RPN/NRPN/bank messages, and legacy rawmidi attachment behavior when
`CONFIG_SND_UMP_LEGACY_RAWMIDI` is disabled.

## Test Signals

Test endpoint/block creation, packet helper extraction, receive/transmit paths, protocol switching,
conversion of running MIDI streams, legacy rawmidi attach stubs, sequence integration, and malformed
UMP packet handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ump_convert.h -->
