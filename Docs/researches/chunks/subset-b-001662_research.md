# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 14827-17356

## Scope

This chunk is a generated AMD DCN 2.1.0 register shift/mask slice. It contains preprocessor constants only: no functions, structs, enums, data storage, or executable branches. The exported contract is the pair of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that AMD display register helpers use to pack, update, and extract fields in DPP/DSCL/CM/perfmon/CNVC registers.

The line range starts in the middle of the DPP1 DSCL register group, covers all of the DPP1 color-management group, includes DPP1 display performance monitor fields, and then starts DPP2 with top-level DPP, CNVC config/cursor, DSCL, and the beginning of CM2 blend-gamma fields.

## Purpose

The purpose of this chunk is to describe the bit layout for per-pipe Display Pipe Processor hardware on DCN 2.1.0. The names are instance-qualified (`DSCL1_`, `CM1_`, `DC_PERFMON12_`, `DPP_TOP2_`, `CNVC_CFG2_`, `CNVC_CUR2_`, `DSCL2_`, `CM2_`) while the runtime DPP code consumes them through generation-specific register tables and field tables.

Major hardware areas represented here are:

- DPP1 DSCL tail: scaler horizontal/vertical ratios, phase initial values, bottom-field initial values, chroma ratios/inits, black offsets, scaler update/autocal controls, overscan, OTG blanking, recout/MPC dimensions, line-buffer data/memory controls, line-buffer counters, DSCL memory power controls/status, output-buffer control, and output-buffer memory power state.
- DPP1 CM: CM bypass/update status, input CSC A/B matrices, gamut-remap A/B matrices, bias fields, degamma LUT index/data/write controls, degamma RAM A/B PWL region descriptors, blend-gamma LUT and RAM A/B PWL descriptors, HDR multiplier coefficient, CM memory power, dealpha, coefficient format, shaper LUT/RAM A/B descriptors, CM memory power status2, 3D LUT mode/index/data/read-write controls, 3D LUT normalization/output offsets, and CM test debug index/data.
- DPP1 perfmon: `DC_PERFMON12_*` counter selection, counter state, perfmon window controls, current-value interrupt/mask/type/clear/status fields, and high/low counter values.
- DPP2 top/CNVC/DSCL/CM start: DPP2 top control/reset/CRC/host-read fields, CNVC2 pixel-format, format, FP bias/scale, color-keyer, alpha LUT, cursor0 control/color/FP-scale-bias, DSCL2 scaler controls mirroring DSCL1, and the start of CM2 input CSC/gamut/degamma/blend-gamma fields.

This header does not define policy. It gives exact bit positions and masks so the DPP implementation can program scaler, color, cursor, CRC, perfmon, and memory-power registers without hard-coding ASIC-specific bit numbers in runtime code.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the generated macro namespace:

- `*_SHIFT` constants give the low bit position of a field.
- `*_MASK` constants give the already-shifted field mask.
- Register comments such as `//CM1_CM_DGAM_LUT_WRITE_EN_MASK` and address-block comments such as `// addressBlock: dce_dc_dpp2_dispdec_dscl_dispdec` group field macros by hardware block.

The direct consumers are the AMD display DPP register table macros:

