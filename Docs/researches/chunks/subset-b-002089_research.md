# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 4416-6585

## Purpose

This chunk is generated AMD DCN 3.5.1 register-field metadata. It contains no executable driver logic; it exports preprocessor constants that describe bit positions and masks for MMIO register fields. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with the matching `dcn_3_5_1_offset.h` register offsets to populate AMD display register tables.

The requested range starts in the middle of the `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` mask group, then covers the rest of Azalia input endpoints 1 through 7, audio descriptor capability registers 0 through 13, immediate-command index/data windows for Azalia endpoint 0 and input endpoint 0, and a set of DCCG clock-generation fields through the beginning of `OTG1_PIXEL_RATE_CNTL`. Although the path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or direct I/O operations in this chunk. The interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit offset of a hardware field.
- `REGISTER__FIELD_MASK`: bit mask for the same hardware field.

Major macro families in this chunk:

- `AZF0INPUTENDPOINT1` through `AZF0INPUTENDPOINT7`: HDA/Azalia HDMI/DP input endpoint converter and pin-control fields. Each endpoint repeats fields for audio-widget capabilities, converter format, channel/stream ID, digital converter control, supported stream formats and rates, pin capabilities, unsolicited responses, pin sense, widget enable, multichannel enable/mute/channel ID for channels 0-7, HBR capability/enable, channel allocation, hot-plug/audio enable, forced unsolicited response payloads, configuration defaults, LPIB snapshots, input activity/channel layout status, and infoframe contents.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: audio SAD-style descriptor payload fields, with channel count, format code, sample-rate flags, byte 3 fields, and the descriptor update bit.
- `AZENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_*` and `AZINPUTENDPOINT0_AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_*`: immediate command output/input interface index and data fields, exposing the full 32-bit data/register-index windows.
- `PHYPLLA_PIXCLK_RESYNC_CNTL` through `PHYPLLE_PIXCLK_RESYNC_CNTL`: per-PHY pixel clock resynchronization enable, deep-color control, pixel-clock enable, and double-rate enable fields.
- `DP_DTO_DBUF_EN`, `DSCCLK*_DTO_PARAM`, `DPREFCLK_CGTT_BLK_CTRL_REG`, `REFCLK_CGTT_BLK_CTRL_REG`, `DISPCLK_CGTT_BLK_CTRL_REG`, `SOCCLK_CGTT_BLK_CTRL_REG`, and `SYMCLK_CGTT_BLK_CTRL_REG`: DTO enable/selection and clock-gating turn-on/turn-off delay fields.
- `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL4`, and `DCCG_GATE_DISABLE_CNTL5`: gate-disable fields for DISPCLK, SOCCLK, DPREFCLK, DPPCLK, DSCCLK, AOMCLK, DSI/BYTE/ESC clocks, SYMCLK front-end/full clocks, HDMI character clocks, DPIA symbol clocks, DTBCLK_P pipes, and DP stream clocks.
- `DPSTREAMCLK_CNTL`, `SYMCLK32_SE_CNTL`, `SYMCLK32_LE_CNTL`, `DTBCLK_P_CNTL`, `DCCG_DS_*`, `DPREFCLK_CNTL`, `DCCG_GTC_*`, `MILLISECOND_TIME_BASE_DIV`, `MICROSECOND_TIME_BASE_DIV`, and `DISPCLK_FREQ_CHANGE_CNTL`: display clock source selection, enable, fractional divider, global-timer, deep-sleep, and time-base fields.
- `DCCG_PERFMON_CNTL` and `DCCG_PERFMON_CNTL2`: display clock generator perfmon enable, mode, OTG selection, and pulse-divider fields.
- `OTG0_PIXEL_RATE_CNTL`, `DP_DTO0_PHASE`, `DP_DTO0_MODULO`, `OTG0_PHYPLL_PIXEL_RATE_CNTL`, and the start of `OTG1_PIXEL_RATE_CNTL`: timing-generator pixel-rate source, DTO enable/status, add/drop-pixel control, DTO source selection, DIO FIFO error reporting, and 32-bit DP DTO phase/modulo fields.

## Control Flow

This header has no runtime control flow. Runtime behavior appears only after the macros are token-pasted into register tables and used by display helper code:

