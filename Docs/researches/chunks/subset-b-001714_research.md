# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 66685-69052

## Scope

This chunk is a generated AMDGPU DCN 3.0.0 register shift/mask header slice. It contains only C preprocessor field constants: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no functions, structs, enums, storage objects, or executable branches in this range.

The covered range starts in the tail of the `AZF0ENDPOINT3` Azalia output endpoint field list, then defines complete repeated field groups for output endpoints `AZF0ENDPOINT4` through `AZF0ENDPOINT7`, and ends at the beginning of `AZF0INPUTENDPOINT0` input endpoint fields. The paired offset/index constants live in `dcn_3_0_0_offset.h`; this file supplies the bit layout used after the driver has selected an indirect Azalia endpoint register.

Within lines 66685-69052 there are 2,042 `#define` entries grouped under 312 register comments/address-block sections.

## Purpose

The purpose of this slice is to describe the bit layout of DCN 3.0 Azalia/HDA codec endpoint registers for HDMI/DisplayPort audio. AMD display code uses these macros through generated register helpers instead of open-coded shifts and masks when programming audio converters, pin widgets, sink/ELD information, channel allocation, IEC 60958 channel status, multichannel controls, hotplug/audio enable state, LPIB snapshots, and endpoint interrupt/status fields.

The output endpoint blocks model HDA codec converter widgets and pin widgets for display audio endpoints. The beginning input endpoint block mirrors the converter/pin field pattern for `AZF0INPUTENDPOINT0`, which represents an Azalia input endpoint space rather than an output pin.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The public interface is the generated macro namespace consumed by AMD display register-table macros:

- `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_2` through endpoint 3 audio interrupt status groups: tail definitions for IEC 60958 channel-status override, pin association, digital output status, LPIB snapshot/readback, format change, remote keepalive, audio enable/disable, and audio format-change interrupt state.
- `AZF0ENDPOINT4_*`, `AZF0ENDPOINT5_*`, `AZF0ENDPOINT6_*`, and `AZF0ENDPOINT7_*`: four complete repeated output endpoint definitions. Each endpoint has the same converter/pin/audio-status schema with instance-specific prefixes.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_CONVERTER_*`: input converter audio widget capability, format, channel/stream ID, digital converter, stream format, and supported size/rate fields.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: beginning of input pin widget capability fields at the chunk boundary.

Important field families include:

- Converter capabilities and format fields: `AUDIO_CHANNEL_CAPABILITIES`, amplifier capability flags, `FORMAT_OVERRIDE`, `STRIPE`, `UNSOLICITED_RESPONSE_CAPABILITY`, `DIGITAL`, `POWER_CONTROL`, `LR_SWAP`, `TYPE`, `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, `SAMPLE_BASE_RATE`, and `STREAM_TYPE`.
- Stream routing and digital converter fields: `CHANNEL_ID`, `STREAM_ID`, `DIGEN`, validity/configuration/pre-emphasis/copy/non-audio/professional/level bits, `CC`, and `KEEPALIVE`.
- Pin capability and widget-control fields: jack/presence/trigger/HDMI/DP capability, output enable, unsolicited response tag/enable, response pin sense, channel allocation/speaker mapping, hotplug control, forced unsolicited response, configuration default, and digital output status.
- Audio descriptor and sink info fields: supported audio format descriptors `0` through `13`, ELD/sink information registers `0` through `8`, latency/HBR response fields, and sink product/manufacturer/port ID style fields.
- Multichannel and channel-status fields: `MULTICHANNEL*_ENABLE`, `MULTICHANNEL*_MUTE`, `MULTICHANNEL*_CHANNEL_ID`, multichannel mode, IEC 60958 mode/source/clock accuracy/word length/sampling frequency/original sampling frequency/channel number fields, and override-enable bits.
- Runtime status and interrupt fields: `AUDIO_ENABLE_STATUS`, audio enabled/disabled/format-changed interrupt flags, interrupt masks, interrupt types, `FORMAT_CHANGED`, change reason/response, `REMOTE_KEEP_ALIVE_*`, LPIB snapshot lock/wrap count, LPIB readback, and LPIB timer snapshot.

The pattern for each register is generated as all shifts followed by all masks. Consumers normally refer to these through `FD_SHIFT`, `FD_MASK`, `SF`, `REG_GET_FIELD`, `REG_SET`, `REG_UPDATE`, or audio-specific helpers rather than by naming the constants directly.

## Control Flow

This header chunk has no runtime control flow. Its effect is compile-time macro expansion:

1. DCN 3.0 display code includes `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`.
2. Resource files instantiate audio register and field tables with generated helper macros. For example, DCN resource code uses `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX, AZALIA_ENDPOINT_REG_INDEX, mask_sh)` and matching data fields to describe the endpoint indirect index/data registers.
3. `dce_audio` code selects an endpoint through the endpoint index/data pair and accesses codec pin/converter indirect registers with `AZ_REG_READ` and `AZ_REG_WRITE`.
4. Field helpers compose or extract values using this chunk's shift and mask constants when updating audio endpoint state.

The chunk does not encode ordering rules. The required ordering for indirect endpoint access, hotplug enablement, audio descriptor programming, ELD/sink info writes, interrupt acknowledgement, and snapshot locking is implemented in the audio/display driver and the hardware programming model.

## State And Persistence Behavior

No software state is stored by this file. It describes fields in hardware-visible Azalia endpoint state.

State represented by this slice includes:

