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
