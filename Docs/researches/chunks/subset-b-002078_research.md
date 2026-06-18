# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 48844-51064

## Scope

This chunk is a generated DCN 3.5.0 ASIC register-field shift/mask range for the AMD display MPCC movable color-management (`MPCC_MCM`) blocks. It contains `#define` constants only; there are no C functions, structs, or executable control flow in this header slice. The range starts inside the `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_10_11` family, covers the rest of the `MPCC_MCM1` movable color-management block, all visible `MPCC_MCM2` movable color-management definitions, and ends partway through the `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21` family.

Within the requested lines I counted 2,217 generated field constants across `MPCC_MCM1`, `MPCC_MCM2`, and `MPCC_MCM3`. The main repeated register families are:

- Shaper LUT RAM A/B region programming: `MPCC_MCM_SHAPER_RAMA_REGION_*`, `MPCC_MCM_SHAPER_RAMB_REGION_*`, `*_START_CNTL_{B,G,R}`, and `*_END_CNTL_{B,G,R}`.
- Movable color-management 3D LUT programming: `MPCC_MCM_3DLUT_MODE`, `MPCC_MCM_3DLUT_INDEX`, `MPCC_MCM_3DLUT_DATA`, `MPCC_MCM_3DLUT_DATA_30BIT`, `MPCC_MCM_3DLUT_READ_WRITE_CONTROL`, output normalization, and RGB output offset/scale registers.
- Post-blend 1D LUT programming: `MPCC_MCM_1DLUT_CONTROL`, `MPCC_MCM_1DLUT_LUT_INDEX`, `MPCC_MCM_1DLUT_LUT_DATA`, `MPCC_MCM_1DLUT_LUT_CONTROL`, and RAM A/B PWL region/start/end/offset registers.
- Memory power control: `MPCC_MCM_MEM_PWR_CTRL` for shaper, 3D LUT, and 1D LUT memories.

## Purpose

These macros are the bit-level contract between the DCN 3.5.0 display driver and the MPCC movable color-management hardware. Each `__SHIFT` macro gives the low bit of a field and each `_MASK` macro gives the field mask inside a 32-bit MMIO register. Runtime code combines these with matching offset macros from `dcn_3_5_0_offset.h` and register-list declarations to perform `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` operations without spelling raw bit positions in driver logic.

The covered fields support color-processing stages attached to MPCC instances:

- The shaper LUT maps input values before the 3D LUT using RAM A/RAM B double-buffering.
- The 3D LUT stores tetrahedral LUT data in multiple RAM banks and supports both 17-cube/9-cube sizes and 12-bit/30-bit packed access modes.
- The post-blend 1D LUT applies a PWL/gamma correction stage after the 3D LUT, also with RAM A/RAM B double-buffering.
- The memory power fields let the driver force or observe low-power states for shaper, 3D LUT, and 1D LUT memories.

## Important APIs And Data Shapes

This header chunk does not define callable APIs, but it is consumed by the DC register helper API. The important macro shape is:

- `MPCC_MCMn_REGISTER__FIELD__SHIFT`: field shift for instance `n`.
- `MPCC_MCMn_REGISTER__FIELD_MASK`: field mask for instance `n`.

The corresponding runtime data structures are populated by token-pasting macros in the display resource and MPC layers:

- `MPC_REG_LIST_DCN3_2` and `MPC_REG_LIST_DCN3_2_RI` enumerate MPCC MCM registers such as `MPCC_MCM_SHAPER_RAMA_REGION_10_11`, `MPCC_MCM_3DLUT_MODE`, `MPCC_MCM_1DLUT_RAMA_REGION_32_33`, and `MPCC_MCM_MEM_PWR_CTRL`.
- `MPC_COMMON_MASK_SH_LIST_DCN32(__SHIFT)` and `MPC_COMMON_MASK_SH_LIST_DCN32(_MASK)` load shift and mask values into `struct dcn30_mpc_shift` and `struct dcn30_mpc_mask`.
- The generated definitions here are accessed through `mpc30->mpc_shift->FIELD` and `mpc30->mpc_mask->FIELD` via the `FN(reg_name, field_name)` macro used by `reg_helper.h`.

The field encodings line up with the MPCC MCM enum definitions in `include/soc24_enum.h` and similar SoC enum headers. Relevant enum domains include `MPCC_MCM_3DLUT_30BIT_ENUM`, `MPCC_MCM_3DLUT_RAM_SEL`, `MPCC_MCM_3DLUT_SIZE_ENUM`, `MPCC_MCM_GAMMA_LUT_MODE_ENUM`, `MPCC_MCM_GAMMA_LUT_SEL_ENUM`, `MPCC_MCM_LUT_NUM_SEG`, `MPCC_MCM_LUT_RAM_SEL`, `MPCC_MCM_LUT_READ_COLOR_SEL`, `MPCC_MCM_MEM_PWR_FORCE_ENUM`, and `MPCC_MCM_MEM_PWR_STATE_ENUM`.

