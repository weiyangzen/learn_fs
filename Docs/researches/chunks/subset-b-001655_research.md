# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 13054-13875

## Scope

This chunk is the final DCN 2.1.0 register-offset segment for AMD display audio/Azalia blocks. It contains generated C preprocessor constants only: no structs, functions, executable control flow, or storage definitions are introduced here. The covered range starts with the last three `AZF0STREAM15` latency counter indices, then defines indirect endpoint register indices for eight output endpoints (`AZF0ENDPOINT0` through `AZF0ENDPOINT7`) and eight input endpoints (`AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`). The file closes with the header guard `#endif`.

The chunk contributes 755 `#define` entries. Every `addressBlock` in this range has `base address: 0x0`, because these values are not direct MMIO offsets by themselves; they are indices written through an Azalia endpoint index/data window.

## Purpose

`dcn_2_1_0_offset.h` is the DCN21 generated register address table used by the AMDGPU display driver for Renoir/DCN 2.1 hardware. Earlier parts of the file define direct MMIO offsets and base-index selectors for display, GPIO, interrupt, DMUB, DCCG, and audio wrapper registers. This tail chunk defines the indirect register numbers inside each Azalia function 0 endpoint.

The constants provide stable symbolic names for hardware-defined audio codec registers:

- `ixAZF0STREAM15_AZALIA_WORSTCASE_LATENCY_COUNT`, `ixAZF0STREAM15_AZALIA_CUMULATIVE_LATENCY_COUNT`, and `ixAZF0STREAM15_AZALIA_CUMULATIVE_REQUEST_COUNT` complete the stream-15 latency/counter group.
- `ixAZF0ENDPOINTn_*` defines output converter and output pin-control register indices for endpoint instances 0-7.
- `ixAZF0INPUTENDPOINTn_*` defines input converter and input pin-control register indices for input endpoint instances 0-7.

The values are small codec register indices such as `0x0001`, `0x0020`, `0x0054`, and `0x006e`, not full bus addresses. Runtime code selects an endpoint's index/data MMIO pair, writes one of these indices into the endpoint index register, and then reads or writes the endpoint data register.

## Important Definitions

### Output Endpoint Blocks

Each `azf0endpointN_endpointind` block, for N in 0-7, repeats the same 75-register output endpoint layout:

- Converter capability and programming:
  - `...CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` at `0x0001`
  - `...CONTROL_CONVERTER_FORMAT` at `0x0002`
  - `...CONTROL_CHANNEL_STREAM_ID` at `0x0003`
  - `...CONTROL_DIGITAL_CONVERTER` at `0x0004`
  - `...PARAMETER_STREAM_FORMATS` at `0x0005`
  - `...PARAMETER_SUPPORTED_SIZE_RATES` at `0x0006`
  - `...STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and GTC delta min/max registers at `0x0007`-`0x000e`.
- Pin capability and pin-control registers:
  - widget and pin capabilities at `0x0020` and `0x0021`
  - unsolicited response, pin sense, widget control, and channel/speaker allocation at `0x0022`-`0x0025`
  - `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` at `0x0028`-`0x0035`, used to expose sink audio format capabilities
  - multichannel, lipsync, HBR, and sink-info registers at `0x0036`-`0x0042`
  - hot-plug/audio enable and forced unsolicited response registers at `0x0054` and `0x0055`
  - configuration default, multichannel mode, codec channel-status overrides, association info, digital output status, LPIB snapshot/status, coding type, format-changed, wireless-display identification, remote-keepalive, and audio enable/interrupt status registers at `0x0056`-`0x006e`.

The output endpoint block is the part most directly tied to normal HDMI/DP audio output. `dce_audio.c` uses generic `ixAZALIA_F0_CODEC_*` names for the active endpoint, while DCN21 resource construction maps endpoint instances through `AZF0ENDPOINTn_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `...DATA` direct MMIO registers elsewhere in this same generated header.

### Input Endpoint Blocks

Each `azf0inputendpointN_inputendpointind` block, for N in 0-7, repeats a smaller 22-register input endpoint layout:

- Input converter capability and programming at indices `0x0001`-`0x0006`.
- Input pin capability and control at `0x0020`-`0x0024`.
- Multichannel enable, HBR, channel allocation, hot-plug/audio-enable, unsolicited response force, configuration default, LPIB snapshot/status, input status control, and input infoframe registers at `0x0036`-`0x0068`.

These names mirror output endpoint concepts but include `INPUT_` in the macro names and omit output-specific descriptors such as the `SINK_INFO0`-`SINK_INFO8`, codec channel-status override, digital output status, coding type, wireless display, and audio-format-change interrupt status registers.

## Runtime Integration

This header is included by DCN21 display code, notably:

- `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`

For this chunk, the meaningful consumer path is the DC audio resource setup:

- `dcn21_resource.c` includes this offset header and builds `audio_regs[]` with `AUD_COMMON_REG_LIST(id)`.
- `AUD_COMMON_REG_LIST(id)` in `display/dc/dce/dce_audio.h` expands to `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and `SRI(AZALIA_F0_CODEC_ENDPOINT_DATA, AZF0ENDPOINT, id)`, plus common audio function and DTO registers.
- `dcn21_create_audio()` passes `&audio_regs[inst]`, `audio_shift`, and `audio_mask` to `dce_audio_create()`.
- `dce_audio.c` implements `write_indirect_azalia_reg()` and `read_indirect_azalia_reg()`: these first program `AZALIA_F0_CODEC_ENDPOINT_INDEX.AZALIA_ENDPOINT_REG_INDEX`, then write/read `AZALIA_F0_CODEC_ENDPOINT_DATA.AZALIA_ENDPOINT_REG_DATA`.
- Higher-level audio setup uses `AZ_REG_READ()` and `AZ_REG_WRITE()` around indirect names such as `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR`, `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, `AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, `AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0 + format_index`, and `AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO0`-`SINK_INFO8`.

The line-range definitions therefore support the final indirect-index step for endpoint-local HDA codec programming. The companion `dcn_2_1_0_sh_mask.h` defines bit shifts and masks for these register payloads, while `soc21_enum.h` provides enum values for many decoded fields, including Azalia widget capabilities, HBR capability, multichannel mode, and input endpoint status concepts.

## Control Flow

There is no local control flow in this generated header chunk. The effective runtime flow is:

1. DCN21 resource initialization selects an audio endpoint instance and stores its direct index/data MMIO addresses in `struct dce_audio_registers`.
2. Audio configuration code computes HDMI/DP audio capabilities from CRTC timing, link information, and sink `audio_info`.
3. The driver writes an indirect endpoint register index, using the `ix...` numeric constants generated in this header family.
4. The driver writes or reads the endpoint data register using bitfield masks from `dcn_2_1_0_sh_mask.h`.
5. Hardware persists the resulting audio endpoint state until changed, reset, or power-managed by the display/audio block.

Typical output endpoint updates include enabling/disabling the audio pin, exposing HBR capability, programming lipsync delay, setting speaker/channel allocation, filling short-audio descriptors, and publishing sink information. The input endpoint definitions in this chunk are available for hardware support and mask/enum completeness, though the common DCN21 `dce_audio.c` path primarily programs output endpoint register names.

## State and Persistence

The header itself has no mutable state. It defines compile-time numeric constants.

The hardware registers named by these constants are stateful. Important endpoint state classes include:

- Capability/configuration state: converter format, stream ID, supported formats/rates, widget/pin capabilities, configuration default.
- Active audio-output state: hot-plug/audio-enable control, widget output enable, channel/speaker allocation, HBR enable/capability, lipsync, audio descriptors, sink info, and digital converter flags.
- Monitoring/counter state: LPIB snapshots, timer snapshots, latency counters, audio enable/disable/format-change interrupt status, input activity, and infoframe validity.
- Protocol-visible state: unsolicited response controls, pin sense, configuration default, and sink-info fields that can affect what the audio stack or connected sink observes.

Because the values are hardware indices, persistence is governed by the GPU display/audio block, suspend/resume paths, display hotplug, and driver reinitialization. Any incorrect constant can persist as an incorrect register write until the block is reset or the endpoint is reprogrammed.

## Dependencies

This chunk depends on the hardware register map generated for DCN 2.1.0. Its definitions are paired with:

- `dcn_2_1_0_sh_mask.h` for the bit-level layout of each endpoint register.
- `soc21_enum.h` for semantic enum values associated with Azalia fields.
- `renoir_ip_offset.h` and `DMU_BASE__INST0_SEG*` base macros for direct MMIO base calculation in DCN21 resource, IRQ, GPIO, and DMUB users.
- `display/dc/dce/dce_audio.h` for `AUD_COMMON_REG_LIST(id)` and the `struct dce_audio_registers` contract.
- `display/dc/dce/dce_audio.c` for indirect Azalia read/write helpers and HDMI/DP audio programming.
- AMD DC register helper macros such as `REG_SET`, `REG_READ`, `REG_SET_FIELD`, `SR`, `SRI`, and `SF`.

The generated naming convention is itself an integration dependency. Call sites synthesize names by token concatenation, so spelling, instance numbering, and suffix consistency are compile-time API surface.

## Risks

- **Wrong index values can program the wrong endpoint-local register.** Since these are indirect indices, a single bad value can redirect writes to unrelated codec state while still compiling cleanly.
- **Instance copy/paste or generator drift is high impact.** The output and input endpoint blocks are repeated for eight instances; mismatched values between instances would create endpoint-specific audio failures that are easy to miss in single-port testing.
- **Confusing direct offsets with indirect indices is a maintenance risk.** Most of `dcn_2_1_0_offset.h` contains `mm...` direct MMIO offsets plus `_BASE_IDX`; this chunk's `ix...` values are endpoint register numbers and must be used through the Azalia index/data window.
- **Field masks must match these offsets.** The companion mask header has instance-specific field names for `AZF0ENDPOINTn_*` and `AZF0INPUTENDPOINTn_*`; stale masks paired with changed indices would produce silent hardware misprogramming.
- **Audio behavior is sink- and timing-dependent.** Registers in this chunk expose EDID-derived audio descriptors, HBR support, channel allocation, lipsync, and sink info. Bad programming may present as missing audio, unsupported sample rates, wrong channel layout, HBR failures, or hotplug/audio enable races.
- **Input endpoint coverage may be lightly exercised.** The source tree's common DC audio path focuses on output endpoint programming. Input endpoint constants can remain compile-validated but receive less runtime coverage unless capture/input-audio paths are tested on supporting hardware.

## Test Signals

Useful signals for this chunk are mostly integration and hardware-behavior tests, not unit tests:

- Build coverage for DCN21/Renoir display code with `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h` included; token-concatenated register names should compile for audio, GPIO, IRQ, and DMUB users.
- HDMI and DisplayPort audio playback on each available endpoint instance, including endpoint instances beyond 0 when hardware exposes multiple display audio pins.
- Hotplug/replug tests that verify `HOT_PLUG_CONTROL`, unsolicited response, and audio enable/disable behavior do not leave stale audio state.
- EDID/audio-mode tests that exercise `AUDIO_DESCRIPTOR0`-`13`, channel/speaker allocation, sink info, and advertised sample-rate/channel capabilities.
- HBR audio tests, especially 192 kHz / 8-channel or compressed high-bitrate formats, to verify `RESPONSE_HBR` and descriptor programming.
- Suspend/resume and display modeset tests to ensure indirect endpoint state is restored after hardware reset or power transitions.
- Register trace/debugfs comparison against known-good DCN21 hardware tables: index writes should match expected values such as `0x0025` for channel/speaker, `0x0038` for HBR response, `0x0054` for hot-plug control, and `0x0064`-`0x0066` for LPIB snapshots.

## Summary

Lines 13054-13875 are a generated register-map chunk for DCN21 Azalia stream, output endpoint, and input endpoint indirect registers. The code does not implement algorithms, but it is part of the compile-time hardware ABI used by AMDGPU display audio setup. Its correctness is validated through successful DCN21 builds and hardware tests that cover HDMI/DP audio enablement, sink capability publication, HBR support, channel allocation, endpoint hotplug, and state restoration.
