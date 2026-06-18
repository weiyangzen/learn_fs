# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 32639-35043

## Scope

This chunk is part of the generated DCN 4.1.0 ASIC register shift/mask header used by the AMD display driver. It contains preprocessor constants only: each hardware field is represented by a `...__SHIFT` bit offset and a matching `..._MASK` value. The file has no functions, structs, or executable control flow, but it is a dependency for the driver register access layer that builds register tables and calls `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT` through `FN()`/`FD()`-style field expansion.

The line range covers the tail of `DP1` secondary packet and DisplayPort controls, the full visible `DIG1` display encoder block, the beginning of `DP2`, and the beginning of `DIG2`. It is instance-aligned register metadata: `DP1`/`DIG1` and `DP2`/`DIG2` expose parallel fields for separate display output pipelines.

## Purpose

The purpose of this chunk is to describe the bit layout for DisplayPort, HDMI/TMDS, HDCP, audio infoframe, generic packet, FIFO, CRC, and low-power panel/link features on DCN 4.1.0 DIO/DIG hardware instances. Driver code does not hard-code these bit positions; it includes generated offset headers and this shift/mask header, then uses common display register helpers to read, write, poll, and update fields.

Important areas in this slice:

- `DP1_DP_SEC_*`, `DP1_DP_GSP*`, `DP1_DP_AUXLESS_ALPM_*`, and `DP1_DP_*SYMBOL_COUNT*`: DisplayPort secondary data packet scheduling, generic SDP channels, double-buffer state, ALPM/panel replay support, and link/stream counters for instance 1.
- `DIG1_DIG_FE_*`, `DIG1_DIG_BE_*`, `DIG1_DIG_FIFO_*`, and `DIG1_DIG_OUTPUT_CRC_*`: DIG front-end/back-end routing, clock/reset/enable gates, FIFO calibration/status, and output CRC/test pattern fields.
- `DIG1_HDMI_*`: HDMI metadata, control/status, ACR, VBI, infoframe, generic packet, general control, and double-buffer controls.
- `DIG1_HDCP_*`: HDCP interrupt/status, I2C handoff, link 0/link 1 status, reset, and receiver local data fields such as BKSV, AKSV, RI/PJ, AN, V prime, BCAPS, and BSTATUS.
- `DIG1_TMDS_*`: TMDS sync/control character, stereo sync, DC balancer, and generated control symbol fields.
- `DP2_DP_*`: the next DisplayPort instance with link control, pixel format, MSA, stream enable, DPHY training/CRC/FEC/scrambler/PRBS, transfer unit, MST/MSE slot allocation, secondary packet/audio timing, MSO, ALPM, symbol counters, and panel replay fields.
- `DIG2_DIG_FE_*` through `DIG2_HDMI_INFOFRAME_CONTROL1`: start of the second DIG display encoder instance, mirroring the DIG1 front-end, FIFO, HDMI, ACR, VBI, and infoframe fields.

## Important Macros and Field Families

The core API exported by this chunk is the macro naming contract:

- `<REG>__<FIELD>__SHIFT` gives the starting bit position.
- `<REG>__<FIELD>_MASK` gives the field mask within a 32-bit MMIO register.
- Repeated instances keep identical field names with different register prefixes, for example `DIG1_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN__SHIFT` and `DIG2_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN__SHIFT`.

Notable register families:

