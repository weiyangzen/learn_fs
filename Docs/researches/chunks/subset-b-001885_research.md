# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 49526-52127

## Scope

This chunk is a large middle/tail slice of the generated DCN 3.1.5 register-field shift/mask header `dcn_3_1_5_sh_mask.h`. It contains C preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw register masks, register grouping comments, and `addressBlock` grouping comments. There are no functions, structs, enums, allocations, branches, loops, locks, or driver-owned state objects in this range.

The slice starts in the tail of `DP_SYM32_ENC2` sideband/audio/video stream definitions and then covers the third HPO DisplayPort stream encoder stack, the third HPO DP symbol encoder, two HPO DP link/DPHY symbol blocks, DCHVM host-VM fields, display HDA/Azalia controller and stream descriptor fields, several RSMU empty address blocks, DC perfmon debug fields, legacy VGA indexed registers, writeback/debug fields, and the beginning of DPG3 debug fields. The span contains 2,087 `#define` lines across 386 register groups.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.5 display hardware. Companion offset headers, especially `dcn_3_1_5_offset.h`, map register names to MMIO offsets and base indices; this file maps register fields to bit shifts and masks. Display code combines both pieces through generated register-list macros and helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `SE_SF`, `HUBBUB_SF`, `SF`, and `DMUB_SF`.

Major hardware areas represented here:

- `DP_SYM32_ENC2_*` tail fields for symbol encoder 2 metadata sideband packets, MSA/VBID timing, video stream enable/status, panel replay tunneling, video CRC, and encoder memory power.
- `dce_dc_hpo_dp_stream_enc3_dispdec` fields for HPO DP stream encoder 3 clock gating, pixel/audio input muxing, and clock-ramp-adjuster FIFO control/status.
- `dce_dc_hpo_dp_stream_enc3_apg_apg_dispdec`, `dme_dme_dispdec`, and `vpg_vpg_dispdec` fields for APG3 audio packet generation, DME9 metadata engine state, and VPG9 generic sideband packet storage/update.
- `dce_dc_hpo_dp_sym32_enc3_dispdec` fields for DP symbol encoder 3: enable/reset, pixel-to-symbol FIFO, MSA and pixel format double buffering, MSA payload words, generic sideband packet controls 0-14, audio/metadata sideband controls, video stream controls, CRC, and memory power.
- `dce_dc_hpo_dp_link_enc0/1_dispdec` and `dce_dc_hpo_dp_dphy_sym320/321_dispdec` fields for HPO DP link clocks, DPHY control/status, virtual-channel rate/slot allocation, training pattern generation, PRBS/custom patterns, error status, symbol override, and DPHY CRC.
- `dce_dc_dchvm_hvm_dispdec` fields for host-VM initialization, memory power request/status, clock gating request modes, RIOMMU prefetch/power state, and RIOMMU status.
- `dce_dc_hda_azcontroller_azdec`, endpoint, input endpoint, root, and stream blocks for display HDA/Azalia CORB/RIRB rings, immediate command/response paths, DMA position buffer address, and output stream descriptors 0-7.
- `dc_perfmon_dc_perfmondebugind`, `vga_*`, `mcif_wb0_mcif_wbdebugind`, and `dpg*_dpgdebugind` fields for debug/perfmon, legacy VGA sequencing/CRTC/graphics/attribute registers, writeback debug windows, and DPG debug registers.

The file is hardware-definition data rather than active logic. Its values are still runtime-critical because callers rely on these macros to preserve unrelated register bits while programming display link, audio, packet, power, VM, and debug state.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-native position.
- `//<REGISTER>` comments group adjacent field macros by register.
- `// addressBlock: ...` comments group following registers by hardware aperture.

Important field families in this chunk:

