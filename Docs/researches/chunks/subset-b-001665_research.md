# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h

Chunk: `subset-b-001665`
Lines researched: 22382-24866

## Purpose

This chunk is part of the generated DCN 2.1 register shift/mask header for the AMD display driver. It defines bit positions (`__SHIFT`) and bit masks (`_MASK`) for selected MPC/MPCC display color blocks. The line range covers:

- The tail of `dce_dc_mpc_mpcc_ogam2_dispdec`, specifically `MPCC_OGAM2` RAM B end and region fields.
- Full output-gamma register field tables for `MPCC_OGAM3` through `MPCC_OGAM7`.
- The beginning of `dce_dc_mpc_mpc_ocsc_dispdec`, covering `MPC_OUT_CSC_COEF_FORMAT` and the first output CSC coefficient registers for `MPC_OUT0`, `MPC_OUT1`, `MPC_OUT2`, and the opening of `MPC_OUT3`.

The header itself contains no executable logic. Its purpose is to give the display core exact ASIC bit layouts so common register helper macros can write output gamma LUT configuration and output color-space conversion coefficients without hard-coded shifts in the C implementation.

## Important Definitions

The `MPCC_OGAMn` definitions are repeated per MPCC instance. For `n = 3..7`, each instance has:

- `MPCC_OGAMn_MPCC_OGAM_MODE`: 2-bit output gamma mode selector.
- `MPCC_OGAMn_MPCC_OGAM_LUT_INDEX`: 9-bit LUT write/read index.
- `MPCC_OGAMn_MPCC_OGAM_LUT_DATA`: 19-bit LUT data payload.
- `MPCC_OGAMn_MPCC_OGAM_LUT_RAM_CONTROL`: write-enable mask, RAM A/B select, and config status fields.
- `MPCC_OGAMn_MPCC_OGAM_RAMA_*` and `MPCC_OGAMn_MPCC_OGAM_RAMB_*`: double-buffered gamma RAM A/B fields for blue, green, and red channel start, slope, end, and 34 region descriptors.

The RAM A/B region definitions use a consistent packed layout:

- Region LUT offset: bits `[8:0]`, mask `0x000001FF`.
- Region segment count: bits `[14:12]`, mask `0x00007000`.
- Paired odd region offset: bits `[24:16]`, mask `0x01FF0000`.
- Paired odd region segment count: bits `[30:28]`, mask `0x70000000`.

Per-channel start/end definitions also repeat:

- `EXP_REGION_START_*`: 18-bit value at shift `0x0`, mask `0x0003FFFF`.
- `EXP_REGION_START_SEGMENT_*`: 7-bit segment field at shift `0x14`, mask `0x07F00000`.
- `EXP_REGION_LINEAR_SLOPE_*`: 18-bit field at shift `0x0`, mask `0x0003FFFF`.
- `EXP_REGION_END_*`: 16-bit field at shift `0x0`, mask `0x0000FFFF`.
- `EXP_REGION_END_SLOPE_*` and `EXP_REGION_END_BASE_*`: two 16-bit fields packed into low/high halves of the end-control register.

The `MPC_OUT_CSC_*` portion begins the output CSC block:

- `MPC_OUT_CSC_COEF_FORMAT`: one coefficient-format bit per OCSC pipe (`MPC_OCSC0_COEF_FORMAT` through `MPC_OCSC3_COEF_FORMAT`).
- `MPC_OUT{0,1,2}_CSC_MODE`: 2-bit `MPC_OCSC_MODE` selectors.
- `MPC_OUT{0,1,2}_CSC_Cxx_Cyy_{A,B}`: paired 16-bit color matrix coefficients packed into one register, with the first coefficient in bits `[15:0]` and the second in bits `[31:16]`.
- `MPC_OUT3_CSC_MODE` and the start of `MPC_OUT3_CSC_C11_C12_A` appear at the chunk boundary; the remaining `MPC_OUT3` CSC masks are outside this chunk.

## Integration Points

These macros are included by generated DCN 2.1 resource/register tables and then consumed through the display core's MPC abstraction. The immediate integration pattern is:

- Resource and MPC headers use `SF(register, field, mask_sh)`-style macros to populate `struct dcn20_mpc_shift` and `struct dcn20_mpc_mask` fields.
- Register-address macros from the companion offset header identify which MMIO register to access.
- `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_UPDATE_2`, and related helpers combine the register address with these shift/mask values.

Observed downstream consumers in the same source tree include:

- `display/dc/mpc/dcn20/dcn20_mpc.h`, which declares the DCN2 MPC register, shift, and mask field lists for MPCC OGAM and MPC output CSC.
- `display/dc/mpc/dcn20/dcn20_mpc.c`, where `mpc2_set_output_csc()`, `mpc2_set_ocsc_default()`, `mpc2_set_output_gamma()`, `mpc2_program_luta()`, and `mpc2_program_lutb()` use these fields indirectly through `mpc20->mpc_shift` and `mpc20->mpc_mask`.
- `display/dc/hwss/dcn20/dcn20_hwseq.c`, where `dcn20_program_output_csc()` chooses custom or default CSC programming and calls the MPC callbacks.

