# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 37215-39587

## Scope

This chunk is a generated AMDGPU DCN 3.0.0 register shift/mask header segment. It contains preprocessor constants only: no functions, structs, enums, storage, or executable control flow. Its exported contract is a dense set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe bit positions and already-shifted masks for display I/O hardware registers.

The range begins in the tail of `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS`, completes the remaining AUX2 GTC-sync status and PHY-wake fields, then covers full repeated DP AUX3, AUX4, and AUX5 register blocks. It then moves into DIG0-adjacent stream output blocks: `VPG0`, `AFMT0`, `DME0`, `DIG0`, HDMI/TMDS controls, and the beginning of `DP0` link, DPHY, and secondary-data-packet registers through the first fields of `DP0_DP_SEC_FRAMING4`.

## Purpose

The purpose of this file chunk is to bind DCN 3.0.0 symbolic register-field names to the ASIC-specific bit layout used by AMD display code. Consumers include the matching `dcn_3_0_0_offset.h` address header and this shift/mask header, then use register-helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SRI`, and `SE_SF` to paste register and field names into address, shift, and mask tables.

The covered hardware areas are:

- AUX channel engines for DP AUX instances 3, 4, and 5, plus the end of AUX2. These implement software AUX transactions, link-service status, AUX data windows, DPHY timing/status, GTC sync, interrupts, arbitration between software and DMCU/DMUB-style clients, HPD-sensitive behavior, and PHY wake handshakes.
- VPG0, the video packet generator for generic secondary-data packets, ISRC data, MPEG info, per-packet frame/immediate update triggers, pending bits, conflict status, and memory-power state.
- AFMT0, the audio formatter, including HDMI audio packet limits, audio layout/channel/HBR controls, audio infoframe fields, IEC 60958 channel-status bits, audio CRC/test-ramp controls, audio enable/HBR/FIFO status, source selection, and memory power.
- DME0, the dynamic metadata engine, with metadata stream enable/source selection, double-buffer state, and memory-power fields.
- DIG0 front-end/backend-facing controls for source selection, stream start, Dolby Vision enable/status, CRC, test patterns, FIFO calibration/status, HDMI metadata/audio/infoframe/generic packet transmission, general-control packet state, ACR timing packet controls, TMDS lane/control-symbol generation, lane enable, and force-disable.
- DP0 link and stream encoding controls for link training complete/status, pixel format, DP MSA fields, video stream enable/defer/status, steer/TU FIFO overflow reporting, video timing M/N generation, DPHY training/test/scrambler/CRC/fast-training controls, and DP secondary packet stream/audio/GSP framing controls.

Although the repository path is under `sources/distributed-fs/ceph-client`, this chunk is AMDGPU display hardware metadata. It has no Ceph, filesystem, distributed storage, or network protocol behavior.

## Important APIs, Types, And Macros

There are no callable APIs or C types defined here. The important interface is the generated macro namespace:

- `*_SHIFT` gives the field's low bit.
- `*_MASK` gives the field mask in its register position.
- Comment lines such as `//DP_AUX3_AUX_CONTROL` and `// addressBlock: ...` group the macros by hardware register and register block.

The AUX3/AUX4/AUX5 groups are structurally repeated. Each instance defines:

- `AUX_CONTROL`: `AUX_EN`, `AUX_RESET`, `AUX_RESET_DONE`, link-service read/update gates, `AUX_IGNORE_HPD_DISCON`, mode detect, HPD select, impedance-calibration request enable, test mode, deglitch enable, and spare high bits.
- `AUX_SW_CONTROL`: software transaction launch via `AUX_SW_GO`, link-service read trigger, start delay, and write-byte count.
- `AUX_ARB_CONTROL`: AUX register arbitration priority, owner/status bits, queued-go suppression, software request/done bits, and DMCU request/done aliases.
- `AUX_INTERRUPT_CONTROL`: SW done, LS done, GTC sync lock-done, and GTC sync error interrupt/ack/mask triplets.
- `AUX_SW_STATUS` and `AUX_LS_STATUS`: done/request state, timeout state, timeout/overflow/HPD disconnect/non-AUX-mode/invalid framing errors, reply byte count, arbitration state for SW, CP IRQ and updated/ack bits for LS.
- `AUX_SW_DATA` and `AUX_LS_DATA`: 8-bit data windows, 5-bit indexes, read/write direction for SW, and SW autoincrement disable.
- `AUX_DPHY_TX_REF_CONTROL`, `AUX_DPHY_TX_CONTROL`, `AUX_DPHY_RX_CONTROL0`, `AUX_DPHY_RX_CONTROL1`, `AUX_DPHY_TX_STATUS`, and `AUX_DPHY_RX_STATUS`: reference selection/dividers, TX precharge/OE timing, RX windows and thresholds, timeout length/multiplier, TX/RX state, and measured half-symbol periods.
- `AUX_GTC_SYNC_CONTROL`, `AUX_GTC_SYNC_ERROR_CONTROL`, `AUX_GTC_SYNC_CONTROLLER_STATUS`, and `AUX_GTC_SYNC_STATUS`: GTC sync enable, impedance calibration, acquisition/maintenance periods, block requests, retry/threshold controls, lock/error state, ACK bits, AUX transaction-style receive errors, reply byte count, NACK, and master request reporting.
- `AUX_PHY_WAKE_CNTL`: wake go, pending, priority, and ack fields.

The VPG0 group defines byte-indexed packet payload access (`VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG_GENERIC_PACKET_DATA`), frame and immediate update controls for generic packets 0-14, pending mirrors, generic lock/conflict status, memory power state, ISRC1/2 indexed data access, and MPEG infoframe payload/update fields.

The AFMT0 group defines audio and protocol-visible fields: HDMI audio packets per line and max-packet behavior, audio layout override/select, channel-enable bitmap, DP audio stream ID, HBR and 60958 overrides, audio infoframe checksum/channel-count/coding-type/extended-coding/channel-allocation/level-shift/downmix/LFE fields, IEC 60958 channel-status and validity fields, audio CRC controls/results, ramp test controls, audio FIFO overflow and enable-change ACKs, infoframe update/source, source select, and memory-power state.

The DIG0 and HDMI/TMDS groups define front-end start/source routing, output CRC, clock/static/random test patterns, FIFO calibration state, HDMI metadata packet control, HDMI 2.0-style scramble/deep-color/clock-channel controls, HDMI error and AVMUTE/audio/VBI/infoframe/ACR controls, generic packet send/continuous/line-reference/update-lock bits for packets 0-14, immediate send and pending bits, generic packet line registers, double-buffer pending bits, general control packet phase/AVMUTE fields, TMDS control characters/sync patterns/control bits/DC balancing, per-control-symbol data-select/delay/invert/modulation/feedback/pattern fields, DIG version, lane enable, and force-disable.

The DP0 portion defines the first stream/link fields for link training and embedded-panel mode, pixel encoding/depth/combine, MSA colorimetry/misc bytes, DP lane count, video stream enable/deferred disable/status, steer/TU FIFO overflow/reset/ack/mask fields, video M/N timing and values, link framing/idle/VBID/enhanced-frame controls, HBR2 eye pattern enable, MSA/VBID location and field polarity, video-disable interrupt/ack/mask fields, DPHY test lanes/FEC/bypass/skew, DPHY training pattern and custom 10-bit symbols, 8b/10b reset/disparity fields, PRBS and scrambler controls, DPHY CRC and MST CRC controls/status, fast-training controls/status, and the start of DP secondary packet controls (`DP_SEC_CNTL`, `DP_SEC_CNTL1`, `DP_SEC_FRAMING1-4`).

## Control Flow

This header has no local control flow. Runtime behavior is created by display code that includes this generated namespace and passes the masks/shifts into register-helper tables.

The main consumption pattern is:

1. DCN 3.0/3.0.2 source includes `dcn/dcn_3_0_0_offset.h` and `dcn/dcn_3_0_0_sh_mask.h`.
2. Register-list macros such as `SRI(AFMT_CNTL, DIG, id)` or `SRI(DP_SEC_CNTL, DP, id)` resolve the correct instance-specific register addresses from the offset header.
3. Field-list macros such as `SE_SF(DP0_DP_SEC_CNTL, DP_SEC_STREAM_ENABLE, mask_sh)` or `AUX_SF(DP_AUX0_AUX_CONTROL, AUX_EN, mask_sh)` paste generated `__SHIFT`/`_MASK` names into shift/mask structures.
4. Driver methods call `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET`, `REG_GET`, `REG_WAIT`, or `REG_READ/WRITE`; those helpers use this chunk's constants to isolate and encode bitfields.

For AUX, the operational sequencing lives in `display/dc/dce/dce_aux.c`: code checks arbitration state, enables/reset AUX, requests software ownership, writes AUX transaction bytes through `AUX_SW_DATA`, launches `AUX_SW_GO`, polls/acks `AUX_SW_DONE`, decodes reply byte counts, and releases ownership through `AUX_ARB_CONTROL`. This chunk provides the per-instance bit layout for those operations on later AUX instances, but it does not implement the transaction state machine.

For stream encoding, `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` and `.c` are representative consumers. The header maps many fields from this chunk into `SE_COMMON_MASK_SH_LIST_DCN30`, including HDMI generic packet controls, `DP_SEC_CNTL`, `DP_SEC_CNTL1`, `DP_SEC_FRAMING4`, `DIG_FE_CNTL`, `DIG_FIFO_STATUS`, `DP_PIXEL_FORMAT`, `DP_VID_STREAM_CNTL`, `DP_VID_TIMING`, `DP_SEC_AUD_N`, `DP_SEC_TIMESTAMP`, and DME metadata controls. The `.c` file then updates HDMI generic packet send/continuous/line registers, DP GSP enable bits, DP secondary stream master enable, HDMI scrambling/deep-color/ACR/VBI/audio-infoframe controls, FIFO reset via `DIG_START`, and DP audio timestamp/N configuration.

For DP link encoding, `display/dc/dio/dcn10/dcn10_link_encoder.h` and `.c` show the shared lower-level DP consumption pattern. Link encoder methods use the DP0 DPHY symbols, PRBS, scrambler, training pattern, link framing, link-training complete, and secondary-packet fields to program test patterns, link training state, MST allocation, PSR fast training, and DP PHY behavior.

## State And Persistence Behavior

The header stores no state and persists nothing. It describes MMIO register state in the DCN display hardware. That state is owned by the display engine, AUX PHY/controller logic, stream encoders, audio formatter, packet generators, metadata engine, power-management logic, firmware-facing display microcontroller paths, and reset/suspend/resume flows.

State represented by this chunk includes:

- AUX controller configuration, ownership, software/link-service transaction progress, indexed data windows, interrupt latches and ACK bits, DPHY timing configuration/status, GTC sync lock/error status, and PHY wake handshakes for AUX2 tail and AUX3-AUX5.
- VPG packet payload storage and update state, including pending frame/immediate updates for generic packets 0-14 and memory power state for packet storage.
- AFMT audio packet configuration, audio infoframe and IEC 60958 metadata, channel enable/layout/HBR state, audio CRC and test-ramp state, FIFO overflow latches, audio enable-change status, and AFMT memory power.
- DME metadata requestor/stream-type/enable and double-buffer pending/taken/clear/disable state, plus DME memory power state.
- DIG/HDMI/TMDS state for source routing, stream start/reset, Dolby Vision enable/missed status, FIFO calibration/error state, HDMI metadata and generic packet scheduling, HDMI error/AVMUTE/deep-color/scrambling/ACR/audio/VBI/infoframe state, TMDS symbol/control generation, lane enables, and forced DIG disable.
- DP link/stream state for link training completion, stream enable/deferred disable, MSA bytes, M/N timing values, FIFO overflow flags, DPHY training/test/FEC/scrambler/CRC/fast-training status, DP secondary stream master enable, GSP enables, GSP0 line/send/pending/deadline fields, secondary-packet framing windows, collision status/ACK, and audio mute status.

