# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 30145-32540

## Scope And Purpose

This chunk is a generated DCN 3.2.1 shift/mask register definition slice for AMD display hardware. It covers the tail of the `DP1` DisplayPort block, the complete `DIG1` digital front/back-end block, the complete `DP2` DisplayPort block, the complete `DIG2` block, and the beginning of `DP3`. The file is not executable code; it is the hardware register field contract used by the AMD DC driver to build per-ASIC register tables and perform register read-modify-write operations through the display core's `REG_*` helper macros.

The chunk's main purpose is to publish exact bit positions (`__SHIFT`) and bit masks (`_MASK`) for display link programming on DCN 3.2.1. These fields control HDMI/TMDS packet generation, DP stream enablement, DP secondary data packets, DSC PPS generic stream packets, MST allocation registers, DP PHY training/test state, active link power management, double-buffer status, CRC/test-pattern plumbing, and encoder enable/disable state.

## Register Groups Covered

The slice begins in the existing `dce_dc_dio_dp1_dispdec` address block. It includes `DP1_DP_GSP8_CNTL` through `DP1_DP_GSP11_CNTL`, `DP1_DP_GSP_EN_DB_STATUS`, and `DP1_DP_AUXLESS_ALPM_CNTL1` through `DP1_DP_AUXLESS_ALPM_CNTL5`. These define generic stream packet controls for SDP/GSP slots 8-11, pending/active/deadline status bits, line-number fields, and auxless ALPM wake/sleep timing and interrupt fields.

The `dce_dc_dio_dig1_dispdec` block defines the first digital encoder instance. It includes `DIG1_DIG_FE_CNTL`, output CRC, clock/test/random pattern registers, FIFO control/status-related fields, HDMI metadata/infoframe/generic packet controls, ACR/audio control and readback fields, AFMT audio clock fields, digital back-end enable and HPD/source selection fields, TMDS control character and DC-balance fields, and DIG version/force-disable bits.

The `dce_dc_dio_dp2_dispdec` block is the largest part of this chunk. It defines DP2 stream/link fields: link status and embedded-panel mode, pixel format and MSA colorimetry, lane count, video stream enable/status/defer controls, steering FIFO overflow/TU size, M/N timing generation, framing, interrupt controls, DPHY controls and test symbols, 8b/10b and scrambler controls, PHY CRC controls and status, fast training, secondary packet enable/send/line fields, DP audio M/N/readback/timestamp fields, MST/MSE rate and slot allocation tables, BS/SR swap and HBR2 pattern controls, MSA timing parameters, MSO and DSC controls, metadata transmission, ALPM, GSP8-11 controls, double-buffer status, and auxless ALPM.

The `dce_dc_dio_dig2_dispdec` block mirrors the DIG1 fields for the second digital encoder instance. The masks are instance-prefixed (`DIG2_*`) but otherwise model the same front-end, HDMI packet, AFMT, back-end, TMDS, version, and force-disable fields.

The chunk ends at the beginning of `dce_dc_dio_dp3_dispdec`, covering DP3 through the opening `DP3_DP_VID_INTERRUPT_CNTL` fields. This partial DP3 block includes base link, format, lane, stream, FIFO, MSA, DPHY internal, M/N timing, framing, HBR2 eye-pattern, VBID, and video-disable interrupt fields. Later DP3 registers continue in the next chunk.

## APIs, Types, And Macros

There are no C functions or structs defined in this header slice. The important API surface is the generated macro naming convention:

- `<REG>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REG>__<FIELD>_MASK` gives the already-positioned bit mask.
- The register instance prefix (`DP1`, `DP2`, `DP3`, `DIG1`, `DIG2`) binds the field layout to an address-block instance.

These constants are consumed indirectly by display-core register table macros. `dcn321_resource.c` includes both `dcn_3_2_1_offset.h` and this `dcn_3_2_1_sh_mask.h`, then uses helper macros such as `SRI(...)` to map register addresses by instance and macros such as `SE_SF(...)` / `LE_SF(...)` to copy shift/mask pairs into stream-encoder and link-encoder mask tables.

