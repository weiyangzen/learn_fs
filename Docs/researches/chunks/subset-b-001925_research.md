# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 5159-7652

## Scope

This chunk is part of the generated DCN 3.2.0 register offset header used by the AMD display driver. It contains C preprocessor constants for MMIO register offsets and base-index selectors for a large middle slice of the display core register map. The covered source range is lines 5159-7652 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`.

The chunk is data-only: it exports `#define` macros and contains no C functions, structs, inline helpers, or runtime branches. Each hardware register has a pair of macros:

- `reg<REGISTER_NAME>`: the register offset within the ASIC register namespace.
- `reg<REGISTER_NAME>_BASE_IDX`: the base-address table index used by AMD display register access helpers.

The slice defines 2400 macros across these address blocks:

- `dcn_dc_mpc_mpcc_ogam1_dispdec`, `dcn_dc_mpc_mpcc_ogam2_dispdec`, and `dcn_dc_mpc_mpcc_ogam3_dispdec`: MPCC output gamma instances 1 through 3.
- `dcn_dc_mpc_mpcc_mcm0_dispdec` through `dcn_dc_mpc_mpcc_mcm3_dispdec`: MPCC multi-color-management instances 0 through 3.
- `dcn_dc_mpc_mpc_ocsc_dispdec`: MPC output mux, denormalization, and output color-space-conversion registers.
- `dcn_dc_opp_abm0_dispdec` through `dcn_dc_opp_abm3_dispdec`: adaptive backlight management instances 0 through 3.
- The beginning of output-pixel-processing pipe blocks: `DPG0`, `FMT0`, `OPPBUF0`, `OPP_PIPE0`, `OPP_PIPE_CRC0`, the corresponding instance-1 blocks, `DPG2`, and the first `FMT2` register pair.

The range starts at `regMPCC_OGAM1_MPCC_OGAM_CONTROL` and ends mid-block at `regFMT2_FMT_CLAMP_COMPONENT_R_BASE_IDX`. Earlier chunks cover preceding MPC/MPCC offsets, and later chunks must complete `FMT2` plus the remaining OPP/ODM/display blocks.

## Purpose

The purpose of this header slice is to provide the generated address side of the DCN 3.2.0 register contract for display color, composition, backlight, formatter, pattern-generator, buffer, and CRC blocks. Driver code includes this header so it can name hardware registers symbolically instead of embedding numeric offsets such as `0x0106`, `0x0790`, or `0x1891` at call sites.

These macros are normally consumed together with the matching shift/mask header for the same ASIC revision, likely `dcn_3_2_0_sh_mask.h`. The offset macro identifies the register, while the shift/mask macros identify fields inside that register. AMD display register helper macros then combine them with a base address table selected by `_BASE_IDX`.

This design keeps the runtime display code mostly hardware-revision-neutral. Higher-level DC code can build register lists for DCN 3.2.0 by referencing `reg...` macros, while shared logic uses common helper APIs to write values, poll status bits, and load LUT data.

## Important API Surface

The exported API is a generated macro namespace. There are no typed APIs, but the macro names themselves are an ABI-like contract with the rest of the AMD display driver.

### MPCC OGAM instances 1-3

`MPCC_OGAM1`, `MPCC_OGAM2`, and `MPCC_OGAM3` expose output gamma programming behind MPCC blocks. Each instance has the same shape and uses `_BASE_IDX 3`, indicating the MPC/MPCC register base table entry. The block includes:

- `MPCC_OGAM_CONTROL`: top-level output gamma control.
- `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_DATA`, and `MPCC_OGAM_LUT_CONTROL`: indexed LUT load and access control registers.
- `MPCC_OGAM_RAMA_*` and `MPCC_OGAM_RAMB_*`: two RAM banks for piecewise output gamma curves. Each bank has per-channel start controls, start slope controls, start base controls, end controls, offsets, and region tables from `REGION_0_1` through `REGION_32_33`.
- `MPCC_GAMUT_REMAP_COEF_FORMAT`, `MPCC_GAMUT_REMAP_MODE`, and `MPC_GAMUT_REMAP_Cxx_Cyy_[AB]`: gamut-remap matrix coefficient format, mode, and A/B coefficient banks.