## Control Flow

This chunk does not implement control flow. Runtime flow is in the MPC and hardware-sequencer code:

1. The DC hardware sequencer decides whether a stream needs custom output CSC or a default CSC matrix.
2. It calls `mpc->funcs->set_output_csc()` or `mpc->funcs->set_ocsc_default()`.
3. The MPC code selects the inactive A/B coefficient set by reading the current OCSC mode, programs the chosen coefficient registers through `cm_helper_program_color_matrices()`, then updates `MPC_OCSC_MODE`.
4. For output gamma, the MPC code checks the current OGAM RAM state, selects the opposite RAM bank, programs region/start/end/slope registers through `cm_helper_program_xfer_func()`, writes LUT data through `MPCC_OGAM_LUT_DATA`, and switches `MPCC_OGAM_MODE` to the newly programmed RAM bank.

The mask definitions in this chunk are the contract that makes those register writes land on the intended fields.

## State And Persistence

There is no software-owned persistent state in this header. The state represented by the macros lives in display hardware registers:

- OGAM mode, LUT index/data, RAM select, and config status are MMIO-visible hardware state per MPCC instance.
- RAM A and RAM B hold double-buffered output gamma transfer-function programming.
- OCSC coefficient banks A and B hold double-buffered output color matrices per output pipe.

State survives only as long as the display hardware register context remains valid. Driver reinitialization, display mode set, GPU reset, power-gating, or register reprogramming can replace it. The driver can also read selected status fields, such as `MPCC_OGAM_CONFIG_STATUS` and OCSC debug status, to choose a non-active bank for updates.

## Dependencies

This chunk depends on the generated register-address companion headers for the actual MMIO offsets; the macros here only describe field positions and masks. It also depends on the driver-side register helper layer interpreting shift/mask pairs consistently.

Important code-level dependencies visible from consumers:

- `reg_helper.h` macros perform read/modify/write operations using the shifts and masks.
- `dcn20_mpc.h` maps these generated definitions into typed `dcn20_mpc_shift` and `dcn20_mpc_mask` structs.
- `dcn10_cm_common.h` and color-management helpers provide `cm_helper_program_xfer_func()` and `cm_helper_program_color_matrices()`, which pack gamma and matrix data into these registers.
- DC stream and pipe state choose when output CSC and OGAM programming happens.

## Risks

- A wrong shift or mask can silently corrupt adjacent fields in an MMIO register. This is especially risky in paired registers such as region pairs and CSC coefficient pairs, where low and high halves share a 32-bit word.
- The repeated `MPCC_OGAM3` through `MPCC_OGAM7` pattern means copy/generation mistakes may affect only a subset of pipes. Such errors can appear as display-dependent color failures rather than global bring-up failures.
- Incomplete coverage at chunk boundaries matters. This chunk begins in the middle of `MPCC_OGAM2` RAM B definitions and ends in the middle of the `MPC_OUT3` CSC table, so whole-file reconciliation must merge adjacent chunks before asserting full register coverage.
- The DCN2 MPC consumer field list samples `MPCC_OGAM0` masks into common per-instance fields, relying on repeated instance layouts. If any generated per-instance mask diverges unexpectedly, code using common shift/mask fields may not detect that divergence at compile time.
- A/B double buffering depends on accurate mode/status fields. Bad `MPCC_OGAM_CONFIG_STATUS`, `MPCC_OGAM_LUT_RAM_SEL`, or `MPC_OCSC_MODE` masks can cause programming into the active bank or switching to an unprogrammed bank.

## Test Signals

Useful signals for validating this chunk's correctness include:

- Build coverage for DCN2.1 resource and MPC code: missing or renamed macros should fail compilation where `SF()` field lists instantiate shift/mask structs.
- Register write tracing or MMIO dumps while enabling output gamma should show `MPCC_OGAM_LUT_RAM_CONTROL`, `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_DATA`, RAM A/B region registers, and `MPCC_OGAM_MODE` changing for the expected MPCC instance.
- Output CSC updates should alternate between coefficient bank A and B, update only the intended `MPC_OUTn_CSC_Cxx_Cyy_{A,B}` registers, and then switch `MPC_OCSC_MODE`.
- Visual color tests should cover multiple pipes/MPCC instances, not only `MPCC_OGAM0`, because this chunk mainly covers higher instances 3 through 7.
- HDR, gamma ramp, color-management, and output colorspace changes are high-value functional paths because they exercise both OGAM and OCSC programming.
- Debug reads of `MPCC_OGAM_CONFIG_STATUS` and OCSC current mode should match the bank chosen by the driver after a programmed update.

## Chunk Notes For Merge Lane

This is a declarative register-mask chunk, not a standalone functional module. The final per-file research should merge it with neighboring chunks to describe the complete `dcn_2_1_0_sh_mask.h` generated-header contract. This chunk specifically contributes the MPC output gamma and output CSC bitfield portion for DCN 2.1.
