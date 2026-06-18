# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0_cleaner_shader.h

## Purpose

This header embeds GFX 9 cleaner shader machine code as static `u32` arrays. The active payload is `gfx_9_4_2_cleaner_shader_hex`, used by the GFX 9.0 implementation for GFX 9.4.2 and related Aldebaran paths that need to clear GPU execution state.

## Important APIs, types, and data

- `gfx_9_0_cleaner_shader_hex[]`: an empty, `__maybe_unused` placeholder for a generic GFX 9.0 cleaner shader.
- `gfx_9_4_2_cleaner_shader_hex[]`: a compiled shader blob containing instructions to clear VGPRs, SGPRs, LDS, `vcc`, flat scratch, and temporary registers. `gfx_v9_0.c` assigns this pointer and size into `adev->gfx.cleaner_shader_ptr` and `adev->gfx.cleaner_shader_size`.

## Control flow and integration

The header itself is data-only. Runtime control flow happens when GFX initialization or reset code chooses the blob, uploads it as a compute program, and dispatches it through the GFX clean-up flow. The blob begins with branch and barrier logic, then clears vector registers via indexed VGPR writes, conditionally clears LDS from the first wave, clears scalar registers through `s_movreld_b32`, and ends the program. A later path halts waves before clearing another SGPR allocation range.

## State and persistence behavior

The shader deliberately overwrites volatile GPU execution state. It does not persist driver-visible state, but it is part of security and RAS hygiene because stale register or LDS contents should not survive across contexts, reset paths, or special clean-up dispatches.

## Dependencies

The blob depends on exact GFX 9.4.2 ISA encoding, wave size assumptions, register allocation assumptions, and dispatch state programmed by `gfx_v9_0.c`. It also depends on consumers using `sizeof(gfx_9_4_2_cleaner_shader_hex)` rather than hard-coded instruction counts.

## Risks

The highest risk is mismatch between the machine-code blob and the dispatch resource registers. If wave size, SGPR/VGPR allocation, LDS size, or halt/barrier sequencing changes, the shader may leave state uncleared or hang. The empty GFX 9.0 placeholder is safe only while no consumer selects it for a required clean-up path.

## Test signals

Signals include successful clean shader dispatch during GPU reset or context cleanup, no timeout on the compute ring, no residual GPR/LDS RAS errors after clean-up, and static build coverage showing that the selected ASIC paths bind to the non-empty GFX 9.4.2 blob.