- `TF_REG_LIST_DCN`, `TF_REG_LIST_DCN20`, and `TF_REG_LIST_DCN201` in `display/dc/dpp/dcn10/dcn10_dpp.h`, `display/dc/dpp/dcn20/dcn20_dpp.h`, and `display/dc/dpp/dcn201/dcn201_dpp.h` paste the register names into instance-specific register arrays.
- `TF_REG_LIST_SH_MASK_DCN*` macros paste field names into shift/mask initializers for `struct dcn10_dpp_shift`, `struct dcn10_dpp_mask`, `struct dcn20_dpp_shift`, `struct dcn20_dpp_mask`, and the DCN201 aliases.
- Runtime code uses `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `IX_REG_GET`, and related helpers from the display register-helper layer. Those helpers receive the shifts and masks through `FN(reg, field)` expansion.

Important field families in this chunk include:

- Scaler and line buffer: `SCL_H_SCALE_RATIO`, `SCL_V_SCALE_RATIO`, chroma variants, `SCL_*_INIT_*`, `SCL_BLACK_OFFSET_*`, `AUTOCAL_*`, `RECOUT_*`, `MPC_*`, `INTERLEAVE_EN`, `ALPHA_EN`, `MEMORY_CONFIG`, `LB_MAX_PARTITIONS`, `LB_NUM_PARTITIONS`, and `LB_MEM_PWR_*`.
- Color matrices: `CM_ICSC_*`, `CM_ICSC_B_*`, `CM_GAMUT_REMAP_*`, and `CM_GAMUT_REMAP_B_*`.
- Transfer functions and LUTs: `CM_DGAM_*`, `CM_BLNDGAM_*`, `CM_SHAPER_*`, `CM_3DLUT_*`, their LUT index/data/write-select/config-status fields, and their RAM A/RAM B region descriptors.
- Memory power: DSCL line-buffer/LUT/OBUF power force/disable/status fields, and CM DGAM/3DLUT/SHAPER/GAMCOR/BLNDGAM memory power controls/status.
- CNVC/cursor: pixel format, format control, FP bias/scale, color-keyer channels, alpha 2-bit LUT, cursor enable/mode/2x-magnify/pitch/line-per-chunk, cursor color entries, and cursor FP scale/bias.
- Perfmon: counter enable/reset/mode/window/selection fields, counter high/low state, current-value interrupt controls, and counter readback registers.

## Control Flow

This chunk has no local control flow. Control flow is in the DPP implementation that includes the generated offset and mask headers and then uses the resulting tables.

Important runtime flows represented by these fields are:

1. DSCL programming in `dcn10_dpp_dscl.c`: `dpp1_dscl_set_scaler_manual_scale()` caches `struct scaler_data`, powers DSCL memory on if needed, disables autocal, programs recout and MPC size, chooses line-buffer partitions, writes black offsets, writes manual scale ratios and initial phases, sets tap counts, programs coefficient RAM, and swaps scaler coefficient RAM selection. The ratio/init/line-buffer/OBUF fields in this chunk are the exact bit layouts used by that flow for DPP1 and DPP2 instances.
2. DSCL memory power: `dpp1_power_on_dscl()` updates `DSCL_MEM_PWR_CTRL` and waits on `DSCL_MEM_PWR_STATUS`. Incorrect force/status masks can leave the scaler LUT or line-buffer memories powered down, or prevent low-power transitions from completing.
3. CM input CSC and gamut remap: `dpp1_program_input_csc()`, `dpp2_program_input_csc()`, `dpp1_cm_set_gamut_remap()`, and `dpp2_cm_set_gamut_remap()` program 3x4 matrices through `cm_helper_program_color_matrices()`. DCN2 uses A/B matrix banks and debug-status reads to select the inactive bank, so the A/B field pairs in this chunk are part of frame-boundary-safe updates.
4. Degamma, blend-gamma, shaper, and 3D LUT programming: DCN2 CM code configures write masks/selectors, writes LUT index/data registers, programs RAM A/B PWL regions, then flips the active mode. Fields such as `CM_DGAM_CONFIG_STATUS`, `CM_BLNDGAM_CONFIG_STATUS`, `CM_*_LUT_WRITE_SEL`, `CM_*_LUT_MODE`, and `CM_*_EXP_REGION*` provide the hardware bank state and region metadata for those flows.
5. CNVC/cursor programming: resource and DPP code use CNVC format, pixel conversion, color-keyer, alpha LUT, and cursor fields to set plane input conversion and hardware cursor appearance for DPP2.
6. DPP top/CRC/perfmon: CRC control/value and performance monitor registers expose diagnostics and counters. The macros describe event selection, counter accumulation windows, interrupt threshold/status bits, and readback fields; test/debug code supplies the sequencing.

The macros do not encode read/write ordering, register volatility, write-one-to-clear behavior, or whether a field is status-only. Callers must still follow the hardware sequencing requirements for modeset, plane update, LUT bank switch, cursor update, memory power, and perfmon interrupt acknowledgement.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes hardware state that persists in MMIO registers until changed by the driver, hardware, firmware, power gating, reset, or a full modeset/reinitialization path.

State represented by this chunk includes:

- Per-DPP scaler state: scale ratios, phase initial values, black offsets, autocal mode, overscan, recout/MPC size, line-buffer memory configuration, and coefficient-bank selection.
- Per-DPP memory power state: DSCL LUT/LB/OBUF memory force/disable/status bits and CM LUT memory force/disable/status bits. These interact with low-power debug flags and deferred register writes in the display core.
- Cached software state in consumers: `struct dcn201_dpp` and related DPP structs cache current `scaler_data`, filter coefficient pointers, and PWL parameters. The generated masks determine how those cached values are serialized into hardware.
- CM matrix and LUT state: ICSC/gamut matrices, degamma/blend-gamma/shaper LUT contents, RAM A/B region descriptors, active/bypass modes, config-status bits, 3D LUT indexing/data, and normalization/offset registers.
- Plane-format and cursor state: CNVC surface pixel format, format-conversion controls, FP bias/scale, color keyer, alpha LUT, cursor mode/color, cursor pitch/chunk layout, and cursor FP scale/bias.
- Observability state: DPP CRC values/control, host read control, perfmon counter values/state, current-value interrupts, and counter windows.

Many of these fields are double-buffered or banked. The matrix and LUT flows often write an inactive A/B RAM, then flip mode or select bits so the new state becomes active on a frame boundary. Bad masks can therefore produce delayed or intermittent failures rather than an immediate register-write error.

## Dependencies And Integration Points

The companion address header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies register offsets. This chunk supplies field layout inside those registers. Both are needed for meaningful MMIO access.

Primary integration points in the source tree are:

- `display/dc/dpp/dcn10/dcn10_dpp.h`, `display/dc/dpp/dcn20/dcn20_dpp.h`, and `display/dc/dpp/dcn201/dcn201_dpp.h`, which define the register/shift/mask structs and macro lists that consume these names.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c`, which uses DSCL fields for manual scaling, line-buffer setup, coefficient RAM programming, memory power, recout, MPC size, and scaler mode.
- `display/dc/dpp/dcn10/dcn10_dpp_cm.c` and `display/dc/dpp/dcn20/dcn20_dpp_cm.c`, which use CM fields for input CSC, gamut remap, degamma, blend-gamma, shaper, and LUT bank programming.
- DCN201 resource construction code, which wires DCN2.1 register tables into DPP instances and selects the right per-instance address/mask arrays.
- Display diagnostics and debug paths that read DPP CRC and `DC_PERFMON12_*` counters.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, network protocol, storage replication, distributed locking, or persistent filesystem behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A generated shift/mask error usually compiles cleanly but causes `REG_SET` or `REG_UPDATE` to write the wrong bits, leave stale bits in place, truncate values, or read a misleading status field.

