# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h

Chunk: `subset-b-001602`
Covered source range: lines 52213-54345 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h`

## Purpose

This chunk is part of AMD's generated DCN 1.0 register shift/mask header. It contains preprocessor constants only; there are no functions, structs, enums, runtime branches, or storage objects in the covered range. The constants describe bit positions and masks for Azalia/HDA HDMI/DisplayPort audio codec endpoint registers.

The source path is under a local `ceph-client` mirror, but the file itself is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The covered range starts mid-register with the final mask for `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_7`, then completes the tail of output endpoint 7. After that it defines the full repeated field layouts for `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind`. These input endpoint blocks expose indexed Azalia codec input converter and input pin fields, including audio widget capabilities, converter format, stream/channel IDs, IEC 60958 digital converter bits, supported formats/rates, pin capabilities, unsolicited responses, input sense, multichannel routing, high-bit-rate audio status, hotplug/audio enable state, configuration defaults, LPIB snapshots, input activity, and channel-status/infoframe capture.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. Its public interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask in the register payload.
- Register names beginning with `AZF0ENDPOINT7_` describe fields behind output endpoint 7's indexed Azalia pin-control/function registers.
- Register names beginning with `AZF0INPUTENDPOINT0_` through `AZF0INPUTENDPOINT7_` describe eight repeated input endpoint indexed register blocks.

The endpoint 7 tail covers:

- `PIN_CONTROL_CODEC_CS_OVERRIDE_8`: IEC 60958 channel number fields for channels 6 and 7.
- `CODEC_PIN_ASSOCIATION_INFO`: full 32-bit association metadata.
- `CODEC_PIN_CONTROL_DIGITAL_OUTPUT_STATUS`: `OUTPUT_ACTIVE`.
- `CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`: link position snapshot lock, wrap count, 32-bit LPIB, and timer snapshot fields.
- `CODEC_PIN_CONTROL_CODING_TYPE`: 8-bit coding type.
- `CODEC_PIN_CONTROL_FORMAT_CHANGED`: format-changed latch, unsolicited-response enable, reason, and response fields.
- `CODEC_PIN_CONTROL_WIRELESS_DISPLAY_IDENTIFICATION` and `REMOTE_KEEPALIVE`: WFD identification, keepalive enable, and capability fields.
- `AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`: audio enable state plus flag/mask/type interrupt triplets.

Each input endpoint instance `0..7` repeats the same field families:

- `CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: HDA widget capability bits for channel capability, input/output amplifiers, amplifier-parameter override, format override, stripe, processing widget, unsolicited responses, connection list, digital support, power control, LR swap, delay, and widget type.
- `CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: channel count, bits per sample, sample-base divisor/multiple/rate, and stream type.
- `CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel ID and stream ID nibbles.
- `CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital enable and IEC-style channel status flags such as validity, validity configuration, pre-emphasis, copy, non-audio, professional mode, level, channel-status category code, and keepalive.
- `CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES`: 32-bit format bitmap plus rate and bit-depth capability fields.
- `CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CAPABILITIES`: input pin widget capability bits plus pin capabilities for impedance sense, trigger requirement, jack detect, headphone drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DisplayPort.
- `CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE` and `UNSOLICITED_RESPONSE_FORCE`: tag/enable fields and a forced unsolicited-response payload trigger.
- `CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: impedance sense and presence detect.
- `CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`: `IN_ENABLE`.
- `CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`: enable, mute, and channel-ID fields for multichannel slots 0-7.
- `CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`: HBR capable and HBR enable bits.
- `CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: 8-bit channel allocation.
- `CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and audio-enabled bit.
- `CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: HDA configuration-default fields such as sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- `CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`: position and timer snapshot fields for input streams.
- `CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`: input activity, channel layout, input-activity unsolicited-response enable, and channel-layout/channel-status infoframe-change unsolicited-response enable.
- `CODEC_INPUT_PIN_CONTROL_INFOFRAME`: channel count, channel allocation, infoframe byte 5, and infoframe-valid bit.

## Control Flow

This header chunk has no local control flow. Every significant line is a `#define` consumed by the C preprocessor.

