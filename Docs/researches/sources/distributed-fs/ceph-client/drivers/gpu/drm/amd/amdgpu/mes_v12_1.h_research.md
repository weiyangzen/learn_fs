# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.h

Purpose: declares the GC 12.1 MES IP block descriptor for registration by the AMDGPU device discovery/IP-block assembly code.

Important APIs and types: the only exported symbol is `extern const struct amdgpu_ip_block_version mes_v12_1_ip_block;`, implemented in `mes_v12_1.c`. The header relies on consumers already seeing the AMDGPU type declarations for `struct amdgpu_ip_block_version`.

Control flow, state, and persistence: this header has no runtime control flow or storage. Its include guard prevents duplicate declarations, and all persistent MES state is maintained by the implementation through `adev->mes`, firmware objects, rings, and hardware registers.

Dependencies and integration points: included by code that needs to select or register the MES v12.1 IP block. Its correctness depends on the implementation exporting a matching const object. Risks are limited to declaration drift or missing type visibility in including files. Test signals are compile/link coverage: the driver must resolve `mes_v12_1_ip_block` and match the expected IP-block interface.
