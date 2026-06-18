# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 54080-56610

## Scope

This chunk covers lines 54080-56610 of the generated DCN 3.0.0 shift/mask header. It is a register-field definition slice only: there are no C functions, structs, enums, or runtime branches here. The exported surface is a large set of preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`, consumed by AMD display register helper macros and paired with register offsets from `dcn_3_0_0_offset.h`.

The slice begins in the middle of the Display Writeback output-gamma RAM B block, covers the MPCC0 through MPCC5 composition/blending register field layouts, then covers MPCC output-gamma and gamut-remap blocks for MPCC_OGAM0, MPCC_OGAM1, MPCC_OGAM2, and the beginning of MPCC_OGAM3. It ends inside `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_28_29`, so MPCC_OGAM3 RAMA continuation and RAMB/gamut-remap fields belong to a later chunk.

## Purpose

The purpose of this chunk is to describe bit positions and masks for DCN 3.0 display composition, output-gamma, and color-remap hardware:

- `DWB_OGAM_RAMB_*` defines the tail of the Display Writeback output-gamma RAM B transfer-function region descriptors: per-channel start/end values, slopes, offsets, and 34 piecewise-linear region descriptors.
- `MPCC0_MPCC_*` through `MPCC5_MPCC_*` define six Multi-Plane Composition Controller instances. These fields select the top DPP input, bottom MPCC link, OPP target, alpha/blend mode, stereo/alternate-frame behavior, per-plane gains, background color, OGAM memory power, and MPCC status.
- `MPCC_OGAM0_*`, `MPCC_OGAM1_*`, and `MPCC_OGAM2_*` provide full per-MPCC output-gamma control, LUT host access, RAM A/RAM B transfer-function descriptors, and gamut-remap matrix storage.
- `MPCC_OGAM3_*` starts the same per-MPCC OGAM pattern, but this chunk only includes control/LUT access and RAM A through region pair 28/29.

The chunk lets driver code avoid hard-coded bit arithmetic while programming blending chains, double-buffered output gamma, writeback gamma, memory power, and 3x4 gamut-remap matrices.

## Important APIs, Types, And Constants

There are no callable APIs in this slice. The important interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: the field's least-significant bit position.
- `REGISTER__FIELD_MASK`: the field mask already shifted into register position.
- Section comments such as `//MPCC0_MPCC_CONTROL` and `//MPCC_OGAM0_MPCC_OGAM_RAMA_REGION_0_1` group related fields.
- Address-block comments such as `// addressBlock: dce_dc_mpc_mpcc0_dispdec` identify the hardware instance block.

Important field groups include:

- DWB OGAM RAM B: `DWB_OGAM_RAMB_START_*`, `DWB_OGAM_RAMB_END_*`, `DWB_OGAM_RAMB_OFFSET_*`, and `DWB_OGAM_RAMB_REGION_0_1` through `DWB_OGAM_RAMB_REGION_32_33`. These mirror the RAM A region model from the preceding chunk and describe blue/green/red channel PWL start, end, slope, base, offset, LUT-offset, and segment-count values.
- MPCC topology: `MPCC*_MPCC_TOP_SEL`, `MPCC*_MPCC_BOT_SEL`, and `MPCC*_MPCC_OPP_ID` use 4-bit selectors for input DPP, lower MPCC in the composition chain, and output pixel processor target.
- MPCC blending: `MPCC*_MPCC_CONTROL` includes `MPCC_MODE`, `MPCC_ALPHA_BLND_MODE`, `MPCC_ALPHA_MULTIPLIED_MODE`, `MPCC_BLND_ACTIVE_OVERLAP_ONLY`, `MPCC_BG_BPC`, `MPCC_BOT_GAIN_MODE`, `MPCC_GLOBAL_ALPHA`, and `MPCC_GLOBAL_GAIN`.
- MPCC stereo/multiview: `MPCC*_MPCC_SM_CONTROL` exposes enable, mode, frame/field alternation, forced next-frame polarity, forced top polarity, and current-frame polarity fields.
- MPCC programming synchronization: `MPCC*_MPCC_UPDATE_LOCK_SEL` selects update-lock routing and reports locked status.
- MPCC gain/background/status: `MPCC*_MPCC_TOP_GAIN`, `MPCC*_MPCC_BOT_GAIN_INSIDE`, `MPCC*_MPCC_BOT_GAIN_OUTSIDE`, `MPCC*_MPCC_BG_R_CR`, `MPCC*_MPCC_BG_G_Y`, `MPCC*_MPCC_BG_B_CB`, `MPCC*_MPCC_MEM_PWR_CTRL`, and `MPCC*_MPCC_STATUS`.
- MPCC OGAM control and LUT access: `MPCC_OGAM*_MPCC_OGAM_CONTROL`, `MPCC_OGAM*_MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM*_MPCC_OGAM_LUT_DATA`, and `MPCC_OGAM*_MPCC_OGAM_LUT_CONTROL` define mode/select state, current mode/select readback, PWL disable, 9-bit LUT index, 18-bit LUT data, color write mask, read color select, host RAM select, debug read, and config mode.
- MPCC OGAM RAM A/RAM B PWL descriptors: `MPCC_OGAM*_MPCC_OGAM_RAMA_*` and `MPCC_OGAM*_MPCC_OGAM_RAMB_*` use repeated field layouts. Start values and start bases are 18-bit masks (`0x0003FFFFL`), start segments are 7-bit fields at bit 20 (`0x07F00000L`), offsets are 19-bit masks (`0x0007FFFFL`), end values are low 16 bits, end slopes are high 16 bits, LUT offsets are 9-bit fields, and region segment counts are 3-bit fields.
- MPCC gamut remap: `MPCC_OGAM*_MPCC_GAMUT_REMAP_COEF_FORMAT`, `MPCC_OGAM*_MPCC_GAMUT_REMAP_MODE`, and `MPCC_OGAM*_MPC_GAMUT_REMAP_Cxx_Cyy_[AB]` define coefficient format, active/current coefficient set, and packed 16-bit matrix coefficient pairs for A/B banks.