Runtime control flow lives in AMD display/audio code that pairs this `dcn_1_0_sh_mask.h` metadata with offset/index definitions and register helpers:

1. DCN 1.0 resource code includes `dcn/dcn_1_0_offset.h` and this mask header, then builds audio register and field tables.
2. `display/dc/dce/dce_audio.h` defines `AUD_COMMON_REG_LIST`, `AUD_COMMON_MASK_SH_LIST`, and related `SF(...)` helpers. These concatenate register and field names into entries in `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask`.
3. `display/dc/resource/dcn10/dcn10_resource.c` instantiates DCN 1.0 audio register tables for audio instances and maps `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` / `DATA` fields into the common audio mask/shift structures.
4. `display/dc/dce/dce_audio.c` writes `AZALIA_F0_CODEC_ENDPOINT_INDEX` to select an indexed Azalia codec register and reads or writes `AZALIA_F0_CODEC_ENDPOINT_DATA` to transfer the payload.
5. Higher-level audio paths such as `dce_aud_az_enable`, `dce_aud_az_disable`, and `dce_aud_az_configure` use `AZ_REG_READ`, `AZ_REG_WRITE`, `set_reg_field_value`, and `get_reg_field_value` against HDA codec pin/function fields. The fields in this chunk describe the same kind of payload layout for endpoint 7 and the input endpoint indexed blocks.

The chunk itself does not encode sequencing. Correct ordering around clock-gating disable, hotplug/audio enable, HBR capability exposure, stream format programming, descriptor updates, LPIB snapshots, and interrupt/status handling is imposed by `dce_audio.c`, stream encoder code, the HDA controller, and hardware register specifications.

## State And Persistence Behavior

The macros are stateless compile-time constants. They do not allocate memory, perform I/O, store persistent data, or modify hardware by themselves.

The hardware fields they describe are stateful. Output endpoint 7 fields can hold channel-status override data, association information, output-active status, LPIB snapshots, coding type, format-change state, wireless-display identification, keepalive settings, audio-enable state, and interrupt flag/mask/type state. Input endpoint fields can hold converter format, stream/channel IDs, digital converter flags, supported format/rate capability data, pin capabilities, unsolicited-response enables and force payloads, input sense, multichannel routing/mute/channel IDs, HBR state, hotplug/audio state, configuration defaults, LPIB snapshots, input activity, channel layout, and infoframe-derived channel information.

Those hardware values persist until changed by the driver, HDA/Azalia controller activity, audio stream start/stop, hotplug events, sink/source format changes, power management, display block reset, suspend/resume, or GPU reset. Some fields are configuration bits, some are capability or readback/status bits, some are interrupt mask/status fields, and some appear to be self-clearing or action-trigger fields based on names such as `*_FORCE`, `*_FLAG`, `*_STATUS`, `*_SNAPSHOT_LOCK`, and `*_FORMAT_CHANGED`. The header does not encode access type, reset value, reserved-bit policy, write-one-to-clear behavior, or power-domain restrictions.

## Dependencies And Integration Points

Immediate dependencies are the C preprocessor and AMD's generated register naming scheme. Practical integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`, which supplies matching `ix...` indexed-register constants for the Azalia endpoint payloads and `mm...` constants for the endpoint index/data MMIO registers.
- DCN 1.0 resource construction in `display/dc/resource/dcn10/dcn10_resource.c`, which includes this mask header and builds `audio_shift` / `audio_mask` tables from generated field names.
- Common audio abstractions in `display/dc/dce/dce_audio.h`, especially `AUD_COMMON_REG_LIST`, `AUD_COMMON_MASK_SH_LIST_BASE`, `AUD_COMMON_MASK_SH_LIST`, and the `struct dce_audio_*` table types.
- Indirect Azalia access helpers in `display/dc/dce/dce_audio.c`: `write_indirect_azalia_reg`, `read_indirect_azalia_reg`, `AZ_REG_READ`, and `AZ_REG_WRITE`.
- Field manipulation helpers in `display/dc/inc/reg_helper.h`, including `REG_SET`, `REG_UPDATE`, `set_reg_field_value`, and `get_reg_field_value`.
- The HDA/Azalia controller and sink/source audio paths that consume endpoint capabilities, channel status, hotplug state, HBR capability, stream format, and infoframe/channel allocation data.

