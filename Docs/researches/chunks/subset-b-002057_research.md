# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 2228-4428

## Scope And Purpose

This chunk is a generated-style AMD DCN 3.5 register shift/mask header segment for Azalia/HD Audio codec endpoint registers. It contains only preprocessor constants: no C functions, structs, runtime branches, or storage definitions. The constants encode bit positions (`__SHIFT`) and bit masks (`_MASK`) used by AMD display/audio register helper macros to read, compose, and update fields in DCN 3.5 audio endpoint registers.

The line range covers 2,201 `#define` entries. It starts mid-register in output endpoint 3 at `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_2__IEC_60958_CS_SAMPLING_FREQUENCY_OVRRD_EN_MASK`, then covers the tail of endpoint 3, all output endpoints 4 through 7, all visible input endpoint 0 fields, and stops partway through input endpoint 1 audio-widget-capability shift definitions. The paired offset header `dcn_3_5_0_offset.h` provides the corresponding register addresses; this file provides the bit layout.

## Register Families Covered

The chunk is organized by endpoint prefix:

- `AZF0ENDPOINT3` lines 2228-2304: tail of output endpoint 3 channel-status overrides, pin control, LPIB snapshot, coding type, format-change, remote keepalive, and audio enable/disable/format-change interrupt status masks.
- `AZF0ENDPOINT4` lines 2305-2774: complete output endpoint 4 converter, pin, channel-status override, and audio status field definitions.
- `AZF0ENDPOINT5` lines 2775-3244: same complete output endpoint layout as endpoint 4.
- `AZF0ENDPOINT6` lines 3245-3714: same complete output endpoint layout as endpoint 4.
- `AZF0ENDPOINT7` lines 3715-4184: same complete output endpoint layout as endpoint 4.
- `AZF0INPUTENDPOINT0` lines 4185-4416: input converter and input pin-control field definitions.
- `AZF0INPUTENDPOINT1` lines 4417-4428: beginning of input converter audio-widget-capability shifts only; masks and later input endpoint 1 fields continue outside this chunk.

For endpoints 4-7, the repeated output endpoint shape includes converter capabilities (`AUDIO_WIDGET_CAPABILITIES`, supported stream formats, supported size/rates), converter controls (`CONVERTER_FORMAT`, `CHANNEL_STREAM_ID`, `DIGITAL_CONVERTER`, `RAMP_RATE`, `GTC_EMBEDDING`), GTC counter delta registers, pin parameters/capabilities, hot-plug/audio enable controls, multichannel assignment controls, HBR/lipsync responses, sink-info registers, IEC 60958 channel-status override registers, LPIB snapshot/status registers, and per-endpoint interrupt status registers.

Input endpoint 0 mirrors part of that model for capture/input use: input converter capabilities and format controls, digital-converter fields, input pin capabilities, unsolicited response controls, input pin sense, input widget enable, multichannel input mapping, HBR response, channel allocation, hot-plug/audio-enabled state, configuration default, LPIB snapshot, input activity/status, and input infoframe fields.

## Important APIs, Types, And Macros

There are no exported functions or C types in this chunk. The meaningful API is the naming contract consumed by AMD register helper macros:

- `REGISTER__FIELD__SHIFT` constants give the low bit of a hardware field.
- `REGISTER__FIELD_MASK` constants give the raw field mask in the register word.
- Register prefixes such as `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` identify endpoint-specific hardware registers or indirect Azalia codec nodes.
- Field suffixes such as `AUDIO_ENABLED`, `CLOCK_GATING_DISABLE`, `HBR_CAPABLE`, `SINK_DESCRIPTION_LEN`, `SUPPORTED_FREQUENCIES`, `NUMBER_OF_CHANNELS`, and `STREAM_ID` are used by helper macros to manipulate values without hard-coding bit positions in driver logic.

The constants are intended to line up with the display driver helper pattern visible in AMD display audio code. `dce_audio.c` selects an indirect Azalia endpoint register through `AZALIA_F0_CODEC_ENDPOINT_INDEX`, reads or writes data through `AZALIA_F0_CODEC_ENDPOINT_DATA`, and uses `set_reg_field_value` with a register name and field name. The helper expansion depends on the `__SHIFT` and `_MASK` symbols being present and correctly named.

## Control Flow

This header segment has no execution control flow. The effective control flow appears in consumers:

1. DCN 3.5 resource, IRQ, or DMUB code includes `dcn_3_5_0_offset.h` and this `dcn_3_5_0_sh_mask.h`.
2. Register tables and helper macros bind a logical register/field name to its offset, base index, shift, and mask.
3. Audio code chooses an endpoint register index, reads the current register value, mutates fields using the shift/mask pair, and writes the new value back.
4. Hardware observes the resulting endpoint register fields to expose or control HDMI/DP audio behavior.

