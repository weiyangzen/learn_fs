# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 62208-64603

Chunk: `subset-b-001562`
Covered source range: lines 62208-64603 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h`

## Purpose

This chunk is a generated AMD DCE 12.0 register field mask header section. It contains no executable driver logic; it publishes C preprocessor constants that encode bit positions and masks for display-controller audio and legacy VGA indexed registers.

The range is dominated by Azalia/HD-audio codec metadata for GPU display audio. It covers the tail of `AZF0INPUTENDPOINT3`, complete input endpoint blocks for `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7`, the `AZALIA_F2_CODEC` function and pin/input-pin register families, descriptor and sink-info indexed blocks, Azalia CRC result blocks, and the beginning of VGA sequencer/CRT indexed fields.

Each register field is represented by generated macro pairs:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask for the field.

The companion address header, `dce_12_0_offset.h`, supplies the `mm*` and `ix*` register offsets. This header supplies the field layout inside those offsets.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or storage objects in this chunk. The macro namespace is the API.

Major covered macro families are:

- `AZF0INPUTENDPOINT3_*`: this chunk begins in the middle of endpoint 3 input-pin audio widget capability definitions, then covers endpoint 3 input-pin capability, unsolicited-response, pin-sense, widget-control, multichannel, HBR, channel-allocation, hot-plug, configuration-default, LPIB, input-status, and infoframe fields.
- `AZF0INPUTENDPOINT4_*` through `AZF0INPUTENDPOINT7_*`: repeated input endpoint blocks for input converter and input pin controls. Converter fields include audio widget capabilities, format fields (`BASE_RATE`, `MULTICHANNEL_TYPE`, `CHANNELS`, `BITS_PER_SAMPLE`, `NUMBER_OF_CHANNELS`), stream/channel IDs, digital converter state (`DIGITAL_ENABLE`, `PROFESSIONAL`, `NONAUDIO`, `COPYRIGHT`, `EMPHASIS`, `CATEGORY_CODE`, `VALIDITY`, `KEEPALIVE_ENABLE`, `DESIRED_SAMPLE_RATE`, `DIGITAL_DEFAULT`), supported formats, and supported sizes/rates. Pin fields include capabilities, unsolicited responses, input pin sense, widget input enable, multichannel enables for channels 0-7, HBR capability/enable, channel allocation, hot-plug audio enable, forced unsolicited responses, default configuration, LPIB snapshots, input activity, channel layout, and incoming infoframe fields.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: root/function-level codec identity, revision, subordinate node count, function power state, subsystem ID response words, converter synchronization, function reset, group type, supported sample sizes/rates, stream formats, and supported power states.
- `AZALIA_F2_CODEC_CONVERTER_*`: output converter format, channel/stream ID, digital converter status/control, stripe control, ramp rate, GTC embedding, converter audio widget capabilities, supported sizes/rates, and stream formats.
- `AZALIA_F2_CODEC_PIN_*`: output pin controls and parameters, including connection-list entry, widget control, unsolicited response, pin sense, configuration default words, speaker allocation, channel allocation, down-mix info, audio descriptor index/data, multichannel enable groups, lip-sync, HBR, sink-info index/data, multichannel mode, codec channel-status override words, pin association info, digital output status, LPIB snapshots, coding type, format-change status, wireless display identification, remote keepalive, pin audio widget capabilities, pin capabilities, and connection-list length.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin counterparts for format, stream ID, digital converter fields, input pin control, pin sense/configuration, channel allocation, per-channel multichannel enables, HBR, LPIB snapshots, input activity/channel layout, input infoframe, channel-status low/high words, and input pin capabilities.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: packed descriptor slots for maximum channels, sample-rate mask, and stereo/6/8-channel PCM or compressed audio coding flags. These describe EDID/ELD-like audio capability descriptors made visible through the Azalia sink path.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` sink-info fields and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`: manufacturer/product ID, sink description length, port IDs, and packed 32-bit sink-description words.
- `AZALIA_INPUT_CRC0_CHANNEL0..7`, `AZALIA_INPUT_CRC1_CHANNEL0..7`, `AZALIA_CRC0_CHANNEL0..7`, and `AZALIA_CRC1_CHANNEL0..7`: full-width 32-bit CRC result fields for input and general Azalia CRC result indexed blocks.
- `SEQ00` through `SEQ04`: legacy VGA sequencer fields, including sequencer reset bits, 8-dot/shift/pixel-clock controls, plane map enables, font select bits, 256K, odd/even, and chain mode.
- `CRT00` through `CRT11`: the beginning of legacy VGA CRT controller fields, including horizontal timing, vertical timing extension bits, row scan/byte pan, cursor start/end/location, display start, vertical sync start/end, vertical interrupt clear/enable, refresh-cycle select, and write-protect behavior.

The range starts after earlier endpoint 3 converter definitions and ends at `CRT11`; `CRT12` and later CRT fields continue in the next chunk.

## Control Flow

This file has no runtime control flow. It is a sequence of `#define` directives inside the larger generated include guard.

