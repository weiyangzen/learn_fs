# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 66922-68033

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C code, functions, structs, or variables. Its purpose is to publish compile-time bit shifts and bit masks for Azalia/HD-audio codec input endpoint registers used by the AMDGPU display stack.

The path is inside a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem logic.

The range covers the end of `AZF0INPUTENDPOINT3` and the full repeated mask/shift definitions for `AZF0INPUTENDPOINT4`, `AZF0INPUTENDPOINT5`, `AZF0INPUTENDPOINT6`, and `AZF0INPUTENDPOINT7`. These are the Azalia function 0 codec input endpoint indirect-register views used for display audio. Each endpoint is exposed through endpoint index/data MMIO registers in the companion offset header; the macros in this chunk describe how to pack and unpack the data values read or written through those indirect registers.

The repeated endpoint families describe:

- Input converter capabilities and stream format controls.
- Converter channel/stream IDs and digital converter status/control bits.
- Supported stream formats, sample rates, and bit depths.
- Input pin widget capabilities and pin capabilities for HDMI/DP-style audio pins.
- Unsolicited response control and forced unsolicited response payloads.
- Input pin sense and widget input-enable state.
- Multichannel enable, mute, and channel ID fields for channels 0 through 7.
- HBR capability/enable state, channel allocation, hot-plug audio enable/clock-gating state, pin configuration defaults, link-position-in-buffer snapshots, input status, and audio infoframe status.

The source chunk starts in the middle of the `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2` masks. The preceding shifts for endpoint 3 multichannel-enable2 live immediately before this range, so final per-file reconciliation must merge adjacent chunks for complete endpoint 3 coverage. Endpoint 4 through endpoint 7 are complete in this chunk.

## Important APIs, Types, And Macros

There are no local APIs or types in this range. The public interface is the generated preprocessor naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for a field in the 32-bit indirect register payload.
- The companion offset header provides `ixAZF0INPUTENDPOINT*_...` indirect indices and `mmAZF0INPUTENDPOINT*_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX/DATA` MMIO register offsets.
- Display audio code uses these through register helper macros such as `SF`, `REG_SET`, `REG_READ`, `REG_UPDATE`, `set_reg_field_value`, and `get_reg_field_value`.

Important macro families in this chunk:

- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: describes converter widget properties. Fields include audio channel capability, input/output amplifier presence, amplifier-parameter override, format override, striping, processing widget, unsolicited response capability, connection list, digital flag, power control, LR swap, widget delay, and widget type.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: describes stream format programming with number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: maps 4-bit channel ID and 4-bit stream ID fields.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: contains digital-converter status/control fields such as `DIGEN`, validity, validity configuration, pre-emphasis, copy, non-audio, professional mode, level, category code, and keepalive.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`: exposes the full 32-bit stream-format support bitmap.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`: splits supported audio rates and bit capabilities into low and high fields.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: describes pin widget capabilities, similar to converter widget capabilities but without the converter-only format-override field in this chunk.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES`: describes pin sense/output/input/HDMI/DP capability bits, VREF control, EAPD capability, and balanced I/O capability.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`: packs a 6-bit tag and enable bit.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: exposes impedance sense and presence detect.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`: currently only the input-enable bit in this generated range.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `...ENABLE2`: pack enable, mute, and 4-bit channel ID fields for multichannel lanes 0-3 and 4-7 respectively. This chunk includes endpoint 3's tail masks for channels 4-7 and complete endpoint 4-7 definitions.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`: exposes HBR capable and HBR enable bits.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: exposes the 8-bit HDMI/CEA channel-allocation value.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: contains clock-gating disable, clock-on state, and audio-enabled bits.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`: provides a 26-bit unsolicited-response payload and a force bit.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: maps HD-audio pin default configuration fields: sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `...LPIB`, and `...LPIB_TIMER_SNAPSHOT`: define fields for locking an LPIB snapshot, cyclic-buffer wrap count, full LPIB value, and timer snapshot.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`: exposes input activity, channel layout, and unsolicited-response enable bits for input activity and channel-layout/channel-status-infoframe changes.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`: exposes channel count, channel allocation, infoframe byte 5, and infoframe-valid status.

## Control Flow

This header chunk has no runtime control flow. It is declarative field metadata. Runtime sequencing is implemented by consumers in the display audio path.

The important runtime pattern is indirect Azalia register access:

1. The display audio resource table selects an audio endpoint instance, using `AUD_COMMON_REG_LIST(id)` in `display/dc/dce/dce_audio.h` and the DCN20 `audio_regs[]` table in `display/dc/resource/dcn20/dcn20_resource.c`.
2. `dce_audio.c` writes an indirect register index to `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
3. It reads or writes the register payload through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
4. Field helpers use masks and shifts from generated `*_sh_mask.h` headers to set or extract fields in that payload.

