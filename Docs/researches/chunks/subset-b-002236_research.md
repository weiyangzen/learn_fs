# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 45016-47434

## Purpose

This chunk is a generated AMD DCN 4.2.0 shift/mask header slice for display hardware register fields. It contains no executable C code; its public surface is a set of `#define` constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for fields in DCN display-controller registers.

The requested range contains 2,166 generated definitions over 2,419 source lines. It starts in the tail of the `DIG3_DIG_BE_EN_CNTL` group, covers the `DIG3` TMDS and version fields, covers the complete `DP3` DisplayPort stream/link encoder register field block, then covers `VPG4`, `APG4`, `DME4`, and most of the `DIG4`/HDMI/TMDS stream-encoder surface. It then starts the `DP4` DisplayPort block and stops inside `DP4_DP_MSO_CNTL1`, before that register's remaining shifts/masks and later `DP4` registers. The boundaries are artificial chunk boundaries rather than semantic register-block boundaries.

Although the file is under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or direct MMIO operations in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for `FIELD`.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for `FIELD`.

The main register-field families in this chunk are:

- `DIG3` tail: `DIG_BE_ENABLE`, TMDS sync/control-character generation, TMDS feedback, stereo sync selection, sync-character patterns, control bits, DC balancer controls, per-control-lane generation controls, and `DIG_TYPE`.
- `DP3`: DisplayPort link status/training, pixel format, MSA colorimetry/misc/timing, lane configuration, stream enable/status, steer FIFO status and overflow interrupt bits, video M/N timing, link framing, DPHY training/symbol/scrambler/PRBS/CRC controls, transfer-unit control, secondary-data packet controls, audio M/N/timestamp registers, MST/MSE rate and slot-allocation table fields, HBlank/MSA timing, MSO secondary packet enables, steer FIFO control, generic secondary packet controls 8 through 11, double-buffer control/status, ALPM and AUX-less ALPM fields, stream/link symbol counters, panel replay controls, and fast-training status.
- `VPG4`: generic packet data access, generic packet payload bytes, frame-update/immediate-update enables for generic secondary packets, conflict status/clear, memory-power controls, and ISRC1/2 packet data access.
- `APG4`: audio packet generator debug channel enable fields and APG memory-power controls.
- `DME4`: dynamic metadata engine enable/reset/ready/configuration fields plus memory-power controls.
- `DIG4`: front-end and back-end control, source selection, stereo sync, clock controls, enable/reset, output CRC, test and random patterns, FIFO controls, HDMI metadata and generic packet controls, HDMI core/deep-color/scrambler/status/audio/ACR/VBI/infoframe/general-control fields, HDMI double-buffer controls, audio front-end control, TMDS controls, and `DIG_TYPE`.
- `DP4` beginning: the same DisplayPort stream/link/DPHY/MSA/MSE/MSO field families as `DP3`, but only through the early `DP4_DP_MSO_CNTL1` shifts in this chunk.

Several fields in this range are consumed through generic instance-0 shift/mask tables even though the chunk itself is for instances 3 and 4. The codebase commonly uses macros such as `SE_SF(DP0_DP_PIXEL_FORMAT, PIXEL_ENCODING_TYPE, mask_sh)` to define a generic field table, while register address tables select the concrete instance (`DP3`, `DP4`, `DIG4`, and so on).

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 4.2.0 code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. Resource macros in `dcn42_resource.c` and `dcn42_resource.h` use token-pasting helpers such as `SRI_ARR`, `SR_ARR`, `SE_SF`, and `LE_SF` to bind generated register addresses, shifts, and masks into typed register tables.
3. Runtime display objects receive those tables during resource-pool construction for stream encoders, link encoders, VPG/APG blocks, AUX/HPD blocks, and HPO-related paths.
4. Common AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the tables to access MMIO bitfields.

