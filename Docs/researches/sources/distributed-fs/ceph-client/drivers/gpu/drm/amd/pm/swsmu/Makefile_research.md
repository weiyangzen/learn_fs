# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/Makefile

Purpose: build-system glue for AMDGPU's software SMU power-management layer. It includes per-generation swsmu Makefiles and adds common swsmu manager objects to the broader PowerPlay file list.

Important variables and control flow: `AMD_SWSMU_PATH` points to `../pm/swsmu` relative to the AMDGPU build path. `SWSMU_LIBS` lists generation subdirectories `smu11 smu12 smu13 smu14 smu15`. `AMD_SWSMU` expands those into included Makefile paths under `$(FULL_AMD_PATH)/pm/swsmu/`. `SWSMU_MGR` lists common objects `amdgpu_smu.o` and `smu_cmn.o`. `AMD_SWSMU_POWER` prefixes those objects with the swsmu path, and `AMD_POWERPLAY_FILES += $(AMD_SWSMU_POWER)` appends them to the driver build.

State and persistence: this file has no runtime state. Its persistent effect is make-time composition of object lists and inclusion of generation-specific build fragments. It relies on outer AMDGPU Makefile variables such as `FULL_AMD_PATH` and `AMD_POWERPLAY_FILES`.

Dependencies and integration: integrates the swsmu directory into the kernel DRM AMDGPU build, while generation sub-Makefiles contribute additional objects. It coexists with the older `powerplay/smumgr` files in this research set by selecting build inputs rather than runtime behavior.

Risks and test signals: risks are path mismatches when the AMDGPU tree layout changes, missing generation Makefiles, object list omissions, and accidental ordering changes in `AMD_POWERPLAY_FILES`. Test signals are kernel build coverage for all configured ASIC generations, `make M=drivers/gpu/drm/amd` dependency expansion, and checking that `amdgpu_smu.o`/`smu_cmn.o` are linked when swsmu-supported ASICs are enabled.
