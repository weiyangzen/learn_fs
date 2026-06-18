# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 34985-37380

## Scope

This chunk is a generated-register slice of AMDGPU's DCN 3.6.0 shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, includes, locking, allocation, or executable control flow. The exported contract is the standard generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace used by AMD display register-helper code to pack and unpack MMIO fields.

The range starts in the middle of the `DP2_DP_DPHY_FAST_TRAINING` register fields, covers the rest of the DP2 DisplayPort encoder block, then covers the full `dce_dc_dio_dig2_dispdec` DIG/HDMI/TMDS block, most of the `dce_dc_dio_dp3_dispdec` DP3 DisplayPort encoder block, and ends at the start of the `dce_dc_dio_dig3_dispdec` DIG3 FIFO fields. In this exact range there are 2,171 `#define` entries: about 668 `DP2_*`, 590 `DIG2_*`, 838 `DP3_*`, and 75 `DIG3_*` macros.

Although the source tree path is under a local `ceph-client` mirror, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this header range is to provide DCN 3.6.0 bit geometry for DisplayPort and DIG/HDMI/TMDS encoder programming. Runtime AMD display code combines these masks and shifts with the matching `dcn_3_6_0_offset.h` register offsets, builds per-ASIC register tables, and uses generic helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to touch only the intended hardware bits.

The covered hardware areas are:

- DP2 tail fields for fast link training, secondary-data-packet transmission, MST payload-slot allocation, main-stream-attribute timing, MSO/DSC, generic secondary packets, double-buffering, VBID/misc metadata, ALPM and auxless ALPM, and stream/link symbol counters.
- DIG2 front-end, HDMI, audio formatter, back-end, and TMDS fields, including clock/reset/enable, output CRC, test patterns, FIFO calibration, HDMI metadata packets, HDMI control/status, audio clock regeneration, VBI/infoframe/generic-packet scheduling, HDMI double buffering, audio clock-regeneration readback, TMDS control characters, DC balancing, and `DIG_VERSION`.
- DP3 fields from the beginning of the DP3 block through the same DP secondary-packet, MSE/MST, MSO/DSC, ALPM, and symbol-counter groups covered for DP2, plus earlier DP3 link/video/DPHY controls that are outside the DP2 tail in this chunk.
- DIG3 beginning fields for front-end clock/source selection, enable, output CRC, test pattern generation, random-pattern seed, and the start of FIFO control.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro pattern:

- `*_SHIFT` gives a field's least-significant bit position.
- `*_MASK` gives the already-shifted mask used for read/modify/write or readback extraction.

The DP2 and DP3 secondary-data-packet groups define fields for `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `DP_SEC_CNTL7`, `DP_SEC_FRAMING*`, `DP_SEC_PACKET_CNTL`, `DP_SEC_METADATA_TRANSMISSION`, `DP_GSP8_CNTL` through `DP_GSP11_CNTL`, and `DP_GSP_EN_DB_STATUS`. These fields control enable bits for audio stream packets, ASP/ATP/AIP/ACM packets, GSP0-GSP11 packets, MPG/ISRC/PPS use, packet line references, send and pending/deadline status, double-buffer-disable bits, and DB pending readbacks.

The DP2 and DP3 MSE/MST groups define `DP_MSE_RATE_CNTL`, `DP_MSE_RATE_UPDATE`, `DP_MSE_SAT0` through `DP_MSE_SAT2`, matching `*_STATUS` readbacks, `DP_MSE_LINK_TIMING`, and `DP_MSE_MISC_CNTL`. They describe stream-source selection, encryption enable/type, slot counts, update triggering/pending state, link timing, and miscellaneous MST behavior. `DP_MSO_CNTL` and `DP_MSO_CNTL1` extend secondary-packet enables across multiple SST links for MSO use, while `DP_DSC_CNTL` exposes DSC mode selection.

The DP timing and link-status groups include `DP_MSA_TIMING_PARAM1` through `PARAM4`, `DP_MSA_VBID_MISC`, and, for DP3, `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_MSA_MISC`, `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, `DP_LINK_FRAMING_CNTL`, `DP_VID_MSA_VBID`, and `DP_VID_INTERRUPT_CNTL`. These fields encode MSA totals/start/sync/active-size values, VBID and misc bytes, pixel encoding/depth, lane count, stream enable/status, FIFO overflow/TU size, M/N generation, enhanced framing, and stream-disable interrupt ack/mask bits.