## Runtime Control Flow

The generated macros participate in several runtime flows, primarily through `display/dc/mpc/dcn32/dcn32_mpc.c`, which is reused by DCN 3.5-family resources.

For post-blend 1D LUT programming:

1. `mpc32_program_post1dlut()` reads `MPCC_MCM_1DLUT_MODE_CURRENT` and `MPCC_MCM_1DLUT_SELECT_CURRENT` from `MPCC_MCM_1DLUT_CONTROL[mpcc_id]` to determine the active RAM.
2. It powers the 1D LUT memory through `MPCC_MCM_MEM_PWR_CTRL` fields such as `MPCC_MCM_1DLUT_MEM_PWR_DIS`, `MPCC_MCM_1DLUT_MEM_PWR_FORCE`, and `MPCC_MCM_1DLUT_MEM_PWR_STATE`.
3. It configures write color masks and RAM host selection through `MPCC_MCM_1DLUT_LUT_CONTROL`.
4. It programs RAM A or RAM B PWL region settings through `MPCC_MCM_1DLUT_RAMA_*` or `MPCC_MCM_1DLUT_RAMB_*` registers, using region fields for LUT offsets and segment counts.
5. It writes LUT samples through `MPCC_MCM_1DLUT_LUT_INDEX` and `MPCC_MCM_1DLUT_LUT_DATA`, then flips `MPCC_MCM_1DLUT_MODE` and `MPCC_MCM_1DLUT_SELECT` to activate the newly written RAM.

For shaper LUT programming:

1. `mpc32_get_shaper_current()` reads `MPCC_MCM_SHAPER_MODE_CURRENT`.
2. `mpc32_configure_shaper_lut()` sets `MPCC_MCM_SHAPER_LUT_WRITE_EN_MASK`, selects RAM A or B, and resets `MPCC_MCM_SHAPER_LUT_INDEX`.
3. `mpc32_program_shaper_luta_settings()` and `mpc32_program_shaper_lutb_settings()` write start/end control and all 34 exponential region descriptors, including the fields covered at the beginning of this chunk for `MPCC_MCM1` RAM A regions 10-33 and the full RAM B region list.
4. `mpc32_program_shaper_lut()` writes PWL sample data through `MPCC_MCM_SHAPER_LUT_DATA`.
5. `MPCC_MCM_SHAPER_LUT_MODE` selects bypass, RAM A, or RAM B.

For 3D LUT programming:

1. `get3dlut_config()` reads `MPCC_MCM_3DLUT_MODE_CURRENT`, `MPCC_MCM_3DLUT_30BIT_EN`, and `MPCC_MCM_3DLUT_SIZE`.
2. `mpc32_select_3dlut_ram()` chooses the target RAM and 12-bit/30-bit access mode with `MPCC_MCM_3DLUT_RAM_SEL` and `MPCC_MCM_3DLUT_30BIT_EN`.
3. `mpc32_select_3dlut_ram_mask()` sets `MPCC_MCM_3DLUT_WRITE_EN_MASK` and resets `MPCC_MCM_3DLUT_INDEX`.
4. `mpc32_set3dlut_ram12()` writes paired samples through `MPCC_MCM_3DLUT_DATA0` and `MPCC_MCM_3DLUT_DATA1`; `mpc32_set3dlut_ram10()` writes packed 30-bit values through `MPCC_MCM_3DLUT_DATA_30BIT`.
5. `mpc32_set_3dlut_mode()` sets `MPCC_MCM_3DLUT_MODE` and `MPCC_MCM_3DLUT_SIZE` after RAM programming.

## State And Persistence

The state represented by this chunk persists in hardware registers, not in software storage:

- Current active RAM state is exposed through fields such as `MPCC_MCM_SHAPER_MODE_CURRENT`, `MPCC_MCM_1DLUT_MODE_CURRENT`, `MPCC_MCM_1DLUT_SELECT_CURRENT`, and `MPCC_MCM_3DLUT_MODE_CURRENT`.
- LUT content persists in MPCC MCM RAMs until overwritten, reset, or powered down according to hardware behavior.
- Region descriptor registers persist the PWL segmentation model: start coordinate, start segment, end coordinate/base/slope, per-region LUT offset, and per-region number of segments.
- Memory power fields persist hardware power policy and status for shaper, 3D LUT, and 1D LUT memories. The driver may wait for state transitions before writing LUT memory.

