# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 61605-62433

## Scope

This chunk is the final slice of the generated DCN 3.0.2 shift/mask header. It contains preprocessor constants only: 742 `#define` entries in this range, split into 370 field shifts and 372 field masks. There are no C functions, structs, enums, or executable statements.

The range starts in the middle of the `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` mask group, then covers the tail of input endpoint 4, all generated input endpoint 5 and 6 field definitions, all generated input endpoint 7 field definitions, and finally the header guard `#endif`.

Address blocks and register families covered here:

- Tail of `azf0inputendpoint4_inputendpointind`: hot-plug-control masks plus input pin controls for unsolicited response forcing, default configuration response, LPIB snapshot/readback, input status, and input audio infoframe.
- `azf0inputendpoint5_inputendpointind`, `azf0inputendpoint6_inputendpointind`, and `azf0inputendpoint7_inputendpointind`: full repeated input endpoint register sets.
- The closing file guard for `_dcn_3_0_2_SH_MASK_HEADER`.

## Purpose

This file is part of AMDGPU Display Core's generated hardware register ABI for DCN 3.0.2. The constants describe bit positions and masks inside Azalia F0 codec input endpoint registers. They allow driver register helpers and generated tables to refer to hardware fields symbolically rather than duplicating numeric bit layouts.

At a hardware level, the chunk describes HDMI/DisplayPort audio input endpoint widgets and pins for endpoint instances 5 through 7, plus the end of instance 4. The fields model HD Audio/Azalia converter capabilities, stream format controls, channel and stream IDs, digital converter controls, pin capabilities, unsolicited response handling, sink/presence sensing, multichannel enable/mute/channel routing, HBR audio capability, channel allocation, hot-plug audio enablement, LPIB snapshots, input activity, channel layout, and input infoframe status.

The generated names are instance-qualified, for example `AZF0INPUTENDPOINT5_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT__NUMBER_OF_CHANNELS_MASK`. This preserves the hardware instance relationship and prevents a caller or generated table from accidentally applying endpoint 5 field definitions to a different indexed endpoint block.

## Important APIs, Types, And Constants

There are no callable APIs or local types. The interface is entirely the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same hardware field.
- `// addressBlock: ...` comments: generated grouping markers for endpoint-indexed address blocks.
- `//<REGISTER>` comments: generated grouping markers for individual registers.

Important repeated macro families for endpoints 5, 6, and 7 are:

- `*_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: HD Audio converter widget capability fields such as channel capability, amplifier presence, format override, processing widget, unsolicited response capability, connection list, digital/power-control/LR-swap support, delay, and widget type.
- `*_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: converter format fields for number of channels, bits per sample, sample base divisor/multiple/rate, and stream type.
- `*_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel ID and stream ID selection fields.
- `*_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital converter control/status fields including `DIGEN`, validity/config/pro/pre/copy/non-audio bits, channel-status category code (`CC`), and `KEEPALIVE`.
- `*_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `*_SUPPORTED_SIZE_RATES`: full stream-format capability mask plus supported audio rates and sample sizes.
- `*_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `*_INPUT_PIN_PARAMETER_CAPABILITIES`: pin widget and pin capability fields including impedance sense, trigger requirement, jack detection, input/output capability, HDMI/DP indication, VREF control, and EAPD capability.
- `*_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE` and `*_UNSOLICITED_RESPONSE_FORCE`: unsolicited response tag/enable bits and forced response payload/force bit.
- `*_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: impedance sense and presence detect readback.
- `*_INPUT_PIN_CONTROL_WIDGET_CONTROL`: input-enable bit.
- `*_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `*_MULTICHANNEL_ENABLE2`: enable, mute, and channel-ID fields for multichannel slots 0-7.
- `*_INPUT_PIN_CONTROL_RESPONSE_HBR`: high-bit-rate audio capability and enable fields.
- `*_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: CEA/HDMI-style channel allocation byte.
- `*_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and audio-enabled fields.
- `*_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: HD Audio default configuration fields including sequence, association, misc, color, connection type, default device, location, and port connectivity.
- `*_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `*_LPIB`, and `*_LPIB_TIMER_SNAPSHOT`: LPIB snapshot locking, cyclic-buffer wrap count, LPIB value, and timer snapshot readback.
- `*_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` and `*_INFOFRAME`: input activity, channel layout, unsolicited-response enables, channel count/allocation, infoframe byte 5, and infoframe validity.

