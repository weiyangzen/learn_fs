# sources/distributed-fs/ceph-client/sound/usb/format.h

## Purpose
Declares USB-audio format parsing entry points.

## APIs and Integration
`snd_usb_parse_audio_format()` parses a UAC1/UAC2 format descriptor and fills an `audioformat`. `snd_usb_parse_audio_format_v3()` parses a UAC3 AS header and fills the same model. These functions are consumed by stream discovery code outside this subset before PCM devices and endpoint constraints are created.

## State, Dependencies, and Risks
The caller owns the `audioformat` object and any lifetime for allocated rate tables. Callers must pass descriptor pointers validated enough for the implementation’s protocol-specific casts. Incorrect `stream` or partially initialized `fp` fields can produce wrong endpoint/rate capability data.

## Test Signals
Build coverage and enumeration of UAC1, UAC2, and UAC3 devices detect API drift. Descriptor parsing tests should confirm that output `audioformat` fields match expected ALSA constraints.
