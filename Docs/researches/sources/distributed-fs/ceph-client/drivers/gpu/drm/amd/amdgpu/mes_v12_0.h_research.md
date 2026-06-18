<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.h

Purpose: declares the MES 12.0 IP block descriptor for AMDGPU IP discovery and binding.

Important APIs: exports `extern const struct amdgpu_ip_block_version mes_v12_0_ip_block`.

Control flow and state: no executable control flow or runtime state. It exposes the implementation’s IP block version object to ASIC setup code.

Dependencies and integration points: requires AMDGPU IP block type declarations from the includer context. Selected GC 12 ASIC tables use this symbol to install MES v12.0 early, software, hardware, suspend, and resume callbacks.

Risks and test signals: risks are limited to symbol/type mismatch. Compile/link coverage and successful MES v12.0 IP lifecycle invocation validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.h -->
