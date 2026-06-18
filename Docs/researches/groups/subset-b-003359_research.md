# Research: subset-b-003359

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pwr/pwr_10_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pwr/pwr_10_0_offset.h

Purpose: generated AMDGPU ASIC register-offset header for the PWR 10.0 block. It gives C preprocessor names to the PWR_MISC_CNTL_STATUS register address metadata so driver code can access power-management status without embedding the raw register index.

Important APIs/types/functions: this header has no C functions or types. Its public interface is two macros: `mmPWR_MISC_CNTL_STATUS` with register index `0x0183`, and `mmPWR_MISC_CNTL_STATUS_BASE_IDX` with value `0`. The include guard is `_pwr_10_0_OFFSET_HEADER`. In AMDGPU register code, the `mm*` symbol is normally paired with SOC15-style helpers and the `_BASE_IDX` value supplies the register aperture/base selector expected by generated register-access tables.

Control flow: none is implemented in this file. Compile-time inclusion only makes the register address macro available. Runtime control flow occurs in consumers that read `mmPWR_MISC_CNTL_STATUS`, usually together with the bit definitions from `pwr_10_0_sh_mask.h`, to inspect graphics power-gating and GFXOFF status.

State and persistence behavior: the header itself is stateless and has no persistence. The named register is hardware state owned by the GPU power block. Its value may change as firmware, the runlist controller, or power-management logic enters and exits clock/power-gated graphics states, so callers must treat reads as snapshots rather than cached software state.

Dependencies: depends only on the C preprocessor. It is semantically coupled to `pwr_10_0_sh_mask.h`, which describes the fields inside the register named here, and to the AMDGPU generated register-access conventions (`mm*`, `_BASE_IDX`, and `REG_GET_FIELD`/`SOC15_REG_OFFSET` style consumers). It intentionally carries no Linux kernel includes.

Integration points: this file sits under `drivers/gpu/drm/amd/include/asic_reg/pwr/` and is included by AMDGPU ASIC support code that needs PWR 10.0 status registers. The single offset is meaningful only when matched to the correct ASIC generation and block instance; including it from the wrong generation would silently point status reads at the wrong hardware address.

Risks: incorrect offset or base-index values can break GFXOFF/CGPG status detection, causing the driver to report the wrong power state, make bad power-transition decisions, or misdiagnose firmware behavior. Because the file is generated-style and tiny, manual edits are high risk relative to their apparent simplicity.

Test signals: compile coverage should catch missing macro names. Useful runtime signals include successful AMDGPU initialization on PWR 10.0 hardware, sane reads from `PWR_MISC_CNTL_STATUS`, correct GFXOFF enter/exit reporting, and absence of timeouts or false status transitions in power-management debug and suspend/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pwr/pwr_10_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pwr/pwr_10_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pwr/pwr_10_0_sh_mask.h

Purpose: generated AMDGPU shift/mask header for the PWR 10.0 `PWR_MISC_CNTL_STATUS` register. It documents how to extract the graphics RLC CGPG enable bit and the multi-bit GFXOFF status field from the register addressed by `pwr_10_0_offset.h`.

Important APIs/types/functions: there are no C functions or types. The exported interface is four bitfield macros under the `_pwr_10_0_SH_MASK_HEADER` include guard: `PWR_MISC_CNTL_STATUS__PWR_GFX_RLC_CGPG_EN__SHIFT` at bit `0`, `PWR_MISC_CNTL_STATUS__PWR_GFXOFF_STATUS__SHIFT` at bit `1`, `PWR_MISC_CNTL_STATUS__PWR_GFX_RLC_CGPG_EN_MASK` as `0x00000001L`, and `PWR_MISC_CNTL_STATUS__PWR_GFXOFF_STATUS_MASK` as `0x00000006L`. The second mask spans bits 1 and 2, so consumers must shift after masking to get the field value.

Control flow: no executable control flow exists here. The macros participate in caller-side control flow when `REG_GET_FIELD`, manual mask/shift code, or status polling decides whether graphics RLC clock-gating/power-gating is enabled and what GFXOFF state the hardware reports.

State and persistence behavior: the file itself stores no state. The described fields are volatile hardware status bits. `PWR_GFX_RLC_CGPG_EN` reflects enablement of graphics RLC coarse-grain power gating, while `PWR_GFXOFF_STATUS` reflects a two-bit graphics-off state. Both can change asynchronously as firmware and hardware power management transition the graphics block.

Dependencies: this header depends on the matching register offset from `pwr_10_0_offset.h` for a complete address-plus-field definition. It also depends on AMDGPU's convention for generated shift/mask names, where register helper macros derive field values from `REG__FIELD__SHIFT` and `REG__FIELD_MASK` identifiers. There are no direct Linux includes.

Integration points: consumers in AMDGPU power-management, SMU, or debug/status paths can combine these masks with reads of `mmPWR_MISC_CNTL_STATUS`. The header is integrated through the ASIC register include tree and must match the PWR 10.0 hardware specification; it is not a generic PWR block definition for other generations.

Risks: using the wrong mask width or failing to shift the two-bit `PWR_GFXOFF_STATUS` field can produce false power-state readings. A stale generated value can mislead suspend/resume diagnostics or GFXOFF gating logic. Because the macros have no type safety, mistakes are normally found only by compile-time missing-symbol errors or hardware behavior.

