# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2_cleaner_shader.asm

## Purpose

This assembly source documents the intended GFX 9.4.2 cleaner shader for MI200/Aldebaran. It explains and encodes a compute shader that clears LDS, VGPRs, SGPRs, flat scratch, `vcc`, and temporary registers. The compiled form appears in `gfx_v9_0_cleaner_shader.h` as `gfx_9_4_2_cleaner_shader_hex`.

## Important APIs, types, and instructions

This is not C API surface, but its labels and instruction sequences define the behavior of the embedded shader blob:

- `shader main asic(MI200) type(CS) wave_size(64)`: declares the target shader type.
- Initial branch on `s0 == 1`: selects the VGPR/LDS/lower-SGPR cleaning path versus the remaining-SGPR path.
- `S_BARRIER`: ensures all workgroup waves have launched before lower-SGPR cleaning can finish.
- `s_set_gpr_idx_on`, repeated `v_mov_b32`, and indexed SGPR moves: clear vector and scalar register ranges.
- LDS clearing loop: first wave writes zeroed vector pairs across the 64 KiB LDS region using `ds_write2_b64`.
- `s_sethalt 1`: halts the second kernel path until CP releases all waves, enabling high SGPR coverage when barriers are unsuitable for the larger wave count.

## Control flow

The shader has two main paths. When `s0` marks the VGPR/LDS path, waves synchronize, clear VGPRs in an indexed loop, let the first wave clear LDS, then clear SGPRs and special registers before ending. Otherwise, the shader halts first, waits for CP unhalt after all waves are launched, clears another SGPR allocation range, clears selected special registers, and exits.

## State and persistence behavior

The shader intentionally destroys transient compute-unit state. It writes zeros into VGPRs, SGPRs, LDS, flat scratch, `vcc`, and selected `ttmp` registers. The only intended persistent effect is removal of stale execution data; it should not update driver memory except through normal dispatch machinery in the caller.

## Dependencies and integration points

The comments describe required CP/SPI launch behavior: one kernel launches one workgroup per CU with four wave64 waves per SIMD, and another launches 24 waves per workgroup with resource-reserve registers preventing lower SGPR allocation. The machine-code version is included by `gfx_v9_0_cleaner_shader.h` and selected in `gfx_v9_0.c` for GFX 9.4.2 cleaner shader setup.

## Risks

This file contains hand-sensitive ISA and scheduling assumptions. A typo in assembly, mismatch between this source and the hex header, changed wave allocation policy, or incorrect CP resource-reserve setup can leave registers uncleared or hang halted waves. The comments contain spelling errors but the technical risk is the exact launch contract, not prose.

## Test signals

Useful signals are assembler-to-hex reproducibility, successful dispatch on MI200/Aldebaran without hangs, hardware validation that all expected SGPR/VGPR/LDS ranges are zeroed, and reset/context-cleanup tests showing no stale state leakage.
