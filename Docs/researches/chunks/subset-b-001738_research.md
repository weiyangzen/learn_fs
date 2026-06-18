# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 39481-42015

## Scope

This chunk covers a generated DCN 3.0.1 register shift/mask header slice. It contains only preprocessor constants and register grouping comments; there are no C functions, structs, enums, or executable statements in this range.

The slice begins inside the `dce_dc_wb0_dispdec_dwbcp_dispdec` writeback color block, continues through `dce_dc_dchvm_hvm_dispdec`, covers the main MPC/MPCC0-3 compositor register fields, then defines most of the MPCC OGAM0, OGAM1, and OGAM2 color pipeline register fields. It ends at the start of the MPCC OGAM3 LUT-control block, so the final MPCC OGAM3 transfer-function and gamut-remap coverage is intentionally left to the next chunk.

## Purpose

The purpose of this header region is to publish the bit layouts for DCN 3.0.1 display writeback, hardware virtualization/memory-control, MPC composition, and per-MPCC output-gamma programming registers. Driver code combines these `__SHIFT` and `_MASK` constants with register offsets from `dcn_3_0_1_offset.h` and AMD display register helpers to program MMIO fields symbolically instead of hard-coding bit positions.

At a subsystem level, this chunk supports:

- DWB color output programming, including gamut remap matrices, output gamma mode selection, OGAM LUT host access, and dual RAM A/B piecewise-linear region tables for red, green, and blue.
- DCHVM control and status fields for host virtual memory style display access, clock gating, memory-selection, RIOMMU control/status, and debug/test windows.
- MPCC0 through MPCC3 composition setup: source selection, OPP routing, blend/alpha/background controls, update-lock selection, memory power control, and status reporting.
- MPCC OGAM0 through OGAM2 full transfer-function programming and double-buffered gamut-remap matrix selection.
- The beginning of MPCC OGAM3 control and LUT host access fields.

This file is a generated hardware contract. Its macro names and numeric masks are consumed through macro concatenation in register tables, so both spelling and bit values are part of the build-time and runtime ABI between generated ASIC headers and display code.

## Important APIs, Types, And Constants

There are no callable APIs or local C types in this chunk. The exported interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field in a register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Comments such as `//DWB_OGAM_CONTROL` and `//MPCC2_MPCC_CONTROL` group fields by hardware register.
- Address-block comments identify generated hardware blocks, including `dce_dc_wb0_dispdec_dwbcp_dispdec`, `dce_dc_dchvm_hvm_dispdec`, `dce_dc_mpc_mpcc<n>_dispdec`, and `dce_dc_mpc_mpcc_ogam<n>_dispdec`.

The main register families in this chunk are:

