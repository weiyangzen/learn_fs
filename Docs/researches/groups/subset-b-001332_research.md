# Research: subset-b-001332

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.h

## Purpose

This header is the minimal public declaration point for the AMDGPU GFX10 IP block implementation. It provides the include guard for `__GFX_V10_0_H__` and exposes `gfx_v10_0_ip_block` so the AMDGPU IP discovery and device initialization code can register and invoke the GFX10 graphics block implementation from its corresponding C file.

## Important APIs, Types, And Data

- `extern const struct amdgpu_ip_block_version gfx_v10_0_ip_block;` is the single exported symbol. The type is part of AMDGPU's IP block framework and carries the block type, version, revision, and lifecycle function table.
- The header assumes `struct amdgpu_ip_block_version` is visible to includers through broader AMDGPU headers; it does not include those headers itself.

## Control Flow

The file contains no executable control flow. Its role is compile-time linkage: code that needs to reference the GFX10 IP block includes this header and obtains the external declaration, while the actual initialization, suspend/resume, reset, and ring behavior are defined elsewhere.

## State And Persistence

No state is stored here. Runtime persistence is represented indirectly by the exported IP block object, which is static storage in the implementation file and is used for the lifetime of the driver module.

## Dependencies And Integration Points

This header integrates with AMDGPU's IP block registration path. It depends on the core AMDGPU type definitions already being in scope and is normally consumed by device-family dispatch code, not by hardware programming code directly.

## Risks

- Because the header is intentionally thin, mismatches between this declaration and the implementation definition would surface as compile or link failures.
- The copyright line appears to say `dvanced Micro Devices`; this is likely a typo in source metadata and has no runtime impact.

## Test Signals

- Build/link coverage that resolves `gfx_v10_0_ip_block` is the primary signal.
- Runtime probing of a GFX10 ASIC should demonstrate that the IP block object is found and its function table is invoked by the AMDGPU common IP lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0_cleaner_shader.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0_cleaner_shader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_1_10_cleaner_shader.asm -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_1_10_cleaner_shader.asm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_3_0_cleaner_shader.asm -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_3_0_cleaner_shader.asm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c

## Purpose

This is the main AMDGPU GFX11 IP block implementation. It wires the GFX11 graphics and compute engines into the AMDGPU IP lifecycle, loads and configures firmware, initializes rings and MQDs, manages RLC/IMU/CP state, emits PM4 packets for graphics/compute/KIQ rings, handles interrupts and queue faults, supports reset and diagnostics, and controls clock/power gating for supported GFX11 and GFX11.5 ASIC variants.

The file ultimately exports `gfx_v11_0_ip_block`, a `struct amdgpu_ip_block_version` whose function table drives early init, software init/fini, hardware init/fini, suspend/resume, idle checks, reset handling, clock/power gating, and IP state dumping.

## Important APIs, Types, And Data

- `gfx_v11_0_ip_block` is the public IP block descriptor for AMD IP block type `GFX`, major 11, minor 0.
- `gfx_v11_0_ip_funcs` implements the AMDGPU IP lifecycle: `early_init`, `late_init`, `sw_init`, `sw_fini`, `hw_init`, `hw_fini`, suspend/resume, idle polling, soft reset, reset probing, post-reset MES resume, clock/power gating, and IP dump/print.
- `gfx_v11_0_gfx_funcs` provides GFX helper callbacks for clock counters, SE/SH selection, wave register reads, ME/pipe selection, perf clock gating, shadow info, and HDP flush mask retrieval.
- `gfx_v11_0_ring_funcs_gfx`, `gfx_v11_0_ring_funcs_compute`, and `gfx_v11_0_ring_funcs_kiq` define ring behavior: pointer access, IB/fence emission, VM flushes, GDS switches, HDP flushes, tests, NOP insertion, register waits/writes, reset hooks, cleaner shader emission, and begin/end use hooks.
- `gfx_v11_0_kiq_pm4_funcs` provides KIQ packet helpers for `SET_RESOURCES`, `MAP_QUEUES`, `UNMAP_QUEUES`, `QUERY_STATUS`, and TLB invalidation.
- `gfx_v11_0_rlc_funcs` abstracts RLC enable/safe-mode/control-state operations.
- IRQ source function tables cover EOP, privileged register faults, bad opcode faults, privileged instruction faults, and RLC GC FED errors.
- Register dump lists (`gc_reg_list_11_0`, `gc_cp_reg_list_11`, `gc_gfx_queue_reg_list_11`) drive diagnostic capture and printing.
- Firmware declarations cover PFP, ME, MEC, RLC, RLC kicker, TOC, and multiple GC 11.0.x / 11.5.x firmware names.

