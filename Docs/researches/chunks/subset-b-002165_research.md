# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 35044-37461

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask table for display I/O register fields. It contains no executable code; its public surface is the set of `#define <REGISTER>__<FIELD>__SHIFT` and `#define <REGISTER>__<FIELD>_MASK` constants consumed by AMD display-core register helpers. The matching offset definitions live in `dcn_4_1_0_offset.h`, while this file describes how to pack and unpack bitfields inside those registers.

The range starts at the tail of `DIG2_HDMI_INFOFRAME_CONTROL1`, covers the rest of the `DIG2` HDMI/HDCP/TMDS field definitions, then covers the full `DP3` DisplayPort stream/link encoder field set, and finally begins the `DIG3` digital encoder field set through `DIG3_TMDS_CTL0_1_GEN_CNTL`. The chunk therefore spans two main display pipelines: the end of DIG2 and the DP3/DIG3 path.

## Register Families Covered

The `DIG2` portion defines fields for:

- HDMI generic packet controls 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, and 10, including generic packet send/continuous/line-reference/update-lock bits for packet slots 0-14 and immediate-send/pending bits.
- HDMI general control and double-buffering: GCP color-depth/packing/AVMUTE and double-buffer trigger/pending/control fields.
- HDMI ACR programming and status for 32 kHz, 44.1 kHz, and 48 kHz audio clocks, plus AFMT and back-end clock/control/enable fields.
- HDCP interrupt, I2C, link status, reset, receiver-port local data, DP bootstrap status, HDCP clock, and engine selection fields.
- TMDS control fields for sync phase, control characters, feedback, stereo sync selection, 10-bit sync patterns, TMDS control bits, DC balancer control, DC balance characters, and CTL0-3 generation control.

The `DP3` portion defines fields for:

- DP stream and link setup: link training completion/status, pixel format and component depth, MSA colorimetry/misc/timing, lane count, video stream enable/status/disable interrupt, video M/N generation, link framing, VBID/MSA transmission, and TU control.
- DPHY and training/test controls: alternate scrambler reset, FEC enable/status/ALPM disable mode, scrambler selection and bypass, training pattern selection, 8b/10b state, PRBS, scrambler controls, CRC enable/control/results, MST CRC, fast training pattern/control/status, HBR2 pattern, byte/symbol swap, and panel replay tunneling optimization.
- Secondary data and audio packetization: `DP_SEC_CNTL*`, secondary framing, audio N/M and readback, timestamp, packet control, generic stream packet controls `DP_GSP8_CNTL` through `DP_GSP11_CNTL`, GSP enable double-buffer status, and metadata transmission.
- MST/MSO and slot allocation: MSE rate controls, CP MSE status, MSE SAT0/SAT1/SAT2 assignments and status, SAT update, link timing, misc control, and MSO control fields including split stream source, enable, input select, format mode, multi-primary, padding, xstart position, and secondary stream index.
- ALPM and counters: ALPM control, auxless ALPM timing/wakeup/FEC state/interrupt fields, stream/link symbol count status and controls.

The `DIG3` portion begins a second digital encoder instance and mirrors much of the DIG2 functionality:

- Front-end source, clock, soft reset, enable, bypass, stereosync, output CRC, test/random patterns, and FIFO control fields.
- HDMI metadata, main HDMI control/status, audio/ACR/VBI/infoframe/generic packet controls, GCP, double buffering, ACR values/status, AFMT, back-end control, HDCP, and TMDS fields through `DIG3_TMDS_CTL0_1_GEN_CNTL`.

## APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The effective API is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the low bit position for a field.
- `REGISTER__FIELD_MASK` gives the mask for that field in the register's native width.
- Consumers pass these constants through helper macros such as `FD`, `FD_MASK`, `FD_SHIFT`, `SE_SF`, and `LE_SF` to populate per-block shift and mask structures.

Representative exported field groups include `DIG2_HDMI_GENERIC_PACKET_CONTROL0__HDMI_GENERIC0_SEND`, `DIG2_HDCP_LINK0_STATUS__HDCP_LINK0_AUTH_SUCCESS`, `DIG2_TMDS_CTL0_1_GEN_CNTL__TMDS_CTL0_DATA_SEL`, `DP3_DP_LINK_CNTL__DP_LINK_TRAINING_COMPLETE`, `DP3_DP_DPHY_CNTL__DPHY_FEC_EN`, `DP3_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE`, `DP3_DP_MSE_SAT0__DP_MSE_SAT_SRC0`, `DP3_DP_AUXLESS_ALPM_CNTL4__DP_ALPM_CURRENT_STATE`, `DIG3_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN`, and `DIG3_DIG_FIFO_CTRL0__DIG_FIFO_RESET_DONE`.