## Control Flow

This header chunk has no runtime control flow. Its practical compile-time flow is:

1. DCN 3.0 display source includes register offset and shift/mask headers.
2. Register-list macros in MPCC/DWB code expand generated register names into address tables.
3. Field-list macros expand these `SHIFT` and `MASK` constants into per-block `shift` and `mask` structs.
4. Runtime code uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and `REG_READ` against those tables to program MMIO registers.

The register order is still meaningful for maintainers and generated-header validation. MPCC0-5 are laid out as identical repeated address blocks, followed by MPCC_OGAM0-3 repeated color blocks. The chunk boundary cuts through generated sequences: it starts after the first two DWB RAMB start-control fields and ends before the MPCC_OGAM3 RAMA/RAMB/gamut-remap block is complete.

## State And Persistence Behavior

The header stores no software state and persists no data by itself. It describes hardware state that persists in DCN registers until overwritten by the driver, reset, or power-gated:

- MPCC topology fields persist composition routing: which DPP feeds the top layer, which MPCC is chained below, and which OPP receives the composited output.
- MPCC blend fields persist plane-composition behavior, including alpha mode, premultiplied alpha interpretation, overlap-only blending, background bit depth, global alpha, and gain factors.
- `MPCC*_MPCC_STATUS` exposes hardware idle/busy/disabled state used by driver wait and state-capture paths.
- `MPCC*_MPCC_MEM_PWR_CTRL` controls OGAM LUT memory force/power-disable/low-power behavior and reports power state. Incorrect settings can block LUT writes or prevent low-power entry.
- MPCC OGAM control fields persist the active output gamma mode and selected RAM bank. Current-mode/current-select fields are readback/status fields used to choose the next bank for double-buffered updates.
- MPCC and DWB OGAM RAM descriptors persist the piecewise transfer-function layout for RAM A/RAM B. These include region starts, bases, slopes, offsets, LUT offsets, and segment counts for each color channel.
- Gamut-remap coefficient registers persist A and B matrix coefficient banks. The mode register selects which bank is active and exposes the current active bank.

Because many field names are repeated across MPCC instances and across RAM A/RAM B, the instance index and register bank are part of the state contract. A correct mask on the wrong instance or wrong bank still programs valid hardware bits, but with incorrect display behavior.

## Dependencies And Integration Points

