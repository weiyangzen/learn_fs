# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 42617-45015

## Purpose

This chunk is a generated AMD DCN 4.2.0 shift/mask register-field header slice. It contains no executable C logic; it exports preprocessor constants that encode field bit positions (`__SHIFT`) and masks (`_MASK`) for display-controller MMIO registers. Runtime AMDGPU display code pairs these constants with the matching DCN 4.2.0 offset header to build typed register tables for register helper calls.

The requested range contains 2,168 `#define` entries: 1,083 shift definitions and 1,085 mask definitions. The apparent imbalance is caused by field names that themselves end in `_MASK`, such as `HDMI_ERROR_MASK`, `DP_VID_STREAM_DISABLE_MASK`, `DP_STEER_OVERFLOW_MASK`, `DPHY_FAST_TRAINING_COMPLETE_MASK`, and `DP_ALPM_WAKEUP_INTERRUPT_MASK`; those fields generate macro names ending in `__SHIFT` and `_MASK_MASK`.

The range starts in the tail of `DIG2_DIG_OUTPUT_CRC_CNTL`, covers the rest of the DIG2 stream encoder and its DP2 DisplayPort register block, then covers VPG3, APG3, DME3, and most of the DIG3 HDMI/DIG front/back-end block through the first `DIG3_DIG_BE_EN_CNTL` shift. The boundaries are artificial chunk boundaries: the first register group begins in the previous chunk, and the final `DIG3_DIG_BE_EN_CNTL` mask continues in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The public contract is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate or preserve the field during MMIO read-modify-write.

The major field families in this chunk are:

- `DIG2_*`: output CRC result/control tail, clock and test pattern generation, random-pattern seed, FIFO control/status/calibration, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet controls, double-buffer status, TMDS control-character/sync/DC-balancer fields, front-end audio selection, back-end clocking, back-end source/HPD selection, and DIG version.
- `DP2_*`: DisplayPort link control, pixel format, MSA colorimetry/misc/timing/VBID, video stream control, steer FIFO control/status, DPHY internal controls, link framing, HBR2/PRBS/scrambling/CRC/training-pattern fields, TU control, secondary-data packet controls, audio M/N readback/programming, MST/MSE slot-allocation tables and status, MSO controls, DP double buffering, metadata transmission, ALPM/AUX-less ALPM, generic stream packet controls, stream/link symbol counters, panel replay, and fast-training status.
- `VPG3_*`: video packet generator generic packet access/data, generic stream packet frame-update and immediate-update controls for packet slots 0 through 14, generic status, memory power, and ISRC1/2 access/data fields.
- `APG3_*`: audio packet generator reset/enable, DP audio stream ID and channel override, debug generator controls, debug ACP/audio-info/channel-status payload fields, audio CRC controls/result, ramp debug controls, enable/HBR/FIFO overflow/output-active status, audio DTO debug, memory power, and spare bits.
- `DME3_*`: DME control and memory-control fields, including enable/reset/reset-done, dynamic metadata packet timing, outstanding request counters, DL delta, memory power controls, and memory power state.
- `DIG3_*`: front-end selection/clock/enable, output CRC, clock/test/random patterns, FIFO controls, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet controls, double-buffer status, ACR programmed/readback values, front-end audio selection, and back-end clock/source/HPD selection. The chunk ends immediately after `DIG3_DIG_BE_EN_CNTL__DIG_BE_ENABLE__SHIFT`.

The repeated HDMI generic packet controls are dense. `HDMI_GENERIC_PACKET_CONTROL0` has send/continuous/line-reference/update-lock-disable fields for packet slots 0-7. `CONTROL6` adds the same controls for slots 8-14. `CONTROL5` exposes immediate-send and immediate-send-pending bits for slots 0-14. `CONTROL1-4` and `CONTROL7-10` hold packet-line fields, with `CONTROL10` also carrying enable double-buffer pending bits.

The DP2 secondary-data and MST families are also central. `DP_SEC_CNTL*` covers global secondary-packet enable, audio/video stream source, packet stream selection, SDP split, VSC/metadata/AS SDP controls, PPS/metadata/DSC/audio timestamp controls, DB pending/taken handshakes, and double-buffering. `DP_MSE_SAT*` and matching status registers describe MST slot allocation, stream source, slot count, and update state.

## Control Flow

This header has no runtime control flow. Its values are consumed through compile-time table construction:

1. DCN 4.2 code includes `dcn_4_2_0_offset.h` and this `dcn_4_2_0_sh_mask.h`.
2. Resource and block headers use token-pasting macros such as `SE_SF`, `VPG_SF`, `APG_SF`, `AUX_SF`, `LE_SF`, `SRI`, `SRI_ARR`, and `SR_ARR_INIT` to pair register offsets with these generated shift/mask constants.
3. DCN 4.2 constructors store those register, shift, and mask tables in stream encoder, VPG, APG, AUX, link encoder, HPD, audio, HPO stream/link encoder, DMUB, IRQ, GPIO, and clock-management objects.
4. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the numeric field metadata to access individual hardware bits.