DSCL risks include black screens, shifted/scaled images, corrupted chroma on YCbCr or 4:2:0 planes, incorrect interlaced bottom-field phase, bad line-buffer partitioning, coefficient RAM writes to the wrong tap/filter type, and failures that only appear with specific taps, ratios, formats, or recout dimensions. The chunk starts after the first `DSCL1_SCL_HORZ_FILTER_SCALE_RATIO` comment, so adjacent chunk context is needed for the complete DSCL1 register group.

CM risks include wrong color conversion, broken degamma/blend-gamma/shaper output, incorrect HDR multiplier behavior, bad 3D LUT indexing/data, bank-switch races, and frame-boundary glitches if A/B config-status or write-select masks are wrong. Because many LUT regions use repeated `REGION_0_1` through `REGION_32_33` patterns, copy-generation mistakes can affect only part of a transfer curve and produce subtle banding or clipping.

Memory power fields are sensitive. Incorrect force/disable/status masks can power down active DSCL/CM memories, prevent optimized low-power entry, or make waits poll the wrong status bits. These bugs tend to surface during suspend/resume, runtime power management, display off/on, or modeset transitions rather than during simple boot tests.

CNVC and cursor risks include wrong pixel-format interpretation, broken FP bias/scale for FP formats, color-keyer mismatches, cursor invisibility/corruption, wrong cursor colors, and chunk/pitch bugs that appear only with certain cursor sizes or magnification settings.

Perfmon and CRC fields are diagnostic but still control-sensitive. Wrong masks can make validation counters meaningless, fail to clear or mask current-value interrupts, or report the wrong counter state. This can hide performance regressions or make debug tooling chase false signals.

Instance repetition matters. The same logical fields appear for DPP1 and DPP2 with instance-qualified prefixes. The merge lane should check structural consistency across `DSCL1`/`DSCL2`, `CM1`/`CM2`, and corresponding offset definitions while still allowing intentional per-instance address differences.

## Test Signals

Useful validation signals are a mix of generated-header checks and real display behavior:

- Compile coverage for DCN2.1/DCN201 display code that includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`, especially DPP, DSCL, CM, resource, and diagnostics paths.
- Generated consistency checks that every `REGISTER__FIELD__SHIFT` has the expected `REGISTER__FIELD_MASK`, masks align with shifts, field widths are plausible, and every register has a matching offset definition.
- Cross-instance checks that repeated DPP1/DPP2 register families have matching field names, widths, and shifts unless the hardware database documents a difference.
- Plane scaling tests covering bypass, RGB scaling, YCbCr scaling, 4:2:0 luma/chroma bypass cases, 1/2/3/4/6/8 tap filters, large downscales, interlaced/bottom-field init paths, recout offsets, and line-buffer pressure.
- Color pipeline tests for input CSC, gamut remap, degamma PWL, blend-gamma PWL, shaper LUT, HDR multiplier, 3D LUT enable/read-write/index/data paths, and transitions between bypass/RAM A/RAM B.
- Power-management tests across display blank/unblank, modeset, runtime PM, suspend/resume, and low-power debug options to catch DSCL/CM memory power mask errors.
- CNVC/cursor tests for multiple pixel formats, FP16/FP conversion, color keying, alpha LUT behavior, cursor color/pitch/chunk layout, 2x cursor magnification, and cursor movement during modesets.
- CRC/perfmon tests that confirm DPP CRC values change with known frame content, perf counters count selected events, current-value interrupts can be masked/cleared, and counter high/low reads are coherent.

Regression symptoms from this chunk include black or incorrectly scaled planes, chroma misalignment, color shifts, LUT banding, cursor artifacts, stuck memory-power waits, failures only after resume or display off/on, useless perf counters, and diagnostics that disagree with visible frame output.

## Cross-Chunk Notes

This is an artificial line-range slice of a generated constants header. It begins inside the DSCL1 family and ends mid-way through CM2 blend-gamma RAM A region definitions. The final per-file report should merge this chunk with adjacent chunks to describe complete DPP1/DPP2 coverage and avoid treating partial register families as standalone modules.
