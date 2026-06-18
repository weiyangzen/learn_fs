# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 22657-25157

## Purpose

This chunk is a generated AMD DCN 4.1.0 register field shift/mask slice. It contains no executable C functions and no runtime data structures; its API is a set of preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Display Core combines these constants with the matching `dcn_4_1_0_offset.h` register offsets and register-helper macros to program MMIO fields by symbolic name rather than hardcoded bit positions.

The range starts in the tail of `dcn_dcec_mpc_mpcc_mcm2_dispdec`, continues through the `dcn_dcec_mpc_mpcc_mcm3_dispdec` movable color-management block, covers `dcn_dcec_mpc_mpc_ocsc_dispdec` output mux/denorm/output-CSC registers, and then enters the `dcn_dcec_opp_abm0_dispdec`, `abm1`, and start of `abm2` adaptive backlight management blocks. The chunk boundary is important: it begins mid-MPCC_MCM2 1D LUT region programming and ends mid-ABM2 luma-statistics coverage at `ABM2_DC_ABM1_LS_MIN_MAX_LUMA__ABM1_LS_MIN_LUMA__SHIFT`.

## Important APIs and register groups

- `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_30_31`, `REGION_32_33`, and the `MPCC_MCM2_MPCC_MCM_1DLUT_RAMB_*` registers finish MPCC instance 2 post-1D-LUT RAM programming. They define RAM A/B PWL region LUT offsets, segment counts, per-channel start/end values, start slopes, start bases, end bases, end slopes, and per-channel offsets.
- `MPCC_MCM2_MPCC_MCM_FIRST_GAMUT_REMAP_*` and `SECOND_GAMUT_REMAP_*` expose two gamut-remap matrix stages for MPCC instance 2. Each stage has coefficient-format and mode/current-mode fields plus packed matrix coefficient registers for A and B banks, with C11-C34 style coefficients packed as 16-bit halves.
- `MPCC_MCM2_MPCC_MCM_MEM_PWR_CTRL`, `MPCC_MCM2_MPCC_MCM_3DLUT_FAST_LOAD_SELECT`, and `MPCC_MCM2_MPCC_MCM_3DLUT_FAST_LOAD_STATUS` provide MPCC MCM memory power control and fast-load plumbing. Fast-load status exposes done, soft-underflow, and hard-underflow signals.
- `MPCC_MCM3_MPCC_MCM_SHAPER_*` covers MPCC instance 3 shaper LUT control: enable/mode, offsets, scales, LUT index/data, write-enable masks, RAM A/B start/end controls, and RAM A/B region layouts for 34 regions. This is the pre-3D-LUT shaper stage used in movable color management.
- `MPCC_MCM3_MPCC_MCM_3DLUT_*` defines MPCC instance 3 3D LUT mode, index, 30-bit/legacy data paths, read/write control, output normalization factor, output offsets, and RAM selection/read-write fields.
- `MPCC_MCM3_MPCC_MCM_1DLUT_*` defines MPCC instance 3 post-1D-LUT control, LUT index/data/control, RAM A/B per-channel PWL start/end/base/slope/offset fields, and the same paired-region offset/segment layout used by instance 2.
- `MPCC_MCM3_MPCC_MCM_FIRST_GAMUT_REMAP_*` and `SECOND_GAMUT_REMAP_*` repeat the dual-bank, dual-stage matrix remap fields for MPCC instance 3.
- `MPC_OUT0_MUX` through `MPC_OUT3_MUX` select MPC output sources and expose rate/flow-control fields for four MPC outputs. The adjacent `MPC_OUT*_DENORM_CONTROL`, `MPC_OUT*_DENORM_CLAMP_G_Y`, and `MPC_OUT*_DENORM_CLAMP_B_CB` fields configure output denormalization mode and per-channel clamp ranges.
- `MPC_OUT_CSC_COEF_FORMAT` plus `MPC_OUT0_CSC_*` through `MPC_OUT3_CSC_*` describe output color-space-conversion mode and packed matrix coefficients for four output pipes. Like MPCC gamut remap, the matrix data is banked into A/B coefficient registers and packed as paired coefficient fields.
- `ABM0_*`, `ABM1_*`, and the beginning of `ABM2_*` repeat the adaptive backlight management layout per ABM instance. The chunk includes PWM ambient/user/target/current/final/minimum levels, PWM ABM control, update sample-rate controls, grouped register locks, ABM enable/bypass, input pixel CSC coefficient selection, ACE PWL controls/data, HGLS read-progress status/clear bits, histogram control, luma-stat readouts, histogram sample-rate controls, histogram shift flags/index registers, result index/data, and master lock.