This generated mask header depends on matching generated offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h` and on AMD display register helper macros that concatenate register/field names.

Observed integration points in this repository include:

- `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h` builds DCN 3.0 MPC register and field tables from these macros. `MPC_REG_LIST_DCN3_0()` includes MPCC gain, memory-power, OGAM LUT, OGAM RAMA/RAMB, gamut-remap, and OGAM control registers. The associated mask/shift lists use fields such as `MPCC_OGAM_RAMA_EXP_REGION_START_BASE_B`, `MPCC_OGAM_RAMB_EXP_REGION_END_SLOPE_B`, `MPCC_GAMUT_REMAP_C11_A`, and `MPCC_OGAM_MEM_PWR_STATE`.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.c` consumes these fields in `mpc3_power_on_ogam_lut()`, `mpc3_configure_ogam_lut()`, `mpc3_program_luta()`, `mpc3_program_lutb()`, `mpc3_program_ogam_pwl()`, `mpc3_set_output_gamma()`, `program_gamut_remap()`, `mpc3_set_gamut_remap()`, `mpc3_get_gamut_remap()`, `mpc3_read_mpcc_state()`, and `mpc3_read_reg_state()`.
- Legacy/common MPC code in `dcn10_mpc.c` and `dcn20_mpc.c` consumes the shared MPCC field names for background color, blending, stereo mode, status waits, gains, and memory power. DCN 3.0 extends those tables with OGAM/gamut-remap fields.
- `drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.h` consumes the DWB OGAM RAMB field macros in `DWBC_COMMON_REG_LIST_DCN30()` and `DWBC_COMMON_MASK_SH_LIST_DCN30()`.
- `drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb_cm.c` uses DWB gamut-remap and gamma programming helpers, so the DWB fields in this chunk are part of writeback color-processing correctness.
- Color helper code such as `dcn30_cm_common` and `dcn10_cm_common` receives these masks through `dcn3_xfer_func_reg` and `color_matrices_reg` structures and performs the actual packing and MMIO writes.

## Risks And Edge Cases

- A wrong shift or mask silently programs the wrong MMIO bits. The compiler will usually only catch missing macro names, not semantically incorrect values.
- MPCC0-5 field layouts are intentionally repeated. Copy/generator skew in one instance can break only a subset of display pipes and be hard to notice without multi-plane or multi-output coverage.
- MPCC topology selector fields are only 4 bits. `0xf` is used by driver code as a disconnected/idle selector in related MPC paths; misdocumenting or misprogramming these selectors can create invalid composition chains.
- The chunk starts mid-DWB RAMB and ends mid-MPCC_OGAM3 RAMA. Whole-file analysis must merge adjacent chunks before making completeness claims about DWB or MPCC_OGAM3.
- OGAM programming is double-buffered between RAM A and RAM B. Incorrect `MPCC_OGAM_SELECT`, current-select readback, or LUT host-select masks can cause writes to the active bank, visible color corruption, or no visible update.
- `MPCC_OGAM_MEM_PWR_STATE` is polled before LUT writes. If its mask or shift is wrong, `REG_WAIT()` may time out or proceed while the LUT memory is inaccessible.
- Region descriptor masks have narrow, mixed widths: 18-bit bases/starts, 19-bit offsets, 16-bit end/slope fields, 9-bit LUT offsets, and 3-bit segment counts. Width drift in any one field changes gamma curve interpretation.
- Gamut-remap registers pack two signed/fixed-point coefficients into one 32-bit register. A mask or shift error swaps or truncates coefficients and can produce strong color casts.
- Later DCN generations reorganize some MPCC fields, for example newer code introduces `MPCC_CONTROL2` for selected blend fields. Reusing this DCN 3.0.0 mask set against another ASIC revision is risky.

## Test Signals

Useful validation signals are mostly build-time macro coverage plus hardware/display behavior:

- Build DCN 3.0 display code with `dcn30_mpc.h`, `dcn30_mpc.c`, `dcn30_dwb.h`, and `dcn30_dwb_cm.c` included; missing or renamed field macros should fail through register-table expansion.
- Exercise MPCC composition with one plane, multiple planes, alpha blending, premultiplied alpha, global alpha/gain, background color, and bottom MPCC chaining.
- Validate MPCC idle/busy/disabled waits and state dumps through `mpc3_read_mpcc_state()` and `mpc3_read_reg_state()`.
- Program output gamma on several MPCC instances and verify RAM A/RAM B switching, LUT host writes, current-mode/current-select readback, and visible transfer-function changes.
- Test OGAM memory power transitions: power on before LUT writes, wait for `MPCC_OGAM_MEM_PWR_STATE`, then allow low-power mode when debug policy enables it.
- Program gamut remap A/B coefficient banks and confirm the driver can read back the current selected bank and matrix values without coefficient swaps.
- Exercise Display Writeback with output gamma RAM B active and validate captured-frame color output, not just scanout color.
- Run suspend/resume, modeset, hotplug, multi-display, and plane-update tests to catch stale MPCC routing or color block state after reprogramming.

## Open Cross-Chunk Questions

- The previous chunk must be consulted for the beginning of `DWB_OGAM_RAMB_START_CNTL_B/G/R`; this chunk starts after some RAMB start fields have already been defined.
- The next chunk must complete `MPCC_OGAM3` and likely cover additional MPCC OGAM instances or downstream MPC/DWB blocks before whole-file coverage can be reconciled.
- Final reconciliation should compare every register listed in `dcn30_mpc.h` and `dcn30_dwb.h` against both the offset and shift/mask headers to catch missing registers, missing fields, or generated-name mismatches.
