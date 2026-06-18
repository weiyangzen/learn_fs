# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 27396-29755

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask table for display I/O hardware. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DC display performance monitoring, DisplayPort AUX controllers, Video Packet Generator (VPG), Audio Formatter (AFMT), Display Metadata Engine (DME), and the first part of digital stream encoder (`DIG0`) HDMI/TMDS registers.

There are no executable functions, structs, or runtime branches in this slice. The exported surface is compile-time field metadata used by AMD display register helper macros. The companion `dcn_3_0_1_offset.h` header provides register addresses such as `mmDP_AUX0_AUX_CONTROL`, `mmVPG0_VPG_GENERIC_PACKET_DATA`, `mmAFMT0_AFMT_VBI_PACKET_CONTROL`, `mmDME0_DME_CONTROL`, and `mmDIG0_HDMI_CONTROL`; this header supplies the matching bit layout, for example `DP_AUX0_AUX_CONTROL__AUX_RESET__SHIFT` and `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK`.

The requested range contains 2,360 source lines with 2,175 `#define` entries, 8 address-block comments, and 161 register delimiter comments. It starts in the tail of `DC_PERFMON16_PERFCOUNTER_CNTL2`, covers complete `DP_AUX0` through `DP_AUX3` AUX field blocks, covers `VPG0`, `AFMT0`, and `DME0`, and ends inside `DIG0_TMDS_DCBALANCER_CONTROL` after the first three shift definitions. The surrounding lines before and after this chunk own the rest of those two partial edge registers.

## Register Blocks Covered

`DC_PERFMON16` is present as a tail from the previous address block. The chunk begins with three masks for `DC_PERFMON16_PERFCOUNTER_CNTL2`, then covers `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`. These fields describe performance-counter state selection, report counts, count-off interrupt enable/status/acknowledge bits, selected readback halves, and low/high counter value storage.

`DP_AUX0`, `DP_AUX1`, `DP_AUX2`, and `DP_AUX3` are replicated under `dce_dc_dio_dp_aux[0-3]_dispdec`. Each instance exposes the same AUX controller register layout: enable/reset, low-speed read, HPD selection, impedance calibration request, test/deglitch control, software transaction control, register arbitration between software and DMCU, interrupt status/ack/mask fields, software and low-speed status/data FIFOs, DPHY TX/RX configuration and status, GTC sync control/status/error tracking, and PHY wake control.

`VPG0` under `dce_dc_dio_dig0_vpg_vpg_dispdec` covers generic packet access and data staging, frame-update and immediate-update controls for generic packets 0 through 14, generic packet conflict status/clear, memory power control, ISRC packet access/data, and MPEG info packet words. This is the packet-generation side used to stage secondary data packets before sending them through the stream encoder.

`AFMT0` under `dce_dc_dio_dig0_afmt_afmt_dispdec` covers audio and infoframe formatting registers. The fields include VBI packet control, HDMI audio packet rate limits, audio infoframe words, IEC 60958 channel status words, audio CRC control/result, ramp controls, AFMT status, audio sample send/control, infoframe update, interrupt status, audio source select, and AFMT memory power.

`DME0` under `dce_dc_dio_dig0_dme_dme_dispdec` covers metadata engine enablement, HUBP requestor selection, stream type, double-buffer pending/taken/clear/disable state, transmission-missed status/clear, and memory power controls. It integrates the display metadata path with the stream encoder and DP/HDMI metadata transmission registers.

`DIG0` under `dce_dc_dio_dig0_dispdec` begins the digital stream encoder block. This range includes front-end source selection, output CRC controls/results, test/random/clock pattern registers, FIFO status, HDMI metadata packet control, HDMI deep color/scramble/keepout/error control, HDMI status and audio/ACR/VBI/infoframe controls, generic HDMI packet controls 0 through 10 for packets 0 through 14, HDMI double-buffer control, ACR constants/status for 32/44.1/48 kHz audio families, AFMT clock control, back-end enable and mode/HPD/source selection, TMDS sync/control character fields, TMDS feedback/stereosync/sync pattern fields, and the start of TMDS DC balancer control.

## Important APIs, Types, And Macros

The important contract is the generated macro naming scheme:

- `<instance>_<register>__<field>__SHIFT` gives the bit offset used when packing or extracting a register field.
- `<instance>_<register>__<field>_MASK` gives the 32-bit field mask.
- Address-block comments identify replicated hardware instances, while register comments delimit groups for generated readability.
- Instance prefixes in this chunk include `DC_PERFMON16`, `DP_AUX0` through `DP_AUX3`, `VPG0`, `AFMT0`, `DME0`, and `DIG0`.

