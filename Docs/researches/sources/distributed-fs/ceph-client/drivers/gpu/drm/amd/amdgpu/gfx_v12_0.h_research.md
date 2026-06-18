# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.h

Purpose: declares the external interface for the GFX 12.0 AMDGPU IP implementation. It gives other driver units access to the IP-block descriptor and to the GFX index mutex request helper.

Important APIs/types/functions: exports `extern const struct amdgpu_ip_block_version gfx_v12_0_ip_block;`, which is defined in `gfx_v12_0.c` and consumed by AMDGPU IP discovery/registration. It also declares `int gfx_v12_0_request_gfx_index_mutex(struct amdgpu_device *adev, bool req);`. That function is not defined in the paired `gfx_v12_0.c` in this source snapshot, so its implementation must be elsewhere, conditionally compiled, or missing from the reduced tree.

Control flow: no executable control flow exists in the header. Its include guard `__GFX_V12_0_H__` prevents repeated declarations. Consumers include it when they need the GFX12 IP block symbol or the mutex request prototype.

State and persistence behavior: no state is stored here. The declarations refer to persistent driver-global state in `gfx_v12_0_ip_block` and to lock/request state managed by the eventual `gfx_v12_0_request_gfx_index_mutex` implementation.

Dependencies: depends on forward-visible definitions for `struct amdgpu_ip_block_version`, `struct amdgpu_device`, and `bool`, normally provided by AMDGPU and Linux headers before or around inclusion. The copyright banner appears to contain a typo, `dvanced Micro Devices`, which is documentation-only but visible in source provenance.

Integration points: included by `gfx_v12_0.c` itself and likely by SOC/IP registration code that builds the list of supported AMDGPU IP blocks. The mutex helper declaration suggests coordination around GFX index/GRBM selection, which is relevant because `gfx_v12_0.c` frequently selects SE/SH, ME, pipe, queue, and VMID targets before MMIO access.

Risks: if `gfx_v12_0_request_gfx_index_mutex` is genuinely undefined in the build, link failures will occur for any user of the prototype. If the helper exists with a divergent signature, callers can compile incorrectly. The header provides no local includes, so it assumes include ordering supplies dependent type definitions.

Test signals: compile and link tests should confirm that `gfx_v12_0_ip_block` resolves and that every caller of `gfx_v12_0_request_gfx_index_mutex` links. Header self-containment can be checked with targeted include-what-you-use or minimal translation-unit builds, although AMDGPU headers often intentionally rely on umbrella includes.
