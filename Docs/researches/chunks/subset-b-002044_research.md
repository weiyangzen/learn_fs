# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h - subset-b-002044

## Scope

- Chunk id: `subset-b-002044`
- Source lines: 42211-44669
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`
- Observed content: 2,459 source lines with 2,135 `#define` entries, 1,070 `__SHIFT` macros, 1,065 `_MASK` macros, 282 register/block comments, and 21 visible `addressBlock` markers.

This chunk is generated AMD DCN 3.2.1 register field metadata. It does not contain executable C code, structs, enums, storage, or inline helpers. Its public interface is a preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants consumed by AMDGPU display code through generated register tables and MMIO field helpers.

## Purpose

The chunk covers a contiguous part of the DCN 3.2.1 display register mask header:

- The tail of DSC compressor 0 (`DSCC0`) picture parameter set and diagnostic fields: final rate-control range entries, memory power controls, squared-error accumulators, max absolute-error counters, rate-buffer fullness counters, and debug bus rotation.
- DSC compressor/interface/top instances 1 through 3 (`DSCC1`, `DSCC2`, `DSCC3`, `DSCCIF1`, `DSCCIF2`, `DSCCIF3`, `DSC_TOP1`, `DSC_TOP2`, `DSC_TOP3`) plus `DSCCIF0` and `DSC_TOP0` blocks. These define the hardware bit layout for Display Stream Compression configuration, PPS programming, interrupt/status bits, input format reporting, and clock/debug controls.
- HPO top-level and stream mapper fields, including clock gate controls, HPO I/O enable, and four `DP_STREAM_MAPPER_CONTROL*` link-target selectors.
- HPO HDMI stream encoder 0 blocks: `AFMT5` audio formatter, `DME5` metadata engine, and `VPG5` video packet generator.
- HPO DP stream encoder 0 blocks: `DP_STREAM_ENC0`, `APG0` audio packet generator, `DME6` metadata engine, `VPG6` video packet generator, and the beginning of `DP_SYM32_ENC0` symbol encoder controls.

The masks and shifts define how driver code inserts values into 32-bit MMIO registers and extracts status values from them. They are the contract between AMD display driver code, generated register-offset headers, and DCN 3.2.1 display hardware.

## Important APIs, Types, and Macros

There are no normal APIs or C types in this chunk. The important exported interface is the generated naming scheme:

- `REGISTER__FIELD__SHIFT` is the bit position for the least significant bit of a field.
- `REGISTER__FIELD_MASK` is the already shifted mask for that field.
- Consumers combine these with matching offset macros from `dcn_3_2_1_offset.h` and AMD display accessors such as `REG_UPDATE`, `REG_GET`, and generated `*_SF(..., mask_sh)` tables.

Important register families in this chunk include:

