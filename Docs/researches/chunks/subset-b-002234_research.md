# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 40201-42616

## Scope

This chunk is part of the generated AMD DCN 4.2.0 ASIC register shift/mask header. It contains preprocessor constants only: each hardware field is represented by a `...__SHIFT` bit offset and a matching `..._MASK` bit mask. There are no C functions, structs, branches, allocations, locks, direct MMIO accesses, or persistence mechanisms in this range.

The slice contains 2,165 `#define` entries across 224 register-comment blocks and 9 `addressBlock` markers. It starts inside the DP0 AUX-less ALPM register family at `DP0_DP_AUXLESS_ALPM_CNTL2__DP_ML_PHY_SLEEP_HOLD_TIME__SHIFT` and ends inside `DIG2_DIG_OUTPUT_CRC_CNTL` after the shift definitions, before the corresponding masks. Adjacent chunks are required to reconstruct the complete `DP0_DP_AUXLESS_ALPM_CNTL1/2` boundary context and the full `DIG2_DIG_OUTPUT_CRC_CNTL` register.

## Purpose

The purpose of this chunk is to publish exact bitfield metadata for DCN 4.2.0 display I/O blocks. Runtime display code uses these generated names with matching register-address headers and AMD display register-helper macros to read, update, poll, or write individual register fields without hard-coded bit arithmetic.

Major covered areas:

- Tail of DP0 DisplayPort controls: AUX-less ALPM sleep/wakeup/FEC timing, stream and link symbol counters, panel replay tunneling optimization, and DPHY fast-training controls/status.
- DIG1 VPG, APG, DME, and front/back-end digital encoder blocks: generic packet storage/update controls, ISRC packet access, audio packet generation/debug/CRC/status, metadata engine control, DIG FE/BE clocking, test patterns, FIFOs, HDMI packet controls, TMDS controls, and DIG version.
- DP1 DisplayPort transport block: link control, pixel format, MSA/timing fields, stream control, FIFO steering, DPHY training/test/CRC/scrambler/TU controls, secondary-data/audio/metadata packet controls, MST/MSE scheduling, ALPM, GSP double-buffer status, symbol counters, panel replay, and fast training.
- DIG2 VPG/APG/DME blocks: instance-2 copies of the generic video-packet generator, audio packet generator, and metadata engine bitfields.
- Opening DIG2 front-end fields: source selection, stereosync, digital bypass, FE clock/reset/gating status, FE enable, and the first output-CRC control shifts.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit position inside the register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by register-helper update paths.
- Instance prefixes are semantically important. `DP0_`, `DIG1_`, `DP1_`, `VPG2_`, `APG2_`, `DME2_`, and `DIG2_` map these fields to specific display pipe, packet, audio, metadata, or link instances.

Important register families in this chunk include:

