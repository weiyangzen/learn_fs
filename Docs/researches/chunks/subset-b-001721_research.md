# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 13005-13271

## Scope And Purpose

This chunk is the final segment of AMD's generated DCN 3.0.1 register-offset header. It contains C preprocessor constants only; it does not define functions, structs, enums, executable branches, or mutable storage. The source path is inside a local `ceph-client` mirror, but this file is AMDGPU display-driver hardware metadata rather than Ceph filesystem logic.

The covered range starts in the tail of the `azf0endpoint7_endpointind` address block, beginning at `ixAZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR5`, and completes output endpoint 7 through `ixAZF0ENDPOINT7_AZALIA_F0_AUDIO_FORMAT_CHANGED_INT_STATUS`. It then defines complete input endpoint indirect-register blocks for `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind` and closes the header guard with `#endif`.

All values in this range are `ix...` indirect register indices with `base address: 0x0`. They are not direct MMIO offsets. Runtime code writes these small index values, such as `0x0038`, `0x0054`, or `0x0068`, into an Azalia endpoint index register and transfers payloads through the matching endpoint data register.

## Important Definitions

The output endpoint 7 tail exposes endpoint-local HDMI/DisplayPort audio pin and status indices:

- `ixAZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR5` through `...AUDIO_DESCRIPTOR13` at `0x002d` through `0x0035`, continuing the EDID/ELD-derived audio descriptor slots started before this chunk.
- `...MULTICHANNEL_ENABLE`, `...RESPONSE_LIPSYNC`, and `...RESPONSE_HBR` at `0x0036` through `0x0038`, used for channel routing, latency reporting, and high bit rate audio capability or enable state.
- `...SINK_INFO0` through `...SINK_INFO8` at `0x003a` through `0x0042`, used by the display audio path to publish sink manufacturer/product/port/name information.
- `...HOT_PLUG_CONTROL`, `...UNSOLICITED_RESPONSE_FORCE`, `...RESPONSE_CONFIGURATION_DEFAULT`, `...MULTICHANNEL_ENABLE2`, and `...MULTICHANNEL_MODE` at `0x0054` through `0x0058`.
- `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` at `0x0059` through `0x0061`, covering IEC 60958 channel-status override payload registers.
- `...CODEC_PIN_ASSOCIATION_INFO`, `...DIGITAL_OUTPUT_STATUS`, LPIB snapshot/readback/timer indices, `...CODING_TYPE`, `...FORMAT_CHANGED`, `...WIRELESS_DISPLAY_IDENTIFICATION`, `...REMOTE_KEEPALIVE`, and audio enable/disabled/format-changed interrupt status indices at `0x0062` through `0x006e`.

Each input endpoint block `0..7` repeats the same 22-index layout:

- Input converter indices at `0x0001` through `0x0006`: audio widget capabilities, converter format, channel/stream ID, digital converter control, stream formats, and supported size/rates.
- Input pin indices at `0x0020` through `0x0024`: input pin widget capabilities, pin capabilities, unsolicited response control, input pin sense response, and widget control.
- Multichannel, HBR, channel allocation, hot-plug/audio state, forced unsolicited response, configuration default, LPIB snapshot/readback/timer, input status control, and infoframe indices at `0x0036` through `0x0068`.

The repeated `ixAZF0INPUTENDPOINTn_AZALIA_F0_CODEC_INPUT_*` names are the exported compile-time API for endpoint-local input audio registers. The input endpoint layout is smaller than the output endpoint layout because it omits output-only sink-info, audio descriptor, channel-status override, digital-output status, coding type, wireless display, keepalive, and audio format-change interrupt groups.

## Control Flow

There is no local control flow in this header. The effective runtime flow is created by AMD display/audio register helpers:

1. `display/dc/resource/dcn301/dcn301_resource.c` includes `dcn/dcn_3_0_1_offset.h` and constructs `audio_regs[]` with `AUD_COMMON_REG_LIST(id)` for audio instances 0 through 6.
2. `AUD_COMMON_REG_LIST(id)` in `display/dc/dce/dce_audio.h` maps `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA` through the per-instance `AZF0ENDPOINT{id}` direct MMIO register pair.
3. `dcn301_create_audio()` passes the selected `audio_regs[inst]` plus shift/mask tables to `dce_audio_create()`.
4. `display/dc/dce/dce_audio.c` uses `AZ_REG_READ()` and `AZ_REG_WRITE()` macros that expand an indirect name to `ix<name>`, write the index through `AZALIA_F0_CODEC_ENDPOINT_INDEX.AZALIA_ENDPOINT_REG_INDEX`, and read or write `AZALIA_F0_CODEC_ENDPOINT_DATA.AZALIA_ENDPOINT_REG_DATA`.
5. Higher-level audio setup programs endpoint registers for HBR, lipsync, hotplug/audio enable, speaker and channel allocation, audio descriptors, and sink-info fields. The endpoint 7 constants in this chunk are the instance-specific generated names for the same indirect index space.

