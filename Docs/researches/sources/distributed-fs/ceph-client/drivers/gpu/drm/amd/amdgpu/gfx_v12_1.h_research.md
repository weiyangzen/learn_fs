# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.h

## Purpose
`gfx_v12_1.h` is the public local header for the GFX 12.1 AMDGPU IP implementation. It does not define hardware logic itself; it declares the two cross-file symbols that other AMDGPU initialization code needs in order to register the GFX 12.1 IP block and invoke XCP partition callbacks.

## Important APIs and types
The header exports `extern const struct amdgpu_ip_block_version gfx_v12_1_ip_block;`, implemented in `gfx_v12_1.c` with type `AMD_IP_BLOCK_TYPE_GFX`, version 12.1.0, and the `gfx_v12_1_ip_funcs` lifecycle table.

It also exports `extern struct amdgpu_xcp_ip_funcs gfx_v12_1_xcp_funcs;`, implemented in `gfx_v12_1.c` with `.suspend` and `.resume` hooks for XCP instance masks. Consumers use this to coordinate per-partition GFX suspend/resume without knowing the internal per-XCC sequence.

## Control flow and integration
The include guard `__GFX_V12_1_H__` prevents duplicate declarations. Driver discovery or IP-version selection code can include this header, then reference `gfx_v12_1_ip_block` when building the AMDGPU IP block list for GC 12.1 devices. XCP management code can reference `gfx_v12_1_xcp_funcs` to suspend or resume selected XCC instances during partition transitions.

## State and persistence behavior
The header owns no state. It provides external linkage to stateful implementations in `gfx_v12_1.c`; all persistent device state remains in `struct amdgpu_device`, IP block registration tables, and XCP callback consumers.

## Dependencies
The declarations require that included translation units already know `struct amdgpu_ip_block_version` and `struct amdgpu_xcp_ip_funcs`, normally through AMDGPU core headers. This header intentionally avoids including those definitions itself, matching a lightweight internal-declaration pattern.

## Risks and test signals
The main risk is declaration drift: if `gfx_v12_1.c` changes the exported symbol names, constness, or linkage, consumers including this header will fail to build. Because the header is minimal, compile/link coverage is the primary test signal. Runtime coverage comes indirectly from successful GC 12.1 IP registration and XCP suspend/resume callback invocation.