These macros are the register-address half of output gamma and per-MPCC gamut-remap programming. The duplicate OGAM shapes for instances 1, 2, and 3 differ only by register offset and instance prefix.

### MPCC MCM instances 0-3

`MPCC_MCM0` through `MPCC_MCM3` expose multi-color-management/shaper registers for each MPCC MCM instance. Each instance also uses `_BASE_IDX 3`. The block is larger than OGAM and includes:

- `MPCC_MCM_SHAPER_CONTROL`, per-channel offsets and scales, `MPCC_MCM_SHAPER_LUT_INDEX`, `MPCC_MCM_SHAPER_LUT_DATA`, and `MPCC_MCM_SHAPER_LUT_WRITE_EN_MASK`.
- `MPCC_MCM_SHAPER_RAMA_*` and `MPCC_MCM_SHAPER_RAMB_*`: two shaper RAM banks with per-channel start and end controls plus region tables.
- `MPCC_MCM_3DLUT_MODE`, `MPCC_MCM_3DLUT_INDEX`, and `MPCC_MCM_3DLUT_DATA`: 3D LUT programming entry points.
- `MPCC_MCM_3DLUT_DLG_ADJUST*` and `MPCC_MCM_3DLUT_DLG_CONTROL`: de-gamma or distribution/log-grid adjustment controls for the 3D LUT path.
- `MPCC_MCM_3DLUT_LUT_CONTROL`, `MPCC_MCM_3DLUT_READ_WRITE_CONTROL`, `MPCC_MCM_3DLUT_OFFSET`, `MPCC_MCM_3DLUT_SCALE`, `MPCC_MCM_3DLUT_DEBUG`, `MPCC_MCM_3DLUT_CONTROL`, `MPCC_MCM_3DLUT_STATUS`, and `MPCC_MCM_3DLUT_TEST_DEBUG_INDEX/DATA`: LUT access, scaling, debug, status, and test/debug register addresses.
- `MPCC_MCM_CONTROL`, `MPCC_MCM_TEST_DEBUG_INDEX`, `MPCC_MCM_TEST_DEBUG_DATA`, `MPCC_MCM_OUT_ROUND_CONTROL`, `MPCC_MCM_OUT_ROUND_OFFSET`, `MPCC_MCM_DEBUG_MISC`, and `MPCC_MCM_MEM_PWR_CTRL`: top-level enable/debug/output rounding/memory power controls.

This is the most substantial macro family in the chunk. It covers the MMIO addresses used for shaper LUTs, 3D LUT programming, output rounding, and memory power control in the MPCC color pipeline.

### MPC output mux and output CSC

`dcn_dc_mpc_mpc_ocsc_dispdec` uses `_BASE_IDX 3` and defines output-stage MPC registers:

- `MPC_OUT0_MUX` through `MPC_OUT3_MUX`: output mux selection for four MPC outputs.
- `MPC_OUT[0-3]_DENORM_CONTROL`, `MPC_OUT[0-3]_DENORM_CLAMP_G_Y`, and `MPC_OUT[0-3]_DENORM_CLAMP_B_CB`: output denormalization and clamp controls.
- `MPC_OUT_CSC_COEF_FORMAT`: coefficient format for output CSC matrices.
- `MPC_OUT[0-3]_CSC_MODE`: per-output CSC mode control.
- `MPC_OUT[0-3]_CSC_C11_C12_A` through `MPC_OUT[0-3]_CSC_C33_C34_B`: per-output color-space-conversion matrix coefficients, with A and B coefficient banks.

These offsets are the MPC-side registers used when routing composed display data into output pipes and applying final output color-space conversion.

### ABM instances 0-3

`ABM0` through `ABM3` use `_BASE_IDX 3` and expose adaptive backlight management and histogram/luma-statistics register addresses. Each instance contains:

