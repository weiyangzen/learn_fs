# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 32177-34584

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.0.1 register field mask header. It contains C preprocessor constants for hardware bit positions (`__SHIFT`) and bit masks (`_MASK`) rather than executable driver code. The covered range starts at the tail of `DP1_DP_ALPM_CNTL`, finishes late DisplayPort secondary-packet fields for `DP1`, covers complete `DIG2` VPG/AFMT/DME/DIG and `DP2` DIO blocks, then begins the `DIG3` VPG/AFMT/DME/DIG block and ends inside `DIG3_HDMI_GENERIC_PACKET_CONTROL0`.

In driver terms, this header is the field-layout half of the DCN 3.0.1 MMIO contract. The matching offset header supplies register addresses; this file supplies the per-field masks and shifts used by AMD display register helpers to pack and extract values. The hardware areas represented here drive DisplayPort stream/link setup, secondary-data-packet scheduling, multi-stream allocation, HDMI packet and audio formatting, generic packet RAM access, metadata transport, DIO/DIG enablement, TMDS test/control patterns, CRC/readback diagnostics, and memory power state for VPG/AFMT/DME engines.

There are no functions, structs, local variables, or runtime branches in this chunk. Its value is the stable macro naming contract that lets common DC display code target repeated hardware instances by prefix, such as `VPG2_`, `AFMT2_`, `DIG2_`, `DP2_`, `VPG3_`, `AFMT3_`, `DME3_`, and `DIG3_`.

## Register Blocks Covered

The first lines complete the end of a previous `DP1` block, including `DP1_DP_ALPM_CNTL` masks and `DP1_DP_GSP8_CNTL` through `DP1_DP_GSP11_CNTL`. These generic secondary-packet controls expose MSO packet enables, packet send triggers, send-in-idle/send-any-line behavior, pending/active/deadline-missed status, and line-number placement. `DP1_DP_GSP_EN_DB_STATUS` adds per-GSP double-buffer pending bits for GSP0 through GSP11.

`dce_dc_dio_dig2_vpg_vpg_dispdec` covers the Video Packet Generator instance 2. It defines indexed packet RAM access (`VPG2_VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG2_VPG_GENERIC_PACKET_DATA`), frame-synchronized and immediate update controls for generic packet slots 0 through 14, generic lock/conflict status, VPG memory power state, ISRC indexed data, and MPEG infoframe payload/update fields.

`dce_dc_dio_dig2_afmt_afmt_dispdec` covers Audio Formatter instance 2. It includes HDMI audio packet pacing, audio layout/channel/stream-id controls, HDMI audio infoframe words, IEC 60958 channel-status fields, audio CRC controls/results, ramp/test-pattern controls, audio FIFO/status bits, audio sample-send and overflow/change acknowledgements, audio infoframe update source, audio-source select, and AFMT memory power controls.

`dce_dc_dio_dig2_dme_dme_dispdec` covers Display Metadata Engine instance 2. Its fields identify the HUBP metadata requestor, enable the metadata engine, select stream type, expose metadata double-buffer pending/taken/clear/disable state, and control DME memory power/default low-power state.

`dce_dc_dio_dig2_dispdec` covers Digital Encoder instance 2. It starts with DIG front-end selection and output CRC/test-pattern/FIFO fields, then defines HDMI metadata, HDMI control/status, audio delay, ACR, VBI, infoframe, generic-packet scheduling and line-placement, HDMI DB control, ACR programmed/status values for 32/44.1/48 kHz families, AFMT clock enable/status, DIG back-end mode/HPD/source routing, TMDS control patterns, lane enablement, DIG version, and forced disable.

`dce_dc_dio_dp2_dispdec` covers DisplayPort instance 2. This is the largest block in the chunk and includes link status/configuration, pixel format, MSA colorimetry/misc/timing, video stream enable/status, steer FIFO overflow handling, DPHY training/scrambler/FEC/CRC/fast-training controls, secondary packet and audio M/N controls, MST MSE rate and slot allocation tables/status, MSO, DSC, ALPM, secondary metadata transmission, DB control, GSP8 through GSP11 controls, and GSP enable double-buffer status.

The range then begins the next repeated DIO instance. `VPG3`, `AFMT3`, and `DME3` mirror the VPG/AFMT/DME2 layouts for instance 3. The final `DIG3` section covers front-end, output CRC, test pattern, FIFO, HDMI metadata/control/status, ACR/VBI/infoframe controls, and starts `DIG3_HDMI_GENERIC_PACKET_CONTROL0` through the mask for `HDMI_GENERIC4_SEND`. The rest of the DIG3 generic-packet block continues in the next chunk.

## Important APIs, Types, And Macros

The exported surface is entirely macro based:

- `<instance>_<register>__<field>__SHIFT` gives the field's low bit position in a 32-bit MMIO register.
- `<instance>_<register>__<field>_MASK` gives the already-shifted field mask.
- Register comments, for example `//DP2_DP_SEC_CNTL`, delimit logical register groups for humans and generated diff review.
- Address-block comments, for example `// addressBlock: dce_dc_dio_dp2_dispdec`, identify the replicated hardware block that owns the following register names.

