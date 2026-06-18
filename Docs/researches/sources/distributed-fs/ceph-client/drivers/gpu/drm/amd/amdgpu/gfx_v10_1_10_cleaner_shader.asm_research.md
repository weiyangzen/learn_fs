# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_1_10_cleaner_shader.asm

## Purpose

This assembly file documents the source for the GFX10.1.10 cleaner shader. It is a compute shader designed to clear LDS, SGPRs, and VGPRs across a CU by launching enough wave32 waves to occupy the target wave slots, with the first wave in each workgroup clearing the shared LDS allocation.

## Important APIs, Types, And Data

- `shader main`, `asic(GFX10.1)`, `type(CS)`, and `wave_size(32)` define the shader target and launch shape.
- The file documents intended occupancy: 32 waves per CU, 16 per SIMD, 64 VGPRs per wave, and 64 KB LDS per workgroup.
- It uses scalar registers, vector registers, `m0`, `exec_lo`, `exec_hi`, `vcc`, and `ttmp0` through `ttmp15`.
- It is the readable source for the `gfx_10_1_10_cleaner_shader_hex[]` blob embedded in `gfx_v10_0_cleaner_shader.h`.

## Control Flow

1. `S_BARRIER` waits until SPI has launched all waves in the workgroup, avoiding early wave termination before all SGPRs are covered.
2. The shader compares `s0` with `1`; if bit/control metadata does not indicate VGPR/LDS cleanup, it branches directly to the SGPR cleanup label.
3. For VGPR cleanup, it sets `s2` to `0x38`, uses `m0` as the relative register selector, and loops over `v0` through `v7` with `v_movreld_b32`, stepping by eight registers until 64 VGPRs are cleared.
4. It detects the first wave using bit 31 from `s1`, then only that wave clears LDS.
5. LDS cleanup forces the exec mask to all lanes, computes per-lane LDS offsets using `v_mbcnt_*`, and loops 64 times issuing paired 64-bit LDS writes at offsets that cover the 64 KB workgroup allocation.
6. SGPR cleanup uses `m0 = 0x68` for 108 SGPRs and repeatedly writes `s0` through `s3` via relative SGPR addressing.
7. It clears `vcc` and temporary trap registers, then terminates with `s_endpgm`.

## State And Persistence

The shader intentionally destroys execution state: VGPRs, SGPRs, LDS, VCC, and trap temporary registers are overwritten with zero-like values. It does not persist state except by scrubbing residual data from GPU hardware resources. The branch on user data / first-wave metadata is a key state input supplied by firmware or the queue launch setup.

## Dependencies And Integration Points

- Depends on GFX10.1 instruction encoding and wave32 behavior.
- Depends on firmware setting `COMPUTE_USER_DATA_0` / `s0` and `COMPUTE_PGM_RSRC2.tg_size_en` first-wave metadata consistently with the comments.
- Integrated by compiling or assembling into the hex array included by the GFX10 cleaner shader header.
- Runtime launch depends on AMDGPU queue isolation / cleaner shader packet support.

## Risks

- The file is not compiled automatically by normal kernel builds unless a separate generation step is run; the embedded hex can diverge from this source.
- The SGPR loop writes `s_movreld_b32 s0, s0` style values, which depends on relative SGPR semantics and current `m0`; incorrect assembler interpretation would break the scrub.
- First-wave detection and LDS coverage are fragile because they rely on launch geometry and metadata rather than self-discovery.
- Comments indicate performance expectations and occupancy assumptions; if hardware scheduling changes, cleanup coverage could change.

## Test Signals

- Assembler regeneration should produce the GFX10.1.10 hex array.
- Hardware validation should observe no stale VGPR/SGPR/LDS data after the cleaner shader runs.
- Firmware integration tests should verify `s0`/`s1` metadata paths, especially the branch that skips VGPR/LDS cleanup.
- Stress tests should run repeated queue teardown/context switches under wave occupancy pressure.
