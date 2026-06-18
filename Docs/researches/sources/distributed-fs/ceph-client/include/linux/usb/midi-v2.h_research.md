# `sources/distributed-fs/ceph-client/include/linux/usb/midi-v2.h`

## Purpose

`midi-v2.h` defines USB MIDI 2.0 class descriptor constants and packed descriptor layouts. It extends the older USB MIDI definitions with group terminal block descriptors, MIDIStreaming 2.0 revisions, protocol identifiers, and helper fields used by ALSA USB MIDI parsing.

## Important APIs, Types, and Constants

- Descriptor constants include class-specific group terminal block descriptor type `USB_DT_CS_GR_TRM_BLOCK`, endpoint subtype `USB_MS_GENERAL_2_0`, group terminal block subtypes, and MIDIStreaming revisions.
- Protocol constants identify MIDI 1.0 over UMP variants, MIDI 2.0, and jitter-reduction timestamp variants.
- Group terminal block type constants identify bidirectional, input-only, and output-only groups.
- The header includes USB MIDI 1.0 definitions and builds on their jack/interface subtype values.
- Packed descriptor structs define group terminal block headers and block entries for parsing class-specific descriptors.

## Control Flow and Lifetimes

USB audio/MIDI drivers parse interface and endpoint descriptors during probe. For MIDI 2.0, they locate group terminal block descriptors, read revision/protocol/group counts, and map UMP groups to ALSA rawmidi/UMP endpoints. Descriptor data is immutable for the device configuration lifetime.

## State and Persistence Behavior

The header defines descriptor ABI and constants. Runtime MIDI endpoint state, UMP group mappings, and stream state live in the ALSA USB MIDI implementation.

## Dependencies and Integration Points

It depends on `linux/types.h` and `linux/usb/midi.h`. It integrates USB class descriptor parsing with ALSA MIDI 2.0/UMP support and generic USB descriptor walking.

## Risks and Edge Cases

Packed descriptor parsing must check `bLength` before accessing trailing fields. Drivers must distinguish MIDI 1.0 and 2.0 revisions and handle unknown protocol values. Group counts and first-group indexes can describe invalid or overlapping ranges if not validated.

## Test Signals

Probe MIDI 2.0 devices, parse descriptors with multiple group terminal blocks, validate fallback for MIDI 1.0 descriptors, fuzz descriptor lengths/protocol IDs, verify ALSA UMP group exposure, and test hot unplug during active MIDI streams.
