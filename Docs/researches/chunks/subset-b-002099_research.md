# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 26549-28768

## Scope

This chunk is a generated AMD DCN 3.5.1 register shift/mask header slice. It contains C preprocessor constants only: every meaningful symbol maps a display hardware register field to a bit shift or bit mask. There are no functions, runtime branches, structs, or direct storage in this range. Its consumers are AMDGPU display code paths that build read-modify-write values for MMIO registers through the `REG_SET`, `REG_UPDATE`, `REG_GET`, and related DC register-access macros.

The slice starts in the tail of `VPG0` MPEG info packet fields, covers the full `AFMT0` audio formatter group and `DME0` metadata engine group, covers a large `DIG0` HDMI/TMDS/back-end and `DP0` DisplayPort transmitter block, then repeats the beginning of the same per-pipe packet/audio/metadata/DIG pattern for instance 1 (`VPG1`, `AFMT1`, `DME1`, and early `DIG1`). The chunk ends mid-register at `DIG1_HDMI_GENERIC_PACKET_CONTROL10__HDMI_GENERIC1_EN_DB_PENDING__SHIFT`, so the next chunk must complete the remaining `DIG1_HDMI_GENERIC_PACKET_CONTROL10` masks and later DIG1/DP1 fields.

## Purpose

These macros provide the authoritative bit layout for DCN 3.5.1 display output hardware. The declarations are split by hardware instance:

- `VPG0` and `VPG1` define Video Packet Generator fields for generic packets, ISRC/MPEG info payload bytes, generic packet frame/immediate update triggers, conflict status, and VPG SRAM power controls.
- `AFMT0` and `AFMT1` define audio formatter packet controls for HDMI/DP audio: channel layout, channel enable mask, DP audio stream ID, HBR override, IEC 60958 channel status fields, HDMI audio infoframe bytes, audio CRC, audio test ramp generation, status, ACK bits, source selection, and AFMT memory power state.
- `DME0` and `DME1` define the display metadata engine controls: HUBP requestor selection, metadata engine enable, stream type, double-buffer pending/taken status and clear bits, DB disable, missed-transmission status/clear, and metadata memory power controls.
- `DIG0` defines the digital encoder/back-end fields for HDMI/TMDS packet scheduling, ACR, VBI, metadata packet injection, generic info packet send/continuous/line-reference/immediate controls, HDMI general-control mute/packing phase, double-buffer handshakes, audio clock gate controls, DIG back-end clock/reset/source selection, TMDS pattern generation, output CRC, and front-end/FIFO/test-pattern knobs.
- `DP0` defines the DisplayPort side of instance 0: link and stream controls, DPHY lane/symbol/training/scrambler/CRC, fast training, secondary data packet stream enables, audio M/N, secondary packet framing, MST/MSE slot allocation tables and status, MSA timing payloads, MSO controls, DSC mode, GSP8-GSP11 packet controls, generic secondary packet DB status, metadata transmission, VBID/MSA fields, video interrupt controls, and ALPM/AUX-less ALPM state/interrupt controls.
- `DIG1` begins the instance-1 digital encoder fields: FE/FIFO/output CRC/test pattern, HDMI control/status/VBI/metadata/generic packet controls, immediate sends, and HDMI general control/line-number fields.

## Important APIs, Types, and Symbols

There are no C types or callable APIs in this range. The exported surface is the naming contract:

- `*_SHIFT` constants give the least-significant bit index used when placing a field value in a register word.
- `*_MASK` constants give the contiguous bit mask used to isolate or update a field.
- Macro names follow `INSTANCE_REGISTER__FIELD_{SHIFT,MASK}`, which lets AMD display register tables and generated accessor macros pair register addresses from companion headers with bitfield definitions from this file.

Key register families in this slice:

- `VPG0_VPG_MPEG_INFO0/1` and `VPG1_VPG_MPEG_INFO0/1` contain MPEG infoframe checksum/message bytes, MPEG frame flags, and update bits.
- `VPG1_VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG1_VPG_GENERIC_PACKET_DATA`, `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, and `VPG1_VPG_GSP_IMMEDIATE_UPDATE_CTRL` cover indexed generic packet payload data and 15 generic packet update slots with pending feedback.
- `AFMT[0-1]_AFMT_AUDIO_PACKET_CONTROL*`, `AFMT_AUDIO_INFO*`, `AFMT_60958_*`, `AFMT_STATUS`, `AFMT_AUDIO_CRC_*`, `AFMT_RAMP_CONTROL*`, and `AFMT_MEM_PWR` are the audio formatter programming interface for audio infoframes, IEC 60958 status, sample transmission, FIFO/enable-change ACKs, test ramps, CRC readback, and memory-light-sleep policy.
- `DME[0-1]_DME_CONTROL` and `DME_MEMORY_CONTROL` provide metadata engine enable/DB/missed-transmission control and memory-power state fields.
- `DIG0_HDMI_*` covers HDMI audio/video transport, including `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_METADATA_PACKET_CONTROL`, `HDMI_ACR_PACKET_CONTROL`, `HDMI_ACR_*`, `HDMI_DB_CONTROL`, `HDMI_GENERIC_PACKET_CONTROL0/1/2/3/4/5/6/7/8/9/10`, and `HDMI_GC`.
- `DIG0_DIG_BE_*`, `DIG0_DIG_FE_CNTL`, `DIG0_DIG_FIFO_CTRL*`, `DIG0_DIG_TEST_PATTERN`, `DIG0_DIG_OUTPUT_CRC_*`, and `DIG0_TMDS_*` cover back-end clock/reset/source selection, FIFO servicing, BIST/test patterns, CRC capture, TMDS sync/control/DC balance, and control-character generation.
- `DP0_DP_*` spans the DP encoder and secondary packet engine, especially `DP_LINK_*`, `DP_VID_*`, `DP_DPHY_*`, `DP_SEC_*`, `DP_MSE_*`, `DP_MSO_*`, `DP_MSA_*`, `DP_GSP8..11_CNTL`, `DP_SEC_METADATA_TRANSMISSION`, `DP_STEER_FIFO`, `DP_ALPM_CNTL`, and `DP_AUXLESS_ALPM_CNTL*`.

## Control Flow and Programming Model

Because the file is declarative, runtime control flow lives in the display driver callers. The implied programming model is:

1. Select a display output instance and register family from the active link/stream encoder.
2. Use companion address/register headers to identify the MMIO register.
3. Use the `*_SHIFT` and `*_MASK` macros here to compose, update, or decode fields.
4. For stateful hardware protocols, write a request bit and poll/read a pending, taken, done, status, or occurred bit from the matching field.

The most important hardware handshakes exposed by this range are:

- VPG generic packet update flow: driver writes packet payload through indexed access/data registers, triggers frame or immediate update bits, and observes `*_PENDING` or conflict status fields.
- AFMT audio flow: driver sets layout/channel/HBR/stream-id/infoframe/channel-status fields, enables sample sending, then monitors `AFMT_STATUS` for audio enable, HBR status, FIFO overflow, and audio-enable-change events. Overflow and enable-change are acknowledged through `AFMT_AUDIO_PACKET_CONTROL`.
- DME metadata flow: driver enables the metadata engine, waits on `METADATA_DB_PENDING` and `METADATA_DB_TAKEN`, clears taken/missed conditions, and can disable DB behavior when required.
- HDMI generic packet flow: `HDMI_GENERIC_PACKET_CONTROL0` and `CONTROL6` enable slots 0-14, select continuous send and line-reference behavior, `CONTROL1/2/3/4/7/8/9/10` set line numbers and DB pending status, and `CONTROL5` requests immediate send while exposing immediate pending bits.
- HDMI DB flow: `HDMI_DB_CONTROL` carries pending/taken/taken-clear/lock/disable plus vupdate DB pending/taken status; callers must use these bits to avoid racing infoframe or generic packet updates.
- DP secondary packet flow: `DP_SEC_CNTL*` enables stream/audio/timecode/info/GSP/MPEG/ISRC packets, schedules GSP line numbers, requests GSP sends, exposes send-pending and deadline-missed flags, and controls DB disable/pending status for GSP slots 0-11.
- DP link training and link-layer flow: DPHY control registers expose lane enable, training pattern selection, scrambler, PRBS, CRC, HBR2 pattern, and fast-training trigger/status bits. These fields participate in link training and diagnostics but this header does not enforce the ordering.
- DP MST/MSO flow: MSE rate, slot allocation tables, SAT update, status readback, link timing, and MSO stream enable fields describe how the encoder allocates payload slots across streams.
- ALPM flow: `DP_ALPM_CNTL` and `DP_AUXLESS_ALPM_CNTL*` define enable/status/state/frame/line/interrupt fields used for low-power panel behavior and wakeup signaling.

## State and Persistence Behavior

The macros have no software state and no persistence. They describe hardware state located in DCN display registers.

Important stateful hardware fields in the chunk include:

- Sticky or event-like bits: `*_OCCURRED`, `*_MISSED`, `*_DONE`, `*_SEND_DEADLINE_MISSED`, `*_WAKEUP_INTERRUPT_OCCURRED`, and FIFO overflow/change flags.
- Clear or ACK bits: `*_CLR`, `*_ACK`, `*_CLEAR`, `AFMT_AUDIO_FIFO_OVERFLOW_ACK`, `AFMT_AZ_AUDIO_ENABLE_CHG_ACK`, `HDMI_DB_TAKEN_CLR`, `VUPDATE_DB_TAKEN_CLR`, `METADATA_DB_TAKEN_CLR`, and `METADATA_TRANSMISSION_MISSED_CLR`.
- Pending/taken DB bits: VPG, DME, HDMI, and DP GSP engines all expose pending/taken/pending-status fields. These are volatile handshakes with hardware double-buffer logic.
- Readback/status registers: audio CRC result, HDMI ACR status, DIG output CRC result, DP DPHY/MSE readbacks, DP MSA timing payload fields, ALPM current state and enable status.
- Power policy fields: AFMT/VPG/DME memory power controls and clock enable/on fields can affect register accessibility and side effects if a caller programs packet engines while memory or clocks are gated.

Any suspend/resume, hotplug, modeset, or link-reset path that reinitializes DCN output hardware must reprogram these registers through higher-level driver code. The header itself does not retain values across resets, power-gating, or display pipe reallocation.

## Dependencies and Integration Points

This header is part of the AMDGPU DRM display register-description layer under `drivers/gpu/drm/amd/include/asic_reg/dcn/`. It depends on generated register address headers for actual offsets and on display-core accessor macros for correct MMIO reads/writes. It is typically integrated indirectly through DCN resource, link encoder, stream encoder, audio, HDMI, DP, packet, and metadata programming code.

Integration points to preserve:

- Field names must match generated `sh_mask` references expected by `dcn*` stream encoder, link encoder, audio, HDMI, DP, and packet-management code.
- Instance suffixes must align with register-address instance tables. `AFMT0` pairs with `DIG0`/`DP0`/`VPG0`/`DME0`, and the repeated `1` groups must pair with the second output instance.
- Register layout must remain synchronized with firmware/hardware specs. These constants are usually regenerated from ASIC register databases; hand edits create high risk unless validated against the source spec.
- HDMI and DP packet fields overlap conceptually with DRM infoframe, audio, HDR metadata, adaptive sync, DSC PPS, PSR/ALPM, MST, and modeset code paths; an incorrect mask can surface far from the immediate write site as a blank screen, missing audio, stale metadata, or link-training instability.

## Risks and Edge Cases

- The chunk begins and ends in the middle of logical generated sections. `VPG0_MPEG_INFO0` starts before this range, and `DIG1_HDMI_GENERIC_PACKET_CONTROL10` continues after it. Merge tooling must concatenate adjacent chunk research for full per-file coverage.
- Off-by-one bit shifts or masks in this file are severe: they can corrupt neighboring fields in the same 32-bit register. Multi-bit fields such as channel masks, M/N values, line numbers, slot counts, ACR CTS/N, MSA timing, and ALPM frame/line numbers are especially sensitive.
- Some fields have similar names but different semantics across packet engines. For example, VPG generic update pending, HDMI generic immediate pending, DME DB pending, and DP GSP DB pending are not interchangeable despite similar pending terminology.
- Write-one-to-clear or ACK fields must not be treated as ordinary persistent enable bits by callers. Clear/ACK fields in DME, HDMI DB, AFMT, DP secondary packets, and ALPM interrupt controls can drop real hardware events if written casually during broad register updates.
- Power and clock gating fields can interact with programming order. AFMT memory power, VPG memory power, DME memory power, AFMT audio clock, and DIG back-end clock/reset fields should be sequenced by existing driver helpers rather than updated independently.
- Instance-number mismatch is a realistic integration risk. Programming `AFMT1` with `DIG0` or `DP0` state can send correct-looking packet data to the wrong pipe or leave the active encoder stale.
- DP MST/MSO and secondary packet scheduling fields include line/frame timing and deadline-missed status; wrong timing can produce intermittent failures that only appear at certain refresh rates, link rates, or blanking intervals.
- DP ALPM/AUX-less ALPM fields include hardware-mode status and wakeup interrupt fields; incorrect masks can create low-power wake failures or persistent wake interrupts.

## Test Signals

Useful validation is mostly integration and hardware-facing:

- Build coverage: compile AMDGPU DC display code for the target ASIC family with `W=1` or equivalent to catch missing or renamed macros.
- Header consistency checks: generated-register validation should compare every `*_SHIFT` and `*_MASK` in this range against the DCN 3.5.1 register database, including field widths and instance repetition.
- HDMI functional tests: modeset to HDMI with audio enabled, verify audio infoframe/channel status/HBR paths, generic info packets, AVMUTE, ACR behavior, and absence of AFMT FIFO overflow.
- DP functional tests: link training at multiple link rates/lane counts, check fast-training completion, scrambler/training-pattern transitions, DPHY CRC diagnostics, and stable video after hotplug and modeset.
- Metadata/infoframe tests: HDR/AVI/vendor-specific/generic packet updates should change on frame or immediate update without stale pending bits, DB conflicts, or deadline-missed flags.
- MST/MSO tests: exercise multiple streams, slot allocation updates, MSE SAT status readback, and secondary data packet scheduling.
- Low-power tests: PSR/ALPM or panel low-power scenarios should enter and exit ALPM cleanly, with expected wakeup interrupt status/clear behavior.
- Suspend/resume and hotplug tests: verify that packet/audio/metadata/DIG/DP state is restored for both instance 0 and instance 1 without cross-instance leakage.