Runtime control flow appears in consumers that:

1. choose a register address from `dce_12_0_offset.h`, such as an `ixAZF0INPUTENDPOINT4_*`, `ixAZALIA_F2_CODEC_*`, `ixAUDIO_DESCRIPTOR*`, `ixSINK_DESCRIPTION*`, `ixAZALIA_CRC*`, `ixSEQ*`, or `ixCRT*` offset;
2. access the correct direct or indexed register window for that DCE/Azalia/VGA block;
3. extract fields with `(value & FIELD_MASK) >> FIELD__SHIFT`, or clear and insert fields with the same pair;
4. write the result back only when the hardware register is writable and the caller follows the required audio/display sequencing.

The generated constants do not enforce any codec verb ordering, stream enable sequencing, hot-plug ordering, LPIB snapshot locking, CRC-latch behavior, or legacy VGA timing restrictions. Those requirements live in display/audio driver code and in the DCE hardware programming guide.

## State And Persistence Behavior

The header itself has no mutable software state and persists only as compiled constants.

The fields describe hardware state in the DCE 12.0 display audio and VGA blocks. State represented by this chunk includes:

- converter and pin widget capability values reported to the HDA/Azalia codec model;
- stream format, channel count, channel ID, stream ID, and digital converter status/control bits;
- input and output pin capabilities, jack/presence sense, unsolicited response enable/tag state, and forced unsolicited response payloads;
- hot-plug audio enable and clock-gating control bits;
- high-bit-rate audio enable/capability and HDMI/DisplayPort channel allocation state;
- LPIB and timer snapshots plus cyclic buffer wrap count state;
- input activity, channel layout, infoframe validity, and channel-status words;
- sink capability data, audio descriptors, port IDs, and sink description words;
- CRC result snapshots for Azalia output/input paths;
- legacy VGA sequencer and CRT timing/cursor/display-start register state.

Persistence depends on the register class. Some fields are read-only capability or status reports, some are writable controls, some are sticky or latched diagnostic values, and some reflect firmware, BIOS, connector, EDID/ELD, or hardware strap-derived state. Values can be reset or reinitialized by display mode set, audio stream setup/teardown, HPD handling, runtime power management, suspend/resume, GPU reset, display core reset, or full device power loss.

## Dependencies And Integration Points