Consumers normally reach these constants indirectly through AMD display register helpers such as `SRI`, `SF`, `SE_SF`, `REG_FIELD`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. The repeated prefixes in this chunk are intentionally compatible with common register-list macros in the display tree. For example, VPG code uses fields such as `VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG_GENERIC_PACKET_DATA`, `VPG_GSP_FRAME_UPDATE_CTRL`, `VPG_GSP_IMMEDIATE_UPDATE_CTRL`, and `VPG_MEM_PWR`; AFMT code uses `AFMT_AUDIO_PACKET_CONTROL`, `AFMT_AUDIO_PACKET_CONTROL2`, `AFMT_60958_*`, `AFMT_AUDIO_SRC_CONTROL`, and `AFMT_MEM_PWR`; DP/DIG encoder code uses the corresponding `DP_*`, `HDMI_*`, `DIG_*`, and `TMDS_*` fields.

No C type is defined here. The implicit type model is 32-bit register words, with callers responsible for shifting, masking, and clamping values before MMIO access.

## Functional Areas

Generic and secondary packet programming is represented in three forms. VPG registers provide indexed packet payload RAM and update triggers for generic packet slots 0-14. HDMI generic-packet registers schedule packet send/continuous modes, line references, update-lock bypass, immediate-send requests, line numbers, and DB-pending status. DP secondary-packet registers schedule ASP/ATP/AIP/ACM/GSP/ISRC/MPG packets, line numbers, send triggers, send-active/send-in-idle status, and deadline-missed reporting.

DisplayPort link and stream fields cover link-training completion/status, embedded-panel mode, UDI lane count, pixel encoding/component depth, MSA misc/colorimetry/timing, video stream enable/deferred disable/status, VBID/enhanced framing, DPHY scrambler and bypass selection, FEC enable/ready/active status, training pattern selection, 8b/10b reset, PRBS/scrambler controls, CRC enable/result/MST slot selection, and fast-training state/interrupt acknowledgement.

DP MST/MSO/DSC support appears through `DP2_DP_MSE_*`, `DP2_DP_MSO_*`, and `DP2_DP_DSC_*` fields. The MSE fields configure rate X/Y, slot allocation table entries for sources 0-5, update-pending state, link timing, misc controls, and SAT readback/status. MSO fields control secondary-link count/selection and pixel/stream width behavior. DSC fields control DSC enable/mode and bytes-per-pixel metadata.

HDMI and TMDS fields cover metadata packet line scheduling, AVMUTE/general-control packets, HDMI scrambling, clock-channel rate, deep color, error acknowledgement/masking, ACR send/source/auto-send/N-multiple, null/GC/ISRC VBI packet controls, audio and MPEG infoframe send/continuous/line fields, TMDS control characters, sync character patterns, DC balancer controls, and lane/clock enables.

Audio formatter fields cover audio channel enablement, DP audio stream ID, HDMI audio packet count limits, audio layout override/select, 60958 channel-status words and per-channel numbers, audio sample send and double-buffer enable, FIFO overflow/change acknowledgements, channel swap, audio test/ramp generation, CRC capture, and memory power state.

Metadata and memory-power fields include DME requestor/engine/stream-type and metadata DB state, `VPG*_VPG_MEM_PWR`, `AFMT*_AFMT_MEM_PWR`, and `DME*_DME_MEMORY_CONTROL`. These let the display driver or power-management paths force, disable, or observe low-power state for packet/audio/metadata RAMs.

Diagnostics and status fields include output CRC control/results, DPHY CRC results, FIFO level/error/calibration status, HDMI audio/VBI packet errors, metadata missed bits, GSP send pending/active/deadline flags, MSE SAT status, DP link and video stream status, and DIG clock/frontend/backend enable status.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior is created when DCN 3.0.1 display modules include this generated mask header, bind these fields to register addresses from the companion offset header, and invoke register-helper macros. A typical path constructs an instance-specific register table, then calls `REG_UPDATE` or `REG_GET` against logical field names; macro expansion selects the concrete `DP2_`, `DIG2_`, `VPG3_`, or similar mask and shift.

The state described by these fields lives in hardware registers, not in this file. Configuration fields persist in the display engine until rewritten or reset, including packet payload bytes, line numbers, link/framing options, audio formatter settings, ACR N/CTS values, MST slot allocations, and memory-power controls. Status fields are live hardware observations, including pending DB updates, send-active flags, FIFO level/error state, CRC results, link/stream state, and power-state readbacks. Event/interrupt-style fields are indicated by names such as `*_ACK`, `*_CLR`, `*_PENDING`, `*_MISSED`, `*_ERROR_INT`, and `*_MASK`; callers must follow the hardware write-to-clear or acknowledge semantics.

