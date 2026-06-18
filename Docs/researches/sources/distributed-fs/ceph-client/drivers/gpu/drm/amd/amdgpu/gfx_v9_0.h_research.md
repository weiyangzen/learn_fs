# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.h

## Purpose

This header is the public local interface for the main GFX 9.0 AMDGPU block implementation. It exposes the GFX 9.0 IP block descriptor and the shader-engine/shader-array selection helper that later GFX 9.x support files reuse when programming GRBM indexed registers.

## Important APIs, types, and functions

- `extern const struct amdgpu_ip_block_version gfx_v9_0_ip_block`: exported IP block descriptor consumed by the AMDGPU device bring-up path to register the GFX 9.0 hardware block callbacks.
- `gfx_v9_0_select_se_sh(struct amdgpu_device *adev, u32 se_num, u32 sh_num, u32 instance, int xcc_id)`: selects a shader engine, shader array, and instance for subsequent register access, with broadcast sentinel values used by callers that need all instances selected.

## Control flow and integration

The header has no executable control flow. It allows `gfx_v9_4_2.c` to call `gfx_v9_0_select_se_sh()` for power-brake setup, and allows broader AMDGPU initialization code to refer to the GFX 9.0 IP block. The concrete implementation in `gfx_v9_0.c` writes GRBM index state and is also wired through the GFX function table as `.select_se_sh`.

## State and persistence behavior

No state is stored here. The declared selector mutates hardware register selection state in the implementation, so callers must pair it with appropriate locking and restore broadcast selection when done.

## Dependencies

The declarations depend on AMDGPU core types such as `struct amdgpu_device` and `struct amdgpu_ip_block_version`, plus kernel fixed-width aliases like `u32`. Those are expected to be available through including translation units rather than this minimal header including them directly.

## Risks

The main risk is misuse of `gfx_v9_0_select_se_sh()` without holding the relevant GRBM mutex or without restoring broadcast selection. Because the header does not encode locking requirements, correctness relies on call-site discipline.

## Test signals

Useful validation signals are successful GFX 9.0 device probe, no register programming races during RAS scans or power-management paths, and no build regressions in translation units including this header.