The endpoint 4 portion is partial. It includes two hot-plug-control masks at the start of the chunk, then the same tail pin-control families from unsolicited response force through infoframe.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time and hardware-indexed:

1. DCN 3.0.2 resource code includes `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h` header.
2. Register-list and field-list macros such as `SR`, `SRI`, `SF`, and block-specific table initializers concatenate register and field names to populate per-ASIC register offsets, shifts, and masks.
3. Runtime helpers use those tables with `REG_SET`, `REG_UPDATE`, `REG_READ`, `REG_WRITE`, `get_reg_field_value`, and `set_reg_field_value` style helpers to compose MMIO values or decode readbacks.
4. Azalia audio code accesses endpoint registers through an indirect index/data model: it writes an endpoint register index and then reads or writes endpoint data. This chunk describes part of the endpoint register data layout for indexed input endpoint blocks; the sequencing policy remains in audio and stream-encoder code.

The order in the header is generated and register-database oriented: each register comment is followed by all `__SHIFT` entries and then all `_MASK` entries. Endpoint blocks are repeated numerically.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes hardware state in DCN 3.0.2 Azalia input endpoint registers.

Programmed control state includes converter format, channel/stream IDs, digital converter enable and channel-status bits, input widget enablement, multichannel enable/mute/channel routing, HBR enablement, channel allocation, hot-plug clock-gating and audio-enable policy, unsolicited-response tags/enables, and forced unsolicited response payloads.

Capability and default-configuration state includes audio widget capabilities, supported formats/rates/sample sizes, pin capabilities, HDMI/DP indication, default device/connection/location/port-connectivity descriptors, and HBR capability.

Readback/status state includes presence detect and impedance sense, clock-on state, LPIB and LPIB timer snapshots, cyclic-buffer wrap count, input activity, channel layout, infoframe channel count/allocation, infoframe byte 5, and infoframe-valid status. These fields can change asynchronously with display/audio link state, hot-plug behavior, stream activity, and hardware buffer progression.

Persistence is hardware-defined. Values generally remain until rewritten, reset by the display/audio block, or cleared by a broader ASIC reset. The shift/mask header does not encode read-only, write-only, volatile, latch, or write-one-to-clear semantics, so users must follow the Azalia endpoint programming model supplied by the surrounding display audio code and hardware documentation.

## Dependencies And Integration Points

This generated header depends on its companion DCN 3.0.2 register offset header. Shift/mask macros only identify bit positions; callers also need matching register offsets or indexed register numbers to reach the correct hardware register.

Observed source-tree integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` and `dcn/dcn_3_0_2_sh_mask.h`, defines the `SF`/`SRI` macro style used to build register tables, and wires Azalia endpoint index/data fields for the DCE audio object.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` implements indirect Azalia endpoint access by programming `AZALIA_F0_CODEC_ENDPOINT_INDEX` and reading/writing `AZALIA_F0_CODEC_ENDPOINT_DATA`. It also reads default configuration port connectivity for endpoint validity, toggles hot-plug clock-gating disable while initializing audio rate and power-state fields, and exposes audio functions such as endpoint validation, hardware init, DTO setup, and HBR enable/disable.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the common audio register, shift, and mask table shapes that resource files populate.
- `drivers/gpu/drm/amd/display/dc/dce/dce_stream_encoder.c` programs audio packet, AFMT, HDMI ACR, and DP audio behavior that must agree with the Azalia endpoint capability and status model described by these generated fields.

The direct contract is the preprocessor name and numeric bit layout. Missing or renamed macros usually fail at compile time when a generated table references them. Incorrect masks or shifts are more dangerous because the driver can still build while reading or writing the wrong hardware bits.

