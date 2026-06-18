<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.h

Purpose: declares the MES 11.0 IP block descriptor for AMDGPU IP discovery.

Important APIs: exports `extern const struct amdgpu_ip_block_version mes_v11_0_ip_block`.

Control flow and state: no executable logic or storage. The implementation’s `amd_ip_funcs` table is reached through this exported descriptor.

Dependencies and integration points: requires the AMDGPU IP block version type to be visible to includers. ASIC setup code uses the symbol to register MES v11.0 lifecycle callbacks.

Risks and test signals: declaration drift would fail link. Runtime validation is MES v11.0 early/sw/hw init being invoked through the IP block table and the scheduler becoming ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.h -->
