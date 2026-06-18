# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 4947-7218

## Scope

This chunk is a generated AMD DCN 3.1.4 register shift/mask table for Azalia/HDA audio endpoint fields. The reviewed span contains 2,024 preprocessor definitions, almost entirely paired `__SHIFT` and `_MASK` constants, and no C functions, structs, enums, storage, or executable control flow. It starts in the `AZF0ENDPOINT7` output endpoint pin-control register set and then covers repeated `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` input endpoint field maps.

The header belongs to the AMDGPU display register contract. It is consumed with the paired `dcn_3_1_4_offset.h` register/index definitions and with register helper macros such as `FD_MASK`, `FD_SHIFT`, `SF`, `REG_SET`, and the Azalia indirect access path in display audio code.

## Purpose

The chunk gives bit positions and masks for DCN 3.1.4 Azalia codec endpoint registers. These constants let driver code pack, unpack, read, and update fields inside HDA/HDMI/DP audio endpoint registers without embedding literal bit arithmetic at every call site.

The output endpoint 7 section describes fields for advertised sink/audio capabilities and runtime audio state, including unsolicited response control, pin sense, widget output enable, channel and speaker allocation, audio descriptors, multichannel routing, lipsync, HBR capability, sink identity strings, hot-plug audio enable, configuration default, channel-status overrides, LPIB snapshots, format-change notifications, wireless display identification, remote keepalive, and audio enable/disable interrupt status fields.

The input endpoint sections describe repeated per-endpoint converter and input-pin fields. Each endpoint has fields for audio widget capabilities, converter format, channel/stream ID, digital converter status, supported formats/rates, input-pin capabilities, unsolicited response handling, pin sense, widget input enable, multichannel enable/mute/channel IDs, HBR response, channel allocation, hot-plug audio enable, configuration default, LPIB snapshot registers, input activity status, and infoframe metadata.

## Important Definitions

The key API surface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift count for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted in-register bit mask for that field.
- Register names beginning with `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_` apply to the output endpoint 7 pin-control/codec endpoint namespace.
- Register names beginning with `AZF0INPUTENDPOINT<n>_AZALIA_F0_CODEC_INPUT_` apply to input endpoint `n`, where this chunk covers `0` through `7`; endpoint 7 starts here but continues after this chunk.

Important output endpoint 7 groups:

- `*_UNSOLICITED_RESPONSE`: `TAG` and `ENABLE` fields for HDA unsolicited responses.
- `*_RESPONSE_PIN_SENSE`: output pin impedance sense.
- `*_WIDGET_CONTROL`: `OUT_ENABLE`.
- `*_CHANNEL_SPEAKER`: speaker allocation, channel allocation, HDMI/DP connection flags, extra connection info, LFE playback level, level shift, and downmix inhibit.
- `*_AUDIO_DESCRIPTOR0` through `*_AUDIO_DESCRIPTOR13`: maximum channels, supported frequencies, descriptor byte 2, and for descriptor 0 the stereo frequency byte.
- `*_MULTICHANNEL_ENABLE` and `*_MULTICHANNEL_ENABLE2`: enable/mute/channel-ID fields for even and odd multichannel lanes.
- `*_RESPONSE_LIPSYNC`, `*_RESPONSE_HBR`, `*_SINK_INFO0` through `*_SINK_INFO8`: video/audio latency, high-bit-rate audio capability/enablement, EDID-derived manufacturer/product IDs, port IDs, and display-name bytes.
- `*_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and `AUDIO_ENABLED`.
- `*_RESPONSE_CONFIGURATION_DEFAULT`: HDA pin default fields such as sequence, association, misc, color, connection type, default device, location, and port connectivity.
- `*_PIN_CONTROL_CODEC_CS_OVERRIDE_*`: channel-status override bytes and validity bits.
- `*_LPIB*`, `*_CODING_TYPE`, `*_FORMAT_CHANGED`, `*_REMOTE_KEEPALIVE`, and `*_AUDIO_*_INT_STATUS`: DMA position/status, stream format change, keepalive, and audio interrupt status fields.

Important repeated input endpoint groups:

- `*_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: converter widget feature flags such as amplifier presence, format override, digital, power control, unsolicited-response capability, delay, and type.
- `*_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: number of channels, bits per sample, base divisor/multiple/rate, and stream type.
- `*_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel ID and stream ID.
- `*_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital enable/status, validity, copyright/non-audio/professional flags, category code, and keepalive.
- `*_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `*_SUPPORTED_SIZE_RATES`: supported stream formats, sample rates, and sample sizes.
- `*_CODEC_INPUT_PIN_PARAMETER_*`: pin widget and pin capability maps for HDMI/DP-style digital input pins.
- `*_CODEC_INPUT_PIN_CONTROL_*`: runtime control/status registers for input pin unsolicited response, pin sense, widget input enable, multichannel layout, HBR, hot-plug, defaults, LPIB, input activity, and infoframe state.

## Control Flow

There is no local control flow in this chunk. All behavior is compile-time macro expansion.

At runtime, audio code writes endpoint-internal Azalia registers indirectly. In `dce_audio.c`, `AZ_REG_READ(reg_name)` and `AZ_REG_WRITE(reg_name, value)` expand an `ix...` endpoint register index, write it into `AZALIA_F0_CODEC_ENDPOINT_INDEX`, then read or write `AZALIA_F0_CODEC_ENDPOINT_DATA`. The register data values are assembled with helper macros that use the shift/mask definitions from ASIC-specific generated headers.

