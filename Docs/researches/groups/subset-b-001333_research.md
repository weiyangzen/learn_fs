# subset-b-001333

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3_cleaner_shader.asm -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3_cleaner_shader.asm

Purpose: provides the GFX11.0.3/Navi3 cleaner compute shader in assembler form. The shader is intended to scrub transient GPU execution state by clearing LDS, SGPRs, VGPRs, VCC, flat scratch registers, and TTMP registers before program termination. The comments describe this as the first 64 dwords of a 192-dword cleaner shader and document the scheduling assumptions: wave32 compute shader, 32 waves per CU, 16 per SIMD, CU-mode workgroups, and 64 KB LDS per CU.

Important APIs/types/functions: this file does not expose C APIs. Its exported artifact is the `shader main` program for `asic(GFX11)`, `type(CS)`, `wave_size(32)`. Key ISA operations include `S_BARRIER`, `v_movreld_b32`, `s_movreld_b32`, `ds_write2_b64`, `v_mbcnt_lo_u32_b32`, `v_mbcnt_hi_u32_b32`, `v_mul_u32_u24`, `v_add_co_u32`, and `s_endpgm`. The shader relies on scalar register `s0` carrying a first-wave/threadgroup marker when `COMPUTE_PGM_RSRC2.tg_size_en` is set.

Control flow: execution starts with `S_BARRIER` so all waves in the workgroup are launched before any wave can exit. The first loop sets `m0` to `0x58` and repeatedly uses relative VGPR writes through `v_movreld_b32 v0..v7` while subtracting 8, clearing a large VGPR range through an unrolled loop. The shader then tests bit 31 of `s0` via `s2`; only the first wave of the workgroup enters the LDS-clearing path. That path opens the full exec mask, computes each lane's LDS address from the lane id, loops 64 times, and writes zeroed VGPR pairs to LDS with `ds_write2_b64` while advancing by `0x400` bytes. All waves then enter the SGPR-clearing path, where `m0` is set to `0x68` and relative scalar writes clear `s0..s3` repeatedly. The epilogue explicitly clears VCC, flat scratch lo/hi, TTMP0 through TTMP15, and ends the program.

State and persistence behavior: the shader is deliberately destructive to live GPU execution state. It persists no data except the intended side effect of writing zeros across the addressed LDS region. It assumes several registers already hold zero-valued data by the time LDS writes are issued; that coupling is encoded in the machine program represented by the companion header. The `S_BARRIER` is a correctness guard because premature wave exit could leave scalar register slots uncleared.

Dependencies: depends on AMD GFX11 assembler syntax and hardware semantics for wave32 execution, CU-mode workgroup launch, LDS addressing, relative SGPR/VGPR writes through `m0`, special scalar registers such as `vcc`, `flat_scratch_*`, and `ttmp*`, and the SPI-provided `tg_size`/first-wave state in `s0`.

Integration points: this source is the human-readable origin for the hex array in `gfx_v11_0_cleaner_shader.h`. Driver ring code elsewhere emits a PM4 cleaner-shader packet to ask CP firmware/hardware to run the cleaner. For GFX12, `gfx_v12_0.c` contains `gfx_v12_0_ring_emit_cleaner_shader`, which emits `PACKET3_RUN_CLEANER_SHADER`; this assembly shows the kind of firmware-side payload such a packet is meant to execute on supported hardware.

Risks: the shader is highly sensitive to ISA encoding, launch geometry, register allocation, wave size, and microcode interpretation of `s0`. A mismatch can leave portions of VGPR, SGPR, or LDS state uncleared or can corrupt an unexpected address range. The branch labels and loop counts encode hardware resource assumptions; changing CU/WGP LDS sizing, wave width, or VGPR count requires revalidation. Because this is a security/isolation primitive, silent partial clearing is more serious than a visible functional failure.

Test signals: useful validation includes disassembling the generated hex back to the expected ISA, running CP cleaner-shader packet paths on GFX11.0.3 hardware, checking that context isolation tests cannot observe prior LDS/GPR contents, and stressing concurrent wave occupancy so the barrier and first-wave LDS path are exercised. Firmware version gates in the driver should be checked alongside any shader update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3_cleaner_shader.asm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_cleaner_shader.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_cleaner_shader.h

Purpose: embeds the compiled GFX11.0.3 cleaner shader as a static `u32` machine-code array for inclusion by AMDGPU driver code or firmware-loading paths. It is the binary form of the adjacent `gfx_v11_0_3_cleaner_shader.asm` program.

Important APIs/types/functions: defines one file-local symbol, `static const u32 gfx_11_0_3_cleaner_shader_hex[]`. The array contains 64 dwords, matching the assembly comment that this is the first 64 dwords, or 256 bytes, of the cleaner shader payload. It relies on the Linux/AMDGPU `u32` typedef being available from the includer; the header itself has no include guard and no direct include of `<linux/types.h>`.

Control flow: the header has no executable C control flow. Its data sequence encodes the assembly shader's runtime flow: workgroup barrier, VGPR relative-clear loop, first-wave LDS clear loop, SGPR relative-clear loop, special-register clearing, program end, and trailing NOP padding.