- `DSCC*_DSCC_CONFIG0`, `DSCC*_DSCC_CONFIG1`, and `DSCC*_DSCC_STATUS` expose DSC slice layout, ICH behavior, rate-control buffer model size, optional ICH disable, and double-buffer update pending status.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` exposes overflow, underflow, rate-control buffer model overflow, end-of-frame-not-reached status, and the matching interrupt-enable bits for each compressor instance.
- `DSCC*_DSCC_PPS_CONFIG0` through `DSCC*_DSCC_PPS_CONFIG22` encode the DSC PPS register layout: DSC version, PPS identifier, line buffer depth, component depth, bits per pixel, VBR, 4:2:2/4:2:0/native modes, chunk size, picture and slice dimensions, initial delays, scale values and intervals, BPG offsets, initial/final offsets, flatness QP, RC model size, RC edge/quant/tgt offsets, 14 RC buffer thresholds, and 15 range table entries.
- `DSCC*_DSCC_MEM_POWER_CONTROL`, `*_SQUARED_ERROR_*`, `*_MAX_ABS_ERROR*`, and `*_RATE*_MAX_FULLNESS_LEVEL` expose DSC memory low-power controls and hardware diagnostic counters for compression error and rate-buffer fullness.
- `DSCCIF*_DSCCIF_CONFIG0` and `DSCCIF*_DSCCIF_CONFIG1` expose DSC input interface underflow recovery/status, pixel format, bits per component, double-buffer pending state, and picture dimensions.
- `DSC_TOP*_DSC_TOP_CONTROL` and `DSC_TOP*_DSC_DEBUG_CONTROL` expose DSC clock enable/gate controls and debug clock mux selection.
- `HPO_TOP_CLOCK_CONTROL`, `HPO_TOP_HW_CONTROL`, and `DP_STREAM_MAPPER_CONTROL0` through `3` expose HPO clock gating, HPO I/O enable, and stream-to-link mapping.
- `AFMT5_AFMT_*` registers define HDMI/DP audio formatter fields: VBI audio packet limits, layout/channel selection, DP audio stream ID, audio infoframe bytes, IEC 60958 channel status words, audio CRC control/result, ramp generator controls, audio FIFO/status acknowledgments, infoframe update source, audio source select, and AFMT memory power.
- `DME5_DME_*` and `DME6_DME_*` define metadata engine enable, HUBP requestor ID, stream type, double-buffer pending/taken status and clears, missed-transmission status and clears, and memory power controls.
- `VPG5_VPG_*` and `VPG6_VPG_*` define generic packet byte access, frame and immediate update controls for generic packet slots 0 through 14, pending bits, lock/conflict status, memory power controls, ISRC packet byte access, and MPEG infoframe fields.
- `DP_STREAM_ENC0_DP_STREAM_ENC_*` defines stream encoder clock enable/status inputs, pixel and audio source mux selectors, clock-ramp FIFO reset/enable/read-level/calibration/error state, and a spare full-width field.
- `APG0_APG_*` defines DP audio packet generator reset/enable, stream ID, channel count override, debug generator controls, packet source selections, audio CRC controls/results, status/clear bits, memory power controls, and spare fields.
- `DP_SYM32_ENC0_DP_SYM32_ENC_*` begins the 32-symbol DP encoder register set: encoder enable/reset/reset-done, pixel-to-symbol FIFO enable/reset/status, MSA and pixel-format double buffering, pixel encoding/component depth, MSA data words 0 through 8, HBLANK minimum symbol width, and repeated SDP generic stream packet controls.

## Control Flow

This file has no local runtime control flow. The runtime flow is implemented by display driver components that include this header indirectly through generated register tables:

1. A DCN 3.2.1 component selects a register offset from the matching offset header.
2. The component selects the corresponding shift and mask macros from this header.
3. AMD display MMIO helpers insert or extract bitfields through read-modify-write or readback operations.
4. Hardware interprets the resulting register value as DSC setup, packet/audio/metadata control, stream mapping, clock gating, FIFO reset, double-buffer update, or status/interrupt state.

The hardware flows implied by the fields are:

- DSC setup flows program PPS fields, slice count/dimensions, rate-control parameters, and input format before enabling compressed output paths.
- DSC error handling flows observe overflow/underflow/end-of-frame status and may enable corresponding interrupt bits.
- Double-buffered flows set update or enable bits, then poll pending/status bits before assuming new PPS, MSA, pixel-format, generic-packet, or metadata values are active.
- HPO stream routing flows map each DP stream to a link target and enable the required HPO, DP stream, HDMI stream, symbol, metadata, video packet, and audio packet clocks.
- Audio/metadata packet flows write packet bytes through indexed data registers, select sources and stream IDs, trigger frame/immediate updates, and clear taken/missed/conflict/FIFO/CRC status where required.
- DP SYM32 encoder flows reset and enable the encoder and pixel-to-symbol FIFO, program MSA/pixel format/HBLANK/GSP transmission timing, then observe reset-done, FIFO overflow, double-buffer pending, and deadline/pending status fields.

## State and Persistence Behavior

The macros are stateless compile-time constants. They describe hardware state with several lifetimes:

- Persistent configuration until reset or reprogramming: DSC PPS values, slice layout, rate-control buffer model size, input pixel format, clock gate disables, HPO I/O enable, DP stream link target, AFMT/APG source selections, stream IDs, channel enables, packet bytes, MSA data, pixel encoding format, FIFO read-start levels, HBLANK width, and memory power policies.
- Double-buffered or update-gated state: DSC double-buffer pending, DSCCIF double-buffer pending, AFMT audio/infoframe update, DME metadata double-buffer pending/taken, VPG frame/immediate update and pending bits, DP SYM32 MSA/pixel-format double-buffer controls, and repeated GSP double-buffer controls.
- Transient command or clear state: FIFO reset, APG reset, audio FIFO overflow acknowledgments, AZ audio-enable-change acknowledgments, CRC done clears, DME taken/missed clears, VPG conflict clears, metadata missed clears, GSP trigger-one-shot-send, and similar clear/status handshake bits.
- Status and diagnostic state: DSC rate-buffer overflow/underflow, end-of-frame-not-reached, rate-buffer fullness maxima, squared-error and max-absolute-error counters, input underflow status, AFMT/APG audio FIFO overflow and HBR/audio-enable status, DME pending/taken/missed status, VPG lock/conflict status, DP stream FIFO calibrated/min/max/average/error state, and SYM32 FIFO/double-buffer/deadline/pending status.
- Memory power state: DSC, AFMT, DME, VPG, and APG blocks expose low-power disable/force/state fields. These reflect block-level SRAM or small-memory power behavior rather than software persistence.

## Dependencies

This chunk depends on the AMDGPU/DCN generated register infrastructure:

- Matching register offsets in `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`.
- DCN 3.2.1 display code that populates register, shift, and mask tables with `SR(...)`, `DSC_SF(...)`, `SE_SF(...)`, and related macros.
- AMD display MMIO helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_SET`, and field-list macros that expect the generated `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.
- Display component implementations under `drivers/gpu/drm/amd/display/dc/dsc`, `drivers/gpu/drm/amd/display/dc/hpo`, `drivers/gpu/drm/amd/display/dc/clk_mgr`, and `drivers/gpu/drm/amd/display/dc/resource`.
- DCN 3.2.1 resource selection and DMUB ASIC identification paths that choose the correct generated register set for this ASIC generation.

The file is part of the AMDGPU display driver tree. It is not Ceph-specific despite the corpus path prefix `sources/distributed-fs/ceph-client`.

## Integration Points

Likely integration points are:

- DSC encoder creation and programming, where `DSCC*`, `DSCCIF*`, and `DSC_TOP*` fields back per-instance compressor register tables.
- Mode set and bandwidth validation paths that compute DSC PPS values and program slice, rate-control, and color-format fields before enabling compressed transport.
- DSC diagnostics and interrupt handling, where overflow, underflow, end-of-frame, squared-error, max-error, and buffer-fullness fields provide health signals.
- HPO DP stream encoder code, where `DP_STREAM_MAPPER_CONTROL*` maps streams to links and `DP_STREAM_ENC0`/`DP_SYM32_ENC0` fields configure stream source, clocks, FIFO, MSA, pixel format, HBLANK, and SDP generic stream packet scheduling.
- HDMI and DP audio paths, where `AFMT5` and `APG0` fields define audio packet generation, IEC 60958 status, channel selection, stream IDs, CRC, mute/test/status, and overflow acknowledgement behavior.
- Metadata and infoframe paths, where `DME5`, `DME6`, `VPG5`, and `VPG6` fields provide generic packet storage, double-buffer update, ISRC, MPEG, infoframe, and metadata transmission controls.
- Power-management paths, where DSC/AFMT/DME/VPG/APG memory power controls and HPO clock-gate fields must match block enable sequencing.

## Risks and Edge Cases

- Generated mask/shift drift silently corrupts MMIO field access. This is high risk for DSC PPS fields, FIFO reset/status, clock gates, stream routing, audio source selection, and packet update controls because the surrounding C code usually trusts generated constants.
- Repeated instances are nearly identical. `DSCC1`, `DSCC2`, `DSCC3`, `DSCCIF*`, `VPG5`/`VPG6`, and many `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL*` fields can be mixed up by copy/paste while still compiling.
- Chunk boundaries split logical register groups. This chunk begins in the middle of `DSCC0_DSCC_PPS_CONFIG19` and ends in the middle of `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`; adjacent chunks are required for a complete per-file view.
- Some status and clear bits are adjacent or similarly named. Incorrect read-modify-write handling can lose events for audio FIFO overflow, CRC done, metadata taken/missed, VPG conflict, DSC buffer overflow/underflow, and GSP transmission deadline/pending state.
- Double-buffer pending bits require sequencing. Programming MSA, pixel format, DSC PPS, VPG generic packet bytes, or metadata fields without waiting for pending bits to drain can cause stale packets or visible mode-set artifacts.
- PPS range and threshold fields are narrow and packed. Values must be range-checked before shifting; otherwise high bits can bleed into adjacent QP, BPG offset, threshold, or chunk-size fields.
- Full-width diagnostic fields such as squared-error counters and MSA data fields use `0xFFFFFFFFL`; callers need to know whether a register is writable data, read-only status, or latched diagnostic state before writing it.
- Memory power force/disable/state fields are easy to misuse across low-power transitions. Forcing memory on or off in one display block can affect resume, blanking, or metadata/audio packet delivery if not restored.
- Clock gate disable fields have inverted semantics. A field named `*_GATE_DIS` enables or disables gating rather than the clock itself, so call sites must distinguish clock enable from gate override.

## Test Signals

Useful validation signals for code using this chunk:

- Compile coverage for DCN 3.2.1 display with `dcn_3_2_1_sh_mask.h` and the matching offset header to catch missing or renamed generated fields.
- Generated consistency checks that every visible non-empty register field has matching `__SHIFT` and `_MASK` definitions, masks align with shifts, and fields in the same register do not overlap unexpectedly.
- Unit or static tests for representative packed fields: DSC bits-per-pixel, picture/slice dimensions, RC thresholds, range min/max QP and BPG offsets, AFMT channel enable, APG stream ID, FIFO read levels, DP stream link target, pixel encoding/component depth, and GSP transmission line number.
- Hardware smoke tests for DSC enable/disable, DSC-compressed modes, multi-slice modes, native 4:2:2/4:2:0 paths, hotplug, suspend/resume, and link recovery.
- DisplayPort HPO tests that verify stream-to-link mapping, SYM32 reset/reset-done, pixel-to-symbol FIFO reset/enable, MSA programming, HBLANK width, and SDP generic packet scheduling.
- HDMI/DP audio tests that verify AFMT/APG audio enable, stream ID, channel layout, IEC 60958 data, HBR status, CRC done/clear, and FIFO overflow acknowledgement.
- Metadata and packet tests that exercise VPG generic packet frame/immediate updates, pending bits, lock/conflict status, ISRC and MPEG packet data, and DME taken/missed clear handling.
- Power-management tests that read back DSC/AFMT/DME/VPG/APG memory power state and HPO clock gate behavior across idle, blank, suspend, and resume transitions.

## Chunk Boundary Notes

The first visible lines complete `DSCC0_DSCC_PPS_CONFIG19`, whose earlier range-min shift fields are in the previous chunk. The last visible line is inside `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`; the rest of that repeated GSP control register and later DP SYM32 fields are expected in the following chunk. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final per-file research document for `dcn_3_2_1_sh_mask.h`.