The macros in this chunk do not prescribe programming order. DisplayPort link training, stream enable/disable, secondary-packet programming, HDMI packet programming, TMDS setup, DME/VPG/APG packet updates, MST slot-allocation updates, ALPM entry/exit, panel replay, CRC capture, and memory-power sequencing are implemented by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- DisplayPort stream state: link-training completion/status, lane count, pixel encoding, component depth, compressed format, stream enable/status, video timing M/N generation, MSA misc/timing values, VBID controls, and HBlank minimum symbol width.
- DisplayPort physical/link state: DPHY bypass, 8b/10b, training-pattern selection, lane symbols, PRBS, scrambler advance/count, CRC control/results/status, HBR2 pattern control, BS/SR swap load/done, fast-training capability/status, and FEC-related fields from the common link-encoder consumers.
- Secondary packet and metadata state: DP generic secondary packet enables/line numbers/priorities, audio timestamp and M/N fields, HDMI generic packet sends/lines, HDMI infoframe/VBI/audio/ACR controls, VPG packet data/update controls, APG audio-stream/debug fields, and DME dynamic-metadata control.
- MST/MSO state: MSE rate update, SAT source/encryption/slot-count entries and status readback, SAT update and keepout bits, MSE link timing/misc controls, and MSO packet enable masks.
- Power and debug state: VPG/APG/DME memory-power controls, HDMI and DIG double-buffer controls, output CRC, FIFO controls, test-pattern generators, and symbol/link counters.