- Converter programming: channel count, sample width, rate divisor/multiple/base-rate, stream type, stream ID, channel ID, digital converter enable, validity/copyright/non-audio/professional bits, channel status category code, and keepalive state.
- Pin widget capability and control: HDMI/DP capability, jack/presence sense, output enable, unsolicited response configuration, default configuration encoding, channel allocation and speaker mapping, hotplug control, and forced response generation.
- ELD and sink metadata: sink information registers, audio descriptors, product/manufacturer/port fields, audio latency, video latency, HBR capability, and display-speaker allocation data used by HDMI/DP audio enumeration.
- IEC 60958 channel-status overrides: mode, source number, clock accuracy, word length, sample frequency, original sample frequency, sampling frequency coefficient, MPEG surround, CGMS-A, and per-channel number fields.
- Multichannel routing: enable/mute/channel ID state for even and odd multichannel slots plus a multichannel-mode bit.
- Runtime and interrupt state: audio enable status, audio enabled/disabled/format-changed flags, masks, type fields, format-change reason/response, remote keepalive capability/enable, LPIB byte position, LPIB timer snapshot, and cyclic buffer wrap count.

Persistence is hardware-dependent. Many converter, pin, ELD, descriptor, channel-status, and multichannel fields remain programmed until a modeset, audio reconfiguration, hotplug event, suspend/resume transition, power-gating event, or ASIC reset overwrites them. Status, interrupt, LPIB, snapshot, format-change, and output-active fields are dynamic and can change asynchronously with display/audio stream activity.

## Dependencies And Integration Points

This chunk is meaningful only with the generated DCN 3.0 register offset/index header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`

Observed direct include points for the DCN 3.0 offset/mask pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Important runtime integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the audio register list entries for `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA`, parameterized by endpoint instance.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` implements `AZ_REG_READ` and `AZ_REG_WRITE` and programs HBR/lipsync responses, hotplug control, channel speaker allocation, audio descriptors, and sink info registers that correspond to field groups in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c` wires DCN 3.0 audio endpoint index/data field metadata into the display resource tables.
- Similar field names are present in adjacent DCN and DCE generation headers, indicating this Azalia endpoint schema is reused across multiple ASIC generations with generated per-generation constants.

## Risks And Edge Cases

- These macros are part of the hardware programming ABI. A wrong shift or mask can compile cleanly while causing the driver to write the wrong bits in an HDA codec endpoint register.
- Output endpoints 4-7 are highly repetitive. Instance-prefix drift can affect only one display audio endpoint, making failures topology-dependent: one connector may lose audio while others still work.
- The range starts and ends mid-logical block. Endpoint 3 is only the tail of an earlier block, and input endpoint 0 continues after line 69052. Whole-file conclusions must merge adjacent chunks.
- Indirect endpoint access requires the correct index/data sequence. These field masks do not distinguish indirect codec registers from ordinary MMIO registers; consumers must not treat `AZF0ENDPOINT*` codec fields as direct addresses.
- Some names describe dynamic or side-effect-sensitive state. `INT_STATUS`, `FORMAT_CHANGED`, `LPIB`, `SNAPSHOT`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `OUTPUT_ACTIVE`, and response/status fields should be handled with the ordering and acknowledge rules expected by the audio hardware.
- Audio descriptor and sink-info fields are externally visible through HDMI/DP audio enumeration. Incorrect masks can advertise invalid channel counts, coding types, sample rates, bit depths, latency, HBR capability, or speaker allocation to the operating system/audio stack.
- IEC 60958 channel-status override fields can create subtle interoperability failures. Bad word length, sample-frequency, clock-accuracy, non-audio, or professional/consumer status bits may only show up with particular receivers or encoded-audio formats.
- LPIB snapshot and cyclic wrap count fields affect stream-position reporting. Incorrect field definitions can cause audio drift diagnostics, underrun handling, or playback-position reporting to fail without an obvious modeset/display symptom.
- Input endpoint fields at the boundary resemble output endpoint fields but are not interchangeable with output pin controls. Reusing output-only assumptions for input endpoints can corrupt the wrong Azalia widget state.

## Test Signals

Useful validation signals are mostly build-time macro expansion plus hardware audio behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.02 support enabled. Missing or renamed macros should fail in resource, audio, IRQ, clock, GPIO, or DMUB consumers that include this generated header.
- Diff this range against the generated source register database and neighboring DCN/DCE generation headers to detect per-endpoint copy/paste drift in endpoints 4-7 and the input endpoint 0 boundary.
- Exercise HDMI and DisplayPort audio on hardware using multiple output endpoints, including hotplug, unplug, DPMS off/on, modeset, suspend/resume, and audio route changes.
- Validate ELD and sink-info programming by checking that the OS audio stack sees correct sink name/manufacturer/product/port data, speaker allocation, latency, HBR support, and audio descriptors.
- Test common PCM formats across channel counts, sample widths, and rates, plus HBR/encoded formats where supported, to cover converter format and IEC 60958 channel-status fields.
- Verify multichannel layouts and channel allocation against receiver-reported capabilities, including mute/enable behavior and per-channel ID mapping.
- Confirm audio enable/disable and audio format-change interrupts are delivered and acknowledged without storms or missed transitions.
- Check LPIB and timer snapshot readback during active playback for monotonic position behavior, wrap-count handling, and absence of underrun/position timeout logs.
- Run receiver interoperability tests with HDMI TVs, AVRs, DisplayPort monitors, and MST/dock paths because channel-status and ELD mistakes often appear only with specific sinks.

## Cross-Chunk Notes

Adjacent chunks are required for a complete view of the Azalia field map. Earlier lines contain the start of `AZF0ENDPOINT3` and prior endpoint blocks; later lines continue `AZF0INPUTENDPOINT0` pin and input-control fields. The final per-file report should reconcile this mask header with `dcn_3_0_0_offset.h` so every indirect Azalia register used by the audio code has both an index/offset definition and matching field masks.
