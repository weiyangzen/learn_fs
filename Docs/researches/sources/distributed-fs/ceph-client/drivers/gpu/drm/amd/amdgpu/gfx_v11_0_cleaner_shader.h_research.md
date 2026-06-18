# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_cleaner_shader.h

Purpose: embeds the compiled GFX11.0.3 cleaner shader as a static `u32` machine-code array for inclusion by AMDGPU driver code or firmware-loading paths. It is the binary form of the adjacent `gfx_v11_0_3_cleaner_shader.asm` program.

Important APIs/types/functions: defines one file-local symbol, `static const u32 gfx_11_0_3_cleaner_shader_hex[]`. The array contains 64 dwords, matching the assembly comment that this is the first 64 dwords, or 256 bytes, of the cleaner shader payload. It relies on the Linux/AMDGPU `u32` typedef being available from the includer; the header itself has no include guard and no direct include of `<linux/types.h>`.

Control flow: the header has no executable C control flow. Its data sequence encodes the assembly shader's runtime flow: workgroup barrier, VGPR relative-clear loop, first-wave LDS clear loop, SGPR relative-clear loop, special-register clearing, program end, and trailing NOP padding.

State and persistence behavior: the C object is immutable static data in the translation unit that includes it. At runtime it may be copied to firmware-visible memory or referenced as a cleaner shader image; the persistent behavior is therefore the compiled shader image, not mutable driver state. Its machine-code contents are security-sensitive because they determine which GPU state is scrubbed.

Dependencies: depends on exact AMD GFX11 instruction encodings and on the driver-side code including the header in a context where `u32` is defined. It also depends on the assembly file remaining the authoritative source so the hex stays reviewable. The no-guard pattern is acceptable for a private data include but risky if included from more than one C file with the same symbol name.

Integration points: consumed by AMDGPU GFX cleaner-shader support for GFX11-family hardware. It complements ring-level cleaner-shader emission in newer GFX code: the ring emits the command packet, while firmware or a driver path supplies the hardware shader body. The firmware-version gating seen in GFX12 support is the type of integration control needed to ensure the packet and shader image are understood by CP firmware.

Risks: stale or incorrectly regenerated hex can diverge from the assembly comments with no compiler-visible error. Because it is `static`, multiple includes create private copies and can hide duplication. Lack of compile-time length checks means consumers must know the expected dword count. A wrong endian interpretation, copy size, or firmware compatibility assumption can break state clearing.

Test signals: compare the array length and disassembly against `gfx_v11_0_3_cleaner_shader.asm`; verify consumers copy exactly `ARRAY_SIZE(gfx_11_0_3_cleaner_shader_hex) * sizeof(u32)` bytes; boot-test on GFX11.0.3 hardware with cleaner shader enabled; run context-isolation and reset/recovery tests that exercise the packet path.