The repeated `AZF0INPUTENDPOINT0..7` naming is a key generated-header contract. Each instance is expected to have the same field layout. Code can then reason about endpoint instance selection through indexed register addresses while field extraction remains identical across instances. The mask header alone does not select an input endpoint; it defines the bit layout once per generated endpoint name.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong shift or mask can compile cleanly but program or interpret the wrong bits in an indexed Azalia endpoint payload.
- The chunk starts mid-register. The final line for `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_7` belongs with definitions in the previous chunk; final file-level reconciliation should merge it before treating endpoint 7's channel-status override fields as complete.
- The input endpoint blocks are highly repetitive. A copied endpoint number, field name, shift, or mask error can affect only one input endpoint and appear as an instance-specific audio capture, infoframe, presence-detect, or channel-layout problem.
- Many fields are protocol-sensitive HDA/HDMI/DP audio metadata. Misinterpreting converter format, sample-size/rate fields, channel allocation, IEC 60958 channel-status bits, or HBR state can produce missing audio, wrong channel mapping, unsupported-format advertisement, or non-audio/pro-audio flag mismatches while the display path still works.
- Indirect endpoint access has two layers: an MMIO index/data pair and an indexed payload register. Mixing `mm...`, `ix...`, and field-mask namespaces is not type-checked by C.
- Status, interrupt, and force fields likely have side effects that are not visible in this generated header. Treating a flag as ordinary read/write state can lose events, retrigger unsolicited responses, or fail to acknowledge a hardware condition.
- `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED` fields affect hardware power/clock visibility. Writes while the endpoint is clock-gated, or leaving clock gating disabled after updates, can cause unreliable readback or unnecessary power use.
- LPIB snapshot fields combine a lock bit, wrap counter, position, and timer. Reading these without the intended snapshot sequence can produce inconsistent audio position/timestamp pairs.
- Capability fields such as widget capabilities, pin capabilities, supported size/rates, and HBR capability may be consumed by upper audio stacks. Advertising unsupported capabilities or hiding supported ones can shift failures into userspace audio enumeration rather than obvious kernel errors.

## Test Signals

Useful validation signals include:

- compile coverage for DCN 1.0 display/audio files that include `dcn_1_0_sh_mask.h`, especially `display/dc/resource/dcn10/dcn10_resource.c`, `display/dc/dce/dce_audio.c`, and `display/dc/dce/dce_audio.h`;
- generated-header consistency checks that every field in this range has both a `__SHIFT` and `_MASK`, except for the intentionally partial first line inherited from the previous chunk;
- consistency checks across `AZF0INPUTENDPOINT0..7` confirming identical field names, shifts, and masks for every repeated input endpoint instance;
- offset/mask pairing checks against `dcn_1_0_offset.h` to ensure matching `ixAZF0ENDPOINT7_...` and `ixAZF0INPUTENDPOINT0..7_...` indexed-register constants exist for the register names described here;
- hardware audio smoke tests over HDMI and DisplayPort: hotplug, modeset, enable/disable audio, suspend/resume, stream start/stop, and rapid display reconfiguration;
- HDA/Azalia enumeration checks confirming expected widget capabilities, supported rates/bit depths, pin capabilities, configuration defaults, HBR capability, and channel allocation;
- DP/HDMI audio functional tests for stereo, multichannel, HBR/non-HBR formats, sample-rate changes, non-audio bitstream formats, channel-status reporting, and infoframe channel allocation;
- event tests for unsolicited responses, format-changed interrupts, audio enabled/disabled interrupts, input activity changes, and infoframe/channel-layout changes;
- debug/readback checks for LPIB snapshot stability, wrap-count movement during playback/capture, `OUTPUT_ACTIVE` / `AUDIO_ENABLE_STATUS`, `INPUT_ACTIVITY`, `INFOFRAME_VALID`, and hotplug/audio-enabled state;
- negative signals in logs or user-visible behavior: missing ALSA HDMI/DP audio device, wrong EDID audio capability exposure, absent HBR formats, channel order errors, stuck audio-enabled state, repeated format-change events, stale LPIB snapshots, or failures isolated to endpoint 7 or a specific input endpoint instance.