## Control Flow

The lifecycle starts in `gfx_v11_0_early_init`. It interprets `amdgpu_user_queue` to decide kernel queue/user queue availability, sets ring/IRQ/GDS/RLC/MQD/IMU function pointers, initializes RLCG register-access scratch controls, and requests firmware through `gfx_v11_0_init_microcode`.

`gfx_v11_0_init_microcode` decodes the GC IP version into a firmware prefix, loads PFP/ME/MEC firmware, conditionally loads RLC firmware outside SR-IOV VF mode, detects RS64 firmware headers, registers microcode pieces with the AMDGPU firmware manager, optionally loads a TOC for RLC backdoor autoload, initializes IMU firmware, and sets `adev->gfx.cp_gfx_shadow` when firmware versions support CP graphics shadowing.

`gfx_v11_0_sw_init` performs software allocation and feature setup. It sets ME/MEC queue topology by IP version, enables MES user queues only when firmware versions are high enough, chooses and initializes the GFX11 cleaner shader when supported, registers IRQ IDs, initializes ME/RLC/MEC structures, creates graphics and compute rings, derives supported reset masks, initializes KIQ unless MES KIQ is used, initializes MQD support, allocates RLC autoload buffers when needed, initializes early GPU config and RAS, allocates IP dump buffers, and creates GFX sysfs entries.

`gfx_v11_0_hw_init` performs hardware bring-up. It initializes the cleaner shader buffer, handles RLC backdoor autoload or direct IMU setup, waits for PSP/RLC autoload completion where required, reads GB address config, configures RS64 program counters for PSP-loaded RS64 firmware, enables the GFXHUB GART and VM fault defaults, programs golden registers, loads SMU firmware for direct/backdoor paths that need it, initializes constants/VMID/GDS state, selects CP firmware architecture outside PSP mode, initializes NBIO doorbells, resumes RLC, resumes CP, and records IMU firmware version from hardware if needed.

`gfx_v11_0_cp_resume` brings command processors online. It disables GUI idle interrupts on discrete GPUs, directly loads CP firmware when using direct firmware loading, programs doorbell ranges, enables CP engines for async gfx ring mode, resumes MES KIQ or legacy KIQ, resumes KCQ compute queues, resumes graphics queues via direct or async path, then ring-tests all enabled graphics and compute rings.

Queue initialization is split by queue type. Graphics queues use `gfx_v11_0_gfx_mqd_init` and `gfx_v11_0_kgq_init_queue`; compute queues use `gfx_v11_0_compute_mqd_init` and `gfx_v11_0_kcq_init_queue`; KIQ uses `gfx_v11_0_kiq_init_queue` and `gfx_v11_0_kiq_init_register`. Reset/suspend paths restore backed-up MQDs and clear ring write pointers rather than rebuilding from scratch.

The hardware finalization path cancels idle work, releases IRQ references, disables user-queue EOP interrupts, disables KGQ/KCQ and MES KIQ where hardware is accessible, skips destructive CP disable on SR-IOV VF, halts CP, disables GUI idle interrupts, disables GFXHUB GART, and clears `adev->gfx.is_poweron`.

## Firmware And RLC Autoload Flow

The file supports direct, PSP, and RLC backdoor autoload firmware models. Direct loading copies firmware blobs into BOs and programs CP instruction/data cache base registers. PSP loading waits for autoload completion and may need RS64 program-counter configuration. RLC backdoor autoload parses the PSP TOC, allocates a combined autoload BO, copies SDMA/GFX/MES/RLC microcode into TOC-defined offsets, writes the enabled firmware mask back into the TOC, programs IMU bootloader address/size registers, starts IMU, disables GPA mode, and waits for RLC autoload completion.

RS64 paths are distinct from legacy CP firmware paths. RS64 loaders allocate separate instruction and data BOs, program IC/DC base registers, invalidate and prime caches, set program counter start registers per pipe, and reset PFP/ME/MEC pipes to pick up the new start addresses. Non-RS64 paths use legacy jump-table writes through CP hypervisor/MEC ucode data registers.