The direct dependency is the matching generated DCE 12.0 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`

That file defines the direct endpoint index/data registers, such as `mmAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` and `mmAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`, and the indexed offsets used with this chunk, such as `ixAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`, `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR`, `ixAUDIO_DESCRIPTOR0`, `ixSINK_DESCRIPTION0`, `ixAZALIA_CRC0_CHANNEL0`, `ixSEQ00`, and `ixCRT00`.

Known local include points for `dce_12_0_sh_mask.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`

The broader integration path is AMDGPU Display Core on DCE 12.0 ASICs. Display audio setup, hot-plug handling, stream formatting, infoframe generation, sink capability exposure, and diagnostic CRC readback all depend on the register layout matching the ASIC. Legacy VGA sequencer/CRT fields integrate with early display/VGA compatibility paths and mode/timing programming.

Although the repository path is under `ceph-client`, this chunk is AMDGPU kernel driver register metadata. It has no distributed filesystem protocol behavior and no Ceph persistence semantics.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Bad masks or shifts compile cleanly but can read the wrong bit, fail to update the target field, or corrupt neighboring fields in packed registers.

This chunk is highly repetitive. Endpoint 4 through endpoint 7 share nearly identical register shapes, and many multichannel fields repeat for channels 0-7. A generation or copy error can put a correct-looking field under the wrong endpoint, channel, or register prefix. Such errors may only appear when a specific input endpoint or channel layout is exercised.

Audio control fields are sequencing-sensitive. Misusing stream format, channel/stream ID, digital converter, HBR enable, channel allocation, hot-plug audio enable, or widget input-enable fields can produce missing audio, wrong channel mapping, incorrect sample size/rate reporting, or broken HDMI/DisplayPort HBR audio behavior.

Presence, unsolicited response, and force-response fields affect event delivery. Incorrect masks can suppress hot-plug or pin-sense notifications, generate spurious responses, or cause the audio stack to believe a sink has changed when it has not.

LPIB and timer snapshot fields are diagnostic/timing-sensitive. Callers must respect the snapshot lock and wrap-count semantics when correlating audio buffer position with display/audio timing; the mask header does not encode that protocol.

Sink-info and audio-descriptor fields are externally visible to audio policy. Incorrect descriptor bits can advertise unsupported codecs, sample rates, channel counts, or sink identity values, leading to bad userspace audio choices or failed link validation.

CRC fields are full-width values. They should be treated as diagnostic readback values, not as bitfield controls, even though they follow the same generated mask/shift naming pattern.

Legacy VGA sequencer and CRT fields are narrow 8-bit-style indexed registers embedded in a 32-bit macro namespace. Using 32-bit assumptions without respecting VGA indexed-register access and timing semantics can corrupt display-start, cursor, blanking, or sync behavior. The chunk ends before the rest of the CRT register family, so file-level analysis must merge the following chunk before validating complete VGA CRT coverage.

## Test Signals

Useful validation signals include:

- kernel build coverage for DCE 12.0/Vega display paths that include `dce_12_0_sh_mask.h`;
- generated-header consistency checks that every `*_MASK` has a matching `__SHIFT` across the complete file, with this chunk's first and last line-boundary splits resolved during file-level merge;
- comparison against the authoritative DCE 12.0 register database and the adjacent `dce_12_0_offset.h` register names;
- static checks that endpoint-specific masks are used with the matching endpoint offsets and index/data windows;
- HDMI and DisplayPort audio bring-up tests across stereo, multichannel, compressed formats, HBR, sample-rate changes, and stream enable/disable cycles;
- hot-plug and pin-sense tests that verify unsolicited response tags/enables, presence-detect state, sink re-enumeration, and audio enable state;
- EDID/ELD or sink-capability inspection tests that confirm audio descriptors, speaker allocation, manufacturer/product IDs, port IDs, and sink descriptions are decoded as expected;
- LPIB snapshot and audio position tests that compare reported buffer position/timer snapshots with playback progress under wraparound;
- CRC diagnostic tests that read `AZALIA_INPUT_CRC*` and `AZALIA_CRC*` channels under known audio/display traffic;
- legacy VGA smoke tests for early console, mode set, cursor, blanking, and suspend/resume paths on DCE 12.0 hardware or emulation.

Regression symptoms from bad constants include missing HDMI/DP audio devices, wrong channel layout, HBR audio failure, spurious or missing audio hot-plug events, incorrect sink capability reporting, unstable playback position reporting, CRC diagnostics changing on the wrong channel, or broken VGA compatibility display behavior.

## Cross-Chunk Notes

This chunk starts inside `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`; earlier endpoint 3 converter and the start of that pin capability block are in the previous chunk. It ends at `CRT11`; `CRT12` and the rest of the VGA CRT indexed register block continue in the next chunk. The final per-file research document should treat these boundaries as chunking artifacts, not as source-level omissions.
