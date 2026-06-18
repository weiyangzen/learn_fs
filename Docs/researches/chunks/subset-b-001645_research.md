# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 10130-12631

## Scope

This chunk is a generated AMD DCN 2.0.1 register field header segment. It contains 2,107 preprocessor definitions: 1,053 `__SHIFT` constants and 1,054 `_MASK` constants. The definitions describe bit positions and masks for color-management (`CM3_CM_*`), multi-plane compositor (`MPCC*`), MPC global/output, and MPCC output-gamma (`MPCC_OGAM*`) hardware registers. There are no C functions, types, branches, or storage objects in this chunk; its runtime effect comes from inclusion by display driver register tables and `REG_*` access macros elsewhere in the AMD display stack.

## Purpose

The chunk provides the bitfield contract for programming display-pipeline hardware blocks on DCN 2.0.1 ASICs. These macros let higher-level display code pack and unpack MMIO register values without hard-coded numeric shifts in functional code. The covered register families configure:

- `CM3_CM_BLNDGAM_RAMB_*`, continuing blend-gamma RAM B endpoint and 34-region piecewise-linear metadata for the CM3 color-management block.
- `CM3_CM_HDR_MULT_COEF`, `CM3_CM_DEALPHA`, `CM3_CM_COEF_FORMAT`, shaper LUT, 3D LUT, and CM memory power control/status fields.
- `MPCC0` through `MPCC4` compositor instance selection, blending, gain, background color, memory power, stall, and status fields.
- MPC global controls such as clock/reset, background bypass, stall window, host read, vertical-update lock sets, output muxes, and denormalization clamp controls.
- `MPCC_OGAM0`, `MPCC_OGAM1`, and the first part of `MPCC_OGAM2` output-gamma RAM A/B mode, LUT index/data/control, PWL region layout, slope, start, and endpoint fields.

## Important APIs, Types, And Macros

This header segment is consumed indirectly by generated register-list macros and typed register structures rather than exposing functions itself. The important API surface is the naming convention:

- `REGISTER__FIELD__SHIFT` gives the low-bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask in the 32-bit register value.
- Comments such as `// addressBlock: dce_dc_mpc_mpcc0_dispdec` group definitions by hardware address block.

For MPC/MPCC integration, `drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h` maps these names through `SF(...)`, `SRII(...)`, and field-list macros into `struct dcn20_mpc_shift`, `struct dcn20_mpc_mask`, and `struct dcn20_mpc_registers`. `dcn20_mpc.c` then reads the generated shift/mask tables when programming output gamma:

- `mpc2_ogam_get_reg_field()` copies `MPCC_OGAM_RAMA_*` shifts and masks into an `xfer_func_reg`.
- `mpc2_program_luta()` and `mpc2_program_lutb()` bind the instance-specific RAM A/B register addresses and call `cm_helper_program_xfer_func()`.
- `mpc20_configure_ogam_lut()` updates `MPCC_OGAM_LUT_RAM_CONTROL` fields for write masks and RAM bank selection.
- `mpc20_get_ogam_current()` reads `MPCC_OGAM_CONFIG_STATUS`.
- `mpc20_power_on_ogam_lut()` writes `MPCC_OGAM_MEM_PWR_DIS`.

The MPCC0-4 and MPC output fields also align with the older DCN10 common MPC code for blending, output muxing, and status reads, while DCN20 adds output gamma and denormalization fields.

## Control Flow

The chunk itself has no executable control flow. At build time the preprocessor makes these shift/mask constants available to DCN-specific register table initializers. At runtime, control flow is driven by display-manager operations:

1. DC creates an MPC implementation for the ASIC generation with register addresses, shifts, and masks initialized from generated headers.
2. Plane composition paths use MPCC fields such as `MPCC_TOP_SEL`, `MPCC_BOT_SEL`, `MPCC_OPP_ID`, `MPCC_MODE`, alpha blending mode, global alpha/gain, background bpc, and gain mode through `REG_UPDATE*` helpers.
3. Color pipeline paths choose an MPCC OGAM LUT bank, program PWL region metadata and LUT data, then switch or query active gamma state using the associated control/status fields.
4. Output paths configure MPC output muxes and denorm/clamp fields for OPP routing and color range handling.
5. Power-management paths toggle CM and MPCC/OGAM memory power controls and may poll status fields in newer generations.

Because `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT` depend on these masks and shifts, an incorrect definition silently changes the MMIO bitfield touched by otherwise type-correct code.

## State And Persistence

The macros do not persist state in system memory. They describe persistent hardware state held in display MMIO registers until overwritten, reset, power-gated, or reinitialized during modesets/resume. Relevant hardware state described by this chunk includes:

- Double-buffer-like gamma bank state for RAM A/RAM B in both CM shaper/blend gamma and MPCC OGAM blocks.
- LUT write index/data/control state for shaper, 3D LUT, and OGAM programming.
- Memory power force/disable/status state for shared CM memory, blend-gamma memory, 3D LUT memory, and MPCC OGAM memory.
- MPCC compositor state for plane links, blending parameters, gains, OPP assignment, status, and stall accounting.
- MPC update-lock and output mux/denormalization state that affects when routed output changes become visible.

The display driver must restore these registers after GPU reset, display resume, or full hardware reinitialization. The header does not encode defaults or sequencing constraints.

## Dependencies

This chunk depends on the generated ASIC register ecosystem around `dcn_2_0_1`. It is meaningful only when paired with register-address headers for the same ASIC and the AMD display register helper macros. Key dependencies and consumers include:

- `drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h` for register/field list construction.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.c` for MPCC, MPC output CSC/denorm, and output-gamma programming.
- Common color helpers such as `cm_helper_program_xfer_func()` and `cm_helper_program_color_matrices()`, which consume register/field metadata.
- `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and related MMIO helpers that combine masks and shifts to access fields.

There are no Linux VFS, Ceph, networking, or distributed-filesystem dependencies in this specific source chunk despite its repository path.

## Integration Points

The major integration point is AMDGPU Display Core on DCN 2.0-class hardware. The chunk is source-tree-aligned under `drivers/gpu/drm/amd/include/asic_reg/dcn`, while functional integration occurs under `drivers/gpu/drm/amd/display/dc`.

Important integration surfaces:

- MPCC blending and routing: `MPCC0_MPCC_*` through `MPCC4_MPCC_*` fields support five compositor instances. Per-instance register names share the same field layout, allowing array-indexed register programming.
- MPC global/output: `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_OUT0_MUX`, `MPC_OUT1_MUX`, and denorm clamp registers connect plane-composition output to OPP/output paths.
- Update locks: `ADR_CFG_CUR_VUPDATE_LOCK_SET*`, `ADR_CFG_VUPDATE_LOCK_SET*`, `ADR_VUPDATE_LOCK_SET*`, `CFG_VUPDATE_LOCK_SET*`, and `CUR_VUPDATE_LOCK_SET*` fields coordinate atomic-ish hardware updates around vertical update windows.
- Color pipeline: CM3 shaper, blend gamma, HDR multiplier, 3D LUT, and MPCC OGAM registers integrate with transfer-function and color-management programming.

## Risks

- Field drift risk: generated masks/shifts must match the DCN 2.0.1 register spec exactly. A wrong bit position can program an adjacent hardware field and cause display corruption, blanking, incorrect gamma, broken blending, or power-state issues.
- Cross-generation reuse risk: DCN20 code often uses instance-zero field definitions as canonical layouts for all instances. If a later ASIC or instance has a divergent layout, the shared `SF(MPCC_OGAM0_..., ...)` pattern can become unsafe.
- Bank-selection risk: OGAM and CM shaper/blend gamma use RAM A/B banks. Incorrect `*_LUT_RAM_SEL`, `*_CONFIG_STATUS`, region, start, end, or slope fields can select the wrong bank or produce transient color glitches during updates.
- Power-control polarity risk: fields named `*_PWR_DIS`, `*_PWR_FORCE`, and `*_PWR_STATE` are easy to misuse because enable/disable polarity differs by field. The header gives masks only, not semantics.
- Partial chunk boundary risk: this segment begins in the middle of `CM3_CM_BLNDGAM_RAMB_*` and ends in the middle of `MPCC_OGAM2_MPCC_OGAM_RAMB_*`; the complete per-file report must merge adjacent chunks for full register-family coverage.
- Testing gap risk: normal compilation verifies macro names exist, but cannot prove that bit masks match hardware. Hardware or emulator validation is needed for behavioral confidence.

## Test Signals

Useful validation signals for code depending on this chunk:

- Build coverage for DCN 2.0.1 AMDGPU display code with generated register lists enabled; missing or renamed macros should fail compilation in `dcn20_mpc.h`/related initialization units.
- Modeset and plane-composition tests that exercise multiple MPCC instances, global alpha/gain, background color, OPP routing, and MPC output mux fields.
- Color-management tests that program output gamma PWL LUTs, switch between RAM A and RAM B, and verify observed gamma output or CRCs.
- HDR/shaper/3D LUT tests that write LUT indices/data and validate rendered output against expected transfer functions.
- Suspend/resume, GPU reset, and display hotplug tests that confirm CM, MPCC, MPC, and OGAM state is restored and no stale power-disabled memory state remains.
- Register readback diagnostics for `MPCC_STALL_STATUS`, `MPCC_STATUS`, `CM*_MEM_PWR_STATUS`, and `MPCC_OGAM_CONFIG_STATUS` when debugging display bring-up.