## Ring Packet Behavior

The ring emitters write PM4 packets for core synchronization and submission behavior:

- IB emission uses `PACKET3_INDIRECT_BUFFER`; graphics additionally handles preemption metadata and DE metadata when required.
- Fences use `PACKET3_RELEASE_MEM`; KIQ fences use `PACKET3_WRITE_DATA` and optionally trigger CPC interrupt status.
- VM flush calls the GMC TLB flush helper and synchronizes PFP to ME on graphics rings.
- Pipeline sync uses `PACKET3_WAIT_REG_MEM` against fence writeback memory.
- HDP flush waits on NBIO-provided flush request/done registers.
- GDS switches program per-VMID GDS/GWS/OA registers through packet writes.
- `gfx_v11_0_ring_emit_gfx_shadow` emits `PACKET3_SET_Q_PREEMPTION_MODE` with conditional execution and token tracking to avoid redundant shadow state programming.
- `gfx_v11_0_ring_emit_cleaner_shader` emits `PACKET3_RUN_CLEANER_SHADER`, tying this driver to the embedded GFX11 cleaner shader binary.

## Interrupts, Faults, And RAS

Late init enables privileged register, privileged instruction, bad opcode, and user-queue EOP interrupts. EOP IRQ processing either routes MES/user-queue doorbell offsets to `amdgpu_userq_process_fence_irq` or maps IH ring IDs back to graphics/compute rings and calls `amdgpu_fence_process`.

Privileged register, bad opcode, and privileged instruction IRQ handlers log the fault and call `gfx_v11_0_handle_priv_fault`, which marks the matching DRM scheduler faulty when kernel queues are enabled. FED IRQ handling is delegated through `adev->gfx.ras->rlc_gc_fed_irq`, allowing the GFX11.0.3-specific RAS helper file to specialize poison handling.

## State And Persistence

Persistent runtime state is kept mostly in `struct amdgpu_device` under `adev->gfx`, `adev->mes`, `adev->sdma`, `adev->gds`, `adev->mqds`, and `adev->gfxhub`. This file initializes or updates:

- Firmware pointers, versions, RS64 enablement, and CP graphics shadow capability.
- Cleaner shader pointer, size, GPU address, and enable flag.
- Ring descriptors, doorbell indices, writeback addresses, EOP addresses, and scheduler readiness.
- MQD backup memory for graphics, compute, and KIQ queues, used across reset/suspend.
- RLC clear-state buffers, CP tables, register access controls, and autoload buffers.
- GFX config fields such as RB/CU/TCC masks, GB address config, tile steering, VM apertures, and max hardware contexts.
- RAS handlers, IP dump buffers, user queue function pointers, and supported reset masks.

Hardware state is programmed through SOC15 register macros and selected GRBM/SRBM instances. Several paths explicitly protect indexed register programming with `adev->srbm_mutex`, `adev->grbm_idx_mutex`, or `adev->gfx.reset_sem_mutex`.

## Dependencies And Integration Points

This file is deeply integrated with:

- AMDGPU core device, ring, IB, fence, IRQ, reset, GFX, GDS, MQD, and sysfs helpers.
- Firmware loading and parsing through `amdgpu_ucode_*` and PSP TOC structures.
- RLC, IMU, SMU, GFXHUB, NBIO, MES, user queue, RAS, and SR-IOV subsystems.
- GC 11 register offset/mask headers, packet3 encoding macros, clear-state data, and GFX11 MQD structures.
- KFD/compute expectations around VMIDs, traps, GDS access, and compute queue ownership.

## Risks

- Firmware-version gating is complex and security-relevant for user queues and cleaner shader enablement. Incorrect thresholds can enable unsupported firmware paths.
- Direct, PSP, and RLC backdoor firmware paths have separate cache, BO, and register programming sequences; regressions can affect only one boot mode.
- RS64 and legacy paths duplicate similar setup with different registers, increasing drift risk.
- Register-indexed programming depends on correct mutex coverage and reset of GRBM selection to broadcast/default state.
- Reset support contains disabled pipe reset fallbacks and comments indicating CP firmware support is incomplete; per-queue reset behavior depends heavily on MES.
- Cleaner shader execution is isolation-sensitive; packet support, shader allocation, and firmware capability checks must all agree.
- `gfx_v11_0_ring_emit_gfx_shadow` intentionally maintains CPU/GPU ring state across emissions; incorrect token or conditional execution handling can skip required preemption state setup.
- SR-IOV branches intentionally skip or alter hardware operations; bare-metal and VF behavior can diverge.

