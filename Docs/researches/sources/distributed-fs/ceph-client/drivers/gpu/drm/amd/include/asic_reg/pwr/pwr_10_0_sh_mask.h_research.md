# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pwr/pwr_10_0_sh_mask.h

Purpose: generated AMDGPU shift/mask header for the PWR 10.0 `PWR_MISC_CNTL_STATUS` register. It documents how to extract the graphics RLC CGPG enable bit and the multi-bit GFXOFF status field from the register addressed by `pwr_10_0_offset.h`.

Important APIs/types/functions: there are no C functions or types. The exported interface is four bitfield macros under the `_pwr_10_0_SH_MASK_HEADER` include guard: `PWR_MISC_CNTL_STATUS__PWR_GFX_RLC_CGPG_EN__SHIFT` at bit `0`, `PWR_MISC_CNTL_STATUS__PWR_GFXOFF_STATUS__SHIFT` at bit `1`, `PWR_MISC_CNTL_STATUS__PWR_GFX_RLC_CGPG_EN_MASK` as `0x00000001L`, and `PWR_MISC_CNTL_STATUS__PWR_GFXOFF_STATUS_MASK` as `0x00000006L`. The second mask spans bits 1 and 2, so consumers must shift after masking to get the field value.

Control flow: no executable control flow exists here. The macros participate in caller-side control flow when `REG_GET_FIELD`, manual mask/shift code, or status polling decides whether graphics RLC clock-gating/power-gating is enabled and what GFXOFF state the hardware reports.

State and persistence behavior: the file itself stores no state. The described fields are volatile hardware status bits. `PWR_GFX_RLC_CGPG_EN` reflects enablement of graphics RLC coarse-grain power gating, while `PWR_GFXOFF_STATUS` reflects a two-bit graphics-off state. Both can change asynchronously as firmware and hardware power management transition the graphics block.

Dependencies: this header depends on the matching register offset from `pwr_10_0_offset.h` for a complete address-plus-field definition. It also depends on AMDGPU's convention for generated shift/mask names, where register helper macros derive field values from `REG__FIELD__SHIFT` and `REG__FIELD_MASK` identifiers. There are no direct Linux includes.

Integration points: consumers in AMDGPU power-management, SMU, or debug/status paths can combine these masks with reads of `mmPWR_MISC_CNTL_STATUS`. The header is integrated through the ASIC register include tree and must match the PWR 10.0 hardware specification; it is not a generic PWR block definition for other generations.

Risks: using the wrong mask width or failing to shift the two-bit `PWR_GFXOFF_STATUS` field can produce false power-state readings. A stale generated value can mislead suspend/resume diagnostics or GFXOFF gating logic. Because the macros have no type safety, mistakes are normally found only by compile-time missing-symbol errors or hardware behavior.

Test signals: compile tests should cover all `REG_GET_FIELD(PWR_MISC_CNTL_STATUS, ...)` uses. Runtime validation should include GFXOFF enabled/disabled transitions, power-gating status dumps, suspend/resume cycles, and checks that status polling does not observe impossible field combinations on PWR 10.0 GPUs.