- `DP0_DP_AUXLESS_ALPM_CNTL2` through `CNTL5`: sleep hold time, wakeup send/immediate/pending, FEC enable immediate/pending, ML PHY lock period, wakeup/FEC line numbers, hardware-mode enable/status, current ALPM state, frame number, wakeup interrupt mask/occurred/status/clear, and interrupt frame/line capture.
- `DP0_DP_STREAM_SYMBOL_COUNT_*` and `DP0_DP_LINK_SYMBOL_COUNT_*`: stream BS count, link SR count, link cycle count, enable bits, and reset bits for symbol-count diagnostics.
- `DP0_DP_SYM8_ENC_VID_PANEL_REPLAY_CONTROL`: panel replay tunneling optimization enable, double-buffer enable, and double-buffer pending status.
- `DP0_DP_DPHY_FAST_TRAINING*`: RX fast-training capability, software start, VBlank edge detect, stream reset behavior, TP1/TP2 timing, fast-training state, completion occurrence, interrupt mask, and acknowledge fields.
- `VPG1_*` and `VPG2_*`: generic packet byte-indexed access, 15 generic packet frame-update and immediate-update bits, pending/status mirrors, memory power controls, and ISRC1/2 data access.
- `APG1_*` and `APG2_*`: audio enable/HBR/sample-rate/source selection, debug generator controls, packet send flags, ACP and audio-info packet fields, IEC 60958 channel-status fields, audio CRC control/result, debug ramp counters, status/overflow clear, DTO debug fields, memory power controls, and spare bits.
- `DME1_*` and `DME2_*`: metadata HUBP requestor selection, engine enable, stream type, double-buffer pending/taken/clear/disable, missed-transmission status/clear, and DME memory power controls.
- `DIG1_*`: front-end source/stereosync/bypass selection, FE clock/reset/gating, FE enable, output CRC control/result, clock/test/random pattern generation, FIFO reset/start/clock-source/pixel-per-cycle/status, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet controls, DB control, ACR values and readback status, FE audio control, BE clock/control/enable, TMDS control-character/sync/DC-balance/control-bit generation, and version fields.
- `DP1_*`: DP link control, pixel format/colorimetry/configuration, stream control, FIFO steering, MSA misc/timing/VBID, DPHY internal/training/symbol/8b10b/PRBS/scrambler/CRC controls, TU control, secondary data/audio/timestamp/packet controls, MSE SAT/rate/timing/status fields, MSO/steer FIFO controls, metadata transmission, ALPM, GSP enable double-buffer status, AUX-less ALPM, symbol counters, panel replay, and fast-training fields.
- `DIG2_DIG_FE_*` and partial `DIG2_DIG_OUTPUT_CRC_CNTL`: front-end source/stereosync/bypass selection, clock/reset/gated-clock state, FE enable, and output CRC enable/link/data selection shift definitions.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. DCN 4.2.0 display code includes this generated shift/mask header with the matching register offset/address headers.
2. Register tables and helper macros pair a register address, such as a `mm` or `ix` offset from the companion headers, with the field shift/mask constants from this file.
3. The AMD display driver uses masked register get/set/update/wait helpers to isolate fields and program the display hardware.
4. Hardware state changes occur in the display, DP, HDMI/TMDS, audio, packet, metadata, and PHY-related registers; this file only supplies compile-time metadata for those operations.

The represented flow is typically: select and enable a DIG front end, configure DP or HDMI/TMDS output formatting and timing, program packet/audio/metadata generators, arm double-buffered updates, drive DP link training or fast training, optionally enable ALPM or panel replay behavior, and poll status/CRC/counter/pending fields for validation or completion.

## State and Persistence Behavior

The file itself has no mutable or persistent state. All state described by these macros resides in hardware registers.

The hardware state represented by this chunk includes:

- Link and stream state: DP link enable/control, training pattern and DPHY modes, TU settings, pixel format/colorimetry, MSA timing and VBID, MST/MSE slot/rate scheduling, MSO control, ALPM state, panel replay optimization, and fast-training state.
- Packet-generation state: VPG generic packet data, generic packet update/immediate-update/pending flags, HDMI generic/infoframe/audio/ACR/VBI packet controls, GSP enable double-buffer pending status, ISRC packet contents, and secondary-data packet controls.
- Audio and metadata state: APG audio enable/HBR/sample-rate/source/debug-generator fields, IEC 60958 channel status, audio CRC counters/results, audio FIFO overflow status, DME metadata engine enable, HUBP requestor, DB pending/taken state, and missed-transmission status.
- Digital encoder state: DIG FE/BE source selection, bypass paths, clock enables, resets, gated-clock status, FIFO enable/reset/read-start state, test/random/clock pattern controls, TMDS sync/control/DC-balance fields, and output CRC selection/result.
- Power-management state: VPG/APG/DME memory power disable/force/state/default low-power fields and DP AUX-less ALPM sleep/wakeup timing.

Persistence is limited to the lifetime of the hardware register programming. Values can be lost or require reprogramming after GPU reset, display engine reset, DIG/DP block reset, power gating, suspend/resume, hotplug retraining, mode set, or link reconfiguration. Higher-level display state in the driver remains the source of truth.

## Dependencies

This chunk depends on matching generated DCN 4.2.0 register-address headers. Shift and mask constants alone do not identify an MMIO or indirect register address.

It also depends on:

- AMD display register-helper infrastructure that consumes generated `__SHIFT` and `_MASK` names for masked reads, writes, updates, and polling.
- DCN 4.2.0 silicon register specifications or register database inputs used to generate this header.
- Display core, link encoder, DP, HDMI/TMDS, audio, metadata, and packet-generator code that programs these fields during mode set, link training, packet emission, audio bring-up, power management, and diagnostics.
- Generated register descriptor tables that preserve correct instance naming for DP0/DIG1/DP1/DIG2 and their VPG/APG/DME sub-blocks.