## Test Signals

- Compile coverage with all referenced firmware names and register/mask headers present.
- Probe/boot tests on GC 11.0.0, 11.0.1, 11.0.2, 11.0.3, 11.0.4, and 11.5.x variants.
- Firmware load tests for PSP, direct, and RLC backdoor autoload modes, including RS64 and non-RS64 firmware headers.
- Ring tests from `gfx_v11_0_ring_test_ring` and `gfx_v11_0_ring_test_ib` for graphics, compute, and KIQ rings.
- Suspend/resume and GPU reset tests that validate MQD backup/restore, CP resume, MES resume, and ring write pointer reset.
- User queue tests that validate MES-backed EOP interrupts and doorbell ranges.
- Fault injection for privileged register, bad opcode, privileged instruction, RLC FED, and poison-consumption paths.
- Clock/power gating tests that compare `gfx_v11_0_get_clockgating_state` with requested gating flags and confirm safe-mode entry/exit.
- IP dump tests that confirm core, compute queue, and gfx queue register snapshots are captured and printed without leaving GRBM selection in a non-default state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.h

## Purpose

This header exposes the GFX11 IP block descriptor and one cross-file helper for the GFX index mutex. It is the public interface used by nearby AMDGPU code, including the GFX11.0.3 RAS helper, to reference GFX11 lifecycle registration and coordinate access to CP indexed reset/register state.

## Important APIs, Types, And Data

- `extern const struct amdgpu_ip_block_version gfx_v11_0_ip_block;` exports the GFX11 IP block descriptor implemented in `gfx_v11_0.c`.
- `int gfx_v11_0_request_gfx_index_mutex(struct amdgpu_device *adev, bool req);` requests or releases the hardware `CP_GFX_INDEX_MUTEX` using the GFX11 implementation's polling protocol.
- The declaration depends on `struct amdgpu_device` and `bool` being available to includers through kernel/AMDGPU headers.

## Control Flow

The header has no executable flow, but it exposes a function used by reset-related code. The implementation writes `CP_GFX_INDEX_MUTEX`, waits for ownership or release, and returns `0` or `-EINVAL` on timeout.

## State And Persistence

No state is stored in this header. The mutex helper manipulates hardware state in the GFX CP block and is used to serialize reset-sensitive operations.

## Dependencies And Integration Points

- Included by `gfx_v11_0.c` for its own declarations and by `gfx_v11_0_3.c` for GFX11.0.3 RAS integration.
- Ties consumers to AMDGPU core types and GFX11 register semantics without exposing register constants in the header.

## Risks

- External users of `gfx_v11_0_request_gfx_index_mutex` must pair request/release calls correctly or they may block firmware/driver indexed access.
- Because the header does not document locking requirements, callers must know from implementation context that reset paths also use `adev->gfx.reset_sem_mutex`.

## Test Signals

- Build coverage should catch declaration/definition mismatches.
- Reset-path tests should verify that request and release both succeed and that timeout handling does not leave the hardware mutex held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c

## Purpose

This file provides GFX11.0.3-specific RAS hooks for RLC GC FED interrupts and poison consumption. It specializes generic GFX11 RAS behavior by decoding RLC FED status registers to decide whether the error belongs to SDMA or GFX and by triggering GPU reset behavior for a specific poison-consumption interrupt shape.

## Important APIs, Types, And Data

- `gfx_v11_0_3_rlc_gc_fed_irq(...)` handles `RLC_GC_FED` interrupts for GFX11.0.3.
- `gfx_v11_0_3_poison_consumption_handler(...)` handles poison-consumption reset policy for selected FED interrupts.
- `struct amdgpu_gfx_ras gfx_v11_0_3_ras` exports the two function pointers consumed by `gfx_v11_0.c` when `amdgpu_ip_version(... GC_HWIP ...) == IP_VERSION(11, 0, 3)`.
- It reads `regRLC_RLCS_FED_STATUS_0` and `regRLC_RLCS_FED_STATUS_1` using GC 11.0.3 register offsets/masks.

## Control Flow