Persistence and side effects are hardware-defined. Configuration fields usually remain until a modeset, stream disable, link reset, power-gating transition, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, counter, update-pending, reset-done, and CRC fields can be latched, write-one-to-clear, self-clearing, read-only, or valid only while the relevant block is powered and clocked. This file only provides bit positions and masks; it does not encode those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies the matching register offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes this header and initializes DCN 4.2.0 stream encoder, VPG, APG, AUX, HPD, and link encoder register/shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` defines `SE_DCN42_REG_LIST_RI(id)` and `VPG_DCN42_REG_LIST_RI(id)`, which require the `DIG`, `DP`, `DME`, and `VPG` register names represented in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_stream_encoder.h` defines `SE_COMMON_MASK_SH_LIST_DCN42`, which consumes the generic stream-encoder field names for DP pixel format, stream control, secondary packets, MSA timing, HDMI packet controls, DME, and DIG controls.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_link_encoder.h` defines `LINK_ENCODER_MASK_SH_LIST_DCN42`, which consumes DIG back-end, TMDS, DP DPHY/link/framing/MSE, AUX, HPD, and DIO clock-gating field names. The concrete `DIG3`/`DP3` and `DIG4`/`DP4` instances in this chunk are part of the repeated generated set behind those tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` provide the VPG/APG field-list macros that map onto the generated `VPG4` and `APG4` field layout.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h` provides shared `DCN2_AUX_REG_LIST_RI(id)` and `HPD_REG_LIST_RI(id)` macros used by DCN 4.2.0 for AUX and HPD register-address tables adjacent to this stream/link encoder metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c` includes the same generated header for DCN 4.2.0 interrupt-source register setup, especially HPD-related plumbing outside this exact slice.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, `dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, and `dc/gpio/dcn42/*` also include the generated offset and shift/mask headers for DCN 4.2.0 block control.

Behaviorally, this chunk supports the DIO stream and link paths for later digital engines: DP/HDMI stream encoding, TMDS output setup, DisplayPort physical/link training, MST/MSO scheduling, generic secondary packet generation, HDMI audio/infoframe/ACR packet generation, VPG/APG/DME metadata/audio blocks, and low-power/panel-replay features.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting only one bitfield at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first line is only the mask half of `DIG3_DIG_BE_EN_CNTL__DIG_BE_ENABLE`, and the final line stops inside `DP4_DP_MSO_CNTL1` before the remaining shifts/masks. Adjacent chunk reports must be merged before making whole-register or whole-instance claims for those two boundary groups.
- Repeated instances are copy-sensitive. `DP3` and `DP4`, plus `DIG3` and `DIG4`, are structurally similar but used for different physical/logical display engines. A generator or table-index error can break only one connector path or only modes routed through one encoder instance.
- HDMI and DP packet controls are dense. Bad masks for generic packet send/line/continue bits, infoframe controls, VSC/HDR/adaptive-sync metadata, or DSC PPS secondary-packet fields can cause missing metadata, sink misconfiguration, HDR/VRR failures, or visible mode issues without obvious compile-time failures.
- MST/MSO and MSE slot-allocation fields must be coherent. Wrong source, slot-count, update, keepout, or status masks can produce bandwidth allocation errors, failed MST displays, or transient corruption during payload-table updates.
- DisplayPort link-training and DPHY fields are sequencing-sensitive. Incorrect masks for training pattern, scrambler, PRBS, CRC, BS/SR swap, fast training, FEC, lane count, or stream-enable/status fields can cause blank displays, link instability, or failures limited to certain link rates or lane counts.
- MSA timing fields directly encode sink-visible timing. Bad masks for totals, starts, sync widths, polarities, width/height, M/N generation, or VBID controls can cause invalid modes even when the higher-level timing calculation is correct.
- HDMI deep color, scrambling, clock-channel-rate, TMDS control, and audio/ACR fields interact with sink capabilities and pixel clock. Incorrect masks can cause HDMI 2.0 high-clock failures, audio dropouts, or incompatibility only on particular monitors.
- VPG/APG/DME memory-power controls can interact with packet update paths. If memory light-sleep or force bits are wrong, metadata/audio packet generation can fail after idle, suspend/resume, or display power-gating transitions.
- Status and counter fields may be read-only, latched, or clear-on-write according to hardware. Treating generated masks as access-policy documentation can lead to stuck status bits or missed diagnostics.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build DCN 4.2.0 AMDGPU display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_resource.h`, `dcn42_dio_stream_encoder.h`, `dcn42_dio_link_encoder.h`, `dcn31_vpg.h`, `dcn31_apg.h`, and `irq_service_dcn42.c`.
- Mechanically compare this range against the authoritative DCN 4.2.0 register-field database and ensure every complete field in the slice has the expected `__SHIFT` and `_MASK` values.
- Cross-check this shift/mask range against `dcn_4_2_0_offset.h` so every completed register group has a corresponding register offset and base-index entry.
- Run static repeated-instance checks across `DP3` and `DP4`, and across `DIG3` and `DIG4`, while allowing the artificial start/end truncation at `DIG3_DIG_BE_EN_CNTL` and `DP4_DP_MSO_CNTL1`.
- Exercise DisplayPort SST on connectors routed through the later DIG/DP instances: link training at multiple rates/lane counts, stream enable/disable, modeset transitions, CRC capture where available, and suspend/resume. Expected signals are stable link training, correct stream status, no stuck FIFO reset/overflow state, and sane MSA timing register dumps.
- Exercise DisplayPort MST/MSO payload allocation and reallocation on `DP3`/`DP4` paths. Expected signals are correct SAT slot counts/status readback, no stuck MSE rate/SAT update state, and stable multi-monitor hotplug/modeset behavior.
- Exercise HDMI/DVI/TMDS modes through the affected DIG instances, including deep color, high pixel clocks requiring scrambling, audio, ACR values, generic packets, and infoframes. Expected signals are working video, correct sink-reported metadata, stable audio, and no HDMI status errors.
- Exercise VPG/APG/DME users: HDR/static metadata, adaptive sync or other generic packets, HDMI/DP audio packet generation, and dynamic metadata paths. Include idle and power-gated transitions to catch memory-power field mistakes.
- Validate low-power and replay features represented here: ALPM, AUX-less ALPM, symbol counters, and panel replay controls/status. Expected signals are correct entry/exit behavior and no stream loss after replay or ALPM transitions.
- Use register dumps around the chunk boundaries to verify `DIG3_DIG_BE_EN_CNTL` and `DP4_DP_MSO_CNTL1` only after the adjacent chunks are reconciled, because this chunk alone does not include those complete register-field groups.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DIG3_DIG_BE_EN_CNTL` and earlier `DIG3` back-end fields. This chunk starts with only the `DIG_BE_ENABLE_MASK` line. The next chunk continues `DP4_DP_MSO_CNTL1`, then covers the remaining `DP4` registers. The final per-file research document should reconcile these boundaries before describing all DCN 4.2.0 DIO stream/link encoder metadata or all instance-4 DP behavior.