## Risks And Edge Cases

- The chunk starts mid-register. `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` is incomplete here, with only trailing masks present in this slice. The final per-file merge must combine this with the previous chunk before making endpoint 4 completeness claims.
- Endpoint families are highly repetitive. A generator error in a single endpoint instance can be visually hard to spot while affecting only one audio engine or stream.
- Many fields are narrow bitfields packed into the same 32-bit register. Bad read/modify/write composition can alter adjacent channel, mute, validity, or enable bits.
- Full-width masks such as `STREAM_FORMATS`, `LPIB`, and `LPIB_TIMER_SNAPSHOT` require callers to preserve unsigned 32-bit behavior.
- High-bit fields such as `AUDIO_ENABLED`, `PRESENCE_DETECT`, and `INFOFRAME_VALID` use bit 31. Signed temporary types or incorrect mask constants can produce bad tests or writes.
- `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2` encode four channels per register, each with enable, mute, and channel-ID fields. Off-by-one endpoint or channel mapping errors could silently route or mute the wrong audio channel.
- HBR capability and enable fields are adjacent but semantically different. Treating a capability readback as a control bit, or enabling HBR without matching stream-format setup, can produce audio negotiation failures.
- Hot-plug clock-gating and audio-enable fields affect hardware accessibility and link-visible behavior. The runtime audio init path explicitly disables clock gating before programming some endpoint registers; incorrect masks here can make endpoint writes unreliable.
- `UNSOLICITED_RESPONSE_FORCE` contains a 26-bit payload plus a force bit. Incorrect payload masking can generate malformed unsolicited responses to the HD Audio controller.
- LPIB snapshot locking and cyclic-buffer wrap-count fields can be timing-sensitive. Polling or snapshot code must avoid assuming static values while audio DMA progresses.
- Similar endpoint macro names exist in sibling DCN headers. Reusing DCN 3.0.2 constants for another ASIC generation is unsafe unless the generated register database confirms identical layouts.

## Test Signals

Useful validation is mostly compile-time, register-generation, and hardware smoke testing:

- Build AMDGPU Display Core with DCN 3.0.2 enabled to catch missing macro names in `dcn302_resource.c`, DCE audio table initialization, and register helper expansions.
- Preprocess the DCN 3.0.2 resource file and verify that `SF`/`SRI` expansions resolve to the intended `dcn_3_0_2_offset.h` and `dcn_3_0_2_sh_mask.h` definitions.
- Compare this slice against the upstream/generated register database and the companion offset header for endpoints 4-7, especially because endpoint 4 is split across chunks.
- Exercise HDMI and DP audio enumeration on DCN 3.0.2 hardware, checking endpoint validity, default configuration port connectivity, supported sample rates, stream formats, and pin capabilities.
- Test audio playback across common formats: 2-channel PCM, multichannel LPCM, high sample rates, and HBR-capable formats where supported.
- Validate hot-plug and suspend/resume behavior while audio is active, watching for stale `AUDIO_ENABLED`, `CLOCK_ON_STATE`, presence-detect, or input-activity state.
- Check channel allocation and infoframe readback for stereo and multichannel modes, including `INFOFRAME_VALID`.
- Exercise LPIB snapshot/readback paths if available through diagnostics, ensuring snapshot lock and timer values progress consistently.
- Run display audio tests across all exposed DCN302 audio instances, because this chunk specifically contains the higher-numbered endpoint blocks.

## Open Cross-Chunk Questions

- The final per-file report should merge the previous chunk's endpoint 4 definitions with this chunk's endpoint 4 tail.
- Whole-file reconciliation should verify how many input endpoint instances DCN 3.0.2 exposes versus how many `audio_regs[]` entries are instantiated by `dcn302_resource.c`.
- If generation provenance is available, the final report should identify the register database/import source. These numeric masks are generated hardware ABI data and should not be hand-edited without regenerating and comparing the full header.
