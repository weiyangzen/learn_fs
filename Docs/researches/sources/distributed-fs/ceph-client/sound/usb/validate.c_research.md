<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/validate.c -->
# sources/distributed-fs/ceph-client/sound/usb/validate.c

## Purpose
Validation layer for USB audio and MIDI class-specific descriptors, preventing parsers from reading malformed descriptor bodies unless the global skip-validation quirk is enabled.

## APIs, Types, and Functions
Exports `snd_usb_validate_audio_desc()` and `snd_usb_validate_midi_desc()`. Internal validator functions cover UAC1 headers, mixer units, processing/extension units, selector units, UAC1/2/3 feature units, UAC3 power domains, and MIDI out jacks. Static tables `audio_validators` and `midi_validators` map protocol/type pairs to fixed-size or function checks.

## Control Flow, State, and Persistence
`validate_desc()` ignores non-class-interface descriptors, finds a matching validator by subtype and protocol, then applies either a fixed minimum length or a protocol-aware length calculation. Public functions dump invalid bytes and accept them only when `snd_usb_skip_validation` is set. There is no persistent state beyond static validator tables.

## Dependencies and Integration
Depends on USB audio v1/v2/v3 and MIDI descriptor definitions, ALSA USB-audio module options from `usbaudio.h`, and `print_hex_dump()` for diagnostics. Descriptor parsers call this before consuming variable-length fields.

## Risks and Test Signals
Risks include incomplete validation for some unimplemented descriptor types, complex variable-length calculations based on untrusted fields, accepting unknown subtypes by default, and skip-validation masking real bugs. Test signals are fuzzed descriptors, known quirky devices with skip enabled, UAC1/2/3 mixer/selector/processing descriptors, MIDI jack descriptors, and parser KASAN/UBSAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/validate.c -->