1. DCN 3.5.1 modules include `dcn_3_5_1_sh_mask.h` with `dcn_3_5_1_offset.h`.
2. Resource and block-specific register-list macros instantiate shift/mask tables. For example, `dcn351_resource.c` builds `dce_hwseq_shift`/`dce_hwseq_mask` entries from `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL4`, and `DCCG_GATE_DISABLE_CNTL5` fields, while shared DCCG tables in `dcn32_dccg.h` consume `OTG*_PIXEL_RATE_CNTL`, `DPSTREAMCLK_CNTL`, `OTG_PIXEL_RATE_DIV`, `DTBCLK_P_CNTL`, and related DCCG fields.
3. Runtime display paths call helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_WRITE`, `REG_WAIT`, `REG_GET`, and `REG_SET`. These helpers use the generated shift/mask constants to read or modify individual hardware fields while preserving unrelated bits.
4. The DCCG path programs DTO phase/modulo values, enables `DTBCLK_DTO_ENABLE`, waits for `DTBCLKDTO_ENABLE_STATUS`, selects `PIPE_DTO_SRC_SEL`, and toggles `OTG_ADD_PIXEL`/`OTG_DROP_PIXEL`. This sequencing comes from `dcn32_dccg.c`; the header only provides field geometry.
5. Audio endpoint paths use Azalia endpoint index/data windows and audio register tables to discover capabilities, program converter format/channel mapping, publish audio descriptors, observe input activity, and manage hot-plug/audio enable state. The field macros do not encode HDA verb semantics by themselves.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed GPU display state.

Represented hardware state includes per-endpoint audio capabilities and controls, audio infoframe/descriptor data, LPIB snapshot and timer values, input activity status, HBR enablement, endpoint hot-plug/audio enable state, DCCG clock-gating overrides, pixel-clock resync configuration, DP/DTB DTO phase and modulo values, pixel-rate source selection, add/drop-pixel one-shot controls, DIO FIFO error counters, display time-base dividers, and DCCG perfmon controls.

Persistence is hardware-defined. Configuration fields usually retain values until display modeset reprogramming, block reset, power gating, suspend/resume, or ASIC reset. Status, counter, update, hot-plug, forced-response, and error fields can be read-only, sticky, write-one-to-clear, self-clearing, or edge-triggered depending on the register. Because the header is untyped, consuming code must know the correct access ordering and whether a field is safe while the audio, DIO, PHY, OTG, or DCCG block is clock gated.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h` for the corresponding MMIO offsets and base indices.
- AMD display register helper infrastructure that consumes generated shift/mask tables through `REG_*`, `SF`, `SRI`, `SRII`, `DCCG_SF`, `DCCG_SFII`, `HWS_SF`, and related token-pasting macros.

