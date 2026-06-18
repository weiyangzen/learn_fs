# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 20053-22519

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.6 display hardware. It contains no executable functions or C data structures; its public surface is a dense set of preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. The constants are consumed with the matching DCN 3.6 offset header and the AMD Display Core register-helper macros so code can program MMIO fields without embedding bit positions directly.

The covered lines are entirely within the MPC/MPCC color-management area. The slice begins with the tail of `MPCC_OGAM2`, covers the full `dce_dc_mpc_mpcc_ogam3_dispdec` address block, covers the full `dce_dc_mpc_mpcc_mcm0_dispdec` address block, and then covers most of `dce_dc_mpc_mpcc_mcm1_dispdec` through the start of `MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_30_31`. In display-pipeline terms, these fields describe MPCC output gamma (OGAM), gamut remap matrices, movable color management (MCM) shaper LUTs, MCM 3D LUTs, MCM 1D LUTs, indexed RAM A/B region tables, and MCM memory power controls.

## Important APIs and register groups

- `MPCC_OGAM2_*` at the beginning is a boundary continuation from the prior chunk. It finishes output-gamma RAMB region definitions for regions 26-33, then defines `MPCC_GAMUT_REMAP_COEF_FORMAT`, `MPCC_GAMUT_REMAP_MODE`, and the A/B gamut-remap coefficient registers `MPC_GAMUT_REMAP_C11_C12` through `C33_C34`.
- `MPCC_OGAM3_MPCC_OGAM_CONTROL` exposes output-gamma mode, LUT bank select, PWL disable, and readback/current-state fields. `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_DATA`, and `MPCC_OGAM_LUT_CONTROL` define indexed host access to 18-bit OGAM LUT entries, write color masks, read color select, host select, and configuration mode.
- `MPCC_OGAM3_MPCC_OGAM_RAMA_*` and `MPCC_OGAM3_MPCC_OGAM_RAMB_*` define dual-bank piecewise-linear output-gamma tables. Each bank has B/G/R start controls, start slopes, start bases, end controls, offsets, and region descriptors for regions 0-33. Region registers pack two regions per register with 9-bit LUT offsets and 3-bit segment counts.
- `MPCC_OGAM3_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM3_MPC_GAMUT_REMAP_*` define the gamut-remap coefficient format, mode/current bits, and two coefficient banks. The coefficient registers pack two 16-bit matrix elements per register, with A and B banks allowing banked or double-buffered matrix programming.
- `MPCC_MCM0_MPCC_MCM_SHAPER_*` defines MCM shaper enable/control, per-channel 19-bit offsets, scale fields, shaper LUT index/data, write-enable color masks, RAMA/RAMB start/end controls, and 34 region descriptors per bank. This is the pre-3D-LUT transfer-function surface in the movable color-management pipeline.
- `MPCC_MCM0_MPCC_MCM_3DLUT_*` defines 3D LUT mode, indexed access, normal and 30-bit data paths, read/write control, output normalization factor, and per-channel output offsets. The read/write control fields include color-channel select, address update, and read/write selectors for host-driven table loading.
- `MPCC_MCM0_MPCC_MCM_1DLUT_*` mirrors the output-gamma style 1D LUT programming surface: control mode/select/PWL-disable/current bits, LUT index/data/control, RAMA/RAMB start controls, slopes, bases, end controls, offsets, and region descriptor tables.
- `MPCC_MCM0_MPCC_MCM_MEM_PWR_CTRL` defines memory power controls and readback states for the shaper, 3DLUT, and 1DLUT memories: force, disable, low-power mode, and power-state fields.
- `MPCC_MCM1_*` repeats the same shaper, 3DLUT, and 1DLUT field layout for MCM instance 1. This chunk reaches `MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_30_31__MPCC_MCM_1DLUT_RAMB_EXP_REGION30_LUT_OFFSET__SHIFT`; the remaining region 30/31 masks, region 32/33, and MCM1 memory power fields are expected in the following chunk.

