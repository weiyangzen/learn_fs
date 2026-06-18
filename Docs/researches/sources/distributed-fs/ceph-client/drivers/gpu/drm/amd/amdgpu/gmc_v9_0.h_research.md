# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.h

## Purpose
`gmc_v9_0.h` exposes the public interface for the GFX9/SOC15 GMC implementation.

## Important APIs, Types, And Functions
It declares `extern const struct amd_ip_funcs gmc_v9_0_ip_funcs`, `extern const struct amdgpu_ip_block_version gmc_v9_0_ip_block`, and `void gmc_v9_0_restore_registers(struct amdgpu_device *adev)`. Unlike the v7/v8 headers, it exposes the raw IP function table and a restore helper used outside the main IP block registration path.

## Control Flow And Integration
The header has no local control flow. External users can bind the GMC IP block or call `gmc_v9_0_restore_registers()` to restore saved SOC15 display/HDP-related register state after suspend or reset sequencing.

## State, Dependencies, Risks, And Test Signals
The restore declaration depends on `struct amdgpu_device`; consumers must include suitable AMDGPU core declarations. Risk is declaration drift against `gmc_v9_0.c`. Build coverage plus suspend/resume tests that call the restore helper provide the main signals.
