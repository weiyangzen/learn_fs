# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_offset.h

Purpose: generated AMDGPU ASIC register-offset header for the RSMU 0.0.2 block. It names the NBIF-side UMC index register used on VG20 GPU paths so callers can address the RSMU/UMC indexing mechanism symbolically.

Important APIs/types/functions: this file exports preprocessor macros only. `mmRSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU` is the register index `0x0d91`; `mmRSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU_BASE_IDX` is `0`. The include guard is `_rsmu_0_0_2_OFFSET_HEADER`. There are no structs, enums, inline functions, or external symbols.

Control flow: no executable control flow is present. Runtime behavior is in consumers that write or read the named index register, often with field packing from `rsmu_0_0_2_sh_mask.h`, to select UMC index windows, instances, and mode state through the NBIF path.

State and persistence behavior: the header is stateless. The register it names is mutable hardware state: writing the index register likely selects an indexed UMC target and may enable mode behavior until the next write or device reset. The chosen value is not persisted by this header and must not be assumed valid across reset, suspend, GPU recovery, or firmware reinitialization.

Dependencies: the file depends only on generated AMDGPU register naming conventions. It is tightly paired with `rsmu_0_0_2_sh_mask.h`, which defines the writable fields for this register. Callers also depend on the AMDGPU register I/O layer to apply the base index and block addressing correctly.

Integration points: located in `drivers/gpu/drm/amd/include/asic_reg/rsmu/`, this header integrates with code that manages RSMU and UMC/NBIF access on VG20-class GPUs. The `_NBIF_VG20_GPU` suffix is an important hardware-specific qualifier; consumers should not treat this offset as portable across unrelated RSMU revisions.

Risks: an incorrect index address can steer UMC index operations to an unrelated register, risking wrong memory-controller diagnostics or configuration. Because indexed-register access often has a write-selector/read-data pattern, stale or wrong selector writes can also make subsequent reads look valid while addressing the wrong instance.

Test signals: compile coverage catches missing macro names. Runtime signals include successful UMC/NBIF indexed register access on VG20 hardware, correct per-instance selection, no GPU recovery events during memory-controller diagnostics, and stable behavior across reset/resume paths that reprogram the index register.
