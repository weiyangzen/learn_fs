# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 17714-20172

## Purpose

This chunk is part of AMDGPU Display Core Next 3.2.0's generated register field mask/shift header. It contains preprocessor constants for the MPC/MPCC movable color management (MCM) register fields used by DCN 3.2 display color programming. The chunk is data-only: it declares `__SHIFT` and `_MASK` macros for hardware bitfields and has no functions, storage, or direct control flow.

The visible range starts by finishing `MPCC_OGAM3_MPC_GAMUT_REMAP_*_B` coefficient fields, then covers the `dcn_dc_mpc_mpcc_mcm0_dispdec`, `dcn_dc_mpc_mpcc_mcm1_dispdec`, and the beginning of `dcn_dc_mpc_mpcc_mcm2_dispdec` address blocks. These blocks describe per-MPCC MCM resources for MPCC instances 0, 1, and part of 2.

## Register Families Covered

- `MPCC_OGAM3_MPC_GAMUT_REMAP_Cxx_Cyy_B`: 16-bit packed gamut remap matrix coefficient fields for MPCC OGAM instance 3. This chunk contains the tail of the B coefficient bank for C11/C12 through C33/C34.
- `MPCC_MCM{0,1,2}_MPCC_MCM_SHAPER_*`: shaper LUT control, offsets, scales, LUT index/data ports, A/B RAM start/end controls, and packed region descriptors.
- `MPCC_MCM{0,1,2}_MPCC_MCM_3DLUT_*`: 3D LUT mode, size/current-state, index, packed 16-bit data pair, 30-bit data path, read/write control, output normalization, and RGB output offset/scale fields.
- `MPCC_MCM{0,1,2}_MPCC_MCM_1DLUT_*`: post-1D LUT control, LUT index/data/control fields, A/B RAM start/slope/base/end/offset controls, and packed 34-region piecewise-linear descriptors.
- `MPCC_MCM{0,1}_MPCC_MCM_MEM_PWR_CTRL`: memory power force/disable/low-power-mode/state fields for shaper, 3D LUT, and 1D LUT memories. The MPCC_MCM2 memory power block appears later in the file outside this exact chunk; this chunk reaches only early MPCC_MCM2 1DLUT RAMA region fields.

The repeated region registers pack two logical regions per register. For example region pairs use offset fields at bits 0 and 16, segment-count fields at bits 12 and 28, masks `0x000001FF`, `0x00007000`, `0x01FF0000`, and `0x70000000`. This same field layout appears for shaper RAM A/B and 1DLUT RAM A/B.

## Important APIs, Types, and Consumers

The header itself exports macros, not C APIs. Its important public surface is the stable naming convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

These macros are consumed by register-table construction macros such as `SF(...)` in `drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h`. That file maps the generated register-specific symbols, usually from instance 0, into the generic `dcn30_mpc_shift` and `dcn30_mpc_mask` members used by the MPC implementation. The register addresses themselves are supplied by companion register headers and `SRII(...)` register list macros; this chunk supplies only bit positions and masks.

Runtime users are in `drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c`, especially:

- MCM memory power setup and waits using `MPCC_MCM_MEM_PWR_CTRL`, `MPCC_MCM_*_MEM_PWR_FORCE`, `*_DIS`, `*_LOW_PWR_MODE`, and `*_STATE`.
- `mpc32_program_post1dlut`, which uses 1DLUT mode/select/current-state, LUT control/index/data, and RAM A/B PWL region fields.
- `mpc32_program_shaper`, which uses shaper LUT mode/current-state, shaper LUT index/data/write-select, shaper start/end controls, and RAM A/B region fields.
- `mpc32_program_3dlut`, which uses 3DLUT mode/size/current-state, index, data, 30-bit data, RAM select, write-enable mask, 30-bit enable, and read-select fields.

## Control Flow and State Behavior

There is no executable control flow in this chunk. The effective control flow is indirect: `REG_SET`, `REG_SET_2`, `REG_SET_4`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_WAIT` expand through the MPC register tables and use these masks/shifts to modify memory-mapped hardware registers.

State is hardware-resident. LUT programming paths select RAM A or RAM B, write indexed LUT data through data ports, program PWL region descriptors, then switch mode/select fields so the hardware consumes the newly loaded RAM. Current-state fields such as `MPCC_MCM_1DLUT_MODE_CURRENT`, `MPCC_MCM_1DLUT_SELECT_CURRENT`, `MPCC_MCM_SHAPER_MODE_CURRENT`, and `MPCC_MCM_3DLUT_MODE_CURRENT` are read back to avoid clobbering the active bank. Memory power fields persist only in the display engine register state; they are not filesystem or driver object persistence.

## Dependencies and Integration Points

- Depends on the generated DCN 3.2 register-address header for matching register addresses. A correct mask with a wrong address or instance binding would still compile but program the wrong hardware field.
- Integrated into `dcn32_mpc.h` through `SF(...)` field-list entries and into per-instance register arrays through `SRII(...)`.
- Used by the AMD Display Core MPC layer, which is reached from color-management state application for planes and MPCC composition.
- Closely tied to DCN 3.2 hardware documentation/generation. The file-wide include guard `_dcn_3_2_0_SH_MASK_HEADER` makes the symbols available to compile-time register table definitions.

## Risks and Edge Cases

- Bitfield drift is the main risk. These constants are generated hardware contracts; a single incorrect shift/mask can silently corrupt unrelated fields in the same register.
- Packed region fields are easy to misuse because code commonly writes generic field names like `MPCC_MCM_SHAPER_RAMA_EXP_REGION0_*` against many different region-pair registers. That relies on every region-pair register sharing the same layout.
- Banked LUT programming depends on the A/B RAM select fields and current-state readback masks. Incorrect masks can cause updates to the active bank, producing visible color corruption or flicker.
- Memory power state masks are used with `REG_WAIT`. Bad state masks can create false success, timeout paths, or power-gated memory access during LUT programming.
- This chunk stops in the middle of the MPCC_MCM2 1DLUT RAMA region list. The continuation, including later MPCC_MCM2 RAMA/RAMB regions and memory power fields, must be covered by adjacent chunks before a whole-file report can claim full MPCC_MCM2 coverage.

## Test Signals

- Compile coverage: any missing or renamed macro referenced by `dcn32_mpc.h` or `dcn32_mpc.c` should fail the AMDGPU/DC build.
- Register table consistency: `SF(...)` entries should resolve the field names from this generated header into the expected `mpc_shift` and `mpc_mask` struct members.
- Runtime display/color validation: enabling post-1DLUT, shaper, and 3DLUT paths should not produce banding, channel swaps, incorrect gamut mapping, or flicker during mode updates.
- Power-management validation: MCM memory power transitions should complete without `REG_WAIT` timeouts and without LUT programming failures after power gating.
- Hardware readback/debug traces can compare programmed register values against expected masks for region descriptors, LUT write masks, RAM select fields, and mode/current-state fields.
