# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.h

## Purpose
Declares the SDMA v4.4.2 IP function table, IP block descriptor, and XCP callback table for newer AMDGPU SDMA hardware.

## APIs, Types, And Functions
The header exports `extern const struct amd_ip_funcs sdma_v4_4_2_ip_funcs;`, `extern const struct amdgpu_ip_block_version sdma_v4_4_2_ip_block;`, and `extern struct amdgpu_xcp_ip_funcs sdma_v4_4_2_xcp_funcs;`. It defines no local helpers or structs.

## Control Flow
No executable flow is present. Consumers use these declarations to register the normal SDMA IP lifecycle and to attach XCP partition suspend/resume callbacks implemented in `sdma_v4_4_2.c`.

## State And Persistence
The declarations are stateless. Persistent runtime state belongs to `adev->sdma` instances, ring structures, XCP partition state, reset-mask state, and RAS structures in the implementation.

## Dependencies And Integration
The includer must have declarations for `struct amd_ip_funcs`, `struct amdgpu_ip_block_version`, and `struct amdgpu_xcp_ip_funcs`. The header is the public interface between IP discovery/XCP code and the v4.4.2 implementation.

## Risks And Test Signals
Risk is limited to stale extern declarations or missing symbol definitions. Build/link success, normal SDMA v4.4.2 IP registration, and XCP suspend/resume callback binding validate this file.
