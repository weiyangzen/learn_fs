# sources/distributed-fs/ceph-client/sound/firewire/amdtp-am824.c

Purpose: implements AM824 payload handling for AMDTP FireWire streams. It maps ALSA S32 PCM frames and rawmidi bytes into IEC 61883-6 AM824 data blocks and extracts them on receive.

Important APIs, types, and functions: `struct amdtp_am824` stores rawmidi substream pointers, MIDI FIFO rate-limit state, PCM/MIDI channel counts, PCM position map, and MIDI data-channel position. Exported APIs include `amdtp_am824_set_parameters()`, position setters, `amdtp_am824_add_pcm_hw_constraints()`, `amdtp_am824_midi_trigger()`, and `amdtp_am824_init()`. Payload callbacks are `process_it_ctx_payloads()` for transmit and `process_ir_ctx_payloads()` for receive.

Control flow: subdrivers initialize an `amdtp_stream` with `amdtp_am824_init()`, configure rate/channel counts before start, optionally remap PCM/MIDI positions, and attach rawmidi substreams through trigger callbacks. Transmit payload processing writes PCM samples as AM824 multi-bit linear audio with `0x40000000`, writes silence when no PCM is attached, and inserts at most rate-limited MIDI bytes into the configured MIDI position. Receive processing converts AM824 words back to ALSA S32 by shifting and forwards MIDI bytes when the AM824 label length is 1..3.

State and persistence: all protocol state is allocated as `s->protocol`. PCM positions default to identity and MIDI position follows PCM channels. MIDI FIFO accounting is per port and measured in byte-rate units against `amdtp_rate_table[s->sfc]`. There is no persistence beyond the stream lifetime.

Dependencies and integration: depends on `amdtp-stream.c` for packet sequencing, rate tables, PCM constraints, and callback invocation. It integrates with ALSA rawmidi and PCM runtime buffers and with FireWire subdrivers that know device channel layouts.

Risks: `amdtp_am824_set_parameters()` duplicates validation with both explicit checks and `WARN_ON()`, which is harmless but noisy if violated. MIDI supports one conformant channel, up to eight ports; larger devices need other handling. PCM conversion assumes S32 format with 24 meaningful bits. `WRITE_ONCE()` protects MIDI pointer publication, but payload code reads plain `p->midi[port]`; race expectations rely on pointer-size atomicity and ALSA trigger lifetime. Test signals include rate/channel limit errors, double-PCM-frame mode, PCM position remaps, silence generation, MIDI rate limiting over long streams, receive port selection with/without `CIP_UNALIGHED_DBC`, and hw constraint msbits.