These constants are consumed through AMD display register macros such as `AUX_SF`, `SE_SF`, `SRI`, `REG_FIELD`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, and `REG_WAIT`. `display/dc/dce/dce_aux.h` uses `DP_AUX0_*` field names as the base mask/shift list for all AUX instances. `display/dc/dcn30/dcn30_vpg.h` uses `VPG0_*` fields for generic-packet data/index/update/conflict state. `display/dc/dcn30/dcn30_afmt.h` uses `AFMT0_*` fields for audio source, audio channel layout, IEC 60958 channel status, sample-send, and memory-power control. `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` uses `DIG0_*`, `DME0_*`, and related `DP0_*` fields to build the DCN 3.0 stream encoder register and mask lists.

The direct DCN 3.0.1 include site found in this tree is `display/dmub/src/dmub_dcn301.c`, which includes this header with the matching offset header. Other DCN display modules use the same generated macro families through versioned resource and stream-encoder setup.

## Functional Field Groups

AUX transaction fields describe a software-driven DisplayPort AUX channel. `AUX_CONTROL` enables and resets the controller, selects HPD input, controls low-speed read, and exposes reset completion. `AUX_SW_CONTROL`, `AUX_SW_DATA`, and `AUX_SW_STATUS` stage request bytes, transaction length, auto-increment behavior, reply data, reply byte count, done/error/timeout state, and the software transaction go bit. `AUX_INTERRUPT_CONTROL` provides done/error interrupt status, acknowledge, and mask bits. `AUX_ARB_CONTROL` arbitrates access between software and DMCU users, with request, pending, done, and status fields. DPHY and GTC sync registers cover physical signaling thresholds/timing, invalid/timeout handling, receive state, wake detection, and global-time-code sync lock/error status.

VPG fields stage generic secondary data packets. The access-control/data pair selects byte indexes and writes four packet bytes at a time. Frame-update and immediate-update registers independently schedule generic packet slots 0 through 14. Status fields report generic-packet conflicts and provide a clear bit, while memory-power fields allow force/light-sleep style power management around the VPG packet RAM.

AFMT fields program HDMI/DP audio packet formatting. They control VBI/audio packet placement, maximum packets per line, audio channel enables and layouts, 60958 channel-status values, audio-source selection, audio-sample sending, CRC testing, audio infoframe updates, and AFMT RAM power behavior. Status and interrupt bits report packet/audio formatter conditions.

DME fields program metadata insertion. They select a HUBP requestor, enable metadata engine operation, choose stream type, manage double-buffer handshakes, clear taken/missed state, and control DME memory power. These fields are timing-sensitive because metadata payloads need to be accepted by the stream pipeline before the intended frame or packet interval.

DIG/HDMI/TMDS fields program the stream encoder. `DIG_FE_CNTL` selects the OTG/source input and stereo/bypass options. `HDMI_CONTROL`, `HDMI_STATUS`, and related packet controls handle scrambling, deep color, keepout, packet generator versioning, HDMI error ack/mask/status, VBI/infoframe/audio packet send behavior, and ACR enable/source selection. Generic packet controls provide continuous send, one-shot send, immediate send, pending, enable double-buffer pending, and line-number fields for slots 0 through 14. TMDS fields select packing phase, control-character output, sync character patterns, CTL bits, feedback delay, stereosync control selection, and DC balancer behavior.

Performance monitor fields define counter state and readback plumbing for the display performance monitor. They expose selected counter states, count-off interrupt controls, report count, low/high counter value readback, and interrupt/status/ack bits for individual performance counters.

## Control Flow And State Behavior

This header has no direct control flow. Runtime behavior appears when the display driver expands register-list and mask-list macros for a selected hardware instance. The offset header supplies the memory-mapped register address, this header supplies the mask/shift constants, and helper macros perform read-modify-write, polling, or direct writes.

Hardware state described here persists in display controller registers until changed by driver writes, firmware/DMCU/DMUB activity, reset, power gating, or hardware event logic. Configuration fields include AUX timing/control, VPG packet RAM indexes and update bits, AFMT audio/infoframe setup, DME metadata mode, DIG source selection, HDMI/TMDS mode controls, packet scheduling, and memory-power controls. Live status fields include AUX done/error/timeout/reply status, reset-done bits, FIFO status, GTC sync lock/error state, VPG conflict state, AFMT status/interrupt state, DME double-buffer and missed-transmission state, HDMI error/status state, generic-packet pending bits, and performance-counter values.

Several fields have acknowledge, clear, or double-buffer semantics. Examples include `*_ACK`, `*_CLR`, `*_CLEAR`, `*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_IMMEDIATE_SEND_PENDING`, and `*_EN_DB_PENDING`. Callers must distinguish status from write-to-clear or handshake bits, because a wrong mask can either fail to clear a condition or clear/take state unexpectedly.

## Dependencies And Integration Points

