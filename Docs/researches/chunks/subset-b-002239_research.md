# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 52360-54779

## Scope

This chunk is part of the generated AMD DCN 4.2.0 ASIC register shift/mask header. It contains C preprocessor constants only: each hardware field is exported as a `...__SHIFT` bit position and a matching `..._MASK` bit mask. There are no functions, structs, branches, allocations, locks, or direct MMIO accesses in this range.

The range contains 2,118 `#define` entries and spans HPO DisplayPort stream/link encoder register families. It starts at the tail of `DP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1`, then covers APG/DME/VPG, DP SYM32 encoder, link encoder, and DPHY SYM32 blocks for stream/link instances 1 and 2, and ends inside the VPG8 immediate-update fields for stream encoder 3. Adjacent chunks are needed for complete boundary context around the first `DP_STREAM_ENC1` FIFO register and the remaining `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL` fields.

## Purpose

The purpose of this chunk is to publish the bitfield contract for DCN 4.2.0 HPO DisplayPort stream processing and symbol/link transmission blocks. Runtime AMDGPU display code combines these field macros with matching offset definitions from `dcn_4_2_0_offset.h` and AMD display register helpers to program DisplayPort stream encoders, audio/debug packet generators, metadata engines, generic secondary-data packets, symbol encoders, link clocks, and DP physical-layer symbol scheduling.

Important covered areas:

- `DP_STREAM_ENC1/2/3` stream encoder control surfaces: clock enables/status, pixel stream mux selection, audio stream mux selection, APG clock enable, clock-ramp FIFO reset/read-level/calibration/status/error fields, and spare fields.
- `APG6/7/8` audio packet generator support: debug generator enable/reset, per-channel audio enable, test-channel disable, and APG memory power force/disable/state/default-low-power controls.
- `DME6/7/8` metadata engine support: HUBP requestor selection, metadata enable, stream type, double-buffer pending/taken/clear/disable states, missed-transmission detection/clear, and DME memory power controls.
- `VPG6/7/8` video packet generator support: generic packet RAM indexed access, generic packet byte packing, frame-update and immediate-update triggers/pending bits for 15 generic packets, conflict/lock status, VPG memory light-sleep controls, and ISRC indexed data for VPG6/7. VPG8 is only partially present in this chunk.
- `DP_SYM32_ENC1/2` symbol encoder support: enable/reset/status, pixel-to-symbol FIFO controls, MSA and pixel-format double buffering, MSA payload registers, HBLANK symbol width, 15 GSP SDP control registers, SDP/audio/metadata packet controls, MSA/VBID/video-stream controls, panel replay tunneling optimization, video CRC, symbol counters, ALPM sleep/wake scheduling, wake interrupts, memory power, and spare fields.
- `DP_LINK_ENC1/2` link encoder clocks: link encoder clock enable/on-status on `SYMCLK32`, plus spare fields.
- `DP_DPHY_SYM321/322` physical/link symbol scheduler fields: DPHY enable/reset, precoder, mode, lane count, output mode, sleep start, status, SAT updates, VC rate controls, stream allocation table programming/status, eDP security/ASSR seeds, ALPM timing, training pattern generation, PRBS/custom pattern data, error status, and LLCP/cycle symbol counters.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` is the bit offset of a field in the hardware register.
- `<REGISTER>__<FIELD>_MASK` is the field mask to preserve adjacent fields during masked updates.
- Prefixes identify replicated hardware instances. `DP_STREAM_ENC2_*`, `DP_SYM32_ENC2_*`, `DP_LINK_ENC2_*`, and `DP_DPHY_SYM322_*` belong to the second HPO DP path; APG/DME/VPG instance numbers are offset (`APG7`, `DME7`, `VPG7`) for stream encoder 2.

Notable field families include:

- Stream encoder FIFO and clocking: `DP_STREAM_ENC*_DP_STREAM_ENC_CLOCK_CONTROL`, `...INPUT_MUX_CONTROL`, `...AUDIO_CONTROL`, and `...CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL0/1` define enable/status bits, source selection, FIFO reset/read-start level/read-clock source, video-active, overflow/underflow error, overwrite level, recalibration, min/max/average levels, and calibrated status.
- Packet generation and metadata: `APG*_APG_DBG_GEN_CONTROL`, `DME*_DME_CONTROL`, and `VPG*_VPG_GENERIC_PACKET_*` fields support audio debug packets, metadata packet handoff from HUBP, generic secondary-data packet storage, and update synchronization.
- VPG update control: `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `...IMMEDIATE_UPDATE_CTRL` have paired trigger bits and pending bits for `VPG_GENERIC0` through `VPG_GENERIC14`, allowing packet changes to be synchronized to frame boundaries or applied immediately.
- Symbol encoder video programming: `DP_SYM32_ENC*_VID_PIXEL_FORMAT`, `...VID_MSA0` through `...VID_MSA8`, `...VID_MSA_CONTROL`, `...VID_VBID_CONTROL`, and `...VID_STREAM_CONTROL` carry pixel encoding/depth, main stream attributes, compressed-stream flag timing, and stream enable/defer/status behavior.
- Secondary-data packet scheduling: `DP_SYM32_ENC*_SDP_GSP_CONTROL0` through `...CONTROL14`, `...SDP_CONTROL`, `...SDP_AUDIO_CONTROL0/1`, and `...SDP_METADATA_PACKET_CONTROL` define continuous or one-shot GSP transmission, idle/video transmission enable, payload size, SOF reference, line-number scheduling, pending/deadline flags, CRC16 enable, ASP/ATP/AIP/ACM/ISRC audio packet enablement, audio mute, and metadata packet double buffering.
- Low-power and diagnostics: `DP_SYM32_ENC*_ALPM_*`, `...VID_CRC_*`, and `...SYMBOL_COUNT_*` fields define ALPM sleep/wake request timing, hardware mode/status/start state, wake interrupts, CRC result/valid/ack fields, and BS symbol counters.
- DPHY scheduling and allocation: `DP_DPHY_SYM32*_CONTROL`, `STATUS`, `SAT_UPDATE`, `VC_RATE_CNTL0-3`, `SAT_VC0-3`, and `SAT_VC_STATUS0-3` configure active/test/training modes, lane count, output target, stream virtual-channel rates, stream allocation slots, encryption flags, and update/status polling.
- DPHY eDP, ALPM, and training/test support: `EDP_CONFIG0`, `EDP_ASSR0-3`, `ALPM_SLEEP_CONFIG0`, `ALPM_WAKE_CONFIG0`, `ALPM_CONTROL`, `TP_CONFIG`, `TP_PRBS_SEED0-3`, `TP_SQ_PULSE`, and `TP_CUSTOM0-10` expose embedded DisplayPort security/ASSR seed programming, low-power pattern timing, training pattern selection, PRBS seeds, square pulse width, and custom pattern words.
- DPHY error and counter status: `ERROR_STATUS`, `SYMBOL_COUNT_STATUS0/1`, and `SYMBOL_COUNT_CONTROL` publish total-slot, rate, duplicate stream-source, missing ACT, unexpected mode transition, illegal symbol, counter overflow, cipher, ALPM wake timing, LLCP count, and cycle count signals.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime flow is indirect:

1. DCN 4.2 display components include this header with `dcn_4_2_0_offset.h`.
2. Register tables or helper macros pair a `reg...` offset with the corresponding `__SHIFT` and `_MASK` definitions.
3. AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and indexed variants perform masked MMIO or indirect register operations.
4. Hardware then applies the state changes in stream encoder, packet generator, symbol encoder, link encoder, and DPHY blocks.

The represented hardware flow is typically: enable clocks for the stream/link path, choose pixel and audio sources, configure video format and MSA data, program generic/audio/metadata SDP packets, arm double-buffered or immediate updates, enable the video stream, configure DPHY mode/lane count/rate/allocation-table state, and poll status/pending/error/counter fields for completion or failure.

## State and Persistence Behavior

The file itself has no mutable or persistent state. All state described by these macros lives in GPU display hardware registers.

Hardware state represented in this chunk includes:

- Clock and reset state for stream encoders, SYM32 encoders, link encoders, APG/DME/VPG memory blocks, and DPHY symbol scheduler blocks.
- Stream routing state, including pixel-stream and audio-stream source selectors.
- FIFO calibration and health state, including reset-done, active-video, error, level, min/max, average, overwrite, and calibrated bits.
- Packet RAM and packet scheduling state for VPG generic packets, ISRC data, SYM32 GSP SDP controls, audio packets, and metadata packets.
- Double-buffer and pending state for MSA, pixel format, GSP packets, metadata packets, frame updates, immediate updates, ALPM requests, and wake interrupts.
- Video link state for MSA payloads, pixel encoding/depth, HBLANK symbol width, VBID compressed-stream flags, stream enable/defer/status, panel replay tunneling optimization, CRC results, and symbol counters.
- DPHY state for mode/lane/output configuration, SAT and VC rate programming, eDP security/ASSR, ALPM pattern timing, training/test pattern generation, error flags, and LLCP/cycle counters.

Persistence is limited to hardware programming lifetime. Values can be lost or require reprogramming after display engine reset, GPU reset, power gating, suspend/resume, hotplug retraining, mode set, stream reallocation, or link disable. Higher-level DC state, link-training policy, and DMUB firmware state remain the durable software authority; these macros only define how software encodes bits in the hardware registers.

## Dependencies

This chunk depends on:

- `dcn_4_2_0_offset.h`, which supplies the register addresses corresponding to these field names.
- AMD display register-helper infrastructure that token-pastes register and field names into masked reads/writes/updates/waits.
- DCN 4.2 display components that include the generated mask header, including DMUB support, IRQ service, resource construction, GPIO translation/factory code, and clock-manager code.
- Generated register tables and DCN 4.2 hardware descriptions that keep stream/link instance prefixes aligned across offset and mask headers.
- Related enum definitions such as the SOC24 `DP_STREAM_ENC`, `DP_SYM32_ENC`, and `DP_DPHY_SYM32` enum blocks, which document expected symbolic values for many of these bitfields.