The DP3 DPHY groups include internal scrambler reset, FEC enable/ready/active and ALPM disable behavior, training pattern selection, 10-bit symbol fields, 8b/10b running-disparity controls, PRBS controls, scrambler controls, CRC control/result/status registers, and fast-training control/status fields. The DP2 part of this chunk starts after most comparable DPHY fields and only includes the tail of fast-training plus CRC result 2/3.

The ALPM groups are present for both DP2 and DP3. `DP_ALPM_CNTL` covers panel replay/ALPM-like enable, PHY sleep/repeat/delay, AUX wake enable, status, power-up PHY display-count, and update-pending bits. `DP_AUXLESS_ALPM_CNTL1` through `CNTL5` describe auxless sleep timing, wakeup send/immediate/pending bits, FEC-enable timing, line numbers, hardware-mode state, force-wakeup, frame counters, and wakeup interrupt mask/status/clear/frame/line fields.

The DIG2 and DIG3 front-end groups define `DIG_FE_CNTL`, `DIG_FE_CLK_CNTL`, `DIG_FE_EN_CNTL`, output CRC control/result, clock/test/random-pattern controls, and FIFO control/calibration fields. These macros select timing-generator source, stereosync, digital bypass, split-link grouping, input pixel select, front-end mode/clock/reset/gating, CRC source/link/data selection, deterministic or random output test patterns, FIFO reset/read level/read clock/output pixel mode, FIFO error, overwrite/calibration/min/max level, and recalibration controls. DIG3 is only partially covered, ending after the first `DIG3_DIG_FIFO_CTRL1` fields.

The DIG2 HDMI groups cover `HDMI_METADATA_PACKET_CONTROL`, `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_PACKET_CONTROL`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL0/1`, `HDMI_GENERIC_PACKET_CONTROL0/1/2/3/4/5/6/7/8/9/10`, `HDMI_GC`, `HDMI_DB_CONTROL`, `HDMI_ACR_*`, and `AFMT_CNTL`. They define packet enable/send/line/continue behavior for many generic packet slots, immediate-send and pending bits, double-buffer pending/taken/lock/disable state, keepout and scrambling controls, HDMI error ack/mask/status, Dolby Vision metadata status, TMDS encoding/deep color fields, ACR source/auto-send/CTS/N behavior, VBI enable/status, and audio clock gate/readback fields.

The DIG2 TMDS groups define back-end clock/control/enable fields and TMDS-specific controls: color depth, 8b/10b bypass, control characters, feedback, stereosync control selection, sync-character patterns, control-bit mappings, DC balancer enable/test/status, sync DC-balance character, and control-character generator fields for CTL0/1 and CTL2/3.

## Control Flow

This header range has no local runtime control flow. Runtime behavior is created by consumers that include the DCN 3.6.0 offset and shift/mask headers and expand register-list macros into register tables.

A typical path is:

1. DCN36 resource, IRQ, DMUB, DIO, stream-encoder, and link-encoder code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list macros paste logical register names onto generated instance names such as `DP2_DP_SEC_CNTL`, `DP3_DP_MSE_SAT_UPDATE`, `DIG2_HDMI_GENERIC_PACKET_CONTROL0`, or `DIG3_DIG_FE_CNTL`.
3. Field macros paste logical field names onto `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
4. Runtime register helpers perform MMIO reads/writes and read/modify/write updates using the generated offset, mask, and shift tables.

The header does not encode sequencing. Callers must still follow hardware ordering for link training, stream enable/disable, MST payload updates, secondary-packet scheduling, HDMI packet double-buffering, TMDS/HDMI mode switches, audio clock regeneration, ALPM/auxless wake transitions, interrupt ack/mask handling, FIFO reset/calibration, and suspend/resume restore.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It describes DCN 3.6.0 hardware register state whose lifetime is controlled by modesets, link training, hotplug, stream enable/disable, MST topology changes, power gating, suspend/resume, and GPU reset.

State represented by this chunk includes:

- DP stream and link state: stream enable/status, pixel format/depth, lane count, M/N timing, MSA timing/misc/VBID fields, link training completion, DPHY training pattern/symbol/scrambler/FEC/CRC/PRBS state, fast-training completion, and stream/link symbol counters.
- DP secondary-packet state: stream/audio packet enables, GSP0-GSP11 scheduling, send/pending/deadline status, line-number targeting, packet framing windows, metadata transmission, double-buffer disable/pending state, collision/audio mute status, and MPG/ISRC/PPS controls.
- MST/MSO/DSC state: MSE rate update, stream-to-slot allocation, slot counts, encryption bits, status readbacks, link timing, MSO per-link secondary packet enables, and DSC mode.
- ALPM state: AUX wake enable/status, PHY sleep/wake timing, auxless wake/FEC line scheduling, hardware-mode enable/status, current state, wakeup interrupts, and update-pending/readback bits.
- DIG/HDMI/TMDS state: front-end source and clock/reset/enable state, FIFO level/calibration/error state, output CRC and test-pattern state, HDMI packet scheduling and double buffering, HDMI control/status/error state, audio clock regeneration values, AFMT audio clock state, TMDS color/control/DC-balance state, and DIG version readback.

Persistence is hardware-defined. Many configuration fields remain active until the relevant stream, link, encoder, or power domain is reprogrammed or reset. Status bits can be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the relevant clock is active. The generated masks do not state access semantics, so consuming code and ASIC documentation must determine whether a field is safe to write, poll, clear, or preserve.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`, which provides matching register offsets. These mask/shift constants are correct only when paired with the DCN 3.6.0 register database and offset header.

Visible integration points in this tree include:

- `display/dc/resource/dcn36/dcn36_resource.c`, which includes the DCN 3.6.0 generated headers and expands DCN36 register and mask/shift lists while constructing the DCN36 resource pool.
- `display/dc/irq/dcn36/irq_service_dcn36.c`, which includes the same generated headers for DCN36 IRQ source metadata.
- `display/dmub/src/dmub_dcn36.c` and `display/dmub/src/dmub_dcn36.h`, where DCN36 DMUB register initialization binds firmware-service register offsets and field masks/shifts.
- Common stream-encoder code under `display/dc/dce/dce_stream_encoder.*`, which uses `DIG_FE_CNTL`, `DP_SEC_CNTL`, HDMI generic-packet controls, HDMI ACR/control/status fields, AFMT, and related field names through generated tables.
- Common link-encoder code under `display/dc/dce/dce_link_encoder.*`, which uses `DP_LINK_CNTL`, `DP_MSE_SAT*`, `DP_MSE_SAT_UPDATE`, `DP_SEC_CNTL`, and `DP_SEC_CNTL1` for link training completion, MST slot programming, and secondary-packet control.
- DIO stream-encoder code under `display/dc/dio/dcn32/`, which demonstrates later-generation use of `DIG_FE_CNTL` and `DP_SEC_CNTL` fields for clock/status and secondary-stream enable handling; DCN36 inherits the same generated-header pattern with ASIC-specific constants.

These macros are cross-generation in shape but not interchangeable. Similar names appear in DCN 3.5.x, 3.2.x, and later DCN headers, but field presence, exact masks, offsets, and instance counts may differ.

## Risks And Edge Cases

- Shift/mask constants are untyped preprocessor values. A wrong value can compile cleanly while writing an adjacent MMIO bit, truncating a field, decoding a status incorrectly, or leaving stale bits behind.
- The chunk starts and ends on artificial boundaries. It begins after the `DP2_DP_DPHY_FAST_TRAINING` comment and initial fields from the previous lines, and it ends in the middle of `DIG3_DIG_FIFO_CTRL1`; adjacent chunks are required before making complete claims about those registers.
- DP2 and DP3 are highly repetitive but not identical in this range. DP3 includes full link/video/DPHY setup from `DP_LINK_CNTL` onward, while DP2 is only the tail of its block. Copying conclusions or masks between instances without checking the generated names can hide instance-specific omissions.
- MST payload fields are sequencing-sensitive. Incorrect `DP_MSE_SAT*`, status, or update masks can produce wrong slot allocations, stuck update-pending state, bandwidth accounting errors, or failures that only appear with MST hubs and multiple streams.
- Secondary packet fields are display-protocol-sensitive. Bad GSP, infoframe, metadata, PPS, audio, MPG, or ISRC masks can cause missing HDR/VRR/DSC metadata, wrong audio packets, stale packets after modeset, deadline misses, or packet collision status that never clears.
- HDMI double-buffer fields can be side-effect-sensitive. Confusing pending, taken, clear, lock, and disable bits can leave packet programming stale, produce one-frame glitches, or make updates race vblank/vupdate timing.
- ALPM and auxless ALPM fields interact with PHY sleep/wake and FEC timing. Bad masks can cause wake failures, excessive power use, link instability, FEC transition problems, or wakeup interrupts that are missed or storming.
- DPHY and TMDS controls affect physical link behavior. Errors in scrambler, FEC, training pattern, 8b/10b, PRBS, DC balancer, color depth, or control-character fields can create blank displays, link-training failures, receiver-specific HDMI/DP failures, or intermittent corruption.
- Status/ack/mask naming is easy to confuse. Many fields have paired `*_STATUS`, `*_ACK`, `*_MASK`, `*_PENDING`, and `*_OCCURRED` names; using a mask constant for the wrong semantic can wedge interrupts or clear diagnostics unexpectedly.

## Test Signals

Useful validation combines generated-header consistency, build coverage, and hardware behavior:

- Build AMDGPU display with DCN36 enabled. Missing or renamed macros should fail in DCN36 resource construction, IRQ service, DMUB register initialization, stream encoder, or link encoder register-table expansion.
- Mechanically verify that every complete field in lines 34985-37380 has the expected `__SHIFT` and `_MASK` pair, while treating the first and last register groups as chunk-boundary partials.
- Diff this range against AMD's authoritative DCN 3.6.0 register database and nearby generated headers such as DCN 3.5.x or later DCN variants, with expected per-generation differences reviewed instead of blindly normalized.
- Exercise DisplayPort link training, stream enable/disable, pixel format/depth changes, M/N timing, CRC capture, PRBS/test patterns, FEC enable/disable, and fast-training status on DCN36 hardware.
- Test MST topologies with multiple streams, payload slot reallocation, hotplug/unplug, suspend/resume, DSC streams, and MSO cases; watch for stuck `DP_MSE_RATE_UPDATE`, wrong slot counts, or stream-to-slot mapping errors.
- Exercise DP secondary packets for audio, VSC, SPD, HDR static metadata, DSC PPS, ISRC/MPG, and generic GSP8-GSP11 packets across modeset, vblank-timed send, immediate send, and double-buffer updates.
- Exercise HDMI output with scrambling, deep color, Dolby Vision metadata status, VBI/infoframes, generic packets 0-14, metadata-packet missed status, ACR CTS/N values for 32/44.1/48 kHz families, and audio stream enable/disable.
- Validate TMDS behavior across 8b/10b bypass, color depth changes, control-character generation, DC balancer state, stereo sync, and receiver hotplug.
- Test ALPM and auxless ALPM with panel/link idle, forced wakeup, FEC wake scheduling, hardware-mode transitions, wakeup interrupts, and resume from suspend.
- Watch kernel logs, display diagnostics, and hardware status for link-training failures, blank output, packet deadline missed bits, HDMI DB pending stuck high, metadata-packet missed bits, FIFO error/overflow, CRC mismatches, audio loss, MST bandwidth failures, wakeup interrupt storms, and failures that appear only on DP2/DP3 or DIG2/DIG3 instances.

## Cross-Chunk Notes

This is not a standalone source module. It is one generated slice inside `dcn_3_6_0_sh_mask.h`. The preceding chunk owns the earlier DP2 DPHY fields and the beginning of `DP2_DP_DPHY_FAST_TRAINING`; this chunk owns the DP2 tail, full DIG2 block, most of the DP3 block, and the start of DIG3. The following chunk continues `DIG3_DIG_FIFO_CTRL1` and later DIG3 HDMI/TMDS/register groups. The merge/reconciliation lane should combine adjacent chunks before making whole-file claims about all DCN 3.6.0 DIO/DIG/DP register fields.
