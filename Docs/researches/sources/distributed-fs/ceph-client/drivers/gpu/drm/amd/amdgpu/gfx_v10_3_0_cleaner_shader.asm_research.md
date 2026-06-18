# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_3_0_cleaner_shader.asm

## Purpose

This assembly file is the source form of the GFX10.3 cleaner shader. Like the GFX10.1.10 shader, it clears SGPRs, VGPRs, and LDS using a compute shader launched with enough wave32 occupancy to cover CU wave slots and LDS space.

## Important APIs, Types, And Data

- `shader main`, `asic(GFX10)`, `type(CS)`, and `wave_size(32)` define a GFX10-family compute shader.
- The shader is documented as the first 64 dwords / 256 bytes of a 192-dword cleaner shader.
- It uses `S_BARRIER`, relative vector/scalar register moves, `ds_write2_b64`, `exec_lo/hi`, `flat_scratch_lo/hi`, `vcc`, and `ttmp0` through `ttmp15`.
- It is the source reference for `gfx_10_3_0_cleaner_shader_hex[]` in `gfx_v10_0_cleaner_shader.h`.

## Control Flow

1. `S_BARRIER` makes all waves in the workgroup arrive before any wave can exit.
2. The shader unconditionally enters the VGPR cleanup loop for GFX10.3, unlike the conditional GFX10.1.10 path.
3. It clears 64 VGPRs using eight unrolled `v_movreld_b32` operations per loop and `m0` as a relative selector.
4. It checks first-wave state by masking bit 31 from `s0`. Non-first waves branch to SGPR cleanup.
5. The first wave sets all exec lanes active, computes per-thread LDS offsets, and uses 64 iterations of paired 64-bit LDS writes to cover the workgroup LDS allocation.
6. The SGPR loop clears 108 SGPRs using relative scalar moves.
7. It explicitly clears flat scratch low/high, VCC, and trap temporary registers before `s_endpgm`.

## State And Persistence

Runtime state is intentionally overwritten. The shader relies on metadata in `s0` to identify the first wave and on the selected workgroup launch geometry to cover all intended registers and LDS. The only persistent product is the cleaned hardware state after the shader exits.

## Dependencies And Integration Points

- Depends on GFX10.3-compatible encoding and compute launch behavior.
- Integrated by encoding into the static GFX10.3 hex blob consumed by AMDGPU cleaner shader setup.
- Depends on AMDGPU and firmware paths that allocate the cleaner shader, provide the expected workgroup shape, and launch it at queue/context cleanup boundaries.

## Risks

- The top comment includes a manual build instruction about changing shader names for compilation; that suggests a non-automated generation path and raises drift risk.
- GFX10.3 first-wave metadata differs from the GFX10.1.10 file; using the wrong binary would likely skip LDS cleanup or run it on the wrong wave.
- The flat scratch clearing operations are present here but commented out in the GFX10.1.10 source, so shared assumptions between variants are unsafe.

## Test Signals

- Regenerate the embedded GFX10.3 hex and compare it to `gfx_10_3_0_cleaner_shader_hex[]`.
- Runtime tests should validate VGPR/SGPR/LDS scrubbing and first-wave-only LDS writes on GFX10.3 ASICs.
- Queue isolation tests should include repeated graphics/compute submissions with preemption and context teardown.