Programming order is not encoded here. HDMI packet setup, DP link training, stream enable/disable, secondary-data packet scheduling, MST allocation, ALPM entry/exit, audio packet generation, DME operation, double-buffer latching, clock gating, and reset sequencing are controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The file stores no software state and persists nothing itself. It names hardware-visible state fields:

- DIG2/DIG3 stream encoder state for front-end source selection, encoder enable, FIFO reset/calibration/error status, output CRC/test-pattern diagnostics, HDMI mode flags, TMDS pixel encoding/color format/deep-color state, Dolby Vision metadata state, AVMUTE/general-control state, audio clock regeneration values, packet lines, generic packet send modes, and HDMI double-buffer pending/taken bits.
- DP2 link and stream state for link enable/training, pixel format and MSA fields, video timing, VBID, stream disable/interrupt control, DPHY PRBS/scramble/CRC/error state, TU/steer FIFO, secondary-data packets, DP audio M/N, MST slot allocation, MSO, metadata, ALPM/AUX-less ALPM, generic stream packets, symbol counters, panel replay, and fast training.
- VPG3 state for generic packet memory access, frame-based and immediate packet update requests, update-pending readbacks, generic status, ISRC data, and VPG memory power.
- APG3 state for audio packet generation, debug packet sources, channel-status payloads, audio CRC capture, ramp debug controls, status/overflow clear bits, DTO debug, and APG memory power.
- DME3 state for dynamic metadata engine enable/reset/timing and memory power.

Persistence and side effects are hardware-defined. Configuration fields generally remain until modeset, link reset, stream disable, suspend/resume, power gating, GPU reset, or ASIC reset reprograms them. Status, interrupt, pending, taken, clear, and reset-done fields can be latched, write-one-to-clear, self-clearing, or valid only while the corresponding display block is powered and clocked. This header only provides bit geometry; access semantics come from the register specification and consuming driver code.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DCN 4.2.0 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which supplies the companion register offsets and base indices.