- `BL1_PWM_AMBIENT_LIGHT_LEVEL`, `BL1_PWM_USER_LEVEL`, `BL1_PWM_TARGET_ABM_LEVEL`, `BL1_PWM_CURRENT_ABM_LEVEL`, `BL1_PWM_FINAL_DUTY_CYCLE`, and `BL1_PWM_MINIMUM_DUTY_CYCLE`: PWM and brightness level inputs/outputs.
- `BL1_PWM_ABM_CNTL`, `BL1_PWM_BL_UPDATE_SAMPLE_RATE`, and `BL1_PWM_GRP2_REG_LOCK`: ABM PWM control, sample-rate, and register-lock addresses.
- `DC_ABM1_CNTL` and `DC_ABM1_IPCSC_COEFF_SEL`: ABM control and input CSC coefficient selection.
- `DC_ABM1_ACE_OFFSET_SLOPE_0` through `_4`, `DC_ABM1_ACE_THRES_12`, `DC_ABM1_ACE_THRES_34`, and `DC_ABM1_ACE_CNTL_MISC`: ambient contrast enhancement curve and threshold controls.
- `DC_ABM1_HGLS_REG_READ_PROGRESS`, `DC_ABM1_HG_MISC_CTRL`, `DC_ABM1_HG_SAMPLE_RATE`, and `DC_ABM1_LS_SAMPLE_RATE`: histogram/luma-statistics control and progress registers.
- `DC_ABM1_LS_SUM_OF_LUMA`, `DC_ABM1_LS_MIN_MAX_LUMA`, `DC_ABM1_LS_FILTERED_MIN_MAX_LUMA`, `DC_ABM1_LS_PIXEL_COUNT`, `DC_ABM1_LS_MIN_MAX_PIXEL_VALUE_THRES`, `DC_ABM1_LS_MIN_PIXEL_VALUE_COUNT`, and `DC_ABM1_LS_MAX_PIXEL_VALUE_COUNT`: luma statistic readback registers.
- `DC_ABM1_HG_BIN_*` and `DC_ABM1_HG_RESULT_1` through `DC_ABM1_HG_RESULT_24`: histogram bin configuration and result readbacks.
- `DC_ABM1_BL_MASTER_LOCK`: ABM/backlight master lock register.

These macros are used by backlight, power, and image-quality code paths that configure automatic brightness and query frame-derived statistics.

### OPP DPG/FMT/OPPBUF/pipe/CRC start

The end of the chunk begins OPP register coverage. These blocks use `_BASE_IDX 2`, distinguishing the OPP base table from the MPC/ABM base table:

- `DPG0`, `DPG1`, and `DPG2`: display pattern generator control, ramp control, dimensions, RGB/YCbCr color registers, offset segment, and status.
- `FMT0` and `FMT1`: formatter clamp component registers, dynamic expansion, control, bit-depth control, dither random seeds, clamp control, side-by-side stereo control, 4:2:0 memory control, and 4:2:2 control.
- `FMT2`: only `FMT_CLAMP_COMPONENT_R` appears in this chunk; the rest of FMT2 is in the next chunk.
- `OPPBUF0` and `OPPBUF1`: OPP buffer control, 3D parameter registers, and secondary control.
- `OPP_PIPE0` and `OPP_PIPE1`: OPP pipe control.
- `OPP_PIPE_CRC0` and `OPP_PIPE_CRC1`: CRC control, mask, and result registers.

The OPP macros are used during pipe bring-up, formatter programming, test-pattern generation, buffer configuration, and CRC validation.

## Control Flow and Runtime Behavior

This header has no executable control flow. The effective control flow appears in caller code that uses these offsets in register sequences. The macro layout reveals several important sequencing patterns:

- LUT programming uses index/data/control triplets. OGAM, MCM shaper, and MCM 3D LUT paths all expose indexed access registers. Runtime code must set an index, write or read data, and use control/status bits from the paired shift/mask header to manage the transaction.
- Dual-bank programming is a recurring pattern. OGAM and MCM shaper curves have `RAMA` and `RAMB` register families; gamut remap and output CSC matrices also expose A/B coefficient banks. Driver code can stage a new curve or matrix in one bank while the other is active, then flip hardware selection at a synchronized point.
- Instance replication drives loop-based register-list construction. OGAM instances 1-3, MCM instances 0-3, ABM instances 0-3, and OPP instances are structurally repeated. Higher-level AMD DC code normally selects the instance by pipe or MPCC index and then uses a per-instance register table populated from these macros.
- ABM statistics are hardware-produced state. Histogram and luma-statistics result registers are readbacks derived from displayed frames. Callers must program sample rates and wait for valid frame/statistic periods before treating the values as current.
- OPP CRC is a programmed measurement path. Callers configure CRC control/mask, wait for result availability according to field semantics in the shift/mask header, and read `RESULT0`, `RESULT1`, and `RESULT2`.
- DPG and FMT programming participates in mode-set sequencing. Pattern generator dimensions/colors, formatter bit depth, dither seeds, clamp settings, stereo/420/422 controls, and OPP buffer registers are normally written before enabling or validating an output pipe.

Because this is an offset header, the macros do not encode whether a register is read-only, write-only, status, clear-on-write, latched, or double-buffered. Those semantics are provided by hardware documentation, the matching field header, and the calling DC code.

## State and Persistence Behavior

The macros themselves are compile-time constants and have no persistence. The hardware registers they address represent volatile ASIC state:

- Color pipeline configuration persists in the display engine until rewritten, reset, power-gated, or reinitialized by a mode set. This includes OGAM curves, MCM shaper/3D LUT state, gamut remap matrices, MPC output CSC matrices, formatter state, and OPP buffer controls.
- Indexed LUT contents are hardware memory state. Writes to `*_LUT_DATA` or `*_3DLUT_DATA` update internal LUT RAM rather than ordinary CPU memory. The corresponding index/control/status registers define how persistent those writes are across power transitions.
- ABM brightness levels and ACE configuration are hardware configuration, while luma and histogram result registers are live measurement/readback state.
- Lock registers such as `BL1_PWM_GRP2_REG_LOCK` and `DC_ABM1_BL_MASTER_LOCK` imply grouped or synchronized updates. Incorrect sequencing can leave shadow values pending or expose partially updated brightness configuration.
- Memory power control registers in MCM (`MPCC_MCM_MEM_PWR_CTRL`) can affect retention or availability of color-management RAM blocks. Callers must coordinate power gating with LUT programming and enable state.
- OPP CRC result registers are transient validation state. They should be treated as tied to a programmed capture interval and current pipe contents, not as persistent configuration.

The `_BASE_IDX` value is also state-adjacent in the register access model. `_BASE_IDX 3` is used throughout the MPC/MPCC/ABM blocks in this chunk, while `_BASE_IDX 2` is used for OPP blocks. A wrong base index can make a correct offset target the wrong register aperture.

## Dependencies and Integration Points

This file depends on the generated AMD DC register naming convention. The key dependencies are:

- The matching DCN 3.2.0 shift/mask header, which provides field-level constants for these same register names.
- AMD display register access helpers that accept register offsets and base indices, commonly through generated register-list structures and macros.
- DCN 3.2.0 hardware sequencing code that populates per-block register tables for MPC, MPCC, ABM, OPP, and color-management components.
- Build configuration that selects the DCN 3.2.0 register set only for ASICs whose register layout matches this generated header.

Important integration points include:

- MPCC and MPC color-management code that loads OGAM curves, shaper LUTs, 3D LUTs, gamut remap matrices, denormalization clamps, and output CSC matrices.
- Hardware sequencer and resource code that builds pipe-specific register lists for MPCC/MPC/OPP instances during mode set, stream enable, pipe split, and plane composition.
- ABM/backlight code that controls PWM levels, automatic brightness, ACE parameters, histogram/luma sampling, and master lock behavior.
- Debug and validation code paths that use DPG test patterns and OPP pipe CRC readbacks to verify pixel pipeline behavior.
- Formatter paths that program bit depth, dithering, clamp, stereo, 4:2:0, and 4:2:2 behavior before pixels leave the display pipe.

