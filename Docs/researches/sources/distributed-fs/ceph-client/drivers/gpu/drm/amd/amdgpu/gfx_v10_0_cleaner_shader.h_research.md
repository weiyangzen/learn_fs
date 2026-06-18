# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0_cleaner_shader.h

## Purpose

This header embeds preassembled cleaner shader binaries for GFX10-family hardware. The cleaner shader is used by AMDGPU firmware/command paths to scrub GPU execution state such as SGPRs, VGPRs, and LDS when queue isolation or context cleanup requires residual data removal. It carries two static `u32` arrays, one for GFX10.1.10 behavior and one for GFX10.3.0 behavior.

## Important APIs, Types, And Data

- `static const u32 gfx_10_1_10_cleaner_shader_hex[]` is a 64-dword machine-code blob for the GFX10.1 path. The matching assembly source is `gfx_v10_1_10_cleaner_shader.asm`.
- `static const u32 gfx_10_3_0_cleaner_shader_hex[]` is a 64-dword machine-code blob for the GFX10.3 path. The matching assembly source is `gfx_v10_3_0_cleaner_shader.asm`.
- The arrays are `static const`, so each including translation unit gets an internal-linkage copy. In normal use this header should be included by the relevant GFX10 implementation file that selects the proper blob.
- The arrays depend on the AMDGPU/kernel `u32` typedef being visible before inclusion.

## Control Flow

There is no C control flow. Operational control flow is encoded in the shader instructions:

- Synchronize the launched waves with `S_BARRIER`.
- Clear VGPR banks with repeated `v_movreld_b32` writes.
- Use first-wave detection to conditionally clear the LDS region.
- Clear SGPRs and special registers near shader termination.
- End with `s_endpgm`.

The two blobs differ in small architecture-specific details, including the GFX10.1 path's conditional behavior based on `s0 == 1`, first-wave extraction from a different SGPR, and the flat scratch clearing difference visible in the assembly sources.

## State And Persistence

The header stores immutable machine code in kernel text/rodata. At runtime the selected blob is copied or referenced by AMDGPU cleaner shader setup logic and eventually made visible to the GPU by cleaner-shader buffer initialization. It does not track dynamic state itself.

## Dependencies And Integration Points

- Integrated with AMDGPU GFX10 cleaner shader initialization, which chooses a blob based on IP version and firmware capability.
- Semantically tied to queue isolation and residual state cleanup paths.
- The generated machine code must remain in sync with the assembly source and with the firmware packet that launches `PACKET3_RUN_CLEANER_SHADER` or equivalent setup commands.

## Risks

- Binary blob drift is the central risk: if the array no longer matches the documented assembly, future reviewers cannot reason about the hardware side effects from source alone.
- Cleaner shader correctness is security-sensitive. A wrong loop bound, first-wave test, or register selection can leave SGPR/VGPR/LDS state uncleared or corrupt a live context.
- These arrays are architecture-specific; using the wrong blob for an ASIC revision can mis-handle first-wave metadata or scratch-register semantics.

## Test Signals

- Build coverage catches missing `u32` definitions and syntax issues.
- Runtime coverage should verify cleaner shader allocation, firmware capability gating, and successful execution on affected GFX10 ASICs.
- Security/isolation validation should check that registers and LDS are cleared after queue teardown or context transitions.
- A useful maintenance signal is byte-for-byte regeneration from the `.asm` source and comparison against these arrays.