The software-visible persistence is indirect: resource construction stores register offsets, masks, and shifts in per-device MPC register tables. The numeric constants in this generated header must remain synchronized with the matching offset header and with the MPC register-list macros.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h` supplies the corresponding MMIO register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h` declares the DCN 3.2-style MPCC MCM register list consumed by DCN 3.5/3.5.1 resource files.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c` instantiates `MPC_REG_LIST_DCN3_2_RI(0..3)` and the DCN32 MPC mask/shift list for a 3.5-family resource.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c` performs runtime shaper, 3D LUT, 1D LUT, and memory-power programming with these fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_cm_common.c` provides `cm_helper_program_gamcor_xfer_func()` and `cm3_helper_translate_curve_to_hw_format()`, which produce and program the PWL region descriptors used by these fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` defines symbolic enum values for MPCC MCM modes, RAM selections, segment counts, and memory-power states.

The source-tree integration pattern is generated-register token pasting. A register field such as `MPCC_MCM_1DLUT_RAMA_EXP_REGION0_LUT_OFFSET` appears in runtime code without an instance number, while the mask/shift list resolves it through a representative instance macro such as `MPCC_MCM0_*`; the per-instance offset arrays select `MPCC_MCM1`, `MPCC_MCM2`, or `MPCC_MCM3` at runtime.

## Risks

- Numeric bitfield drift is high impact. If a shift or mask is wrong, LUT programming can silently corrupt color output, select the wrong RAM, write wrong LUT samples, or mis-handle memory power state.
- The chunk starts and ends in the middle of repeated generated families. A reviewer must merge with adjacent chunks before making whole-file completeness claims for `MPCC_MCM1` or `MPCC_MCM3`.
- The RAM A/B double-buffering model depends on current-state fields matching mode/select fields. Wrong masks for `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `*_LUT_MODE`, or `*_LUT_SELECT` can cause updates to target the active RAM or fail to activate new LUT content.
- The region descriptors use compact bitfields: LUT offset uses the low 9 bits, segment count uses a 3-bit field at bit 12 or 28, and paired-region registers pack two regions per word. Off-by-one generation errors in region numbering or masks would be difficult to catch through compilation.
- `MPCC_MCM_MEM_PWR_CTRL` fields control and observe low-power states. Bad masks can make the driver wait on the wrong status field or power down LUT memory while programming it.
- Some runtime code writes RAMB shaper registers with field names carrying `RAMA` in the field token. That works only because the generated field names and masks are intentionally compatible across RAM A/B variants; changing the generated naming convention would break token-pasted access.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for DCN 3.5/3.5.1 display code with `dcn_3_5_0_sh_mask.h`, `dcn_3_5_0_offset.h`, and the DCN32 MPC register/mask lists enabled. Token-paste mismatches should fail compilation.
- KMS color-management tests that exercise shaper LUT, 3D LUT, and post-blend 1D LUT programming on supported hardware.
- Runtime traces or register dumps showing `MPCC_MCM_1DLUT_CONTROL`, `MPCC_MCM_SHAPER_CONTROL`, `MPCC_MCM_3DLUT_MODE`, and `MPCC_MCM_MEM_PWR_CTRL` fields changing as expected when enabling, disabling, and swapping LUTs.
- IGT/DRM color tests with gamma, degamma, CTM/3D LUT, PQ, HLG, and gamma 2.2 transfer functions. The PWL conversion path should produce expected segment distributions and no `DC_LOG_ERROR("Losing delta precision while programming shaper LUT.")` messages.
- Low-power validation with `enable_mem_low_power.bits.mpc` and `.cm` toggled. `REG_WAIT` on `MPCC_MCM_SHAPER_MEM_PWR_STATE`, `MPCC_MCM_3DLUT_MEM_PWR_STATE`, and `MPCC_MCM_1DLUT_MEM_PWR_STATE` should complete without hitting debug breaks.
- Cross-header diffing against adjacent generated DCN headers, such as `dcn_3_2_0_sh_mask.h` and `dcn_3_5_1_sh_mask.h`, for matching MPCC MCM field layout where hardware compatibility is expected.

## Chunk Boundary Notes

This chunk begins after the first lines for `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_10_11`; the corresponding `REGION_0_1` through early `REGION_10_11` definitions are in the previous chunk. It ends at `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_20_21__MPCC_MCM_1DLUT_RAMB_EXP_REGION21_NUM_SEGMENTS__SHIFT`; the remaining masks for that register, later RAMB regions, and the likely `MPCC_MCM3_MPCC_MCM_MEM_PWR_CTRL` fields continue in the next chunk. The final per-file research document should merge these boundaries before summarizing complete per-instance coverage.