`gfx_v11_0_3_rlc_gc_fed_irq` reads both FED status registers. If both are zero, it warns and returns success because the interrupt carried no useful status. It checks SDMA FED error bits in status0; SDMA errors route to `adev->sdma.ras_if`, otherwise the interrupt routes to `adev->gfx.ras_if`. If the selected RAS block is missing, it returns `-EINVAL`. On bare metal it fills `ras_dispatch_if.head` and calls `amdgpu_ras_interrupt_dispatch`. On SR-IOV VF it calls the virtualization poison handler if available, otherwise it logs that the VF path has no handler.

`gfx_v11_0_3_poison_consumption_handler` recognizes a workaround condition: an IH entry from GFX with source ID `RLC_GC_FED_INTERRUPT` and both `vmid` and `pasid` equal to zero. It reads FED status0; if SDMA FED bits are set, it ORs `AMDGPU_RAS_GPU_RESET_MODE2_RESET` into the RAS reset flags. If the RAS context exists and the device is not in RMA, it calls `amdgpu_ras_reset_gpu`.

## State And Persistence

The file does not allocate persistent storage except the exported `gfx_v11_0_3_ras` function table. Runtime state changes include reading sticky or event status registers, dispatching RAS interrupt data, possibly setting `ras->gpu_reset_flags`, and initiating a GPU reset.

## Dependencies And Integration Points

- Depends on AMDGPU core, SOC21, SOC15, GC 11.0.3 register headers, GFX IRQ source IDs, RAS common interfaces, SDMA/GFX RAS block initialization, and SR-IOV virtualization hooks.
- Integrated by `gfx_v11_0_gpu_early_init`, which assigns `adev->gfx.ras = &gfx_v11_0_3_ras` only for IP version 11.0.3.
- The generic `gfx_v11_0_rlc_gc_fed_irq` delegates into this file through `adev->gfx.ras`.

## Risks

- If FED status bits are decoded incorrectly, SDMA errors may be reported as GFX errors or vice versa, affecting reset scope and diagnostics.
- Missing `ras_if` state results in `-EINVAL`; callers must tolerate this during partial init or faulty teardown.
- The poison workaround triggers a GPU reset on zero VMID/PASID FED interrupts. If the interrupt condition is too broad, it can cause unnecessary resets; if too narrow, poison may remain unhandled.
- SR-IOV behavior depends on an optional `ras_poison_handler`; absence only logs a warning.

## Test Signals

- Fault injection or hardware RAS tests should generate GFX and SDMA FED bits and verify dispatch target selection.
- SR-IOV VF tests should confirm virtualization poison-handler routing.
- Poison-consumption tests should cover zero and nonzero VMID/PASID entries and verify reset flag changes only for SDMA FED bits.
- Regression tests should confirm GFX11.0.3 assignment of `adev->gfx.ras` and non-11.0.3 paths do not call these handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.h

## Purpose

This header exposes the GFX11.0.3-specific RAS function table to the generic GFX11 implementation. It lets `gfx_v11_0.c` bind `adev->gfx.ras` to the specialized GFX11.0.3 handlers without exposing the implementation details of FED interrupt decoding.

## Important APIs, Types, And Data

- `extern struct amdgpu_gfx_ras gfx_v11_0_3_ras;` is the sole exported symbol.
- The exported table provides `rlc_gc_fed_irq` and `poison_consumption_handler` callbacks in the `.c` file.
- It depends on `struct amdgpu_gfx_ras` being visible from the including AMDGPU headers.

## Control Flow

The header has no runtime control flow. Control is introduced when GFX11 early init assigns the exported table to `adev->gfx.ras` for IP version 11.0.3, after which generic GFX interrupt/RAS paths indirectly call the specialized functions.

## State And Persistence

No state is stored in the header. The external function table has static lifetime in `gfx_v11_0_3.c`.

## Dependencies And Integration Points

- Included by `gfx_v11_0.c`.
- Couples GFX11.0.3 RAS behavior to the generic GFX11 IP block while keeping ASIC-specific code in its own source file.

## Risks

- If the table declaration and definition diverge, build/link failures occur.
- If the generic GFX11 code assigns this table to the wrong IP revision, RAS FED status decoding may use incompatible register definitions.

## Test Signals

- Build coverage verifies the symbol is defined and linkable.
- Runtime GFX11.0.3 initialization should show `adev->gfx.ras` populated with this table and RLC GC FED interrupts delegated through it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.h -->