Many packet controls are double-buffered or synchronized to frame/update boundaries. VPG frame-update, VPG immediate-update, HDMI DB, DP DB, MSE rate/SAT update, metadata DB, and GSP enable DB fields represent pending/taken state. Incorrect sequencing can leave new packet data pending for the wrong frame, collide with a lock, miss a packet deadline, or expose stale metadata/audio information on the link.

## Dependencies And Integration Points

This chunk depends on the DCN 3.0.1 hardware register database and must stay aligned with `dcn_3_0_1_offset.h`, which supplies the MMIO addresses for the same register names. The file is included directly by the DCN 3.0.1 DMUB implementation (`display/dmub/src/dmub_dcn301.c`) and is part of the broader generated-register include set consumed by DCN 3.0.1 display code.

Important integration points are the DIO encoder/link/audio/packet subsystems under `drivers/gpu/drm/amd/display`. VPG register-list code maps the generic packet access/data/update/memory-power fields used here. AFMT register-list code maps the audio info, 60958, audio packet, source-select, and memory-power fields. DIG/DP encoder paths use these masks to program HDMI, TMDS, DisplayPort, DSC, MST/MSO, secondary-packet, link-training, and CRC registers.

Higher-level display workflows that depend on these definitions include link enable/disable, DisplayPort link training and fast training, HDMI mode setup, audio enablement and channel-status programming, infoframe and HDR/static metadata packet transmission, DP MST allocation, DSC transport setup, low-power memory gating, debug CRC collection, and interrupt/error acknowledgement for FIFO/link/packet conditions.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is imported Linux AMD GPU display driver code and is not Ceph filesystem logic.

## Risks And Edge Cases

The primary risk is generated-register drift. A one-bit error in a `_MASK` or `__SHIFT` value can make otherwise correct driver code write adjacent hardware fields, fail to acknowledge status, or read misleading diagnostics. This is especially risky in tightly packed registers such as HDMI generic-packet controls, VPG update bitmaps, DP secondary-packet controls, MSE slot allocation tables, and AFMT 60958 channel-status words.

The chunk boundaries are partial. It starts after the beginning of `DP1_DP_ALPM_CNTL` and ends partway through `DIG3_HDMI_GENERIC_PACKET_CONTROL0`; final per-file reconciliation must combine adjacent chunks before claiming complete `DP1` or `DIG3` coverage.

Instance replication can hide defects. The `VPG2` and `VPG3`, `AFMT2` and `AFMT3`, and `DME2` and `DME3` groups are structurally mirrored, while `DIG2` and `DP2` are complete enough to exercise large independent hardware paths. A generation error in only one instance may show up as a pipe-specific failure rather than an obvious compile problem.

Packet timing fields are mode- and frame-phase-sensitive. Bad line numbers, line-reference bits, immediate-send triggers, update-lock-disable bits, or DB disable/pending controls can cause packets to be sent on the wrong line, never sent, sent during idle unexpectedly, or missed under deadline pressure.

Status and acknowledge fields are easy to misuse. Confusing `*_PENDING`, `*_TAKEN`, `*_TAKEN_CLR`, `*_ACK`, `*_MASK`, and error-status masks can leave interrupts stuck, clear evidence before it is sampled, or allow packet/FIFO/link errors to go unreported.

Value-width truncation is another risk. Many fields are small packed quantities: 6-bit MST slots, 8-bit payload bytes and infoframe fields, 16-bit line positions, 20-bit ACR N/CTS values, and 24-bit audio/video M/N values. Callers must validate values before packing because this header only masks; it does not enforce semantic ranges.

## Test Signals

Build-time coverage is the first signal. DCN 3.0.1 display and DMUB objects that include `dcn_3_0_1_sh_mask.h` should compile without missing `DP2_*`, `DIG2_*`, `VPG*_*`, `AFMT*_*`, or `DME*_*` field identifiers in register tables and helper macros.

Static validation should compare this generated header against AMD's authoritative register database and adjacent DCN generations for expected replicated layouts. High-signal checks include matching `VPG2`/`VPG3` and `AFMT2`/`AFMT3` field shapes, verifying `DP2` secondary-packet and MSE/MSO/DSC masks, and confirming the companion offset header has corresponding register addresses.

Runtime validation should exercise DCN 3.0.1 hardware paths that use instance 2 and 3 DIO blocks: HDMI modes with infoframes, metadata packets, AVMUTE, ACR, deep-color/scrambling, and TMDS patterns; DP modes with link training, FEC/scrambler settings, MSA programming, secondary packets, MST slot allocation, MSO, DSC, and ALPM; and audio enablement with channel layout, channel status, sample-send, and FIFO overflow handling.

Diagnostic signals include output CRC and DPHY CRC readback, FIFO status staying clear of level errors, GSP/HDMI/DP packet pending bits draining after updates, no deadline-missed flags during metadata/infoframe transmission, correct MSE SAT status after MST allocation, and memory-power state readbacks matching low-power entry/exit requests.