Representative consumers found in this tree:

- `display/dc/resource/dcn20/dcn20_resource.c` includes `dcn_2_0_0_sh_mask.h`, builds `audio_regs[]` for audio instances 0 through 6, and initializes `audio_shift`/`audio_mask` from generated field macros. The DCN20 table only names endpoint index/data and common function fields directly; per-pin/per-converter indirect register fields are reached through the generic Azalia helper macros.
- `display/dc/dce/dce_audio.h` defines `AUD_COMMON_REG_LIST`, `AUD_COMMON_MASK_SH_LIST`, `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` used by DCE/DCN audio blocks.
- `display/dc/dce/dce_audio.c` defines `AZ_REG_READ` and `AZ_REG_WRITE`, which call `read_indirect_azalia_reg()` and `write_indirect_azalia_reg()`. These helpers program `AZALIA_ENDPOINT_REG_INDEX` and move payloads through `AZALIA_ENDPOINT_REG_DATA`.
- `dce_aud_az_enable()` and `dce_aud_az_disable()` read `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, change `CLOCK_GATING_DISABLE` and `AUDIO_ENABLED`, and write the value back. Those generic field names correspond to per-endpoint hot-plug-control fields represented in this chunk for input endpoints 3-7.
- `set_high_bit_rate_capable()` reads `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR`, updates `HBR_CAPABLE`, and writes it back. This chunk defines the same HBR bit layout for input endpoint 3 tail state and endpoints 4-7.
- `dce_aud_az_configure()` and related audio configuration code use EDID-derived audio information, DP/HDMI signal type, channel count, sample rates, and latency data to configure Azalia codec state and expose capabilities to the audio driver.

Because the header only supplies masks and shifts, it does not impose operation ordering. Callers must know when endpoint state is valid, when the audio endpoint is assigned to a pipe/connector, when hotplug/audio enable should be toggled, and how hardware treats read-only, write-one-to-clear, self-clearing, sticky, and latched fields.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. It describes hardware register fields.

The represented hardware state includes:

- Converter capability state: widget type, digital capability, stream-format capability, rate/bit-depth capability, power-control capability, LR swap capability, and processing/connection/unsolicited-response support.
- Converter runtime state: number of channels, bits per sample, sample-rate encoding, stream type, channel ID, stream ID, digital converter enable, status bits, category code, and keepalive.
- Pin capability state: HDMI/DP capability bits, input/output capability bits, jack/presence/impedance capability, EAPD capability, VREF capability, and default pin configuration fields.
- Pin runtime state: unsolicited-response enable/tag, forced unsolicited response payload, pin sense presence, input-enable bit, multichannel enable/mute/channel mapping, HBR exposed capability and enable state, channel allocation, and hot-plug audio enable/clock gating state.
- Audio stream status state: LPIB snapshot controls and values, input activity, channel-layout state, infoframe change unsolicited-response enable, infoframe channel count/allocation/byte 5, and infoframe valid bit.

Persistence is hardware-defined. Some fields are capability/status fields that software reads to expose behavior to the OS audio stack. Other fields are programming knobs that remain active until modeset reconfiguration, endpoint reassignment, audio disable, display power gating, GPU reset, suspend/resume, or driver teardown. Snapshot and status fields may be transient or latched. Unsolicited response, hot-plug, clock-gating, and forced-response fields can have side effects when written.

Software-visible persistence around these registers appears in higher layers:

- `amdgpu_dm_audio_init()` initializes `adev->mode_info.audio` pin state from `dc->res_pool->audio_count`.
- `amdgpu_dm_commit_audio()` updates connector-to-audio-instance mappings under `audio_lock` and notifies the DRM audio component of ELD changes.
- DC hardware sequencing disables and releases dynamic audio endpoints when a stream is torn down, including `pipe_ctx->stream_res.audio->funcs->az_disable()` and `update_audio_usage()` in DCN hardware sequencing paths.

The masks in this header are therefore part of a hardware ABI boundary. They must match the endpoint data payload format or those higher-level audio state transitions will manipulate the wrong bits.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 register-header ecosystem:

- `dcn_2_0_0_offset.h` supplies the matching `ixAZF0INPUTENDPOINT*_...` indirect register indices and endpoint index/data MMIO offsets.
- `dcn_2_0_0_sh_mask.h` supplies the field masks and shifts in this chunk plus the earlier/later field families.
- AMD display register helper macros (`SR`, `SRI`, `SF`, `REG_SET`, `REG_READ`, `REG_UPDATE`, `set_reg_field_value`, and related helpers) consume the masks and shifts.
- Audio resource setup in `display/dc/resource/dcn20/dcn20_resource.c` ties DCN20 instances to the common DCE audio helper.
- Shared display audio logic in `display/dc/dce/dce_audio.c` performs endpoint indirect reads/writes and programs HDMI/DP display-audio state.
- DRM audio component integration in `display/amdgpu_dm/amdgpu_dm.c` exposes ELD/audio instance changes to the OS audio side.

Direct include points for `dcn_2_0_0_sh_mask.h` in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`