## Control flow and usage model

There is no local control flow in this header. The constants are generated hardware metadata. A typical DCN 3.6 use path is:

1. Include `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h` file.
2. Expand register lists and field lists with macros such as `SRII`, `SRI_ARR`, `SF`, `FD_MASK`, and `FD_SHIFT`.
3. Store offsets, masks, and shifts in block-specific register tables, for example MPC/MPCC tables built from the DCN32 resource-header macros and instantiated from `dcn36_resource.c`.
4. Let color-management and hardware-sequencing code call register helpers such as `REG_SET`, `REG_UPDATE`, `REG_SET_2`, and indexed LUT write routines to program the hardware fields.

The key integration pattern is name concatenation. Resource headers refer to generic names such as `MPCC_MCM_1DLUT_RAMB_REGION_28_29` with a block and instance (`MPCC_MCM`, `0` or `1`); the preprocessor expands that into symbols from this generated header, such as `regMPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_28_29` from the offset header and `MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_28_29__..._MASK` from this mask header. This makes exact generated naming part of the ABI between the ASIC register database and the driver sources.

## State and persistence behavior

The header itself has no mutable state and persists only as compile-time constants. The state described by these constants lives in MPCC/MPC MMIO registers and indexed LUT RAMs. That state is hardware-visible across a modeset or color-management update until overwritten, reset, power-gated, or lost through display IP reset/suspend/resume.

The output-gamma and MCM 1D/shaper LUT blocks are banked with RAMA/RAMB tables. Software selects banks, programs indexes/data/control fields, loads per-channel values, writes region descriptors, and then selects the active mode/bank. `*_CURRENT` fields expose the hardware's active mode or bank readback, while `*_SELECT` fields are software-programmed selections. The region tables are persistent programmed curves: incorrect offsets or segment counts remain active and can affect later frames until corrected.

The 3D LUT state is also indexed and persistent. Host programming depends on `INDEX`, `DATA`, `DATA_30BIT`, and `READ_WRITE_CONTROL` coordination. The output normalization and per-channel output offsets are separate persistent scalar fields that shape the result after table lookup.

`MPCC_MCM*_MEM_PWR_CTRL` is power-management state for LUT memories. The force/disable/low-power-mode fields affect whether the shaper, 3DLUT, and 1DLUT memories are accessible and retained, while the state fields are readbacks. These controls must be sequenced with LUT programming and runtime power management, because a powered-down LUT memory can make later indexed writes ineffective or stale.

## Dependencies and integration points

- Requires `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` for matching register addresses and base indices.
- Included by DCN 3.6 display code such as `display/dc/resource/dcn36/dcn36_resource.c`, `display/dc/irq/dcn36/irq_service_dcn36.c`, and `display/dmub/src/dmub_dcn36.c`.
- Integrated through `display/dc/resource/dcn32/dcn32_resource.h`, whose MPC register lists enumerate `MPCC_OGAM_*` and `MPCC_MCM_*` registers for instances using `SRII`. DCN 3.6 resource initialization includes the DCN 3.6 offset and mask headers before expanding those register-list macros.
- Consumed by the Display Core register-helper layer through generated field masks and shifts. The field constants are not type checked; compile-time symbol resolution is the main guard against mismatched names.
- Tied to higher-level DC color-management APIs and state objects that describe output gamma, gamut remap, shaper LUTs, 3D LUTs, 1D LUTs, and the movable color-management pipeline placement. User-visible effects surface through HDR, color-managed desktop, display calibration, and multi-plane composition paths.
- Related debug state appears in `dc.h`, including pipe debug capture fields for `MPCC_OGAM_CONTROL` mode/select/PWL-disable. Those debug surfaces depend on these exact field positions when dumping or interpreting hardware state.

## Risks and edge cases