## Control flow and usage model

There is no local control flow in this header. These macros are consumed as generated metadata by Display Core register tables.

The runtime flow is:

1. The DCN 4.1 resource layer includes the matching generated offset and mask/shift headers.
2. ASIC-specific tables use macros such as `SRII`, `SRI_ARR`, `SF`, and `ABM_SF` to map symbolic register/field names onto offset, shift, and mask values.
3. Block code uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_SET_3`, and related helpers to read-modify-write named MMIO fields.

For the MPCC/MPC fields, `display/dc/mpc/dcn401/dcn401_mpc.h` declares the DCN4.01 register, mask, and shift lists that include the MPCC MCM gamut-remap and 3D-LUT fast-load fields. `display/dc/mpc/dcn401/dcn401_mpc.c` uses those tables in functions such as `mpc401_update_3dlut_fast_load_select`, `mpc401_get_3dlut_fast_load_status`, `mpc401_populate_lut`, `mpc401_program_lut_mode`, `mpc401_program_lut_read_write_control`, and `mpc401_set_gamut_remap`.

For the ABM fields, `display/dc/dce/dce_abm.h` defines the `ABM_MASK_SH_LIST_DCN401` mapping from the instance-0 generated names to the generic ABM field names used by the ABM implementation, while `display/dc/resource/dcn401/dcn401_resource.h` registers per-instance ABM addresses with `SRI_ARR(..., ABM, id)`. The generic DCE/DMUB ABM code then programs sample rates, histogram/luma controls, input CSC, PWM levels, ACE PWL data, missed-frame clears, and histogram result reads.

## State and persistence behavior

The header itself has no mutable state. The state represented by these masks lives in display hardware registers and persists according to display IP lifecycle: DC initialization, modeset, stream enable/disable, color-management updates, backlight updates, runtime power management, suspend/resume, and GPU/display reset.

Important stateful areas include:

- MPCC MCM LUT RAMs. Shaper, 3D LUT, and 1D LUT RAM A/B contents are programmed by software and selected by mode/bank fields. Banked programming lets software prepare one bank while another is active, but bank selection and RAM write controls must be sequenced correctly.
- MPCC MCM PWL region tables. Region offsets and segment counts define interpolation domains for shaper and post-1D LUTs. Bad starts, slopes, bases, or segment counts can produce visible color discontinuities or out-of-range values.
- Gamut-remap matrices. First and second matrix stages can be independently enabled/mode-selected and have A/B coefficient banks. Coefficient-format fields determine interpretation of the packed matrix values.
- 3D-LUT fast-load state. The select register chooses the source/hubp path for fast loading, while done/soft-underflow/hard-underflow are hardware status signals that can change asynchronously while LUT load is active.
- MCM memory power control. Forced-on, force-disable, shutdown, and light-sleep style fields affect availability of MPCC MCM memory backing the LUTs. These controls can persist until explicitly reprogrammed or reset.
- MPC output mux, denorm, and output-CSC state. These fields define which composition output feeds each downstream path and how final color values are clamped/converted before OPP/encoder use.
- ABM PWM and brightness state. Ambient, user, target, current, final duty, minimum duty, auto-update, and step-size fields collectively determine panel backlight behavior.
- ABM HGLS, ACE, and histogram/luma state. Histogram, luma-sum/min/max, filtered luma, pixel counts, ACE thresholds/slopes, sample-rate counters, lock bits, pending bits, missed-frame bits, and read-progress bits are live hardware/firmware-facing state, some of it read-only or write-one-to-clear.

## Dependencies and integration points

- Requires the matching `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` offsets. The offset and shift/mask headers are generated as a synchronized pair.
- Depends on AMDGPU Display Core register access helpers from `reg_helper.h`; callers are expected to use generated field metadata through helpers instead of open-coded full-register writes.
- Integrates with `display/dc/mpc/dcn401/dcn401_mpc.h` and `.c` for DCN4.01 movable color management, including shaper LUTs, 3D LUTs, post-1D LUTs, gamut remap, MCM memory power, and fast-load status.
- Integrates with older shared MPC helpers from DCN30/DCN32 because `dcn401_mpc` extends those register and field lists; several LUT RAM programming routines are reused from `mpc32`.
- Integrates with `display/dc/dce/dce_abm.h`, `display/dc/dce/dce_abm.c`, `display/dc/dce/dmub_abm_lcd.c`, and `display/dc/resource/dcn401/dcn401_resource.h` for ABM register lists, field mappings, initial setup, DMUB-facing ABM behavior, and per-instance ABM resource tables.
- Integrates with the broader display pipeline as follows: MPCC/MCM color processing sits in the MPC composition path, MPC output mux/OCSC feeds downstream OPP/encoder paths, and ABM belongs to the OPP/panel backlight/luma-statistics path.
- Shares repeated layouts across MPCC instances and ABM instances. This chunk covers complete instance-3 MCM masks, a tail of instance-2 MCM masks, and partial ABM2 masks; final per-file reconciliation must merge adjacent chunks for complete instance coverage.

## Risks and edge cases

- Generated header drift is the main risk. A correct mask with a stale offset, or a correct offset with stale bit definitions, can silently program the wrong hardware field.
- The chunk has two meaningful truncations. It starts after earlier MPCC_MCM2 shaper/3D/1D fields and stops before completing ABM2 luma-statistics and histogram/result fields. Consumers should not infer whole-file or whole-instance coverage from this chunk alone.
- Dense packed registers make full-register writes risky. Many registers pack two coefficients, two thresholds, offset plus segment count, status plus clear bits, or lock/pending/readback controls into one word.
- Bank-selection mistakes can be visible. 1D LUT, shaper LUT, 3D LUT, and gamut remap fields have RAM A/B or coefficient A/B banks; programming the active bank or switching mode before data is complete can create frame glitches or wrong color output.
- Width and sign/format mistakes are plausible. Coefficients, PWL starts, slopes, bases, offsets, thresholds, luma values, and LUT offsets use different 9-, 10-, 11-, 13-, 16-, 18-, 19-, 24-, and 32-bit masks. The generated masks protect bit placement but not semantic range.
- Hardware-owned status fields should not be treated as persistent software configuration. `*_CURRENT`, `*_DONE`, `*_UNDERFLOW`, `*_UPDATE_PENDING`, `*_READ_IN_PROGRESS`, `*_MISSED_FRAME`, luma/stat readouts, and histogram result fields can change asynchronously.
- ABM lock and missed-frame clear fields are especially sensitive. Incorrect lock sequencing or frame-start selection can cause ABM/ACE/PWM updates to miss vblank-safe update windows; clearing missed-frame bits incorrectly can hide timing bugs.
- Memory-power fields can make LUT programming unreliable if software powers down MCM memories while subsequent code assumes RAM contents or write access are available.
- ABM0/1/2 repeated layouts invite copy/paste instance mistakes. The DCN resource tables must pair the right ABM instance offsets with the generic fields; using instance-0 masks with wrong offsets is intentional in the table macros, but mixing register instances manually would be unsafe.

## Test signals

- Build coverage with DCN 4.1.0 enabled should compile all generated register tables that include `dcn_4_1_0_sh_mask.h` and `dcn_4_1_0_offset.h`, especially `dcn401_mpc` and `dcn401_resource` ABM tables.
- Static generated-header checks should verify representative `__SHIFT`/`_MASK` pairs for MPCC_MCM2/3, MPC_OUT0-3, and ABM0-2, and should compare repeated ABM layouts for intentional instance consistency.
- Color-management tests should exercise MPCC instance 3 shaper LUT, 3D LUT, post-1D LUT, first/second gamut remap, RAM A/B bank switching, 9-cube vs 17-cube 3D LUT sizes, 10-bit vs 12-bit 3D LUT data paths, and movable CM before/after placement.
- Fast-load tests should select a hubp source through `MPCC_MCM_3DLUT_FAST_LOAD_SELECT`, wait for `FL_DONE`, and validate soft/hard underflow status handling.
- Power-management tests should cover MCM memory power force/disable/shutdown/light-sleep fields across LUT programming, stream disable, runtime PM, suspend/resume, and GPU reset.
- MPC output tests should validate output mux selection, denorm clamp ranges, and output CSC matrices for all four `MPC_OUT*` instances in single-display, multi-display, and cloned/combined output scenarios.
- ABM tests should cover enable/bypass, user/target/current PWM transitions, ambient-level use, minimum/final duty cycle calculation, frame-start update locking, sample-rate counters, and automatic ABM current-level step size.
- ABM diagnostics should read luma sum/min/max, filtered luma, pixel counts, histogram result index/data, histogram shift flags/indexes, and missed-frame/read-progress bits while verifying write-one-to-clear behavior.
- Visual validation should include HDR/SDR color ramps, gamut-remap matrices, LUT-bank flips, brightness changes, and suspend/resume to catch color discontinuities, stale LUT contents, underflows, or ABM timing glitches.