Representative integration points in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c` includes this header and fills DCN 3.5.1 register, shift, and mask structures. The visible consumers in this range include DCCG gate-disable fields, `AZALIA_AUDIO_DTO`, and clock/power-management metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c` include the same DCN 3.5.1 header pair, so generated-field correctness is part of the wider ASIC support contract even where this chunk's fields are not their main focus.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.h` maps `OTG*_PIXEL_RATE_CNTL`, `DPSTREAMCLK_CNTL`, `SYMCLK32_*`, `DTBCLK_P_CNTL`, and DTO fields into DCCG masks/shifts; `dcn32_dccg.c` then programs DTBCLK DTOs, DP stream clocks, and add/drop-pixel controls using those tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.h` and `dce_clock_source.c` integrate `DP_DTO0_PHASE`, `DP_DTO0_MODULO`, `OTG0_PIXEL_RATE_CNTL`, and `OTG0_PHYPLL_PIXEL_RATE_CNTL` style fields into DP DTO and pixel-clock source programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the shared Azalia audio register-table pattern for endpoint index/data access and codec capability fields. This chunk's input-endpoint and audio-descriptor definitions provide the lower-level field map for the hardware audio endpoint area.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc.h` has debug/trace storage for DTO enable/source/divider, add/drop-pixel, and DP DTO phase state, matching fields represented by this chunk.

## Risks And Edge Cases

- Shift/mask drift is the main risk. These are untyped constants, so an incorrect mask can compile cleanly while modifying the wrong hardware bits.
- The chunk starts and ends at artificial boundaries. It begins after the first endpoint-1 widget-capability shifts and ends before the rest of `OTG1_PIXEL_RATE_CNTL` and later OTG/DTO instances; adjacent chunks are needed for complete file-level conclusions.
- Azalia endpoint blocks are copy-sensitive. Endpoints 1-7 repeat near-identical converter and pin-control layouts; a single instance typo can affect only one display audio endpoint, making failures appear connector-specific.
- Audio-format fields directly affect HDMI/DP audio behavior. Bad converter format, channel/stream ID, digital converter, HBR, channel allocation, infoframe, or descriptor masks can cause missing audio, wrong channel mapping, HBR failures, malformed EDID/SAD reporting, or incorrect audio hot-plug behavior.
- LPIB and snapshot fields may be timing-sensitive. Incorrect lock, buffer-wrap, position, or timer-snapshot fields can produce incorrect audio position reporting without an obvious display failure.
- DCCG and pixel-rate fields are sequencing-sensitive. The shared code enables DTOs, waits for status, then selects the DTO source; wrong `DTBCLK_DTO_ENABLE`, `DTBCLKDTO_ENABLE_STATUS`, `PIPE_DTO_SRC_SEL`, `DP_DTO*_PHASE`, or `DP_DTO*_MODULO` masks can cause blank displays, unstable pixel valid generation, or incorrect DP/HDMI timing.
- Clock-gate override fields can hide power bugs or create access hazards. Wrong `DCCG_GATE_DISABLE_*` bits can leave clocks unnecessarily on, gate a block while it is in use, or break suspend/resume and low-power transitions.
- Error and perfmon fields are diagnostic-sensitive. Bad DIO FIFO error masks or DCCG perfmon controls can make validation misleading even when normal modesets appear to work.

## Test Signals

Useful validation signals are a mix of build-time generated-header checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.5.1 support enabled. Missing or renamed macros should fail in `dcn351_resource.c`, `dmub_dcn351.c`, `irq_service_dcn351.c`, DCCG, clock-source, or audio register-table construction.
- Mechanically verify that each field in lines 4416-6585 has the expected shift/mask pair where the generated pattern requires both, and that masks align with shift values and field widths.
- Diff this range against AMD's authoritative DCN 3.5.1 register database and nearby generated DCN headers where register layouts are expected to match, especially the repeated endpoint and OTG/DCCG instance blocks.
- Exercise HDMI and DP audio on every available output: hot-plug, EDID/audio descriptor discovery, 2-channel and multichannel LPCM, HBR-capable formats where supported, sample-rate and bit-depth changes, mute/unmute, suspend/resume, and connector replug.
- Validate endpoint-specific behavior by cycling streams across multiple physical links and checking for endpoint-only failures in converter format, channel allocation, input activity, infoframe valid state, and LPIB position reporting.
- Exercise DCCG and clock-source paths with DP, HDMI, HPO/DP stream encoder, pixel-rate changes, link-rate changes, modesets, fast modesets, add/drop-pixel controls, and dynamic refresh scenarios. Watch for blank displays, timing instability, FIFO error counters, or `REG_WAIT` timeouts on DTO enable status.
- Test clock-gating and power-management paths through runtime PM, display off/on, suspend/resume, and multi-monitor attach/detach. Clock-gate mask errors often show up as hangs, missed status transitions, or unexpected power draw rather than direct compile failures.
- Use debug traces or register dumps for `OTG*_PIXEL_RATE_CNTL`, `DP_DTO*_PHASE`, `DP_DTO*_MODULO`, `DCCG_GATE_DISABLE_*`, and Azalia endpoint registers to confirm programmed values match expected masks and shifts.

## Cross-Chunk Notes

Earlier chunks own the start of `dcn_3_5_1_sh_mask.h` and the beginning of the Azalia endpoint area, including endpoint 0 and the missing first part of endpoint 1 widget-capability definitions. Later chunks continue the OTG1 pixel-rate group and the rest of the DCCG/OTG/DTO field map. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.5.1 audio endpoints, all DCCG gate controls, or all OTG/DTO instances.
