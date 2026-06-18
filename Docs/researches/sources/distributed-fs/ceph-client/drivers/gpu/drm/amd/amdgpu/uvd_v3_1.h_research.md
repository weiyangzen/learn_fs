# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v3_1.h

Purpose: Declares the UVD 3.1 IP block version exported by `uvd_v3_1.c`.

Important APIs and types: The only functional declaration is `extern const struct amdgpu_ip_block_version uvd_v3_1_ip_block;`, protected by `__UVD_V3_1_H__`.

Control flow and integration: Other AMDGPU IP discovery or ASIC tables include this header to reference the UVD 3.1 block without depending on implementation internals.

State and persistence: The header owns no state. The declared object is immutable block metadata in the C file.

Dependencies and risks: It assumes `struct amdgpu_ip_block_version` is visible to includers through the broader AMDGPU include chain. Any symbol rename or major/minor mismatch must be fixed in both the C file and ASIC block table users.

Test signals: Build coverage is the main signal: missing or mismatched declarations surface as compile/link errors when the UVD 3.1 block is selected.