Functional integration points include display audio endpoint allocation, HDMI/DP audio enable/disable, HBR audio capability exposure, EDID/ELD audio capability propagation, channel allocation and multichannel mapping, audio status/infoframe reporting, hotplug-audio state, and LPIB snapshot/status observation.

## Risks And Edge Cases

- These masks and shifts are hardware ABI. A wrong mask or shift can compile cleanly while silently programming the wrong bit in an indirect register.
- The chunk boundary is non-semantic. It begins after endpoint 3 multichannel-enable2 shifts and includes only endpoint 3 tail masks plus later endpoint 3 pin-control families. Adjacent chunks are required for a complete endpoint 3 summary.
- Repetition across endpoints 4-7 creates off-by-one and copy/paste risk. Endpoint field layouts are expected to stay identical, but each macro name encodes a specific endpoint instance. A single generated drift can affect only one audio endpoint and only when that endpoint is selected.
- Indirect register access increases blast radius. Software writes an index first and a data payload second; a stale or wrong index combined with correct-looking masks can update a different Azalia register.
- Some names imply side effects, but the header does not encode access type. `UNSOLICITED_RESPONSE_FORCE`, `HOT_PLUG_CONTROL`, `LPIB_SNAPSHOT_CONTROL`, and status/control fields may be read-only, write-sensitive, sticky, self-clearing, or latched depending on hardware documentation.
- HBR, channel allocation, multichannel enable, and stream-format fields are interoperability-sensitive. Bad values can cause no audio, channel swapping, muted channels, incorrect surround layout, receiver incompatibility, or failures with high-bit-rate compressed audio formats.
- `AUDIO_ENABLED` and `CLOCK_GATING_DISABLE` sequencing matters. Toggling hot-plug/audio state while the endpoint is assigned or while the display/audio clock path is changing can cause transient audio loss or stale state exposed to the OS audio driver.
- LPIB and timer snapshot fields describe live stream position state. Misinterpreting snapshot lock or wrap-count bits can produce incorrect buffer-position reporting and audio synchronization bugs.
- Pin configuration default fields affect how the codec presents topology/configuration to the audio driver. Bad port connectivity, default device, association, or sequence fields can expose the wrong jack/port layout.
- Because DCN20 code creates only the resource tables and relies heavily on shared DCE audio helpers, build tests catch missing macro names but not necessarily wrong numeric bit definitions.

## Test Signals

Useful validation combines generated-header checks, build coverage, and display-audio behavior on DCN20 hardware:

- Build AMDGPU/DC with DCN20 enabled. Missing or renamed fields should break `dcn20_resource.c`, shared DCE audio helpers, or related generated field initialization paths.
- Diff this chunk against adjacent generated families such as `dcn_2_1_0_sh_mask.h`, `dcn_3_0_0_sh_mask.h`, and `dcn_3_2_0_sh_mask.h` where endpoint register layouts are expected to remain compatible.
- Verify endpoint index/data access by reading/writing non-destructive Azalia endpoint fields through debug or instrumented driver paths and confirming the expected bit positions.
- Exercise HDMI and DisplayPort audio on hardware across endpoint instances, including hotplug, modeset, suspend/resume, and audio stream enable/disable cycles.
- Validate common audio formats: stereo PCM, multichannel PCM, high sample rates, different bits-per-sample settings, and HBR/compressed formats where supported by sink and link.
- Check channel mapping and channel allocation with multichannel test content; failures may show as swapped channels, silent channels, or incorrect receiver speaker layout.
- Confirm ELD/audio component notifications after connector hotplug and modeset. User-visible signals include `aplay -l`, desktop audio device presence, and correct ELD content for the active connector.
- Watch kernel logs for audio endpoint allocation/release issues, HPD flapping, EDID/ELD changes without audio device updates, audio disable paths leaving endpoints acquired, or GPU reset/suspend resume regressions.
- Monitor runtime symptoms: no HDMI/DP audio, HBR formats missing from the audio driver, clicks/pops during modeset, audio clock instability, stale connected state, incorrect LPIB position reporting, or receiver channel layout mismatch.