Because the header is generated silicon metadata, manual edits are risky unless regenerated from the same register database as the offsets and any associated register tables.

## Integration Points

Main integration points are the macro-name ABI and register-field layout contract consumed by AMDGPU display code.

- Display mode programming uses `DP_STREAM_ENC*` and `DP_SYM32_ENC*` fields to route streams, program pixel format/MSA, configure stream enable/defer behavior, and synchronize double-buffered updates.
- Audio and secondary-data packet programming uses APG, VPG, DME, and SYM32 SDP fields to transmit audio, generic packets, ISRC, metadata, and other DisplayPort sideband data with frame or line timing.
- Link training and link operation use DPHY control/status, training pattern, lane-count, mode, rate, SAT, and error fields to transition from training patterns to active transmission and to diagnose protocol-level problems.
- Power management uses APG/DME/VPG/SYM32 memory power fields, ALPM sleep/wake scheduling, wake interrupts, and DPHY ALPM controls.
- Validation and debug paths use CRC result/status, symbol counters, FIFO error/level fields, DPHY error status, PRBS/custom pattern controls, LLCP/cycle counters, generic packet conflict status, and deadline/pending bits.
- DMUB/DCN42 resource and clock code depend on the generated header resolving consistently when building register tables or firmware-facing control paths.

## Risks and Failure Modes

- A wrong shift or mask can corrupt neighboring fields in the same 32-bit register, causing blank display, bad packet timing, audio loss, metadata loss, broken ALPM entry/exit, or link-training failures.
- Instance-prefix mistakes are easy in this repeated generated section. A field from stream 1, 2, or 3 can compile while targeting the wrong stream/link/APG/DME/VPG/DPHY instance if paired with the wrong offset macro.
- Boundary incompleteness matters: this chunk starts after some `DP_STREAM_ENC1` FIFO fields and ends before the rest of `VPG8_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, so final per-file synthesis must reconcile neighboring chunks before drawing whole-register conclusions.
- Pending, clear, reset, and status bits have hardware-specific write semantics. Misusing masks for `*_PENDING`, `*_CLR`, `*_RESET`, `*_RESET_DONE`, `*_VALID_ACK`, `*_OCCURRED`, or `*_CLEAR` fields can hang update flows or lose diagnostics.
- Generic packet update conflicts can happen if VPG lock/conflict fields and frame/immediate pending bits are ignored when packet RAM is rewritten.
- DPHY SAT/VC rate mistakes can allocate the wrong stream source, slot count, or rate, producing protocol errors that only appear at specific lane counts, link rates, MST/SST layouts, or DSC/compression modes.
- ALPM and eDP ASSR/security fields are timing-sensitive. Incorrect masks can create intermittent resume/wake failures, early wake requests, unexpected mode transitions, or panel-specific blanking.
- High-bit masks such as `0x80000000L`, `0xFFFF0000L`, and `0xFE000000L` require unsigned-safe register math in consumers.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Build coverage for DCN 4.2 display code with all referenced `DP_STREAM_ENC*`, `APG*`, `DME*`, `VPG*`, `DP_SYM32_ENC*`, `DP_LINK_ENC*`, and `DP_DPHY_SYM32*` `__SHIFT`/`_MASK` symbols resolving.
- Register-generation consistency checks comparing `dcn_4_2_0_sh_mask.h` against the matching `dcn_4_2_0_offset.h` and the authoritative DCN 4.2 register database.
- Display smoke tests covering DP/eDP mode set, hotplug, link retraining, suspend/resume, GPU reset, stream enable/disable, MST if supported, DSC/compressed stream paths, and different lane-count/link-rate combinations.
- Packet tests covering generic SDP/VSC/HDR-style metadata, ISRC, audio packet enable/mute, metadata double buffering, VPG frame/immediate update pending bits, and packet conflict status.
- Link/PHY diagnostics covering DPHY mode/lane/output programming, SAT update pending/status, VC rate programming, training pattern generation, PRBS/custom pattern paths, DPHY error status, LLCP/cycle counters, and link error recovery.
- Power-management tests covering APG/DME/VPG/SYM32 memory power state transitions, ALPM sleep/wake request timing, ALPM wake interrupt occurrence/clear behavior, and panel replay tunneling optimization.
- CRC/counter validation using SYM32 video CRC valid/ack/result fields and BS symbol counters to confirm stream data path integrity.

## Chunk Notes

This is a source-tree-aligned chunk research document only. It intentionally does not create the final per-file report for `dcn_4_2_0_sh_mask.h`; that synthesis belongs to the merge/reconciliation lane after all chunks for the generated header are available.