The input endpoint constants in this chunk are available to code that needs input/capture endpoint metadata, input activity state, channel layout, or infoframe-derived channel information. The common DC display audio path seen in this tree primarily exercises output endpoint programming, so input endpoint runtime coverage may depend on hardware and feature paths outside the usual HDMI/DP playback setup.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. They do not store state and cannot perform hardware I/O on their own.

The hardware registers selected by these indices are stateful. Output endpoint 7 can retain audio descriptor slots, multichannel routing, HBR and lipsync state, sink metadata, hotplug/audio enable state, forced unsolicited-response state, configuration defaults, channel-status overrides, LPIB snapshots, coding and format-change status, wireless display identification, keepalive control, and audio interrupt status. Input endpoints can retain converter format, stream/channel identifiers, digital converter flags, pin capabilities, input sense, multichannel routing, channel allocation, HBR state, hotplug/audio state, configuration defaults, LPIB snapshots, input activity, channel layout, and infoframe validity.

Persistence is governed by the GPU display/audio block, HDA/Azalia controller behavior, display hotplug, stream start/stop, suspend/resume, power gating, and GPU/display resets. Some indices select configuration state, some select readback/status state, and some select action or interrupt-related registers. This offset header does not encode access type, reset value, write-one-to-clear behavior, reserved-bit policy, or required sequencing.

## Dependencies And Integration Points

This chunk depends on the DCN 3.0.1 ASIC register database that generated `dcn_3_0_1_offset.h`. It must remain aligned with:

- `dcn_3_0_1_sh_mask.h`, which supplies bit shifts and masks for the endpoint payload registers selected by these indices.
- `display/dc/resource/dcn301/dcn301_resource.c`, which includes this offset header and builds the DCN 3.0.1 audio resource tables.
- `display/dc/dce/dce_audio.h`, especially `AUD_COMMON_REG_LIST`, `AUD_COMMON_MASK_SH_LIST_BASE`, and the `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` contracts.
- `display/dc/dce/dce_audio.c`, where `write_indirect_azalia_reg()`, `read_indirect_azalia_reg()`, `AZ_REG_READ()`, and `AZ_REG_WRITE()` implement the index/data access pattern.
- AMD register helper macros such as `SR`, `SRI`, `SF`, `REG_SET`, `REG_READ`, `set_reg_field_value`, and `get_reg_field_value`.

The file is also included by `display/dmub/src/dmub_dcn301.c` for DCN 3.0.1 DMUB register definitions, though this specific Azalia endpoint tail is most directly relevant to display audio rather than DMUB command processing.

## Risks And Edge Cases

The main risk is treating these constants as direct MMIO offsets. The `ix...` values are endpoint-local indices, and using them outside the Azalia index/data path would target the wrong address space.

Wrong index values are hardware ABI bugs. They can compile cleanly while redirecting a descriptor, sink-info, HBR, hotplug, LPIB, status, or infoframe operation to the wrong endpoint-local register. Symptoms may be missing HDMI/DP audio, wrong channel count or channel allocation, absent HBR formats, stale monitor audio names, bad lipsync values, stuck audio enable state, or incorrect input activity reporting.

The chunk boundary is artificial. Output endpoint 7 begins before line 13005, so this range only covers descriptor 5 onward and the later pin/status registers. Final per-file reconciliation should merge this with the previous chunk before describing endpoint 7 as a complete block.

The input endpoint blocks are highly repetitive. Copy or generator drift affecting only `AZF0INPUTENDPOINT3` or another single instance would be easy to miss in review and may only fail on hardware paths that expose that input endpoint. Structural checks should compare all eight input endpoint blocks for identical names and index values aside from the instance number.

Status, interrupt, snapshot, and force registers may have side effects that are not visible in this offset file. In particular, unsolicited response force, audio enabled/disabled/format-changed interrupt status, input status control, and LPIB snapshot controls must be used with the access semantics from the hardware specification and companion mask header.

## Test Signals

High-signal build checks include compiling DCN 3.0.1 display code that includes `dcn_3_0_1_offset.h`, especially `dcn301_resource.c`, `dmub_dcn301.c`, `dce_audio.h`, and `dce_audio.c`. Missing or renamed macros should surface through token-concatenated `SRI`, `SF`, and `IX_REG` usage.

Generated-header validation should verify that each `ixAZF0ENDPOINT7_...` and `ixAZF0INPUTENDPOINT0..7_...` index in this range has a matching field layout in the companion shift/mask header, and that all eight input endpoint blocks are structurally identical.

Runtime validation requires DCN 3.0.1-class hardware. Useful signals include HDMI/DP audio playback across exposed audio endpoints, hotplug/replug behavior, modeset and suspend/resume audio restoration, HBR and multichannel playback, EDID audio descriptor publication, sink manufacturer/name fields visible through the audio stack, and stable `HOT_PLUG_CONTROL` / audio enable state.

For the input endpoint constants, useful signals include input activity changes, channel-layout/status infoframe changes, `INFOFRAME_VALID` readback, HBR and channel-allocation behavior where supported, and LPIB snapshot/timer consistency during active input streams. Negative signals include endpoint-specific audio failures, wrong advertised audio capabilities, repeated unsolicited responses, stale LPIB snapshots, or failures isolated to one generated input endpoint instance.