- DisplayPort secondary packet controls: `DP*_DP_SEC_CNTL`, `DP*_DP_SEC_CNTL1` through `DP*_DP_SEC_CNTL7`, `DP*_DP_GSP8_CNTL` through `DP*_DP_GSP11_CNTL`, and `DP*_DP_GSP_EN_DB_STATUS`. These fields model enable, send, pending, active, deadline-missed, line-reference, line-number, priority, and double-buffer disable/pending behavior for GSP and other secondary packets.
- DisplayPort link/PHY controls: `DP2_DP_LINK_CNTL`, `DP2_DP_DPHY_CNTL`, `DP2_DP_DPHY_TRAINING_PATTERN_SEL`, `DP2_DP_DPHY_FAST_TRAINING`, `DP2_DP_DPHY_FAST_TRAINING_STATUS`, `DP2_DP_DPHY_CRC_*`, `DP2_DP_DPHY_PRBS_CNTL`, and `DP2_DP_DPHY_SCRAM_CNTL`. These are integration points for link training, FEC/ALPM interactions, CRC validation, scrambler control, and physical-layer test patterns.
- MST/MSE controls: `DP2_DP_MSE_RATE_CNTL`, `DP2_DP_MSE_SAT0/1/2`, matching `*_STATUS` registers, `DP2_DP_MSE_SAT_UPDATE`, `DP2_DP_MSE_LINK_TIMING`, and `DP2_DP_MSE_MISC_CNTL`. These describe stream allocation table programming and status for multi-stream transport.
- DIG/HDMI packet controls: `DIG*_HDMI_GENERIC_PACKET_CONTROL0/1/2/3/4/5/6/7/8/9/10`, `DIG*_HDMI_METADATA_PACKET_CONTROL`, `DIG*_HDMI_INFOFRAME_CONTROL0/1`, and `DIG*_HDMI_VBI_PACKET_CONTROL`. These fields control scheduled and immediate sends, line numbers, continuations, update-lock behavior, and pending status.
- HDCP controls for DIG1: `DIG1_HDCP_INT_CONTROL`, `DIG1_HDCP_LINK0_STATUS`, `DIG1_HDCP_LINK1_STATUS`, `DIG1_HDCP_I2C_CONTROL_*`, `DIG1_HDCP_I2C_STATUS`, `DIG1_HDCP_RESET`, and local receiver data registers. These map authentication result interrupts, ack/mask bits, DDC selection, retries/timeouts/NACKs, deauthentication, and protocol data storage.

## Control Flow and Runtime Integration

There is no direct control flow in this header. Runtime flow is indirect:

1. ASIC-specific resource files include the DCN 4.1.0 offset and shift/mask headers.
2. Resource constructors populate register address, shift, and mask tables with macros such as `SR`, `SRI_ARR`, and `SF`.
3. Hardware blocks such as DIO stream encoders, link encoders, AFMT/audio, HDCP, and DisplayPort helpers call register helper macros (`REG_UPDATE`, `REG_GET`, `REG_WAIT`, `REG_SET`, `REG_UPDATE_N`).
4. The helper macros expand a register and field pair through `FN(reg, field)`/`FD(...)` into the shift and mask constants from this header, then call generic MMIO helpers.
5. Hardware state changes occur in MMIO registers, not in this file.

For example, an HDMI or DP stream encoder operation may set an enable/send/pending bit by naming the logical field. The generic register helper uses the generated `__SHIFT`/`_MASK` constants here to update only the target bit range. This makes the correctness of these constants critical even though this file contains no executable logic.

## State and Persistence Behavior

The header itself has no persistent state. It defines symbolic compile-time constants.

The state represented by the fields is hardware state:

- Pending/taken/ack/clear bits such as `DP*_DP_DB_CNTL`, `DIG*_HDMI_DB_CONTROL`, `*_SEND_PENDING`, `*_DEADLINE_MISSED`, `*_INT`, `*_ACK`, and `*_MASK` are latched by display hardware and observed or cleared by the driver.
- Double-buffer fields (`*_DB_*`, `*_EN_DB_PENDING`, `*_UPDATE_LOCK_DISABLE`) affect when packet or timing changes become active relative to vertical update or programmed line timing.
- Status fields such as HDMI errors, HDCP authentication result, DPHY CRC validity, fast-training completion, FIFO reset done/error, and ALPM wakeup status reflect live hardware progress.
- Local HDCP data registers expose protocol material read from or written through the HDCP engine and DDC/I2C path.

Persistence is therefore device-local and reset-sensitive. Values survive only as long as the relevant display engine/register block retains power and is not reset. Driver suspend/resume, mode set, link training, or stream disable paths must reprogram relevant fields from higher-level display state.

## Dependencies

This chunk depends on matching generated register offset definitions in `dcn_4_1_0_offset.h`; shifts/masks alone do not identify MMIO addresses. It also depends on the display core register helper layer in `drivers/gpu/drm/amd/display/dc/inc/reg_helper.h` and similar DMUB helpers, where `REG_GET`/`REG_UPDATE`/`REG_WAIT` combine register addresses with field shifts and masks.

Consumers are expected in AMD display modules that manage:

- DisplayPort stream/link encoders and DPHY operations under `display/dc/dio/`.
- AFMT/audio packet programming and HDMI infoframes.
- HDCP authentication and DDC/I2C handoff.
- Resource tables for DCN ASIC variants, where instance arrays map `DP1`/`DIG1` and `DP2`/`DIG2` registers to block instances.
- Diagnostic paths that use CRC, PRBS, test pattern, symbol count, and error status fields.

Because this is generated silicon metadata, its semantic dependency is the DCN 4.1.0 hardware specification. Manual changes should be treated as high risk unless they are synchronized with the register database and matching offset headers.

## Integration Points

The most important integration point is the macro-name ABI between generated headers and display block source. If a consumer calls `REG_UPDATE(HDMI_CONTROL, HDMI_DATA_SCRAMBLE_EN, value)` through a per-instance register table, the table must have been built from the correct `DIGx_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN__SHIFT` and mask. Similarly, DP link training or secondary-packet code depends on the `DPx_DP_*` field names matching the corresponding register list in resource headers.

Instance mirroring is also an integration constraint. `DIG1` and `DIG2`, and similarly `DP1` and `DP2`, must have consistent field layouts unless the hardware intentionally diverges. A mismatch between instance prefixes can produce bugs that only appear on one physical connector or stream encoder.

The chunk also bridges multiple protocol layers:

- DP fields integrate with link training, MST allocation, FEC, ALPM, panel replay, and secondary data packets.
- HDMI fields integrate with TMDS link setup, scrambling, deep color, ACR/audio clock regeneration, generic packets, and metadata/infoframes.
- HDCP fields integrate authentication state, interrupt handling, and DDC/I2C transactions.

## Risks and Failure Modes

- Incorrect shift or mask values can corrupt neighboring fields in the same 32-bit register, causing link training failures, incorrect packet scheduling, broken HDMI metadata, HDCP authentication failures, or display blanking.
- Instance prefix mistakes (`DIG1` vs `DIG2`, `DP1` vs `DP2`) can silently program the wrong encoder instance when resource arrays are generated or maintained.
- Pending/ack/clear bit semantics are easy to misuse. Writing a status or ack bit with the wrong mask can lose interrupts or leave hardware stuck waiting for a double-buffer update.
- Wide masks such as `0xFFFFFFFFL` and high-bit masks such as `0x80000000L` require unsigned-safe handling in helper code. The constants use `L` suffixes; consumers should avoid signed truncation assumptions.
- HDCP local data and I2C status fields are protocol-sensitive. Wrong field definitions can break protected-content playback or cause DDC retry/timeout handling to misreport failures.
- DP ALPM, FEC, panel replay, and fast training fields interact with timing-sensitive link state. Register metadata drift can produce intermittent failures that depend on sink capability, refresh timing, or low-power transitions.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: all DCN 4.1.0 display resource and DIO modules build with no missing `__SHIFT`/`_MASK` macro names.
- Register table sanity: generated `shift` and `mask` tables for DP/DIG instances contain the expected values and match the offset header instance mapping.
- DisplayPort functional tests: link training across rates/lane counts, MST stream allocation, FEC enable/disable, ALPM transitions, panel replay, secondary data packet transmission, and stream/link symbol counter reads.
- HDMI functional tests: deep color, scrambling, audio ACR for 32/44.1/48 kHz families, infoframe and generic packet scheduling, VBI packet paths, metadata packet line timing, and AVMUTE behavior.
- HDCP tests: HDCP auth success/fail interrupts, ACK/mask handling, DDC/I2C transfer request/done paths, retry/timeout/NACK status, deauthentication, and dual-link status reads.
- Diagnostics: output CRC enable/result, DPHY CRC, PRBS/test pattern generation, FIFO reset/calibration/error bits, TMDS DC balancer and control-symbol generation.
- Multi-instance smoke tests: exercise connectors or pipes backed by both `DIG1`/`DP1` and `DIG2`/`DP2` to catch prefix or array-index mismatches.

## Chunk Notes

This chunk begins in the middle of the `DP1_DP_MSO_CNTL1` definitions and ends at `DIG2_HDMI_INFOFRAME_CONTROL1__HDMI_AUDIO_INFO_LINE_MASK`; neighboring chunks are needed for the complete register set before producing a final per-file report. The observations above are limited to the visible register sections in lines 32639-35043.