State and persistence behavior: the C object is immutable static data in the translation unit that includes it. At runtime it may be copied to firmware-visible memory or referenced as a cleaner shader image; the persistent behavior is therefore the compiled shader image, not mutable driver state. Its machine-code contents are security-sensitive because they determine which GPU state is scrubbed.

Dependencies: depends on exact AMD GFX11 instruction encodings and on the driver-side code including the header in a context where `u32` is defined. It also depends on the assembly file remaining the authoritative source so the hex stays reviewable. The no-guard pattern is acceptable for a private data include but risky if included from more than one C file with the same symbol name.

Integration points: consumed by AMDGPU GFX cleaner-shader support for GFX11-family hardware. It complements ring-level cleaner-shader emission in newer GFX code: the ring emits the command packet, while firmware or a driver path supplies the hardware shader body. The firmware-version gating seen in GFX12 support is the type of integration control needed to ensure the packet and shader image are understood by CP firmware.

Risks: stale or incorrectly regenerated hex can diverge from the assembly comments with no compiler-visible error. Because it is `static`, multiple includes create private copies and can hide duplication. Lack of compile-time length checks means consumers must know the expected dword count. A wrong endian interpretation, copy size, or firmware compatibility assumption can break state clearing.

Test signals: compare the array length and disassembly against `gfx_v11_0_3_cleaner_shader.asm`; verify consumers copy exactly `ARRAY_SIZE(gfx_11_0_3_cleaner_shader_hex) * sizeof(u32)` bytes; boot-test on GFX11.0.3 hardware with cleaner shader enabled; run context-isolation and reset/recovery tests that exercise the packet path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_cleaner_shader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c

Purpose: implements the AMDGPU graphics IP block for GFX 12.0 hardware, including early/software/hardware lifecycle hooks, CP and RLC firmware handling, graphics and compute ring setup, MQD construction, interrupt management, clock/power gating, IP-state dumping, and queue reset behavior. It registers `gfx_v12_0_ip_block` for `AMD_IP_BLOCK_TYPE_GFX` with major/minor/rev `12.0.0`.

Important APIs/types/functions: the public entry is `const struct amdgpu_ip_block_version gfx_v12_0_ip_block`. The main IP callbacks are in `gfx_v12_0_ip_funcs`: `early_init`, `late_init`, `sw_init`, `sw_fini`, `hw_init`, `hw_fini`, `suspend`, `resume`, `is_idle`, `wait_for_idle`, clock/power-gating setters, and IP dump/print hooks. Ring behavior is supplied through `gfx_v12_0_ring_funcs_gfx`, `gfx_v12_0_ring_funcs_compute`, and `gfx_v12_0_ring_funcs_kiq`. Firmware/RLC helpers include `gfx_v12_0_init_microcode`, `gfx_v12_0_rlc_resume`, direct RS64 loaders for PFP/ME/MEC, and RLC backdoor-autoload copy/enable functions. Queue and MQD setup is handled by `gfx_v12_0_gfx_mqd_init`, `gfx_v12_0_compute_mqd_init`, `gfx_v12_0_kgq_init_queue`, `gfx_v12_0_kcq_init_queue`, and `gfx_v12_0_kiq_init_queue`. Debug and topology interfaces include wave register readers, CU/WGP bitmap readers, shadow-info helpers, and IP-dump register lists.

Control flow: `gfx_v12_0_early_init` interprets `amdgpu_user_queue`, decides kernel/user queue enablement, sets function tables, initializes RLCG register-access metadata, and loads firmware images. `gfx_v12_0_sw_init` configures ME/MEC topology for IP versions 12.0.0 and 12.0.1, gates user queues and cleaner shader support by firmware versions, registers IRQ sources, initializes ME/RLC/MEC state, creates gfx/compute/KIQ rings and MQD software storage, optionally allocates an RLC autoload BO, initializes GPU config, allocates IP-dump buffers, and installs sysfs state. `gfx_v12_0_hw_init` performs firmware-load-specific bring-up: RLC backdoor autoload and IMU sequencing, PSP/direct wait paths, golden register programming, GB address config, GFXHUB/GART enablement, SMU firmware dependency handling, constants/VMID setup, RLC resume, TCP harvest placeholder, and finally CP resume. `gfx_v12_0_cp_resume` loads direct CP firmware when needed, sets doorbell ranges, enables compute/gfx CP as required, resumes KIQ/KCQ/KGQ queues, and runs ring self-tests.

State and persistence behavior: driver state is stored under `adev->gfx`, `adev->mqds`, `adev->userq_funcs`, `adev->psp.toc`, and ring objects. Persistent allocations include firmware BOs for PFP/ME/MEC RS64 code/data, MEC HPD/EOP memory, RLC clear-state and jump-table BOs, MQD backing storage and backups, optional RLC autoload VRAM, and IP-dump buffers. Hardware state is programmed via SOC15 register writes, GRBM/SRBM selection, doorbell ranges, VMID apertures, CP/RLC control registers, interrupt-enable registers, and CP ring MQDs. Runtime write pointers live in writeback memory and doorbell registers; MQD backups preserve queue programming across reset/suspend paths.