Relevant consumers in the same source tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which selects the DCN 3.2.1 offset and shift/mask headers for resource construction.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.h`, whose stream encoder mask lists reference fields present here such as `DP_SEC_GSP*`, `DP_GSP11_CNTL`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_VID_TIMING`, `HDMI_*`, `AFMT_CNTL`, and generic HDMI packet controls.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c`, which uses `REG_UPDATE`, `REG_UPDATE_2`, `REG_SET_*`, and `REG_GET` against these logical fields to program DP info packets, DSC PPS packets, AFMT clock state, SDP line numbers, and stream enablement.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.h`, whose link encoder register list references DP link, DPHY, PRBS, scrambler, training pattern, MST allocation, and TMDS DC balancer registers covered by the DP2/DIG blocks.

## Control Flow

This header contributes data to runtime control flow rather than executing itself. During DCN 3.2.1 resource initialization, the driver includes this header and builds register, shift, and mask tables for each stream/link encoder instance. Later, common DCN stream and link encoder functions use logical field names through `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT`. Those helpers combine the selected register address from the offset table with the field shift/mask from this header and issue MMIO read-modify-write or read operations.

For HDMI/DIG paths, the control flow commonly starts from stream configuration and info-packet update code. The encoder code programs `DIG*_DIG_FE_CNTL` source, color/TMDS settings, `HDMI_CONTROL` scrambling/deep-color state, ACR/audio packet fields, generic HDMI packet send/continuous/line controls, and `HDMI_DB_CONTROL` double-buffer behavior. DIG FIFO and output CRC/test-pattern fields provide diagnostic and validation paths.

For DP paths, link and stream setup code programs `DP*_DP_LINK_CNTL`, `DP*_DP_CONFIG`, `DP*_DP_PIXEL_FORMAT`, `DP*_DP_VID_STREAM_CNTL`, M/N timing fields, MSA fields, and DPHY training/scrambler/FEC/test fields. Secondary data packet control flows use `DP_SEC_CNTL*` and `DP_GSP*_CNTL` fields to enable specific packet slots, request sends, poll pending/active/deadline state, and schedule packets on particular lines. DSC PPS setup in `dcn30_dio_stream_encoder.c` is a concrete example: it sets `DP_SEC_GSP11_PPS`, updates generic info packet payloads, writes `DP_SEC_GSP11_LINE_NUM`, enables `DP_SEC_GSP11_ENABLE`, and enables `DP_SEC_STREAM_ENABLE`.

For MST/MSO paths, the DP2 fields in this chunk define MSE rate and slot-allocation table registers (`DP_MSE_RATE_*`, `DP_MSE_SAT*`, `DP_MSE_SAT*_STATUS`, `DP_MSE_SAT_UPDATE`) and MSO controls (`DP_MSO_CNTL`, `DP_MSO_CNTL1`). The control flow is register-table driven: higher-level MST allocation code writes source IDs and slot counts, triggers updates, and checks update/status fields.

## State And Persistence Behavior

The header itself has no mutable state, allocation, persistence, or lifetime behavior. Its constants become compile-time metadata in the amdgpu display driver.

The hardware fields described by the chunk are stateful MMIO registers. Some are programmed configuration state, such as pixel encoding, color depth, lane count, stream enable, FIFO levels, secondary packet enable bits, line numbers, ACR N/CTS values, DSC/MSO/MSE settings, and ALPM timings. Some are transient command bits, such as `*_SEND`, `*_ACK`, `*_CLEAR`, `*_RESET`, and immediate update controls. Some are hardware status/readback bits, such as packet pending/active/deadline, double-buffer pending/taken, FIFO error/calibrated, link status, stream status, ALPM interrupt/status/pending, CRC result valid, and MSE slot status.

Persistence is therefore hardware-scoped. Values can survive across parts of a modeset or link training sequence until the driver rewrites them or the display engine is reset. Incorrect masks can leave stale fields in place during read-modify-write operations, while incorrect shifts can write valid-looking values into unrelated hardware fields.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.2.1 register offset header for actual MMIO addresses. A mask from this file is only meaningful when paired with the corresponding `reg...` address and base index in `dcn_3_2_1_offset.h`.