For DCN 3.1.4, `dcn314_resource.c` includes `dcn/dcn_3_1_4_offset.h` and this header, builds `audio_regs[]` through `AUD_COMMON_REG_LIST(id)`, and builds `audio_shift`/`audio_mask` through `SF(..., __SHIFT)` and `SF(..., _MASK)` expansion. `dce_audio_create()` receives those tables so common DCE audio code can operate on the DCN 3.1.4 register layout.

## State and Persistence

The header itself owns no state and persists nothing. Its values describe hardware register layout, so state is held in the DCN/Azalia hardware blocks:

- Endpoint index/data registers select and expose endpoint-internal HDA codec registers.
- Audio descriptor and sink-info registers cache EDID-derived audio capabilities and display identity for the hardware/OS audio path.
- Hot-plug and unsolicited-response bits control whether audio activity and notification state are visible to higher layers.
- LPIB and timer snapshot fields report live buffer position/timing state.
- Interrupt status fields represent hardware-latched audio enable/disable/format-change events.

Persistence across boot or suspend is not handled here. Correct restoration depends on DC resource construction and audio configuration paths reprogramming these registers when display/audio state changes.

## Dependencies

Primary dependencies:

- `dcn_3_1_4_offset.h` supplies the matching register addresses, base indices, and endpoint internal indexes.
- `reg_helper.h` and AMD display helper macros consume `__SHIFT`/`_MASK` pairs for register packing.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` performs generic Azalia endpoint reads/writes and uses HDA/HDMI/DP audio fields such as descriptors, sink info, HBR, lipsync, hot-plug audio enable, and channel allocation.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the audio register/shift/mask table shapes and common audio register list macros.
- `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` binds DCN 3.1.4 generated offsets and masks into the display resource pool's audio object construction.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c` and `drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c` include the same generated DCN 3.1.4 offset and mask headers for other register-table and IRQ setup paths.

This chunk is also coupled to adjacent generated ASIC generations such as DCE 12.0 and DCN 3.2.0, which carry similar Azalia macro families. That similarity is useful for consistency checks but also means copy/generation errors can propagate.

## Integration Points

The audio integration path is:

1. DCN 3.1.4 resource construction selects generated register addresses and masks for each audio instance.
2. Common DCE audio code selects endpoint-internal Azalia indexes with `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
3. Common DCE audio code reads/writes `AZALIA_F0_CODEC_ENDPOINT_DATA`.
4. The fields described in this chunk shape payloads for HDMI/DP audio capability advertisement, hot-plug audio enablement, multichannel layout, HBR support, sink identity, lipsync, and status reporting.

The chunk's output endpoint 7 fields are especially relevant to display connector audio programming and sink capability exposure. The input endpoint blocks are repeated hardware surfaces for capture/input-style audio endpoint handling and status, even when most display paths primarily exercise output endpoint codec controls.

## Risks

- Bitfield drift: any incorrect mask or shift silently corrupts hardware register programming. Failures can appear as missing HDMI/DP audio, wrong channel count, unsupported format advertisement, broken HBR audio, stale sink names, or lost unsolicited responses.
- Paired-header mismatch: these macros must match `dcn_3_1_4_offset.h` register indexes. A correct field mask with an incorrect index still writes the wrong endpoint-internal register.
- Repetition errors: the input endpoint 0-7 blocks are mechanically repeated. A single endpoint-specific typo can break only one pipe/endpoint and be missed in broad testing.
- Width/type assumptions: masks use `L` suffixed constants and include high-bit values such as `0x80000000L` and full-width `0xFFFFFFFFL`; call sites should keep using unsigned 32-bit register values to avoid sign-extension surprises.
- Chunk boundary: endpoint 7 input support is partial in this chunk; the input endpoint 7 pin-parameter/control definitions continue after line 7218. Whole-file reconciliation must merge neighboring chunks before making conclusions about endpoint 7 completeness.
- Generated-file maintainability: hand edits are risky. Updates should come from the ASIC register generation source so offset and mask headers remain synchronized.

## Test Signals

Useful validation signals for changes affecting this chunk:

- Kernel build coverage for DCN 3.1.4 paths, especially expansion of `dcn314_resource.c`, `dmub_dcn314.c`, and `irq_service_dcn314.c` against this header.
- Static comparison against adjacent known-good generated headers, especially DCE 12.0/DCN 3.2.0 Azalia endpoint field maps, to catch missing or shifted fields.
- Runtime HDMI/DP audio smoke tests on DCN 3.1.4 hardware: audio device enumeration, hot-plug/replug, enable/disable, suspend/resume, monitor-name propagation, and multi-display endpoint selection.
- EDID audio capability tests for PCM and compressed formats to confirm descriptor fields, supported frequencies, channel counts, and HBR capability are advertised correctly.
- Multichannel playback tests for 2-channel, 6-channel, and 8-channel layouts to validate channel/speaker allocation and multichannel enable/channel-ID fields.
- Interrupt/status tests for audio format-change and enable/disable events if the platform exposes those paths.

## Open Questions for Merge

- Confirm in neighboring chunks whether all output endpoints 0-7 have the same pin-control field coverage and whether endpoint 7 is intentionally the last output endpoint in this generation.
- Confirm after line 7218 that `AZF0INPUTENDPOINT7` has the same input pin-control tail as endpoints 0-6.
- Cross-check the generated DCN 3.1.4 Azalia endpoint field set against the hardware register database used to generate `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.
