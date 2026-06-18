# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v2_4.h

Purpose: exposes the SDMA v2.4 IP block descriptor to AMDGPU discovery and device initialization code.

Important APIs/types/functions: declares `extern const struct amdgpu_ip_block_version sdma_v2_4_ip_block;`.

Control flow: no direct flow. Discovery code references the descriptor and the AMDGPU IP framework calls the function table stored in the implementation.

State and persistence behavior: no state in the header. The descriptor in `sdma_v2_4.c` persists for the module lifetime and identifies block type, version, and callbacks.

Dependencies and integration points: included by AMDGPU discovery/setup code that adds the SDMA v2.4 IP block for supported ASICs.

Risks and test signals: risks are missing declaration or mismatch with the implementation symbol. Test signals are successful builds and SDMA v2.4 block registration during device discovery.