The repeated instance layout makes this header sensitive to code generation consistency. Register lists in runtime code often assume that instance `n` has the same semantic registers as instance `n+1` with only address and prefix changes.

## Risks and Edge Cases

- Generated offset drift is high impact. If a single numeric offset is wrong, the driver can write a valid-looking register macro to the wrong hardware address, causing color corruption, black screen, backlight misbehavior, or hard-to-debug display hangs.
- `_BASE_IDX` mismatches are as dangerous as wrong offsets. Most of this chunk uses base index 3, but the OPP section switches to base index 2. Mixing these in a register table would redirect otherwise correct offsets.
- Chunk boundaries split logical hardware blocks. This chunk starts at OGAM1 rather than OGAM0 and ends after only the first FMT2 register pair. Any final per-file research must reconcile adjacent chunks before claiming whole-file coverage of OGAM, FMT, or OPP instance sets.
- Repeated blocks invite copy/paste or generator skew. OGAM1-3, MCM0-3, ABM0-3, and OPP0-2 follow similar patterns. A single missing register or wrong instance prefix can affect only one pipe and escape broad compile checks.
- Indexed LUT registers require strict ordering. Writing data before setting the index/control register, using the wrong bank, or ignoring hardware status can corrupt gamma/shaper/3D-LUT contents.
- Color matrix A/B banks and RAMA/RAMB banks can be confused. Callers must know which bank is active and whether update selection is double-buffered before switching curves or matrices during a live frame.
- ABM has mixed configuration and readback registers. Histogram/luma result registers, read-progress registers, lock registers, and brightness level registers have different semantics; generic read-modify-write patterns can be wrong if field-level clear, latch, or lock behavior is ignored.
- Some OPP state is validation-only or mode-test-only. DPG and CRC registers may be compiled into production drivers but primarily used by tests, debugfs paths, or diagnostics. Incorrect enable sequencing can interfere with normal frame output.
- ASIC specificity matters. DCN 3.2.0 offsets should not be reused for other DCN generations even when register names look similar.

## Test Signals

Useful signals for validating code that consumes this chunk include:

- Compile coverage for DCN 3.2.0 display code, proving each referenced `reg...` macro and `_BASE_IDX` macro resolves with the expected generated name.
- Register-list construction tests or build-time checks that ensure MPC/MPCC/ABM register tables use base index 3 and OPP register tables use base index 2.
- Color-management tests that load OGAM curves for MPCC instances 1-3, MCM shaper LUTs and 3D LUTs for MPCC MCM instances 0-3, then verify expected output through CRC or visual pipeline validation.
- Gamut remap and output CSC tests that program A/B coefficient banks for MPCC and MPC output paths, switch modes, and confirm no stale bank is used.
- Backlight and ABM tests that update user/target/current/final PWM levels, configure ACE thresholds/slopes, collect histogram and luma statistics, and verify lock/update behavior does not leave stale values.
- OPP pipe tests that use DPG generated patterns, FMT bit-depth/dither/clamp settings, OPP buffer configuration, and `OPP_PIPE_CRC0/1` result registers to validate known pixel outputs.
- Multi-pipe tests across at least four MPC/ABM instances and the visible OPP instances to catch one-instance register offset or prefix mistakes.
- Power-management tests around `MPCC_MCM_MEM_PWR_CTRL` that verify LUT contents and color behavior across memory power state changes.

## Open Questions for Merge

- The chunk does not include OGAM0, so the final per-file report should check adjacent chunks to determine whether OGAM0 has the same register family and how instances are ordered.
- The FMT2 block is split after `FMT_CLAMP_COMPONENT_R`; later chunk research must complete FMT2 and likely cover additional FMT/OPP instances.
- This offset header should be reconciled with the matching `dcn_3_2_0_sh_mask.h` chunks to distinguish ordinary configuration registers from read-only status, clear-on-write, double-buffered, or indexed access registers.
