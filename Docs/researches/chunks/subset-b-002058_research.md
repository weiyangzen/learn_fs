# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 4429-6597

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains C preprocessor constants for hardware register bitfields, not executable driver logic. Each macro names a register field and supplies either the bit shift (`__SHIFT`) or the positioned mask (`_MASK`) used by AMD display register helpers when packing and unpacking memory-mapped display hardware registers.

The requested range contains 2,169 `#define` lines: 1,083 shift macros and 1,086 mask macros. There are no local comments in this slice. The imbalance comes from the line boundary starting after some preceding AZALIA input endpoint 1 field shifts and ending before the complete `OTG1_PIXEL_RATE_CNTL` field set.

The chunk covers two broad hardware surfaces:

- HDMI/DisplayPort audio codec endpoint register fields for `AZF0INPUTENDPOINT1` through `AZF0INPUTENDPOINT7`, plus audio descriptor and endpoint immediate-command fields.
- DCN display clock generator fields for pixel clock resync, DTOs, stream clocks, DCCG gating, perf monitors, time bases, DISPCLK ramping, and OTG pixel-rate controls.

## Important Constants And Register Areas

The first large section describes `AZF0INPUTENDPOINT1` through `AZF0INPUTENDPOINT7`. These are generated bitfield layouts for the function-0 AZALIA/HDA input endpoint codec widgets used by display audio. Each endpoint repeats nearly the same register groups:

- Converter widget capability fields, including channel capability, amplifier presence, format override, processing widget, unsolicited response capability, digital/power/LR-swap flags, delay, and widget type.
- Converter format and stream routing fields, including channel count, bits per sample, base-rate divisor/multiple, base rate, stream type, channel ID, and stream ID.
- Digital converter control bits such as `DIGEN`, validity/config/preemphasis/copyright/non-audio/professional flags, category code, and keepalive.
- Supported stream formats, size/rate capabilities, and pin audio widget capabilities.
- Pin capabilities for impedance sense, trigger requirement, jack detect, headphone/output/input support, balanced I/O, HDMI, VREF, EAPD, and DP.
- Pin control/status fields for unsolicited responses, pin sense, widget input enable, multichannel channel enable/mute/channel IDs, HBR support, channel allocation, hot-plug/audio-enabled state, forced unsolicited response payloads, default configuration response, LPIB snapshots, input activity/status, and infoframe channel metadata.

`AZF0INPUTENDPOINT1` starts at line 4429 after the first two shifts of its converter widget capability register were defined in the prior chunk. Endpoints 2 through 7 are complete in this range for the repeated input converter and input pin field groups.

`AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` define compact audio descriptor fields: `MAX_CHANNELS`, `SUPPORTED_RATES`, `DESCRIPTOR_BYTE_2`, and `SUPPORTED_FORMATS` with matching masks. These are the hardware layout used to expose or consume per-format sink audio capabilities.

`AZENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_DATA`, `AZENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_INDEX`, `AZINPUTENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_DATA`, and `AZINPUTENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_INDEX` define full-width immediate command data and 16-bit index fields for indirect endpoint command paths.

The DCCG section begins at `PHYPLLA_PIXCLK_RESYNC_CNTL` and continues through the beginning of `OTG1_PIXEL_RATE_CNTL`. Important register families include:

- `PHYPLL[A-E]_PIXCLK_RESYNC_CNTL` for PHY PLL pixel-clock resync enable and delay per PHY.
- `DP_DTO_DBUF_EN`, `DPSTREAMCLK_CNTL`, `DTBCLK_P_CNTL`, `DSCCLK[0-3]_DTO_PARAM`, `DCCG_DS_*`, and `DCCG_GTC_*` for display DTO enablement, stream-clock selection, DSC clock DTO phase/modulo, deep-sleep DTOs, and global time counter DTO/current fields.
- `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL4`, and `DCCG_GATE_DISABLE_CNTL5` for display, SOC, DPREF, DPP, DSC, PHY symbol, HDMI character, DTB, DP stream, HPO, and other clock-gate disable bits.
- `DCCG_PERFMON_CNTL` and `DCCG_PERFMON_CNTL2` for selecting and running display clock/perf monitor counters.
- `DISPCLK_FREQ_CHANGE_CNTL` for DISPCLK ramp step delay/size, ramp completion, FIFO error-detection control/state, and forward-correction disable.
- `MICROSECOND_TIME_BASE_DIV` and `MILLISECOND_TIME_BASE_DIV` for time-base dividers and clock source selectors.
- `OTG_PIXEL_RATE_DIV`, `OTG0_PIXEL_RATE_CNTL`, `DP_DTO0_PHASE`, `DP_DTO0_MODULO`, `OTG0_PHYPLL_PIXEL_RATE_CNTL`, and the start of `OTG1_PIXEL_RATE_CNTL` for output timing generator pixel-rate source, DTO enable/status, add/drop pixel correction, pipe DTO source selection, FIFO error reporting, and DP DTO phase/modulo.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The public surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives a field bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