Dependencies: includes AMDGPU core headers, SOC24 register definitions, GFX12 register masks, firmware header formats, MES/user-queue interfaces, PSP/SMU helpers, IMU v12 functions, and shared GFX helpers. It relies heavily on `WREG32_SOC15`, `RREG32_SOC15`, `soc24_grbm_select`, `amdgpu_ring_*`, `amdgpu_gfx_*`, `amdgpu_mes_*`, `amdgpu_ucode_*`, `amdgpu_bo_*`, and IRQ/fence/scheduler infrastructure. Firmware files declared with `MODULE_FIRMWARE` cover GC 12.0.0 and 12.0.1 PFP, ME, MEC, RLC, kicker, and TOC binaries.

Integration points: plugs into the AMDGPU IP-block framework through `gfx_v12_0_ip_block`. It coordinates with PSP and RLC autoload for firmware loading, SMU for power-management dependencies, GFXHUB/GMC for VM and TLB management, MES for user queues and legacy queue reset/map/unmap, KFD-visible compute VMID/trap setup, NBIO doorbell initialization, DRM scheduler/fence processing, and sysfs/IP-dump diagnostics. It also exposes ring packet emitters used by command submission, VM flush, fences, cleaner shader execution, register access, and preemption.

Risks: most failures are hardware-sequencing or firmware-compatibility sensitive. Firmware version gates control user queue and cleaner shader enablement; incorrect thresholds can expose unsupported packet paths. Timeout loops around cache invalidation, RLC autoload completion, ring tests, and idle waits can fail on slow emulation or broken firmware. GRBM selection and SRBM mutex coverage are critical because writes often target a selected ME/pipe/queue or SE/SH instance. Direct and backdoor firmware loading allocate VRAM/GTT BOs and copy firmware slices based on header offsets; malformed or mismatched firmware can produce bad GPU addresses or incomplete code/data loading. Pipe reset support is deliberately disabled because CP firmware support is not complete, so reset paths often rely on MES and full helper recovery.

Test signals: expected tests include boot/resume/suspend on GC 12.0.0 and 12.0.1, direct/PSP/RLC-backdoor firmware-loading modes, ring self-tests for gfx and compute, IB scheduling tests, VM/TLB flush tests, fence IRQ processing, KIQ/KCQ/KGQ queue map/unmap, MES user queue paths, cleaner-shader packet emission when firmware gates allow it, GPU reset and timed-out fence recovery, SR-IOV VF paths, clock/power-gating toggles, and IP dump generation. Build signals should cover firmware declarations, register macro availability, and structure layout compatibility for `v12_gfx_mqd` and `v12_compute_mqd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.h

Purpose: declares the external interface for the GFX 12.0 AMDGPU IP implementation. It gives other driver units access to the IP-block descriptor and to the GFX index mutex request helper.

Important APIs/types/functions: exports `extern const struct amdgpu_ip_block_version gfx_v12_0_ip_block;`, which is defined in `gfx_v12_0.c` and consumed by AMDGPU IP discovery/registration. It also declares `int gfx_v12_0_request_gfx_index_mutex(struct amdgpu_device *adev, bool req);`. That function is not defined in the paired `gfx_v12_0.c` in this source snapshot, so its implementation must be elsewhere, conditionally compiled, or missing from the reduced tree.

Control flow: no executable control flow exists in the header. Its include guard `__GFX_V12_0_H__` prevents repeated declarations. Consumers include it when they need the GFX12 IP block symbol or the mutex request prototype.

State and persistence behavior: no state is stored here. The declarations refer to persistent driver-global state in `gfx_v12_0_ip_block` and to lock/request state managed by the eventual `gfx_v12_0_request_gfx_index_mutex` implementation.

Dependencies: depends on forward-visible definitions for `struct amdgpu_ip_block_version`, `struct amdgpu_device`, and `bool`, normally provided by AMDGPU and Linux headers before or around inclusion. The copyright banner appears to contain a typo, `dvanced Micro Devices`, which is documentation-only but visible in source provenance.

Integration points: included by `gfx_v12_0.c` itself and likely by SOC/IP registration code that builds the list of supported AMDGPU IP blocks. The mutex helper declaration suggests coordination around GFX index/GRBM selection, which is relevant because `gfx_v12_0.c` frequently selects SE/SH, ME, pipe, queue, and VMID targets before MMIO access.

Risks: if `gfx_v12_0_request_gfx_index_mutex` is genuinely undefined in the build, link failures will occur for any user of the prototype. If the helper exists with a divergent signature, callers can compile incorrectly. The header provides no local includes, so it assumes include ordering supplies dependent type definitions.

Test signals: compile and link tests should confirm that `gfx_v12_0_ip_block` resolves and that every caller of `gfx_v12_0_request_gfx_index_mutex` links. Header self-containment can be checked with targeted include-what-you-use or minimal translation-unit builds, although AMDGPU headers often intentionally rely on umbrella includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.h -->