The full register name in this generated file usually includes the hardware instance number (`DIG2`, `DP3`, `DIG3`), but many display-core field tables are written against instance-zero names and expanded by macros. This is safe only when the generated register families share identical field layouts across instances. This chunk confirms that DIG2 and DIG3 have mirrored HDMI/HDCP/TMDS layouts in the covered region, and DP3 mirrors the DP0-style field names used by the DCN401 stream/link encoder tables.

## Control Flow

This header has no runtime control flow. It participates in compile-time register access setup:

1. DCN401 code includes `dcn_4_1_0_offset.h` and this shift/mask file.
2. Resource code builds register-address tables from offset macros and field tables from shift/mask macros.
3. Runtime functions call register helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_READ`; those helpers use the precomputed register addresses plus the field shifts and masks from this file.
4. Hardware state changes occur through MMIO writes to the display encoder, DP link, HDMI packet, HDCP, and TMDS registers represented by this chunk.

The important flow consequence is that a bad shift or mask changes behavior inside otherwise-correct runtime code. For example, `REG_UPDATE(HDMI_CONTROL, HDMI_DATA_SCRAMBLE_EN, 1)` depends on the HDMI control field layout in this header. If the mask/shift pair is wrong, the helper may toggle a neighboring field such as clock-channel rate, packet-generator version, error acknowledge, Dolby Vision enable, or deep-color state.

## State And Persistence

The header stores no state and persists nothing by itself. The state it describes is hardware state inside DCN display blocks:

- HDMI packet generator state, including generic packet enable/continuous mode, immediate sends, line scheduling, audio/ACR/infoframe/VBI packet transmission, GCP, AVMUTE, and double-buffer pending bits.
- DIG front-end/back-end state, including source selection, enable/soft reset, clock gates, FIFO reset/status/error, CRC/test-pattern generation, and TMDS mode/control character generation.
- DP3 link and stream state, including training status, lane count, pixel encoding/depth, MSA/VBID parameters, stream enable/disable status, TU pacing, FEC, scrambler, fast training, CRC, secondary packet generation, MST slot allocation, MSO split-stream routing, ALPM/auxless ALPM state, and link/stream symbol counters.
- HDCP state, including interrupt mask/status/ack bits, link authentication success/fail fields, receiver BKSV/AKSV/RI/PJ/AN/V' local data, Bcaps/Bstatus/Binfo, I2C request state, and deauthenticate controls.

Persistence is limited to programmed hardware registers across a mode set, link training cycle, HDCP authentication session, or low-power transition. Some fields are status or pending/acknowledge fields, so they are not simple stored configuration. Examples include HDMI generic immediate-send pending bits, HDMI double-buffer pending bits, DP stream disable interrupt/ack/mask, GSP send pending/active/deadline-missed bits, ALPM wakeup interrupt occurred/status/clear, HDCP interrupt/status bits, and FIFO/CRC status bits.

## Dependencies And Integration Points

The direct dependency is the generated AMD register-header convention shared with `dcn_4_1_0_offset.h`. Offset macros identify the register address, while the shift/mask macros in this chunk identify fields inside that address. The two headers must remain generated from the same ASIC register database.

Observed integration points include:

- `display/dc/resource/dcn401/dcn401_resource.c` includes this header and uses `BASE`, `SR`, `SRI`, and related macros to build DCN401 register tables, then initializes stream encoder, link encoder, AFMT, VPG, APG, DSC, AUX, HPD, clock, and DMUB-facing structures.
- `display/dc/dio/dcn401/dcn401_dio_stream_encoder.h` consumes many of this chunk's field names through `SE_SF(...)`, including `HDMI_CONTROL`, `DP_SEC_CNTL`, `DP_MSE_RATE_CNTL`, `DP_SEC_CNTL1/2/4/5/6`, `DP_GSP11_CNTL`, `DIG_FE_CNTL`, `DIG_FE_EN_CNTL`, `DIG_FE_CLK_CNTL`, and `DIG_FIFO_CTRL0`.
- `display/dc/dio/dcn42/dcn42_dio_link_encoder.h` and the closely related DCN35 link encoder field lists show the shared link-encoder expectations for fields such as `DIG_FE_SOURCE_SELECT`, `HDCP_SOFT_RESET`, TMDS control bits, `DP_LINK_TRAINING_COMPLETE`, `DP_SEC_GSP0_LINE_NUM`, and MSE SAT fields. DCN401 uses the same generated style for equivalent DIO blocks.
- `display/dc/dio/dcn314/dcn314_dio_stream_encoder.c` and related stream encoder implementations show runtime use of the generated fields via `REG_UPDATE`/`REG_GET` for HDMI control, DIG FIFO, DP GSP11, and DP secondary-stream enable state. DCN401 inherits the same register-helper model with generation-specific field tables.
- `display/dmub/src/dmub_dcn401.c` includes this header and uses `FD_MASK`/`FD_SHIFT` to build DMUB register metadata for DCN401. The macros in this specific chunk are mostly display-stream/link facing, but they share the same generated mask/shift namespace and compile-time contract.
- Higher-level DRM/display paths depend indirectly through modeset, link training, MST, HDMI audio/infoframe setup, HDCP handling, panel replay/ALPM, and hotplug/link services.

## Risks

The main risk is silent hardware misprogramming. The macros are compile-time constants, so a bad mask or shift can compile successfully while writes alter the wrong register bits or reads interpret the wrong status bits.

Instance drift is a concrete risk in this chunk. DIG2 and DIG3 use near-identical layouts, and DP3 must match the field-list assumptions made against DP0-style names in shared DCN stream/link encoder code. A mismatch in one instance can break only a subset of physical display outputs, making the failure look like a connector, sink, or link-training issue rather than a generated-header error.

Status, pending, and acknowledgement bits have high blast radius. Wrong masks for `*_ACK`, `*_PENDING`, `*_STATUS`, `*_INT`, `*_CLEAR`, or `*_MASK` fields can leave interrupts stuck, clear the wrong condition, spin waiting for a bit that never changes, or falsely report completion. Examples in this chunk include HDMI generic immediate-send pending bits, DP stream disable ack, DP GSP pending/active/deadline-missed fields, ALPM wakeup interrupt clear/status, HDCP I2C status, and HDCP auth success/fail.

Packet-scheduling fields are timing-sensitive. HDMI infoframes and generic packets, DP secondary packets, GSP line-number controls, ACR N/CTS values, MSE SAT updates, MSO timing, and ALPM wakeup/FEC line scheduling all rely on exact field widths. Off-by-one masks can produce malformed metadata, missed packet deadlines, missing audio, MST slot corruption, panel replay wake failures, or sink compatibility failures.

Security-related HDCP fields should not be treated as ordinary debug plumbing. Incorrect masks for receiver-port local data, key/auth state, deauthentication, and I2C request status can make HDCP fail authentication, report false success/failure, or disrupt multi-link HDCP state.

Cross-generation reuse is risky. Many field names are common across DCN 3.x, 3.5, 4.1, and 4.2, but not every bit layout is guaranteed to be identical. DCN401 code must use the DCN 4.1.0 shift/mask header paired with the matching DCN 4.1.0 offset header.

## Test Signals

Useful validation is a mix of build-time, register-table, and hardware/display behavior checks:

- Build DCN401 display and DMUB code with `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h` together. Missing or renamed macros in resource, stream encoder, link encoder, and DMUB field tables are immediate generation-contract failures.
- Add compile-time or debug assertions for representative fields: `DIG3_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN_MASK` should remain a single-bit field at bit 1, `DIG3_HDMI_CONTROL__TMDS_COLOR_FORMAT_MASK` should cover bits 13-14, `DP3_DP_LINK_CNTL__DP_LINK_TRAINING_COMPLETE_MASK` should cover bit 4, `DP3_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK` should cover bit 0, and `DIG3_DIG_FIFO_CTRL0__DIG_FIFO_RESET_DONE_MASK` should cover bit 20.
- Exercise HDMI modes through DIG2/DIG3 paths: deep color, HDMI scrambling above TMDS clock thresholds, Dolby Vision/HDR metadata where supported, audio ACR, AVI/audio/vendor infoframes, generic packets, AVMUTE, and TMDS control output. Expected signals are stable video, correct color/deep-color negotiation, no HDMI packet error interrupts, and working audio.
- Exercise DP3 link bring-up and retraining at multiple link rates/lane counts with and without FEC. Expected signals are successful link training, correct DPCD state, no stuck training/status bits, valid MSA/VBID, no DPHY CRC/test leakage, and no stream-disable interrupt hangs.
- Exercise DP secondary-packet paths: audio SDP, VSC/Adaptive-Sync/HDR/SPD packets, PPS/GSP11 for DSC-like flows, and generic GSP8-11 line scheduling. Expected signals are no GSP deadline-missed bits and correct sink-visible metadata.
- Exercise MST/MSO flows that use MSE rate, SAT allocation/status, and MSO control fields. Expected signals are correct stream mapping, no slot allocation aliasing, stable multi-stream output, and correct MSE status readback.
- Exercise ALPM, auxless ALPM, panel replay, and FEC wake transitions. Expected signals are wake interrupts at the programmed frame/line, clearable interrupt status, correct ALPM state readback, and no missed wake or black-screen resume.
- Exercise HDCP authentication and deauthentication for link0/link1-style data fields where hardware exposes them. Expected signals are correct auth success/fail status, I2C request state progression, valid local receiver-port data readback, and no stuck HDCP interrupts.
