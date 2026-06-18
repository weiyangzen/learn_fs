<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.h

Purpose: declares the LSDMA 6.0 function table used by AMDGPU common LSDMA code.

Important APIs: includes `soc15_common.h` and exports `extern const struct amdgpu_lsdma_funcs lsdma_v6_0_funcs`.

Control flow and state: no executable logic and no runtime state. It is a build-time integration point connecting ASIC/IP discovery to the version-specific callbacks in `lsdma_v6_0.c`.

Dependencies and integration points: requires the common SOC15 and AMDGPU LSDMA type declarations to be visible to includers. Consumers assign the exported table to an AMDGPU device or IP-version dispatch path.

Risks and test signals: risk is limited to declaration drift from the implementation or missing includes for `struct amdgpu_lsdma_funcs`. Compile/link coverage and runtime invocation of copy/fill/power-gating callbacks validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v6_0.h -->