The main integration point is the AMD display core register helper layer. The generated field names must match the logical names expected by stream/link encoder mask-list macros. For example, a `SE_SF(DP0_DP_GSP11_CNTL, DP_SEC_GSP11_ENABLE, mask_sh)` entry depends on this header providing the matching per-instance field layout, even when the runtime object is built for DP1/DP2 style instances through register-list expansion.

The chunk also integrates with protocol-level features:

- HDMI 2.x/FRL-adjacent packet generation, scrambling, deep color, ACR, audio, AVI/audio/MPEG infoframes, metadata packets, and generic packets.
- DisplayPort main link stream control, MSA/VBID timing, FEC/DPHY control, link training/test patterns, scrambler and CRC diagnostics.
- DisplayPort secondary data packets and generic stream packets used for VSC, SPD, HDR static metadata, adaptive sync, DSC PPS, and other SDP payloads.
- DisplayPort MST slot allocation and update status.
- DSC, MSO, ALPM, and auxless wake/sleep behavior.

## Risks And Edge Cases

Generated header correctness is critical because most mistakes compile cleanly. A wrong mask or shift can cause hardware programming errors without a type-system signal.

High-risk fields in this chunk include write-one or command/status-style bits such as `*_ACK`, `*_CLEAR`, `*_SEND`, `*_RESET`, and `*_IMMEDIATE`. If a mask is too wide, a read-modify-write can acknowledge or clear adjacent status unintentionally. If a mask is too narrow, a command may never reach hardware.

DP secondary packet and GSP fields are timing-sensitive. `DP_SEC_GSP*_LINE_NUM`, `*_LINE_REFERENCE`, `*_SEND_PENDING`, `*_SEND_ACTIVE`, and `*_SEND_DEADLINE_MISSED` must align with vblank/line scheduling expectations. Errors can manifest as missing HDR metadata, VSC/Adaptive-Sync packets, or DSC PPS packets even when the display link otherwise trains successfully.

HDMI generic packet controls span many packet slots across `HDMI_GENERIC_PACKET_CONTROL0`, `5`, `6`, and `10`, with line fields split across additional control registers. Slot numbering errors or instance-prefix mismatches can route packet control to the wrong generic packet buffer.

MST/MSE allocation fields pack multiple source IDs and slot counts into the same registers. Incorrect widths can corrupt neighboring allocation entries and cause bandwidth allocation failures only on multi-stream topologies.

ALPM and auxless ALPM fields mix command, timing, interrupt, and line/frame scheduling state. Bad definitions can create intermittent resume/wakeup, FEC timing, or panel power behavior problems that are difficult to reproduce in simple single-monitor testing.

The DIG1/DIG2 blocks are intentionally duplicated. Copy/paste or generator drift between instances would create asymmetric behavior where only one connector/encoder instance fails. The same applies to DP1/DP2/DP3 instance families, especially because this chunk starts and ends mid-instance.

## Test Signals

Build-time test signals are limited: this header is primarily validated by successful compilation of the amdgpu display driver with DCN 3.2.1 resources enabled. Missing or renamed macros should fail compilation in resource, stream encoder, or link encoder mask-list construction.

Runtime validation requires display hardware or register-level simulation. Useful signals include:

- HDMI modeset tests covering deep color, scrambling, audio ACR, generic/infoframe/metadata packets, AVMUTE, and TMDS character generation on both DIG1 and DIG2.
- DP link training and modeset tests covering link status, lane count, stream enable/status, M/N timing, MSA/VBID fields, FEC, scrambler, PRBS/test patterns, and DPHY CRC.
- DSC enablement tests that verify PPS packets are sent through GSP11 and that `DP_SEC_GSP11_ENABLE`, `DP_SEC_GSP11_LINE_NUM`, and `DP_SEC_GSP11_PPS` interact correctly.
- HDR, VSC, SPD, Adaptive-Sync, and other SDP packet tests that confirm GSP enable/send/pending/deadline behavior.
- MST tests that exercise MSE rate programming, slot allocation table updates, status readback, and multiple streams sharing a DP link.
- ALPM/auxless ALPM suspend-resume and panel power tests that check wakeup interrupts, wake/FEC line numbers, sleep intervals, and hardware-mode transitions.
- Register dump comparisons against AMD golden values or firmware traces for DCN 3.2.1 are strong regression signals because they catch silent bitfield drift in generated mask headers.