The chunk depends on the DCN 3.0.1 hardware register database and must remain aligned with `dcn_3_0_1_offset.h`, where the corresponding `mm*` address and base-index macros are defined. It also depends on the generated AMD display naming convention that lets a single `DP_AUX0_*`, `VPG0_*`, `AFMT0_*`, `DME0_*`, or `DIG0_*` field list seed per-instance register tables.

The AUX definitions integrate with `display/dc/dce/dce_aux.c` and `display/dc/dce/dce_aux.h`. Those paths reset AUX, poll `AUX_RESET_DONE`, program software request length/data, trigger `AUX_SW_GO`, wait for `AUX_SW_DONE`, read reply bytes and error state, and acknowledge `AUX_SW_DONE_ACK`.

The VPG and AFMT definitions integrate with DCN 3.0 packet/audio helpers in `display/dc/dcn30/dcn30_vpg.*` and `display/dc/dcn30/dcn30_afmt.*`. These modules stage infoframe/generic-packet bytes, request frame or immediate updates, configure HDMI audio channel/layout/channel-status data, and control audio mute/sample sending.

The DME and DIG definitions integrate with `display/dc/dio/dcn30/dcn30_dio_stream_encoder.*` and related stream-encoder construction. The register list includes HDMI generic packet controls 0 through 10, HDMI audio/ACR/infoframe controls, `DME_CONTROL`, HDMI metadata packet control, front-end source selection, FIFO status, and clock/test pattern registers. These fields are used during stream enable, modeset, infoframe/metadata updates, audio setup, and DP/HDMI packet programming.

## Risks And Edge Cases

The primary risk is mismatch between this generated mask header, the companion offset header, and real DCN 3.0.1 hardware. A bad shift or mask silently targets the wrong bitfield in memory-mapped display registers, which can break AUX transactions, corrupt HDMI infoframes, disable audio packets, leave metadata double buffers stuck, misroute DIG sources, or cause spurious/missed interrupts.

The replicated AUX blocks are easy to drift. `DP_AUX0` through `DP_AUX3` should remain structurally identical except for instance prefix and offsets. A generation error in one instance could affect only one connector path and might only reproduce with a display attached to that AUX channel.

Partial-block boundaries matter for chunk reconciliation. `DC_PERFMON16_PERFCOUNTER_CNTL2` begins before this range, and `DIG0_TMDS_DCBALANCER_CONTROL` continues after line 29755. Any final merged research should avoid treating those two registers as fully owned by this chunk alone.

Handshake and clear bits are high risk. AUX `GO`/`DONE`/`ACK`, arbitration request/done bits, VPG conflict clear, DME double-buffer taken/pending/clear, HDMI error ack/mask, HDMI double-buffer state, and generic packet pending bits are adjacent to configuration fields. Confusing status masks with acknowledge masks can create lost completion signals or stale pending state.

Packet and audio fields are width-sensitive. Generic packet line numbers are packed 16-bit values, packet byte lanes are packed in 8-bit fields, ACR N/CTS values have fixed field widths, and many update controls are one-bit slot selectors. Callers must clamp or validate values before packing; overwide values will be truncated by these masks.

Power-management fields can hide state. VPG, AFMT, and DME memory power controls interact with packet RAM or metadata state. Programming packet data while RAM is gated, or failing to restore state after power transitions, can manifest as missing infoframes, stale audio metadata, or missed HDR/metadata packets.

## Test Signals

Build-time signals include compilation failures for missing `DP_AUXx_*`, `VPG0_*`, `AFMT0_*`, `DME0_*`, or `DIG0_*` macros used by `AUX_SF`, `SE_SF`, `SRI`, `REG_FIELD`, `REG_UPDATE`, and related AMD display helpers. These are strong indicators that generated headers and consumer field lists are out of sync.

Runtime AUX signals include successful EDID/DPCD reads, stable hotplug detection across all AUX-backed connectors, no AUX timeout storms, correct `AUX_RESET_DONE` polling behavior, and successful reply byte counts for DP link training and I2C-over-AUX transactions.

Runtime packet/audio/metadata signals include correct HDMI/DP infoframes, HDR or vendor metadata arriving on the sink, audio playback with expected channel layout and sample status, correct ACR/N/CTS behavior for 32/44.1/48 kHz families, no stale generic-packet pending bits after updates, and no VPG conflict or DME missed-transmission status after mode changes.

Stream-encoder signals include successful HDMI modesets with deep color and scrambling where required, correct DIG source routing, stable TMDS output, expected FIFO status, no HDMI error interrupts left uncleared, and clean behavior when enabling/disabling double-buffered HDMI packet updates.

Because this file is generated register metadata rather than algorithmic code, the best regression coverage combines hardware register-database diffing, build coverage for every DCN 3.0.1 display path, and hardware smoke tests that exercise every AUX instance, packet slot, audio formatter path, metadata engine path, and HDMI/TMDS stream-encoder mode represented by this chunk.