Some fields are configuration latches, some are live readback, some are write-one-to-clear or ACK-style bits, and some are double-buffer pending indicators. The generated names and masks do not encode access type or ordering requirements. Incorrect writes can persist until a modeset, link retrain, hotplug, display stream reprogramming, power transition, suspend/resume restore, or GPU/display reset rewrites the block.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the matching register addresses and base indices. In that header, the DP0 block in this chunk maps to addresses such as `mmDP0_DP_LINK_CNTL` at `0x2108`, `mmDP0_DP_DPHY_CNTL` at `0x2117`, `mmDP0_DP_SEC_CNTL` at `0x212b`, and `mmDP0_DP_SEC_FRAMING4` at `0x2130`, all with base index 2. The offset file continues beyond this chunk with later DP0 secondary, MST, DSC, metadata, ALPM, and GSP registers whose masks appear in later chunks.

Visible include sites for `dcn_3_0_0_sh_mask.h` in this tree include:

- `display/dc/resource/dcn30/dcn30_resource.c`, which builds DCN 3.0 resource objects and register tables.
- `display/dc/irq/dcn30/irq_service_dcn30.c` and `display/dc/irq/dcn302/irq_service_dcn302.c`, which use generated masks for IRQ source/status/ack programming.
- `display/dc/gpio/dcn30/hw_factory_dcn30.c` and `display/dc/gpio/dcn30/hw_translate_dcn30.c`, which use the same generated register namespace for GPIO/HPD/DDC translation.
- `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, which includes DCN 3.0 register metadata for display clock manager programming.
- `display/dmub/src/dmub_dcn30.c` and `display/dmub/src/dmub_dcn302.c`, which expose DCN 3.0/3.0.2 register metadata to DMUB-facing support.

Functional integration points include `display/dc/dce/dce_aux.*` for AUX transaction state, `display/dc/dio/dcn30/dcn30_dio_stream_encoder.*` for HDMI/DP stream packet/audio/metadata programming, `display/dc/dio/dcn10/dcn10_link_encoder.*` for DP PHY/link training and MST-related programming, `display/dc/dio/dcn30/dcn30_vpg.*` for VPG packet payload/update paths, and `display/dc/dio/dcn30/dcn30_afmt.*` for AFMT audio formatter control.

Direct textual references to every exact `DP_AUX3_`, `DP_AUX4_`, or `DP_AUX5_` macro are uncommon because register tables usually instantiate a generic AUX object with an instance ID. Macro pasting converts a generic field like `AUX_SW_GO` into the correct generated `DP_AUXn_AUX_SW_CONTROL__AUX_SW_GO_*` constants.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong shift or mask usually still compiles; it can update the wrong bit, truncate a value, fail to clear an ACK bit, decode stale status, or corrupt adjacent fields during read/modify/write.

AUX fields are timing- and ownership-sensitive. Bad arbitration masks can let software and firmware contend for the same AUX registers. Bad `AUX_SW_DATA` index/data masks can corrupt DP AUX payload bytes or addresses. Bad status/error masks can cause false timeouts, missed HPD disconnects, undetected invalid replies, or loops waiting on the wrong done bit. GTC sync status includes sticky error and ACK fields; confusing status bits with ACK bits can hide lock-loss or critical error conditions.

Repeated AUX3/AUX4/AUX5 layouts are easy to copy incorrectly. If one instance's mask diverges accidentally, only connectors wired to that AUX instance may fail, making the bug appear board- or port-specific.

Packet scheduling fields are dense. VPG and HDMI generic packet controls pack many send/continuous/update/pending bits into one register. Off-by-one shifts can make the driver enable the wrong packet index, use the wrong line number, leave update locks disabled, or wait on another packet's pending bit. That can break HDR metadata, VSC/SPD/adaptive-sync packets, ISRC/MPEG packets, or HDMI vendor-specific packets without breaking basic modeset.

AFMT and HDMI audio fields are protocol-visible. Incorrect channel-count, channel-allocation, IEC 60958, HBR, ACR, or audio-packet fields can produce missing HDMI/DP audio, wrong speaker mapping, broken HBR/non-PCM playback, audio FIFO overflow, invalid CRC/test results, or audio that only fails at specific sample rates/deep-color modes.

DIG/HDMI/TMDS fields can affect visible video. Bad `DIG_START`, source-select, lane-enable, TMDS control-symbol, scrambling, deep-color, FIFO, or force-disable fields can cause blank screens, unstable links, color/deep-color mismatches, HDMI 2.0 scrambling failures above 340 MHz, or hard-to-reproduce FIFO underflow/overflow symptoms.

DP DPHY and link fields are link-training sensitive. Wrong masks for training patterns, PRBS, scrambler, 8b/10b, FEC, fast training, link-training complete, M/N timing, or steer FIFO status can cause link training failure, PSR/fast-training regressions, MST timing problems, CRC validation failures, or invalid custom PHY test patterns.

Chunk boundaries matter. This chunk starts after the beginning of the AUX2 GTC sync controller status register, so the full AUX2 GTC sync field set is split across chunks. It also ends inside `DP0_DP_SEC_FRAMING4`; the final masks for `DP_SEC_AUDIO_MUTE` and `DP_SEC_AUDIO_MUTE_STATUS`, plus later DP0 secondary/MST/DSC/metadata fields, are in following chunks. Per-file reconciliation should merge adjacent chunks before drawing complete-register conclusions.

## Test Signals

Useful validation is mostly generated-header and hardware-behavior oriented:

- Compile coverage for all DCN 3.0 and DCN 3.0.2 files that include `dcn_3_0_0_sh_mask.h`, especially resource, IRQ, GPIO, clock manager, DMUB, AUX, stream encoder, link encoder, VPG, and AFMT paths.
- Generated-header consistency checks that each `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, that the mask width/position agrees with the shift, and that each register in this chunk has a matching offset/base index in `dcn_3_0_0_offset.h`.
- Cross-generation diffs against neighboring DCN headers, reviewed against the ASIC register database, for repeated AUX blocks, HDMI generic packet controls, AFMT audio fields, DP DPHY fields, and DP secondary packet controls.
- AUX functional tests for DPCD reads/writes, I2C-over-AUX EDID reads, reply-byte counts, timeout/defer/NACK handling, HPD disconnect during AUX, CP IRQ/update handling, suspend/resume, and ports wired to AUX3/AUX4/AUX5.
- HDMI and DP modeset tests covering RGB/YCbCr formats, deep color, HDMI scrambling above and below 340 MHz, audio enable/disable, AVMUTE, ACR packets, audio infoframes, HDR/static metadata, vendor-specific packets, and generic packet immediate/frame updates.
- DP link tests for link training, custom/test patterns, PRBS, scrambler, FEC status, enhanced framing, MSA/M/N values, MST allocation, PSR fast training, stream disable/defer, and DPHY/MST CRC reporting.
- Audio tests for stereo and multichannel layouts, HBR/non-PCM formats, sample-rate changes, channel allocation, IEC 60958 channel status, FIFO overflow handling, audio mute/status, and suspend/resume restore.
- Power-management tests that exercise VPG/AFMT/DME memory-power fields and verify packet/audio/metadata state is restored after light sleep, display power gating, and DCN reset paths.

Regression symptoms from bad constants include AUX timeouts or invalid replies on only some ports, missing EDID/DPCD reads, blank HDMI/DP output, bad color depth or HDMI scrambling, missing HDR/adaptive-sync/info packets, no or incorrectly mapped audio, audio FIFO overflows, failed DP link training, PSR fast-training failures, MST allocation errors, stale packet pending bits, or unexpected interrupt storms/missed ACKs.

## Cross-Chunk Notes

This chunk is one slice of the generated DCN 3.0.0 register-layout contract. The previous chunk owns the beginning of `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS`; this chunk completes AUX2 tail state and adds complete AUX3-AUX5 blocks. The next chunk should complete `DP0_DP_SEC_FRAMING4` and continue through additional DP0 secondary/MST/DSC/metadata registers. The final per-file document should treat this chunk as part of the DCN 3.0 display I/O register namespace, not as an independently maintained module.
