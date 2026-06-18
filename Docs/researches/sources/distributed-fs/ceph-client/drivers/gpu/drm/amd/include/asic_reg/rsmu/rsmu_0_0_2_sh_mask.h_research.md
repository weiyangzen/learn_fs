# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_sh_mask.h

Purpose: generated AMDGPU shift/mask header for `RSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU`. It defines how callers pack and unpack the UMC index write-enable bits, target instance selector, and mode-enable bit for the RSMU 0.0.2 NBIF/VG20 register.

Important APIs/types/functions: there are no C functions or types. The exported macros are `RSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU__RSMU_UMC_INDEX_WREN__SHIFT` at `0x0`, `...__RSMU_UMC_INDEX_INSTANCE__SHIFT` at `0x10`, and `...__RSMU_UMC_INDEX_MODE_EN__SHIFT` at `0x1f`. Matching masks are `0x0000FFFFL` for the 16-bit WREN field, `0x000F0000L` for the 4-bit instance field, and `0x80000000L` for the mode-enable bit. The include guard is `_rsmu_0_0_2_SH_MASK_HEADER`.

Control flow: the header has no own execution path. Its masks shape caller control flow for indexed UMC access: callers compose a register value, set the desired write-enable lanes in bits 0-15, choose a UMC instance in bits 16-19, optionally set mode enable at bit 31, and then write the value to the offset from `rsmu_0_0_2_offset.h`.

State and persistence behavior: this file has no state. The fields describe volatile hardware selector/configuration state. A selected instance or enabled mode may affect later UMC indexed operations until changed by another write or cleared by reset, so consumers must program the complete intended value rather than relying on previous register contents.

Dependencies: this header must be used with `rsmu_0_0_2_offset.h` for the actual register address. It relies on AMDGPU generated-register helper conventions (`REG_SET_FIELD`, `REG_GET_FIELD`, mask/shift names) and on the RSMU/NBIF hardware specification that assigns the WREN, instance, and mode-enable bit positions.

Integration points: integrated through AMDGPU code paths that access RSMU UMC indexed registers on VG20 GPU hardware. It is a low-level hardware contract, not an abstraction layer; higher-level memory-controller diagnostics, ras/error paths, or SMU-adjacent support code may use it indirectly through common register helper macros.

Risks: the wide `WREN` field can enable writes to multiple lanes, so a wrong mask or unvalidated input can affect more UMC index bits than intended. A bad instance value can address the wrong memory-controller instance. Mishandling bit 31 can leave index mode enabled or disabled at the wrong time. Since all exports are untyped macros, these errors are behavioral and may only appear on the relevant ASIC.

Test signals: compile coverage should catch macro spelling drift. Runtime validation should include indexed UMC reads/writes for all valid instances, tests that write-enable masks affect only intended bits, RAS or memory-controller diagnostic paths on VG20 hardware, and reset/resume/GPU-recovery tests that verify index-mode state is reinitialized.