Direct DCN 4.2 include users include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which builds resource-pool register tables. This chunk feeds `vpg_regs`, `apg_regs`, `stream_enc_regs`, `link_enc_aux_regs`, `link_enc_regs`, `hpo_dp_stream_enc_regs`, and related shift/mask tables through `DCN31_VPG_MASK_SH_LIST`, `DCN31_APG_MASK_SH_LIST`, `SE_COMMON_MASK_SH_LIST_DCN42`, `DCN_AUX_MASK_SH_LIST`, `LINK_ENCODER_MASK_SH_LIST_DCN42`, and `DCN4_2_HPO_DP_STREAM_ENC_MASK_SH_LIST`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h`, which defines DCN 4.2 register-list and mask-list shapes, including audio and stream/link encoder field lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_stream_encoder.h` and `.c`, which consume `DIGx`, HDMI, TMDS, VPG, and APG tables for DIO stream encoder construction and programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_link_encoder.h` and `.c`, which consume DIO link-encoder fields such as DIG back-end clock/source controls and DP DPHY controls.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.h`, whose AUX field-list macros use `DP_AUXn_*` style shift/mask constants from this generated header. This exact chunk does not contain the `DP_AUX2_*` block but it does contain the DP2 stream/link-side fields that pair with AUX/DDC link management.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h`, which define VPG/APG field-list contracts consumed by `VPG3_*` and `APG3_*` definitions here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, which include the DCN 4.2 generated headers for register access across service, interrupt, GPIO, and clock-management paths.

Behaviorally, this chunk sits on the display-output path: stream encoder programming for HDMI/TMDS and DP, DP secondary-data packet delivery, MST/MSO allocation, low-power and fast-training link features, audio/video packet generation, dynamic metadata transport, and diagnostic CRC/test-pattern/status reporting.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bit, corrupting an adjacent field, missing a status condition, or breaking only one encoder instance.
- The file is generated. Manual edits risk divergence from the authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. `DIG2_DIG_OUTPUT_CRC_CNTL` starts before this range, and `DIG3_DIG_BE_EN_CNTL` continues after it. Adjacent chunk reports must be reconciled before making whole-register or whole-file claims.
- `DIG2` and `DIG3` are structurally similar but not interchangeable. Copy-sensitive generator errors can affect only one DIO pipe, causing failures tied to a specific connector routing or encoder assignment.
- HDMI packet-control fields have multiple state models: one-shot send, continuous send, immediate send, line scheduling, update-lock disabling, double-buffer pending, and DB taken/clear. Wrong masks can produce missing HDR/AVI/audio infoframes, stale metadata, repeated packets, or update races around vblank.
- Audio clock regeneration fields (`HDMI_ACR_*` CTS/N, status readback, and packet controls) are interoperability-sensitive. Incorrect masks can cause HDMI audio drift, silence, receiver-specific sample-rate failures, or broken ACR auto-send behavior.
- TMDS and HDMI mode fields such as scrambling, clock-channel rate, deep color, pixel encoding, color format, control characters, sync characters, and DC balancing can produce link-only failures where DP paths still work.
- DP2 DPHY/link-training/status fields are sequencing-sensitive. Wrong training-pattern, scramble, PRBS, CRC, fast-training, link-framing, or stream-disable bits can manifest as failed link training, intermittent blanking, bad compliance-test output, or false error reporting.
- DP secondary-data and metadata controls are broad. Bad PPS, VSC, metadata, SDP split, audio timestamp, or double-buffer masks can break DSC metadata delivery, HDR metadata, Adaptive Sync/panel replay sideband data, or audio packet timing.
- MST/MSE slot allocation fields must be coherent across allocation registers, status registers, and update/timing controls. A field error can affect only MST topologies or only high-bandwidth multi-stream scenarios.
- ALPM and AUX-less ALPM fields are low-power handshake state. Incorrect masks can cause missed wake interrupts, stuck low-power entry/exit, resume-only blanking, or panel replay/ALPM interactions that are hard to reproduce.
- VPG/APG/DME memory-power fields interact with power gating and clock gating. Wrong force/state/default-low-power masks can create resume failures, diagnostics that read as idle when active, or packet generator stalls after power transitions.
- Fields ending in `_MASK` generate macro names such as `_MASK__SHIFT` and `_MASK_MASK`. Naive scripts that identify masks by suffix can miscount or mishandle these fields.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU display support with DCN 4.2 enabled. Missing or renamed macros should surface in `dcn42_resource.c`, DCN 4.2 DIO stream/link encoder code, VPG/APG headers, AUX helpers, DMUB setup, IRQ, GPIO, and clock-manager users.
- Mechanically compare lines 42617-45015 against the authoritative DCN 4.2.0 register-field database and ensure each register-field has the expected shift and mask, allowing for artificial chunk boundaries and `_MASK`-named fields.
- Cross-check this range against `dcn_4_2_0_offset.h` so every register family has matching offsets and base-index entries.
- Exercise all DIO stream encoders that can map to `DIG2` and `DIG3`: HDMI modes, DP modes, connector hotplug, encoder reassignment, suspend/resume, and rapid modeset sequences. Watch for pipe-specific failures.
- Validate HDMI/TMDS paths with deep color, scrambling, FRL/TMDS clock-rate changes where applicable, HDR/Dolby Vision metadata, generic infoframes, AVMUTE, and HDMI audio. Expected signals are stable link, correct metadata on a sink analyzer, no stuck HDMI DB pending/taken bits, and valid ACR CTS/N behavior.
- Exercise DP2 link paths across link training, retraining, fast training, PRBS/compliance patterns, CRC capture, stream disable/enable, pixel-format changes, MST, MSO, panel replay, ALPM/AUX-less ALPM, and suspend/resume. Watch for false DPHY errors, stuck update-pending bits, failed wake interrupts, or stream symbol counter anomalies.
- Validate DP secondary-data packet behavior with DSC PPS, VSC, HDR metadata, Adaptive Sync/panel replay sideband traffic, and audio timestamps. Register dumps should show coherent enable, line, DB pending/taken, and packet scheduling state.
- Exercise VPG3/APG3 packet generation through both DIO and HPO mappings in `dcn42_resource.c`. Expected signals are correct generic packet data writes, frame/immediate update completion, valid APG audio status, no APG FIFO overflow, and stable memory-power state after idle/resume.
- Exercise DME3 dynamic metadata paths if exposed by the platform, including metadata enable/disable and power-state transitions.
- Run repeated instance consistency checks across `DIG2`/`DIG3` and corresponding DP/VPG/APG/DME instances, while allowing intentional per-instance prefixes and known boundary splits.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DIG2_DIG_OUTPUT_CRC_CNTL`. This chunk starts with its mask definitions and then covers the rest of DIG2 and DP2 plus VPG3/APG3/DME3 and most of DIG3 HDMI/DIG metadata. The next chunk should continue `DIG3_DIG_BE_EN_CNTL` with its mask and then cover the remaining DIG3, DP3, and subsequent DCN 4.2.0 register families. The final per-file document should merge these boundaries before describing all DCN 4.2.0 stream encoder, DP, VPG, APG, or DME metadata.
