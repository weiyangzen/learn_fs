# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3_cleaner_shader.asm

Purpose: documents and sources the MI300/GC 9.4.3 cleaner shader used to scrub LDS, VGPRs, SGPRs, flat scratch, VCC, and TTMP registers before or between isolated compute workloads. The compiled form is embedded in `gfx_v9_4_3_cleaner_shader.h` and selected by `gfx_v9_4_3.c` when supported by MEC firmware.

Important APIs/types/functions: this is GPU assembly, not C API. It declares `shader main`, `asic(MI300)`, `type(CS)`, and `wave_size(64)`. The comments describe two launch modes: one wave-group mode clearing VGPRs, LDS, and lower SGPRs, and another mode clearing remaining SGPRs after CP releases halted waves.

Control flow: the shader checks `s0` for a mode bit. In the VGPR/LDS path it starts with `S_BARRIER`, uses indexed VGPR writes to clear 128 VGPRs per wave, lets the first wave clear the 64 KB LDS block with `ds_write2_b64`, then loops through relative SGPR writes to clear allocated SGPRs and scalar special registers before `s_endpgm`. In the SGPR-only path it branches to `label_0023`, executes `s_sethalt 1` so CP can wait for all waves to launch, then clears SGPRs and exits. The loop counters are hard-coded for the expected physical register allocation pattern.

State and persistence behavior: the shader mutates only wave-local register files and LDS of the launched workgroup. It has no persistent software state. Its effect is deliberately destructive to shader-visible state, so it must run only when the queue isolation protocol intends to scrub stale execution context.

Dependencies and integration points: depends on MI300 instruction encoding, wave64 execution, CP setup of `COMPUTE_USER_DATA_3`/SGPR mode state, SPI resource reservation for the second kernel, and the AMDGPU cleaner-shader upload/dispatch path. The C ring layer emits `PACKET3_RUN_CLEANER_SHADER` after programming the shader address through KIQ `SET_RESOURCES`.

Risks and test signals: the shader is tightly coupled to CU/SIMD register allocation assumptions, 64 KB LDS, wave64, and MEC/CP launch sequencing. The comments contain minor typos but also critical sequencing notes: omitting the initial barrier in the first path or the halt/unhalt protocol in the second path can leave physical SGPRs uncleared. Test signals require hardware/firmware validation: successful compilation to the embedded hex, no shader hang, expected scrub coverage for LDS/VGPR/SGPR classes, and no launch on unsupported ASIC or firmware combinations.