Test signals: compile tests should cover all `REG_GET_FIELD(PWR_MISC_CNTL_STATUS, ...)` uses. Runtime validation should include GFXOFF enabled/disabled transitions, power-gating status dumps, suspend/resume cycles, and checks that status polling does not observe impossible field combinations on PWR 10.0 GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/pwr/pwr_10_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_offset.h

Purpose: generated AMDGPU ASIC register-offset header for the RSMU 0.0.2 block. It names the NBIF-side UMC index register used on VG20 GPU paths so callers can address the RSMU/UMC indexing mechanism symbolically.

Important APIs/types/functions: this file exports preprocessor macros only. `mmRSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU` is the register index `0x0d91`; `mmRSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU_BASE_IDX` is `0`. The include guard is `_rsmu_0_0_2_OFFSET_HEADER`. There are no structs, enums, inline functions, or external symbols.

Control flow: no executable control flow is present. Runtime behavior is in consumers that write or read the named index register, often with field packing from `rsmu_0_0_2_sh_mask.h`, to select UMC index windows, instances, and mode state through the NBIF path.

State and persistence behavior: the header is stateless. The register it names is mutable hardware state: writing the index register likely selects an indexed UMC target and may enable mode behavior until the next write or device reset. The chosen value is not persisted by this header and must not be assumed valid across reset, suspend, GPU recovery, or firmware reinitialization.

Dependencies: the file depends only on generated AMDGPU register naming conventions. It is tightly paired with `rsmu_0_0_2_sh_mask.h`, which defines the writable fields for this register. Callers also depend on the AMDGPU register I/O layer to apply the base index and block addressing correctly.

Integration points: located in `drivers/gpu/drm/amd/include/asic_reg/rsmu/`, this header integrates with code that manages RSMU and UMC/NBIF access on VG20-class GPUs. The `_NBIF_VG20_GPU` suffix is an important hardware-specific qualifier; consumers should not treat this offset as portable across unrelated RSMU revisions.

Risks: an incorrect index address can steer UMC index operations to an unrelated register, risking wrong memory-controller diagnostics or configuration. Because indexed-register access often has a write-selector/read-data pattern, stale or wrong selector writes can also make subsequent reads look valid while addressing the wrong instance.

Test signals: compile coverage catches missing macro names. Runtime signals include successful UMC/NBIF indexed register access on VG20 hardware, correct per-instance selection, no GPU recovery events during memory-controller diagnostics, and stable behavior across reset/resume paths that reprogram the index register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_sh_mask.h

Purpose: generated AMDGPU shift/mask header for `RSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU`. It defines how callers pack and unpack the UMC index write-enable bits, target instance selector, and mode-enable bit for the RSMU 0.0.2 NBIF/VG20 register.

Important APIs/types/functions: there are no C functions or types. The exported macros are `RSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU__RSMU_UMC_INDEX_WREN__SHIFT` at `0x0`, `...__RSMU_UMC_INDEX_INSTANCE__SHIFT` at `0x10`, and `...__RSMU_UMC_INDEX_MODE_EN__SHIFT` at `0x1f`. Matching masks are `0x0000FFFFL` for the 16-bit WREN field, `0x000F0000L` for the 4-bit instance field, and `0x80000000L` for the mode-enable bit. The include guard is `_rsmu_0_0_2_SH_MASK_HEADER`.

Control flow: the header has no own execution path. Its masks shape caller control flow for indexed UMC access: callers compose a register value, set the desired write-enable lanes in bits 0-15, choose a UMC instance in bits 16-19, optionally set mode enable at bit 31, and then write the value to the offset from `rsmu_0_0_2_offset.h`.

State and persistence behavior: this file has no state. The fields describe volatile hardware selector/configuration state. A selected instance or enabled mode may affect later UMC indexed operations until changed by another write or cleared by reset, so consumers must program the complete intended value rather than relying on previous register contents.

Dependencies: this header must be used with `rsmu_0_0_2_offset.h` for the actual register address. It relies on AMDGPU generated-register helper conventions (`REG_SET_FIELD`, `REG_GET_FIELD`, mask/shift names) and on the RSMU/NBIF hardware specification that assigns the WREN, instance, and mode-enable bit positions.

Integration points: integrated through AMDGPU code paths that access RSMU UMC indexed registers on VG20 GPU hardware. It is a low-level hardware contract, not an abstraction layer; higher-level memory-controller diagnostics, ras/error paths, or SMU-adjacent support code may use it indirectly through common register helper macros.

Risks: the wide `WREN` field can enable writes to multiple lanes, so a wrong mask or unvalidated input can affect more UMC index bits than intended. A bad instance value can address the wrong memory-controller instance. Mishandling bit 31 can leave index mode enabled or disabled at the wrong time. Since all exports are untyped macros, these errors are behavioral and may only appear on the relevant ASIC.

Test signals: compile coverage should catch macro spelling drift. Runtime validation should include indexed UMC reads/writes for all valid instances, tests that write-enable masks affect only intended bits, RAS or memory-controller diagnostic paths on VG20 hardware, and reset/resume/GPU-recovery tests that verify index-mode state is reinitialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_sh_mask.h -->
