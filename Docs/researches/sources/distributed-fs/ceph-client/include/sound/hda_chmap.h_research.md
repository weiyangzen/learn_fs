# sources/distributed-fs/ceph-client/include/sound/hda_chmap.h

## Purpose
This header defines HD-audio HDMI/DisplayPort channel-map support: CEA speaker allocation data, operation callbacks, and helper APIs for channel allocation, mapping, and ALSA controls.

## Important APIs, Types, and Functions
`struct hdac_cea_channel_speaker_allocation` stores CEA channel-allocation index, up to eight speakers, and derived channel count/speaker mask. `struct hdac_chmap_ops` provides overridable callbacks for TLV map generation, validation, speaker allocation lookup, get/set channel map, PCM attachment check, pin slot channel get/set, and channel count programming. `struct hdac_chmap` stores max channels, ops, and hdac device. Functions register ops, compute channel allocation, active channel count, set up mapping, print allocation, map CA to allocation records, convert channel/speaker encodings, and add ALSA channel-map controls.

## Control Flow
HD-audio HDMI codecs register chmap ops, expose controls on PCM devices, validate user channel maps, compute CEA allocation from speaker allocation/channel count/non-PCM status, program converter/pin slot assignments, and report current maps through ALSA TLVs.

## State and Persistence
Current channel maps and speaker allocations are maintained by codec hardware and driver state. `hdac_chmap` persists for the codec/device lifetime. User-selected maps may be runtime control state and need restore across stream prepare/resume as implemented by codec drivers.

## Dependencies and Integration Points
It depends on ALSA PCM and `sound/hdaudio.h`. It integrates with HDMI/DP audio codecs, ELD/speaker allocation, ALSA channel-map controls, and HDA pin/converter programming.

## Risks and Edge Cases
CEA allocation validation is subtle, especially for non-PCM streams and devices with non-standard mapping. Ops callbacks may be partially overridden; defaults must remain coherent. Channel count and slot mapping must be synchronized with stream prepare state to avoid wrong speaker output.

## Test Signals
Channel-map ALSA control tests for 2/6/8 channels, CEA allocation conversion, invalid user maps, non-PCM mode, HDMI ELD speaker masks, and prepare/resume mapping restoration are important.