Examples of runtime paths that depend on these symbols include enabling/disabling Azalia audio through `HOT_PLUG_CONTROL.AUDIO_ENABLED`, exposing HBR capability through `RESPONSE_HBR.HBR_CAPABLE`, programming speaker/channel allocation, writing sink-info display-name bytes, programming audio descriptor fields, and updating endpoint format-change or audio-enable interrupt state.

## State And Persistence Behavior

The header itself has no mutable state and no persistence. Its constants describe persistent hardware register state in the GPU display/audio block:

- Endpoint converter controls persist in hardware registers until reprogrammed or reset, including format, channel/stream IDs, digital converter control bits, GTC embedding, and ramp-rate state.
- Pin-control fields describe or control connector-facing state such as hot-plug audio enabled, HBR capability, speaker/channel allocation, sink identity, input activity, and unsolicited response payloads.
- LPIB and timer snapshot fields expose stream position or timing snapshots and wrap counts.
- Interrupt status fields carry event state for audio enabled, disabled, and format changed conditions.

Because these are hardware bit definitions, persistence is ultimately governed by the DCN hardware register file and the driver lifecycle. Suspend/resume, hot-plug, stream reconfiguration, and audio endpoint reinitialization are the scenarios that must preserve or rebuild correct state using these constants.

## Dependencies And Integration Points

The direct dependencies are compile-time:

- `dcn_3_5_0_offset.h` supplies the matching DCN 3.5 Azalia register offsets and base indexes.
- AMD display register helpers such as `REG_SET`, `REG_READ`, `REG_WRITE`, `set_reg_field_value`, and generated shift/mask structs expect the macro names in this header.
- `dcn35_resource.c`, `irq_service_dcn35.c`, and `dmub_dcn35.c` include this header directly for DCN 3.5 display, interrupt, and DMUB integration.
- Common DCE/DC audio code uses the Azalia endpoint names through indirect endpoint-index/data accesses and field helper macros.

The broader integration surface is the Linux DRM AMDGPU display stack. These constants connect C driver code to ASIC-specific DCN 3.5 register layouts for HDMI/DisplayPort audio, codec endpoint discovery, channel mapping, stream format advertisement, sink information, audio hot-plug behavior, and interrupt handling.

## Risks And Edge Cases

- Generated header drift is high impact. A wrong bit shift or mask can silently program the wrong hardware field while the C code still compiles.
- The range starts and ends mid-logical block. Endpoint 3 has earlier channel-status definitions outside this chunk, and input endpoint 1 is incomplete here. Whole-file consumers need adjacent chunks for complete endpoint analysis.
- Endpoints 4-7 are structurally repetitive. Copy-generation mistakes may affect only one endpoint while visual review assumes all repeated blocks are identical.
- Some field names include `MASK` as part of the hardware field name, for example `AUDIO_ENABLED_MASK_MASK`. This is intentional naming but easy to mishandle in scripts that strip suffixes naively.
- Many fields describe externally visible audio capabilities: supported sample rates, bit depths, channel counts, HBR support, sink info, and channel allocation. Bad definitions can cause user-visible audio mode loss, channel misrouting, incorrect EDID/audio exposure, or format-change storms.
- Several state bits are event or interrupt related (`AUDIO_ENABLED_FLAG`, `AUDIO_DISABLED_FLAG`, `AUDIO_FORMAT_CHANGED_FLAG`, unsolicited responses). Mis-masks here can cause missed or spurious audio events.
- Indirect Azalia register access requires correct endpoint selection. These endpoint-specific prefixes must stay aligned with offset/index definitions and any generated register tables.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/audio behavior checks:

- Kernel or module compilation with DCN 3.5 enabled catches missing, renamed, or syntactically malformed macros referenced by register tables and helpers.
- Static generation checks should verify that every visible field has a consistent `__SHIFT`/`_MASK` pair, except known chunk-boundary partials such as the first endpoint 3 mask and final input endpoint 1 shifts.
- Register-header consistency checks should compare this file against `dcn_3_5_0_offset.h` and the source register database used to generate both headers.
- Runtime display audio tests should cover HDMI and DisplayPort audio enable/disable, hot-plug, HBR exposure, multichannel speaker allocation, audio descriptor programming, sink-info propagation, and format changes on DCN 3.5 hardware.
- Interrupt tests should confirm audio-enabled, audio-disabled, and format-changed events are reported and masked as expected for endpoints 4-7.
- Capture/input endpoint validation, where supported by hardware, should exercise input activity, infoframe, pin-sense, multichannel input mapping, and LPIB snapshot fields for `AZF0INPUTENDPOINT0`.
