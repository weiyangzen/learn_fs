# sources/distributed-fs/ceph-client/sound/usb/format.c

## Purpose
Parses USB Audio Class format descriptors into ALSA `audioformat` capabilities. It maps UAC type I/II/III formats to ALSA PCM format bits, builds sample-rate tables for UAC1 and UAC2/UAC3, applies device-specific rate and DSD quirks, and rejects unusable descriptors.

## Important APIs and Functions
Public functions are `snd_usb_parse_audio_format()` for UAC1/UAC2 format descriptors and `snd_usb_parse_audio_format_v3()` for UAC3 AS headers. Core helpers include `parse_audio_format_i_type()`, `parse_audio_format_rates_v1()`, `parse_uac2_sample_rate_range()`, `parse_audio_format_rates_v2v3()`, `validate_sample_rate_table_v2v3()`, `parse_audio_format_i()`, and `parse_audio_format_ii()`.

## Control Flow
For type I/III, parsing determines sample width/subslot size from protocol-specific descriptors, converts UAC format bits to ALSA formats, applies endian and DSD quirks, then parses rates. UAC1 reads discrete or continuous rates from descriptor triplets. UAC2/UAC3 resolves the clock source, issues `UAC2_CS_RANGE` requests, parses min/max/resolution triplets, optionally allocates a rate table, filters known-bad Presonus and Focusrite altsetting rates, validates altsettings for quirked devices by setting sample rates and querying `VAL_ALT_SETTINGS`, and computes rate bitmasks/min/max. Type II maps AC3/MPEG-like streams and parses rates similarly. UAC3 infers type I vs type III from AS `bmFormats`.

## State and Persistence
The function mutates the caller-provided `audioformat`: `formats`, `fmt_type`, `fmt_bits`, `fmt_sz`, `channels`, `frame_size`, `rate_table`, `nr_rates`, `rate_min`, `rate_max`, `rates`, and DSD flags. It allocates `rate_table` memory owned by the format object. Device state may be temporarily changed by validation via clock sample-rate writes and interface altsetting reset.

## Dependencies and Integration
Depends on USB audio descriptors, ALSA PCM format/rate helpers, `clock.c` for source/rate queries, `helper.c` for descriptor lookup, and quirk helpers for endian and DSD handling. Parsed formats feed PCM hw constraints, endpoint setup, and implicit feedback matching.

## Risks and Test Signals
Risks include malformed descriptor lengths, rate-table allocation leaks on repeated parsing, validation side effects on devices that misbehave after rate probes, infinite rate loops if resolution is zero, and hard-coded device filters becoming stale. Test with UAC1 discrete/continuous rates, UAC2 range descriptors, UAC3 BADD/generic formats, Focusrite multi-altsetting devices, Presonus Studio devices, Line 6/Rode fixed-rate quirks, DSD raw/DoP paths, and fuzzed descriptor buffers.
