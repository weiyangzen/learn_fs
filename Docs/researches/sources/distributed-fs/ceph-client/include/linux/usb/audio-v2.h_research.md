<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/audio-v2.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/audio-v2.h

Purpose: defines USB Audio Class 2.0 descriptor layouts, control-bit decoders, class-specific constants, and selector codes.

Important APIs and types: `uac_v2v3_control_is_readable()` and `uac_v2v3_control_is_writeable()` decode two-bit `bmControls` fields. Packed descriptor structs model AC headers, format type I, clock source/selector/multiplier, input/output terminals, feature/effect units, AS headers, isochronous endpoint descriptors, connector control blocks, and interrupt messages. `DECLARE_UAC2_FEATURE_UNIT_DESCRIPTOR(ch)` builds fixed-size feature-unit descriptors. Constants define function categories, descriptor subtypes, effect/process/encoder/decoder types, request codes, clock/terminal/mixer/selector/feature/effect/processing/extension/AS/endpoint control selectors, and raw-data format bits.

Control flow: USB audio host and gadget code parse class-specific descriptor streams using these packed structures, inspect `bmControls` through helpers, build requests with selector constants, and generate descriptors for gadget functions.

State and persistence: no runtime state is stored. The structs describe on-wire descriptor data and request parameters supplied by devices or gadget descriptors.

Dependencies and integration points: depends on fixed-width Linux types and common USB Audio 1.0 definitions in `audio.h` for shared constants. It integrates with ALSA USB audio parsing, UAC2 gadget functions, and USB descriptor validation.

Risks and test signals: risks include variable-length descriptor under/over-read, little-endian field handling, invalid `bmControls` selector numbers, spec typo compatibility, and channel-count size calculations. Test with real UAC2 devices, descriptor fuzzing, gadget enumeration against hosts, control read/write requests, and malformed feature/effect units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/audio-v2.h -->