- `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL` exposes metadata packet enable, double-buffer enable, SOF reference, double-buffer pending, and transmission line number. The preceding `DP_SYM32_ENC2` GSP/audio fields are partly in the previous chunk, so this chunk begins mid encoder-2 sideband coverage.
- `DP_SYM32_ENC2_DP_SYM32_ENC_VID_MSA_CONTROL`, `VID_VBID_CONTROL`, `VID_STREAM_CONTROL`, and `VID_PANEL_REPLAY_CONTROL` cover MSA line scheduling, compressed-stream VBID line scheduling, video stream enable/deferred-disable/status, and panel replay tunneling optimization.
- `DP_SYM32_ENC2_DP_SYM32_ENC_VID_CRC_*` expose video CRC enable/continuous mode, four 16-bit result fields, and a valid bit. `DP_SYM32_ENC2_DP_SYM32_ENC_MEM_POWER_CONTROL` exposes default low-power state, force, disable, and current power state fields.
- `DP_STREAM_ENC3_DP_STREAM_ENC_CLOCK_CONTROL` exposes the stream encoder clock enable and readback/status bits for DISPCLK, SOCCLK, DPSTREAMCLK, and SYMCLK32. `INPUT_MUX_CONTROL` and `AUDIO_CONTROL` select pixel and audio stream sources.
- `DP_STREAM_ENC3_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL0/1` expose FIFO enable/reset/read start level/read clock source, reset done, active-stream, error, overwrite level, recalibration/recompute triggers, min/max/calibrated levels, and average calibration state.
- `APG3_APG_CONTROL` and `APG3_APG_CONTROL2` expose APG reset/done, APG enable, DP audio stream ID, and ASP channel-count override. `APG3_APG_DBG_GEN_CONTROL` configures debug audio generation and per-channel test enable/disable. `APG3_APG_PACKET_CONTROL` chooses packet/audio info sources.
- `APG3_APG_AUDIO_CRC_CONTROL`, `CONTROL2`, and `RESULT` expose audio CRC enable/continuous mode/channel selection/count, default forced count, done/done-clear, and 16-bit CRC result. `APG3_APG_STATUS` exposes audio enable, HBR enable, FIFO overflow status, and overflow clear. `APG3_APG_MEM_PWR` mirrors the common memory power disable/force/state/default low-power pattern.
- `DME9_DME_CONTROL` covers metadata hubp requestor ID, engine enable, stream type, double-buffer pending/taken/taken-clear, DB disable, transmission missed, and missed-clear. `DME9_DME_MEMORY_CONTROL` covers DME memory power force/disable/state/default low-power.
- `VPG9_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG9_VPG_GENERIC_PACKET_DATA` provide indexed byte access to generic sideband packet RAM. `VPG9_VPG_GSP_FRAME_UPDATE_CTRL` and `IMMEDIATE_UPDATE_CTRL` contain update bits and pending bits for generic packet slots 0-14. `VPG9_VPG_GENERIC_STATUS` exposes lock/conflict status and conflict clear. `VPG9_VPG_ISRC1_2_*` and `VPG9_VPG_MPEG_INFO*` expose indexed ISRC bytes and MPEG infoframe bytes/update bits.
- `DP_SYM32_ENC3_DP_SYM32_ENC_CONTROL`, `VID_FIFO_CONTROL`, `VID_MSA_DOUBLE_BUFFER_CONTROL`, `VID_PIXEL_FORMAT_DOUBLE_BUFFER_CONTROL`, and `VID_PIXEL_FORMAT` define symbol encoder 3 enable/reset, FIFO reset/done/overflow, MSA/pixel-format DB enable/pending, pixel encoding type, uncompressed encoding, and component depth.
- `DP_SYM32_ENC3_DP_SYM32_ENC_VID_MSA0..8` provide full 32-bit MSA payload data words. `DP_SYM32_ENC3_DP_SYM32_ENC_HBLANK_CONTROL` exposes minimum hblank symbol width.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL0..14` repeat the same generic sideband control layout per packet slot: video/idle continuous transmission, one-shot trigger and position, double-buffer enable, payload size, SOF reference, missed-deadline status, trigger pending, double-buffer pending, and 16-bit transmission line number.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_CONTROL` exposes SDP stream enable, GSP0 priority, and CRC16 enable. `SDP_AUDIO_CONTROL0/1` expose ASP/ATP/AIP/ACM/ISRC enables, ASP priority, ATP version, audio mute/status, ASP concatenation enable, and sample count limits for 2-channel, 8-channel, and HBR layouts.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL`, `VID_MSA_CONTROL`, `VID_VBID_CONTROL`, `VID_STREAM_CONTROL`, `VID_PANEL_REPLAY_CONTROL`, `VID_CRC_*`, and `MEM_POWER_CONTROL` mirror the encoder-2 tail fields for encoder 3.
- `DP_LINK_ENC0/1_DP_LINK_ENC_CLOCK_CONTROL` expose HPO link encoder clock enable and SYMCLK32 clock-on status. The associated `SPARE` registers are full-width fields.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_CONTROL` expose DPHY enable/reset, precoder enable, mode, and lane count. `STATUS` exposes active/reset status, current mode, encryption enabled, rate update pending, and SAT update pending.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_VC_RATE_CNTL0..3`, `SAT_VC0..3`, and `SAT_VC_STATUS0..3` define stream virtual channel rate X/Y values, stream source selection, encryption enable/type, and slot count for four virtual channels.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_TP_CONFIG`, `TP_PRBS_SEED0..3`, `TP_SQ_PULSE`, and `TP_CUSTOM0..10` define training-pattern selection, PRBS selection/seeds, square-pulse width, and custom symbol patterns.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_ERROR_STATUS`, `SYMBOL_OVERRIDE`, and `CRC_*` expose link-level error flags, per-stream symbol override controls, CRC enable/reset/source/start/end/length configuration, CRC done/value, and symbol count.
- `DCHVM_CTRL0`, `DCHVM_CTRL1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0` expose host-VM init, memory power requests/status, DISPCLK/DCFCLK clock gate disables, request/response clock request modes, host-VM prefetch request/power status, RIOMMU active, and prefetch done.
- HDA/Azalia controller fields include `CORB_*` write/read pointers, ring reset/control/status/size; `RIRB_*` lower/upper base address, write pointer/reset, response interrupt count, control/status/size; immediate command output/data/index, immediate response input, command busy/result-valid, and DMA position buffer base address/enable.
- `AZENDPOINT_*`, `AZINPUTENDPOINT_*`, and `AZROOT_*` immediate command data/index fields provide endpoint/root windows into codec command paths.
- `AZSTREAM0..7_OUTPUT_STREAM_DESCRIPTOR_*` repeat the HDA output stream descriptor layout: stream reset/run, interrupt enables, stripe control, traffic priority, stream number, FIFO/descriptor error status, FIFO ready, link position, cyclic buffer length, last valid index, FIFO size, audio format, BDL lower/upper base address, and link position alias.
- `PERFMON_DEBUG_ID` and `PERFMON_DEBUG01..12` expose debug index/data fields and control-like bits such as `PERFMON_TEST_DEBUG_INDEX`, `PERFMON_TEST_DEBUG_DATA`, `TEST_DEBUG_OUT_EN`, and timeout/counter fields in `PERFMON_DEBUG12`.
- `SEQ00..04`, `CRT00..22`, `GRA00..08`, and `ATTR00..14` define legacy VGA sequencer, CRTC, graphics, and attribute indexed-register bit fields. These include reset/clocking, map mask, character/font select, memory mode, CRTC timing/cursor/start-address/line-compare, graphics set/reset/read/write/mode, and attribute palette/mode/color-select fields.
- `VGADCC_DBG_DCCIF_C`, `IDDCCIF*_DBG_DCCIF_*`, `MCIF_WB_DEBUG_ID`, `ID*_WB_*`, `DPG0..3_DPG_DEBUG*`, and `FMT0/1_FMT_DEBUG*` are debug/index windows. Many expose only a single shift at bit 0 because the full register payload is consumed as debug data by external debug selection logic.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when DCN 3.1.5 display code combines these constants with offsets and base indices from `dcn_3_1_5_offset.h` and routes them through AMD Display Core register helpers.

A typical use path is:

1. A hardware block implementation selects a register address and base index from the generated offset header.
2. The block's field-list macro expands a shift/mask pair from this header into a register descriptor table.
3. Code calls a helper such as `REG_UPDATE`, `REG_SET`, `REG_GET`, or `REG_WAIT`.
4. The helper packs, masks, reads, modifies, writes, polls, or decodes the actual MMIO register field.

The represented state is hardware state:

- Persistent configuration fields include stream/audio/pixel mux selection, stream enable, packet enable, double-buffer enable, packet transmission line numbers, APG audio stream ID, debug generator controls, DME/VPG/APG memory power policy, DPHY mode/lane count, VC rates, SAT slot allocations, HDA ring bases/sizes/control bits, HDA stream descriptor format and BDL addresses, DCHVM clock/memory control, legacy VGA mode/timing fields, and perf/debug selection.
- Volatile readback fields include stream status, FIFO reset done/error/active/calibrated states, double-buffer pending, trigger pending, missed-deadline flags, APG CRC done/result, APG FIFO overflow, DME DB taken/transmission missed, VPG update pending/conflict, DPHY current mode/rate/SAT pending/error/CRC status, RIOMMU active/prefetch done, HDA busy/result-valid/FIFO-ready/error, CORB/RIRB status, and debug payload registers.
- Side-effecting write fields include reset bits, done-clear/status-clear bits, APG audio CRC done clear, APG FIFO overflow clear, DME DB taken clear, metadata missed clear, VPG conflict clear, HDA CORB/RIRB resets, immediate command output windows, stream reset/run bits, and DPHY CRC reset.
- Double-buffer and pending semantics are a recurring theme. Metadata, MSA, pixel format, generic sideband packets, and encoder packet controls expose enable/pending bits, so software must write in the order expected by the display hardware and usually coordinate with stream timing, vblank, or packet update boundaries.

The macros do not encode sequencing constraints. Callers must still know whether a bit is write-one-to-clear, read-only, latched at frame start, double-buffered, power-gated, indexed through an access/data register pair, or valid only while a link/audio engine is enabled.

## Dependencies And Integration Points

This chunk depends on the matching register-offset definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. The shift/mask names here are useful only when paired with the corresponding `reg*`/base-index definitions for the same DCN revision.

Known source integration points for this exact DCN 3.1.5 header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h` to build the DCN 3.1.5 DMUB register interface.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the same generated headers for interrupt service register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes this header while constructing the DCN 3.1.5 resource pool and display objects, including stream encoders.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c`, which include this header for GPIO/DDC/AUX-related register translation and construction.

Related cross-revision consumers show how the field families in this chunk are normally used:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and `.c` use `SE_SF` field lists and `REG_UPDATE`, `REG_GET`, and `REG_SET` flows for HPO DP link/DPHY fields such as `DP_LINK_ENC_CLOCK_CONTROL`, `DP_DPHY_SYM32_CONTROL`, `DP_DPHY_SYM32_STATUS`, `SAT_VC0`, `VC_RATE_CNTL0`, `TP_CONFIG`, and `TP_CUSTOM*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.h` and related hubbub code use `HUBBUB_SF` and register helpers for `DCHVM_CTRL0`, `DCHVM_MEM_CTRL`, `DCHVM_CLK_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0`.
- HDA/audio and stream encoder code paths use the AZ controller/endpoint/stream and DP/APG/VPG/DME/SYM32 field families indirectly through generated register tables, resource construction, and display/audio packet programming.
- Legacy VGA, perfmon, writeback, DPG, and FMT debug fields integrate mainly through diagnostic, register-dump, or indexed debug access paths rather than high-level display feature code.

Because this file is generated, most direct dependencies are compile-time macro expansions. Missing names usually break compilation where a field list expands. Incorrect numeric shifts or masks can compile cleanly and become runtime MMIO corruption.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.5 hardware register database is the main risk. A wrong mask or shift can silently program the wrong bit in stream enable, packet scheduling, link training, DPHY rate, HDA DMA, or DCHVM power/RIOMMU state.
- This chunk starts mid `DP_SYM32_ENC2` and ends mid DPG3 debug block. The final per-file merge should connect the preceding and following chunks rather than treating this span as a complete logical unit.
- Repeated instance names are easy to confuse. `DP_SYM32_ENC2` versus `DP_SYM32_ENC3`, `DP_DPHY_SYM320` versus `DP_DPHY_SYM321`, `AZSTREAM0..7`, and packet slots `GSP_CONTROL0..14` all have nearly identical field layouts but target different hardware instances or slots.
- Double-buffer pending and update-pending fields are timing-sensitive. Misusing `*_DOUBLE_BUFFER_ENABLE`, `*_DOUBLE_BUFFER_PENDING`, VPG frame/immediate update bits, or GSP trigger-pending fields can create stale packets, missed metadata transmission, or packet updates at an unintended frame boundary.
- Status and clear fields share nearby names. Examples include `APG_AUDIO_CRC_DONE` versus `APG_AUDIO_CRC_DONE_CLEAR`, `APG_AUDIO_FIFO_OVERFLOW_STATUS` versus clear, `METADATA_DB_TAKEN` versus clear, `METADATA_TRANSMISSION_MISSED` versus clear, and `VPG_GENERIC_CONFLICT_OCCURED` versus clear. Treating clear bits as persistent state is a common MMIO hazard.
- Indexed data windows require correct access ordering. VPG generic packet data, ISRC data, VGA indexed registers, perf/debug windows, and HDA immediate command data/index registers can all compile correctly while addressing the wrong indexed byte or register if software uses an incorrect index.
- DPHY link training and CRC fields are link-state-sensitive. Programming training pattern, PRBS, custom symbol, symbol override, VC rate, or SAT slot fields while the link is active can produce transient link errors unless sequenced by the HPO link encoder logic.
- HDA stream descriptors contain split lower/upper base address fields and low unimplemented/alignment bits. Incorrect BDL or DMA position base packing can break audio DMA or corrupt the position buffer protocol.
- Legacy VGA fields use 8-bit masks and historical indexed-register semantics. They are not interchangeable with modern DCN timing-generator fields even when names like horizontal/vertical total look similar.
- Debug-only registers often expose only a bit-0 shift with no explicit mask in this chunk. They should not be assumed to be normal typed configuration fields; many are debug selector/data windows whose interpretation depends on separate hardware debug mux state.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU Display Core with DCN 3.1.5 enabled. This catches missing macros, malformed macro names, and include/field-list expansion failures in DMUB, IRQ, GPIO, resource, HPO, and hubbub code.
- Regenerate `dcn_3_1_5_sh_mask.h` from the authoritative register database and compare this chunk byte-for-byte or by structured field name/shift/mask tuples.
- Cross-revision spot checks against adjacent DCN headers where the hardware block is expected to be compatible, especially HPO DP, DCHVM, HDA/AZ, VGA, and debug field families.
- DisplayPort HPO bring-up tests on DCN 3.1.5 hardware: stream enable/disable, link training, lane count/mode changes, DSC/compressed-stream VBID behavior, generic sideband packet transmission, metadata packets, panel replay tunneling, and DPHY error counters staying clear.
- Audio-over-DP/HDMI validation: APG enable/reset, audio packet generation, HBR status, audio CRC done/result, no APG FIFO overflow, CORB/RIRB command transport, immediate command busy/result-valid, output stream descriptor run/reset, and DMA position updates.
- Metadata and packet update validation: VPG generic packet RAM writes, frame/immediate update pending bits clearing, DME DB taken/pending behavior, no metadata transmission missed flags, and correct ISRC/MPEG infoframe bytes on the wire.
- Host-VM/hubbub validation where DCHVM is used: host VM init request, RIOMMU active/prefetch done polling, memory power request/status, and clock request mode programming.
- Runtime register dumps around feature operations. Writes should modify only fields covered by the intended masks and preserve unrelated fields in the same register.

## Open Questions For Merge

- The final per-file report should connect this chunk with the neighboring chunks that contain the start of `DP_SYM32_ENC2` and the continuation of DPG3/FMT debug definitions.
- This chunk documents field layout only. The final report should avoid inferring higher-level packet, audio, link, or VM sequencing beyond what is corroborated by functional source files.