- Generated-header drift is the largest structural risk. The offset and shift/mask headers must describe the same ASIC register database. A stale mask with a new offset, or the reverse, can compile while programming the wrong bits.
- Instance mismatch is easy because `MPCC_OGAM2`, `MPCC_OGAM3`, `MPCC_MCM0`, and `MPCC_MCM1` have near-identical field names. Programming the wrong MPCC or MCM instance can produce per-pipe color failures that look like plane, stream, or timing issues.
- Chunk-boundary truncation matters for documentation and automated analysis: this chunk starts mid-`MPCC_OGAM2` and ends mid-`MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_30_31`. Final per-file analysis must reconcile adjacent chunks before claiming complete coverage for those register families.
- Packed-field writes can corrupt neighboring fields. Many registers pack two coefficients, two region descriptors, multiple mode/current bits, or multiple per-memory power controls into one 32-bit register. Full-register writes can clobber adjacent fields or readback/status bits.
- Width constraints are hardware-specific: common fields here include 1-bit selectors, 2-bit modes, 3-bit segment counts, 9-bit LUT offsets, 16-bit coefficients and slope/end fields, 18-bit LUT data/start/base fields, 19-bit offsets, and 30-bit 3DLUT data. Callers must clamp before shifting.
- Bank and current-state sequencing is subtle. `SELECT`, `MODE`, `PWL_DISABLE`, and `*_CURRENT` fields imply double-buffered hardware behavior. Switching banks before all RAMA/RAMB or coefficient values are loaded can produce visible frame-to-frame color artifacts.
- Indexed LUT programming is order-sensitive. Wrong host selection, color write mask, read color select, index auto-update, or data width can silently load only one channel, load the wrong index, or mix 18-bit and 30-bit data paths incorrectly.
- Memory power controls can invalidate color programming assumptions. Disabling or low-powering shaper/3DLUT/1DLUT memory while a pipeline expects it active can cause black, bypassed, or distorted color output depending on hardware behavior.
- Cross-version copy assumptions are risky. These fields resemble DCN 3.2 and DCN 3.5 layouts, but DCN 3.6 is its own generated header. Any shared driver macro must still be verified against the DCN 3.6 generated symbols and bit positions.

## Test signals

- Build DCN 3.6 display support and ensure `dcn36_resource.c`, the DCN 3.6 IRQ service, and DMUB DCN 3.6 code compile against the paired `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` headers.
- Static checks can compare repeated `MPCC_OGAM3`, `MPCC_MCM0`, and `MPCC_MCM1` field layouts against neighboring instances and against the register-list expectations in `dcn32_resource.h`.
- Color-management functional tests should load and switch MPCC OGAM LUTs, gamut-remap matrices, MCM shaper LUTs, MCM 3D LUTs, and MCM 1D LUTs across SDR, HDR, and calibrated-color paths.
- Bank-switch tests should verify RAMA/RAMB programming, `SELECT`/`CURRENT` readback, PWL enable/disable behavior, and no visible corruption during commit or modeset transitions.
- Instance-coverage tests should exercise multiple pipes/MPCCs so `OGAM2`, `OGAM3`, `MCM0`, and `MCM1` register tables are not only compile-tested.
- Runtime register-dump diagnostics should inspect `MPCC_OGAM*_MPCC_OGAM_CONTROL`, `MPCC_OGAM*_MPCC_GAMUT_REMAP_MODE`, `MPCC_MCM*_MPCC_MCM_3DLUT_MODE`, `MPCC_MCM*_MPCC_MCM_1DLUT_CONTROL`, LUT index/control registers, and `MPCC_MCM*_MPCC_MCM_MEM_PWR_CTRL` when investigating color artifacts or LUT programming failures.
- Power-management tests should cover suspend/resume, display off/on, runtime power gating, and memory low-power transitions while MCM shaper/3DLUT/1DLUT state is enabled.
- Visual validation should include gradients, color ramps, HDR metadata/color-management paths, and multi-plane composition, because bad region offsets, segment counts, coefficient packing, or bank selection often appears as banding, clipped channels, or only one affected pipe.