These macros are consumed by generated register-list initializers and AMD display register helpers. For DCN 3.5, `drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c` includes this header and builds static `dccg_shift`, `dccg_mask`, `audio_shift`, and `audio_mask` tables from the generated macro names. `drivers/gpu/drm/amd/display/dc/dccg/dcn35/dcn35_dccg.h` defines `DCCG_MASK_SH_LIST_DCN35()`, which maps many fields in this chunk into `struct dccg_shift` and `struct dccg_mask` through `DCCG_SF` and `DCCG_SFII`.

The audio side is indirectly integrated through `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` and `dce_audio.c`. The runtime helpers write an AZALIA endpoint index and data register with `REG_SET()` and `REG_READ()`. This chunk does not provide the high-level audio programming routines, but its endpoint and descriptor field definitions are the low-level bit layout those routines depend on when an indirect endpoint command or descriptor value is constructed.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs in display driver code that reads or writes the hardware registers described by these bitfields.

The implied audio flow is HDA/AZALIA endpoint programming and readback. Driver code selects an endpoint register through endpoint index/data registers or immediate-command paths, then programs converter format, channel/stream routing, digital converter state, pin capabilities/status, channel allocation, HBR support, LPIB snapshot controls, and infoframe-related status. Hotplug or audio stream changes can cause the higher-level display stack to revisit these fields for audio enablement, supported mode reporting, unsolicited responses, or DP/HDMI audio metadata.

The implied DCCG flow is clock programming and status observation. DCCG code enables or disables DTOs, chooses stream-clock and DTB clock sources, sets phase/modulo values, controls root and leaf clock gating, observes enable status bits, handles DISPCLK ramp/error state, and selects pixel-rate sources for OTGs. The line range contains the register fields that let DCN 3.5 DCCG functions such as clock-gating control, DSC clock control, DP stream clock setup, and pixel DTO setup address the correct bits.

Several fields are sequencing-sensitive. DTO enable bits should be coordinated with phase/modulo programming and status readback. Clock-gate disable bits should be coordinated with active display pipes and PHY/stream ownership. Pixel-rate source and add/drop pixel controls affect live timing generator behavior and therefore must be changed only through established modeset or clock-update paths.

## State And Persistence

The file itself stores no mutable state. It defines how software addresses state stored in DCN 3.5 display hardware registers.

Persistent hardware state represented here includes audio converter format and routing, pin/widget capability and control fields, hotplug/audio-enabled state, audio infoframe/channel allocation state, LPIB snapshot/readback values, audio descriptors, clock source selections, DTO phase/modulo values, clock-gate disables, time-base divisors, perf-monitor configuration, DISPCLK ramp/error controls, and OTG pixel-rate settings. These values may survive across frames and remain active until reset, modeset, suspend/resume restore, hotplug handling, or explicit clock/audio reprogramming changes them.

Readback/status fields in the range include pin presence/input activity, LPIB snapshots, DTO enable status, DCCG perf/run state, FIFO error state/counts, GTC current value, CAC status, and DISPCLK ramp completion/error-detection state. The macros do not encode read-only versus writable semantics; callers must know that from the hardware programming model and use the established helper layer.

## Dependencies And Integration Points

This generated shift/mask header depends on the matching DCN 3.5.0 register-address header, especially `dcn_3_5_0_d.h`, and on the AMD display register helper framework that combines register offsets, shifts, and masks. Numeric values in this chunk are ASIC-generation-specific and should not be mixed with another DCN generation unless a generated register database confirms the layout is identical.

Important integration points include:

- `dcn35_resource.c`, which includes `dcn_3_5_0_sh_mask.h` and instantiates DCCG and audio shift/mask tables.
- `dcn35_dccg.h` and the DCN35 DCCG implementation, where fields such as `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL5`, `DPSTREAMCLK_CNTL`, `DTBCLK_P_CNTL`, `DSCCLK*_DTO_PARAM`, `OTG*_PIXEL_RATE_CNTL`, `OTG_PIXEL_RATE_DIV`, and `DISPCLK_FREQ_CHANGE_CNTL` are surfaced to `REG_SET`, `REG_UPDATE`, and `REG_READ` helper calls.
- `dce_audio.h` and `dce_audio.c`, where AZALIA endpoint index/data helpers and audio DTO fields bridge display audio policy to hardware registers.
- DC resource construction for DCN 3.5 and DCN 3.6, which reuses `DCCG_REG_LIST_DCN35()` and `DCCG_MASK_SH_LIST_DCN35()` patterns for matching hardware blocks.
- Display modeset, link encoder, DSC, DP/HDMI stream, HPO, power-management, and hotplug paths that depend on correct DCCG and audio register programming.

The register field names are part of the integration contract. A typo, removed field, or layout drift usually breaks compilation only when a consumer references that exact token; a wrong numeric mask or shift may compile cleanly and fail only on hardware.

## Risks And Edge Cases

Generated-header drift is the primary risk. Incorrect shifts or masks can write the wrong audio or clock bits without type-system help. Audio symptoms could include missing channels, wrong sample format reporting, HBR failure, broken hotplug notification, or invalid infoframes. Clock symptoms could include blank displays, unstable links, incorrect pixel rate, FIFO errors, DSC stream failures, or bad suspend/resume restore.

The line boundaries are incomplete. The start omits the first two `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` shifts, and the end cuts off `OTG1_PIXEL_RATE_CNTL` after `OTG1_DIO_ERROR_COUNT__SHIFT`. Whole-file reconciliation must merge adjacent chunks before making complete claims for those two register groups.

Repeated endpoint and clock-instance layouts are easy to mishandle. Endpoints 2 through 7 and many clock fields follow regular patterns, but instance-specific naming still matters. A single instance mismatch can affect only one audio endpoint, PHY, stream, DSC engine, or OTG, so validation must exercise more than the first pipe.

Clock gating fields are side-effect-prone. A value named `*_GATE_DISABLE` often uses inverted semantics where `1` disables gating rather than disables the clock itself. Higher-level code should continue using the DCCG helper functions and initialized mask tables rather than open-coding register writes.

Full-width masks and `L` suffixes require normal register-width discipline. Fields such as DTO phase/modulo and LPIB snapshots use `0xFFFFFFFFL`; consumers should use unsigned 32-bit register values and the central field helpers to avoid sign-extension or shift mistakes.

## Test And Validation Signals

Build validation should include DCN 3.5 display objects that include `dcn_3_5_0_sh_mask.h`, especially `dcn35_resource.c`, `dmub_dcn35.c`, and DCCG/audio consumers. Missing or renamed macros generally surface at compile time through the generated shift/mask table initializers.

Useful generated-data checks include:

- Compare this range against the authoritative DCN 3.5 register database.
- Verify each complete register group has matching shift and mask definitions and that masks do not overlap unexpectedly.
- Diff repeated AZF0 input endpoint instances 2 through 7 for structural consistency while accounting for the incomplete endpoint 1 boundary.
- Diff DCCG fields against the `DCCG_MASK_SH_LIST_DCN35()` consumer list so every referenced field has the expected shift and mask in the DCN 3.5 header.
- Include the next chunk when validating `OTG1_PIXEL_RATE_CNTL`, because this range stops before its mask lines.

Runtime validation signals include successful HDMI/DP audio enumeration and playback across multiple connectors, correct channel allocation and HBR behavior, stable hotplug/unplug audio transitions, successful modesets at varied pixel rates, no DCCG/OTG FIFO error accumulation, stable DSC/HPO/DP stream clocks, correct suspend/resume restore of audio and display clocks, and clean multi-monitor operation where more than one endpoint, PHY, stream clock, and OTG instance is active.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002058_research.md`. Whole-file research for `dcn_3_5_0_sh_mask.h` must merge neighboring chunks to complete the opening AZALIA endpoint 1 capability register and the trailing `OTG1_PIXEL_RATE_CNTL` register group.