- `DWB_GAMUT_REMAPA_*` and `DWB_GAMUT_REMAPB_*`: two banks of 3x4-ish color remap coefficients, two signed/fixed-point coefficients per 32-bit register with low/high 16-bit fields.
- `DWB_OGAM_CONTROL`, `DWB_OGAM_LUT_INDEX`, `DWB_OGAM_LUT_DATA`, and `DWB_OGAM_LUT_CONTROL`: mode/current-mode, RAM select/current-select, PWL disable, LUT index/data, per-color write mask, read color select, debug read, host RAM select, and config-mode fields for the DWB output-gamma LUT.
- `DWB_OGAM_RAMA_*` and `DWB_OGAM_RAMB_*`: dual RAM A/B transfer-function programming fields. Each RAM has per-channel start, start-base, start-slope, end-base, end/slope, offset, and region descriptors for regions 0-33. Region-pair registers pack LUT offset and segment-count fields for two adjacent regions.
- `DCHVM_CTRL0`, `DCHVM_CTRL1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, `DCHVM_RIOMMU_STAT0`, `DCHVM_DEBUG_CTRL0`, `DCHVM_TEST_DEBUG_INDEX`, and `DCHVM_TEST_DEBUG_DATA`: control, clock-gating, memory, RIOMMU, status, and debug/test access fields for the display HVM block.
- `MPCC<n>_MPCC_TOP_SEL`, `BOT_SEL`, `OPP_ID`, `CONTROL`, `SM_CONTROL`, `UPDATE_LOCK_SEL`, gain/background registers, `MEM_PWR_CTRL`, and `STATUS`: repeated MPCC compositor field sets for instances 0-3.
- `MPCC_OGAM<n>_MPCC_OGAM_CONTROL`, `LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL`: per-MPCC OGAM mode/current-mode, RAM select/current-select, PWL disable, host LUT selection, color write mask, read color select, and config mode.
- `MPCC_OGAM<n>_MPCC_OGAM_RAMA_*` and `RAMB_*`: per-MPCC dual transfer-function RAM descriptors matching the DWB OGAM shape.
- `MPCC_OGAM<n>_MPCC_GAMUT_REMAP_COEF_FORMAT`, `MPCC_GAMUT_REMAP_MODE`, and `MPC_GAMUT_REMAP_*_{A,B}`: per-MPCC gamut-remap coefficient format, active/current mode, and two banks of remap coefficients.

The repeated blocks are mechanically consistent but not identical at the chunk boundaries: DWB starts mid-gamut-remap block, MPCC OGAM0-2 are complete in this range, and MPCC OGAM3 is partial.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time expansion into display register access code:

1. DCN 3.0.1 resource and DMUB code include `dcn/dcn_3_0_1_offset.h` and `dcn/dcn_3_0_1_sh_mask.h`.
2. Register-list macros such as `SRII(...)` bind offsets for indexed register instances, while field macros such as `SF(register, field, mask_sh)` bind shift and mask values.
3. Runtime helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT` use the precomputed register offsets plus these shift/mask values to access MMIO fields.
4. Higher-level color and composition code, especially DCN3 MPC code, programs OGAM RAMs, selects active LUT RAM A/B, writes LUT data, updates MPCC blend state, and reads status/current-state fields.

The ordering within the header is still semantically useful. Each register section lists shifts first and masks second. Indexed blocks are ordered by hardware instance, and dual RAM A/B programming registers use the same field layout so shared color helper code can reuse one field table.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state in the GPU display engine:

- DWB OGAM and gamut-remap state controls writeback color conversion. Programmed LUT RAMs, remap matrices, and current-select fields persist in hardware until overwritten or reset.
- MPCC composition state controls which top/bottom surfaces feed each compositor, how alpha and blending behave, which OPP receives the output, gain/background values, and update-lock behavior.
- MPCC memory power fields determine whether MPCC and OGAM memories are forced on, disabled, in low-power mode, or reporting a powered state. These fields directly affect whether later LUT writes can succeed.
- MPCC OGAM state includes the active mode, currently selected RAM, host-write target RAM, LUT index/data, per-color write mask, PWL region tables, and two banks of gamut-remap matrices.
- DCHVM state covers enable/control bits, clock-gating policy, memory selection, RIOMMU control/status, and debug-indexed data access.

The persistence boundary is hardware-defined. Values can survive normal software object lifetimes but are generally reset by display engine reset, ASIC reset, power transitions, or explicit reprogramming during modeset, color-management, writeback, or resume paths. Some fields are status/current mirrors rather than direct controls; the generated shift/mask names do not encode read-only versus writable access.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.1 register model remaining synchronized across files:

- `dcn_3_0_1_offset.h` supplies the register addresses paired with these fields.
- `dcn_3_0_1_sh_mask.h` supplies field placement for AMD display register helpers.
- `dcn301_resource.c` and `dmub_dcn301.c` include this header and the offset header for DCN 3.0.1 hardware setup.
- DCN3 MPC code consumes the MPCC and MPCC OGAM fields through `dcn30_mpc.h` register lists and `dcn30_mpc.c` helpers. For example, it reads `MPCC_OGAM_MODE_CURRENT`/`MPCC_OGAM_SELECT_CURRENT`, powers OGAM memory through `MPCC_MEM_PWR_CTRL`, configures `MPCC_OGAM_LUT_CONTROL`, writes `MPCC_OGAM_LUT_INDEX`/`DATA`, and fills RAM A/B transfer-function register descriptors.
- Display color management integrates conceptually through transfer-function programming, gamut remap, LUT RAM selection, and PWL region setup.
- Display writeback integrates through DWB OGAM and DWB gamut-remap fields, while MPC composition integrates through MPCC mux/blend/gain/background/status fields.

