# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/cik_dpm.h

### Purpose
`cik_dpm.h` is a small legacy DPM header for CIK/Kaveri-era power management. It exposes the Kaveri SMU IP block version object to code that registers or references the legacy SMU block.

### Important APIs, Types, And Functions
The header contains the include guard `__CIK_DPM_H__` and one external declaration: `extern const struct amdgpu_ip_block_version kv_smu_ip_block;`.

### Control Flow
There is no direct control flow. Consumers include this header to access the `kv_smu_ip_block` descriptor, which is defined in a corresponding legacy DPM/SMU source file and used by AMDGPU IP block registration.

### State, Persistence, And Dependencies
The header owns no state. The declared `kv_smu_ip_block` is a persistent constant descriptor supplied elsewhere. The declaration depends on the wider AMDGPU IP block type being visible to including translation units.

### Integration Points
This is part of the legacy DPM path built conditionally by the adjacent Makefile when CIK support is enabled. It connects legacy Kaveri SMU support to the AMDGPU IP block framework.

### Risks
The declaration must match the definition exactly; otherwise builds fail or consumers cannot register the correct SMU block. If legacy CIK support is refactored, this tiny header can become stale because it provides only a single symbol and no additional context.

### Test Signals
Compile tests with `CONFIG_DRM_AMDGPU_CIK=y` are the main signal. Runtime initialization on supported Kaveri/CIK hardware should show the SMU IP block is registered and DPM functionality is available through the common PM interfaces.