Because this is generated silicon metadata, manual changes are risky unless synchronized with the register database, companion offset headers, and any generated register tables.

## Integration Points

Primary integration points are the macro names used by AMD display code and register tables. A consumer naming a field such as `DP1_DP_DPHY_TRAINING_PATTERN_SEL__DPHY_TRAINING_PATTERN_SEL` or `DIG1_HDMI_GENERIC_PACKET_CONTROL0__HDMI_GENERIC0_SEND` relies on this header to supply the correct bit position and mask.

Integration surfaces include:

- DP link bring-up and training: `DP1_DP_LINK_CNTL`, `DP1_DP_CONFIG`, DPHY training/symbol/8b10b/PRBS/scrambler/CRC controls, TU control, MSA timing, VBID, and fast-training status.
- DP power and replay features: DP0 and DP1 AUX-less ALPM timing/status/interrupt fields, panel replay tunneling optimization, wakeup and FEC enable timing, and symbol counters.
- HDMI/TMDS output: DIG1 HDMI packet controls, ACR values/status, GC and infoframe controls, TMDS control characters, sync patterns, DC-balancer controls, and BE clock/control/enable bits.
- Packet and metadata generators: VPG generic packets, ISRC access, APG audio packets/status/CRC/debug fields, DME metadata engine state, and secondary-data packet controls.
- Diagnostics and validation: output CRC, DPHY CRC, stream/link symbol counters, audio CRC, random/test/clock patterns, FIFO reset/status fields, GSP pending status, metadata missed transmission flags, and APG overflow status.
- Multi-instance display mapping: the instance prefixes in this chunk must remain aligned with the matching address namespace so writes target DP0, DIG1, DP1, VPG2/APG2/DME2, or DIG2 as intended.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent fields in the same register, causing blank display, broken link training, invalid HDMI/DP packet emission, audio loss, metadata loss, CRC false positives, or unstable power transitions.
- Instance-prefix mistakes can compile cleanly while programming the wrong display pipe or packet/audio/metadata engine.
- Double-buffer and pending fields require correct semantics. Misprogramming generic packet, GSP, MSE SAT, or metadata DB fields can leave stale packets active or prevent updates from taking effect.
- ALPM, panel replay, and fast-training fields affect timing-sensitive DP behavior. Wrong masks can cause missed wakeups, FEC timing errors, failed fast training, or intermittent link recovery issues.
- HDMI/TMDS packet and ACR fields are format-sensitive. Bad bit definitions can break sink audio/video interpretation even when the link remains electrically active.
- Status/clear fields, such as audio FIFO overflow clear, metadata missed-transmission clear, fast-training acknowledge, CRC clear/done, and DB taken clear, must be updated with precise masks to avoid losing events or holding stale state.
- This chunk starts and ends inside larger register families. A final per-file report must reconcile the partial `DP0_DP_AUXLESS_ALPM_CNTL2` beginning context and the partial `DIG2_DIG_OUTPUT_CRC_CNTL` ending context with neighboring chunks.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DCN 4.2.0 display code builds without missing `DP0_`, `DIG1_`, `DP1_`, `VPG2_`, `APG2_`, `DME2_`, or `DIG2_` shift/mask symbols.
- Register-table sanity: generated register tables pair these field constants with the matching DCN 4.2.0 offsets and preserve correct instance ordering.
- DP smoke tests: DP mode set, hotplug, link retraining, suspend/resume, GPU reset, fast training, AUX-less ALPM entry/exit, panel replay paths, and lane-rate/lane-count variation.
- HDMI/TMDS smoke tests: HDMI mode set, audio enable, ACR programming/readback, infoframe/generic packet transmission, TMDS control character generation, and sink compatibility checks.
- Packet and metadata validation: VPG generic packets, ISRC data, APG audio packets, DME metadata transmission, DB pending/taken transitions, missed-transmission reporting, and GSP pending status.
- Diagnostics: output CRC and DPHY CRC results, stream/link symbol counters, audio CRC done/result, FIFO reset-done/read-start behavior, random/test pattern output, and APG/DME/VPG memory power state readback.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dcn_4_2_0_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.