The primary integration contract is preprocessor naming. A missing or renamed macro usually fails at compile time when an `SF`/`REG_*` macro expands. A wrong numeric shift or mask can compile cleanly and only surface as incorrect MMIO programming on DCN 3.0.1 hardware.

## Risks And Edge Cases

- The chunk starts and ends mid-generated structure. Whole-file reconciliation must merge adjacent chunks before judging DWB or MPCC OGAM3 completeness.
- The DWB and MPCC OGAM RAM A/B fields are highly repetitive. A generator drift in one channel, RAM bank, or region-pair mask can silently corrupt only a narrow part of the transfer function.
- Several fields pack two 16-bit coefficient or region values into one register. Incorrect masks or shifts can cross-write adjacent coefficients, especially gamut-remap Cxx pairs and region-pair `LUT_OFFSET`/`NUM_SEGMENTS` fields.
- Mode/current-mode and select/current-select fields are separate. Confusing control fields with current-status fields can make color-management code believe a RAM switch happened before hardware reports it.
- Memory power fields in `MPCC<n>_MPCC_MEM_PWR_CTRL` affect LUT accessibility. Wrong `MPCC_OGAM_MEM_PWR_DIS`, `FORCE`, `LOW_PWR_MODE`, or `STATE` masks can cause LUT writes to be dropped, hang waiting for power state, or keep memory unnecessarily powered.
- `DCHVM_*` and `RIOMMU_*` fields are low-level display memory-path controls/status. Misprogramming them can affect address translation, debug visibility, or clock gating rather than producing a local color-only failure.
- The MPCC compositor fields are repeated per instance 0-3. A single instance-specific macro typo can produce failures only for a particular pipe/plane topology.
- Full-width and high-bit masks require unsigned handling. Status fields, coefficient fields, and packed fixed-point values should not be treated as signed integers merely because the macros use `L` suffixes.
- Cross-generation reuse is risky. Nearby DCN 3.x headers have similar names but not guaranteed identical bit positions, field coverage, or instance counts.

## Test Signals

Useful validation signals for this header are build-time, generator-comparison, and hardware-integration oriented:

- Compile DCN 3.0.1 display and DMUB code with the normal AMDGPU build to catch missing field names in `SF`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT` expansions.
- Compare this slice against the matching `dcn_3_0_1_offset.h` and generator source to confirm every register with fields has a matching offset and every indexed MPCC/OGAM instance is consistently generated.
- Exercise modesets with multiple planes to validate MPCC0-3 source selection, OPP routing, alpha/blend modes, update locking, gains, backgrounds, and status reads.
- Run color-management tests that program MPCC OGAM RAM A and RAM B, switch between RAMs, verify `MPCC_OGAM_MODE_CURRENT`/`SELECT_CURRENT`, and compare output against expected transfer functions.
- Test gamut remap matrix programming for both A and B banks, including coefficient-format changes and mode/current-mode transitions.
- Exercise DWB/writeback paths with color transforms enabled to verify DWB OGAM LUT, gamut remap, and HDR multiplier behavior.
- Run suspend/resume, display reset, and power-management tests to catch stale MPCC memory-power or OGAM RAM state and to verify LUT writes still work after reinitialization.
- Include hardware debug or register-dump checks for DCHVM clock/memory/RIOMMU status fields when enabling display memory virtualization paths.

## Open Cross-Chunk Questions

- The final per-file report should merge this with the previous DWB chunk and the following MPCC OGAM3 chunk before summarizing completeness.
- Reconciliation should verify that DCN 3.0.1 actually exposes four MPCC instances and at least four MPCC OGAM blocks in the generated offset header, not just in this shift/mask range.
- If generator provenance is tracked elsewhere in the repository, the final report should identify it, because manual edits to these repetitive field constants would be unusually high risk.
