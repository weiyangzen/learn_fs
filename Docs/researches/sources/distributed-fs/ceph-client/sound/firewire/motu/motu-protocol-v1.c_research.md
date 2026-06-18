# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v1.c

## Purpose

This file implements MOTU protocol version 1 support for original 828 and 896 models. It decodes their distinct clock/status registers, controls frame fetching/output, detects packet formats, and defines the two v1 model specs.

## Important APIs, types, and functions

Exports include `snd_motu_protocol_v1_get_clock_rate()`, `set_clock_rate()`, `get_clock_source()`, `switch_fetching_mode()`, and `cache_packet_formats()`. 828 helpers operate on `CLK_828_STATUS_OFFSET` and support only 44.1/48 kHz. 896 helpers operate on `CLK_896_STATUS_OFFSET` and support up to 96 kHz. `snd_motu_spec_828` and `snd_motu_spec_896` provide fixed chunk defaults.

## Control flow

Public entry points dispatch by comparing `motu->spec` to the exact model spec. Read paths issue MOTU transactions, convert big-endian registers, and decode bitfields into generic clock enums. Write paths read-modify-write only the relevant bits. Fetching mode for 828 includes a 100 ms delay before enabling PCM frame fetch and output because the device can mute until packets arrive.

## State and persistence behavior

Persistent hardware state is in MOTU registers under `0xfffff0000000`. Driver state updated here is limited to packet-format caches. Packet format detection starts from fixed chunks and adds optical ADAT channels when register state or model assumptions require it.

## Dependencies and integration points

It depends on `snd_motu_transaction_read/write()`, the common rate table, and `motu-stream.c` start/finish sequencing. ALSA constraints in `motu-pcm.c` depend on the cached chunks produced here.

## Risks and test signals

Risks include undocumented register-bit interpretation, device-specific delays, and spec pointer dispatch missing future v1-compatible devices. Test signals are clock-rate changes per model, optical S/PDIF versus ADAT format changes, 828 output unmute behavior, and error handling on invalid register encodings.
