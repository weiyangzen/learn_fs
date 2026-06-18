# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/Makefile

### Purpose
This Makefile fragment contributes legacy AMDGPU DPM manager objects to the broader AMD PowerPlay build. It keeps pre-SMU or older-family DPM code grouped under `legacy-dpm` while appending selected objects into `AMD_POWERPLAY_FILES`.

### Important APIs, Types, And Functions
The key variables are `AMD_LEGACYDPM_PATH`, `LEGACYDPM_MGR-y`, conditional `LEGACYDPM_MGR-$(CONFIG_DRM_AMDGPU_CIK)`, conditional `LEGACYDPM_MGR-$(CONFIG_DRM_AMDGPU_SI)`, `AMD_LEGACYDPM_POWER`, and the final `AMD_POWERPLAY_FILES += $(AMD_LEGACYDPM_POWER)`. Objects always include `legacy_dpm.o`; CIK support adds `kv_dpm.o` and `kv_smc.o`; SI support adds `si_dpm.o` and `si_smc.o`.

### Control Flow
Kbuild evaluates this fragment while building the AMD PM subsystem. It accumulates object names according to kernel configuration symbols, prefixes them with `../pm/legacy-dpm`, and appends them to the shared PowerPlay object list consumed by a parent makefile.

### State, Persistence, And Dependencies
There is no runtime state. Build state depends on Kconfig symbols `CONFIG_DRM_AMDGPU_CIK` and `CONFIG_DRM_AMDGPU_SI`, the parent makefile defining and later consuming `AMD_POWERPLAY_FILES`, and the listed source files existing under the legacy DPM path.

### Integration Points
This file integrates legacy DPM code into the AMDGPU PM build without making it a standalone module. It is part of the build-time boundary between common PM code and older ASIC support for SI, CIK/Kaveri-style families.

### Risks
Path or variable drift in the parent makefile can silently omit legacy DPM objects. Conditional object lists must stay aligned with Kconfig and source availability; otherwise affected ASIC families can lose power management support at build or runtime. Because objects are appended into a shared variable, ordering changes in parent fragments may affect link composition.

### Test Signals
Build tests should cover configurations with both legacy families disabled, only `CONFIG_DRM_AMDGPU_CIK`, only `CONFIG_DRM_AMDGPU_SI`, and both enabled. Link logs or `make V=1` output should show the expected legacy objects. Runtime smoke on SI/CIK hardware should verify DPM initialization and basic clock/fan telemetry.
