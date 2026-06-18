# subset-b-001355 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c Research

## Purpose
`sdma_v5_0.c` implements the AMDGPU SDMA 5.0 IP block for Navi-family GC 10.1 hardware. It binds firmware declarations, SDMA register programming, ring packet emitters, VM page-table update helpers, reset/preemption handling, interrupt handling, clock gating, memory copy/fill callbacks, and IP-block lifecycle callbacks into the `sdma_v5_0_ip_block` descriptor consumed by the AMDGPU device bring-up path.

## Important APIs, Types, And Functions
The file exports `sdma_v5_0_ip_block` and otherwise uses static helpers wired into AMDGPU callback tables. `sdma_v5_0_ip_funcs` provides the IP lifecycle: `early_init`, `sw_init`, `hw_init`, suspend/resume, idle polling, clock/power gating, reset, and diagnostic dump/print. `sdma_v5_0_ring_funcs` exposes the SDMA ring ABI: read/write pointers, IB emission, fences, VM flushes, HDP/cache flushes, waits, NOP insertion, preemption, and per-queue reset. `sdma_v5_0_buffer_funcs` provides TTM copy/fill packet generation. `sdma_v5_0_vm_pte_funcs` supports VM PTE copy/write/set operations. `sdma_v5_0_sdma_funcs` links kernel queue stop/start/reset callbacks.

The main register and hardware helpers are `sdma_v5_0_get_reg_offset()`, `sdma_v5_0_init_golden_registers()`, `sdma_v5_0_init_microcode()`, `sdma_v5_0_load_microcode()`, `sdma_v5_0_gfx_resume_instance()`, `sdma_v5_0_start()`, `sdma_v5_0_stop_queue()`, `sdma_v5_0_restore_queue()`, and `sdma_v5_0_ring_preempt_ib()`. The MQD path uses `struct v10_sdma_mqd` in `sdma_v5_0_mqd_init()`.

## Control Flow
Early initialization loads per-instance SDMA firmware metadata, installs ring/buffer/IRQ/MQD callbacks, and registers SDMA as a VM PTE scheduler. Software init registers SDMA0/SDMA1 trap IRQ IDs, initializes each `adev->sdma.instance[i].ring`, allocates an IP dump buffer sized by `sdma_reg_list_5_0`, records supported reset masks, and initializes the sysfs reset mask. Hardware init programs ASIC-specific golden registers, optionally loads direct firmware, unhalts engines, enables context switching/preemption, and starts every GFX SDMA ring.

Ring submission uses writeback or doorbell-backed pointers shifted by two bits between dword and byte units. IB emission aligns indirect packets to an 8-DW boundary, emits a VMID-tagged indirect packet, and includes a CSA address from `amdgpu_sdma_get_csa_mc_addr()`. Fences write one or two 32-bit fence words and optionally emit an SDMA trap. Pipeline sync and register waits are implemented with `POLL_REGMEM`; VM flush delegates to `amdgpu_gmc_emit_flush_gpu_tlb()`.

Reset and recovery are split between whole-IP and queue paths. The top-level `sdma_v5_0_soft_reset()` is a stub, while per-engine reset uses `GRBM_SOFT_RESET`. Per-queue reset suspends KFD, calls `amdgpu_sdma_reset_engine()`, resumes KFD, and wraps recovery with ring reset helper begin/end. Queue stop enters GFX RLC safe mode, disables ring/IB, freezes the SDMA instance, waits for frozen or idle status, halts F32, disables UTC L1, and exits safe mode. Restore unfreezes and reruns `sdma_v5_0_gfx_resume_instance()` with `restore=true`.

## State, Persistence, And Dependencies
Persistent driver state lives under `adev->sdma`: per-instance firmware, ring objects, engine reset mutexes, reset capabilities, function pointers, trap IRQ source, and `ip_dump`. Runtime state also uses writeback memory for ring rptr/wptr and fence tests. Hardware state is persisted in SDMA registers, doorbell routing, microcode RAM, golden-register programming, ring base/rptr/wptr/doorbell registers, and clock-gating bits.

The file depends on Linux firmware/module/delay APIs; AMDGPU core ring, IB, fence, VM, WB, KFD, reset, and sysfs helpers; SOC15 register access macros; GC 10.1 register headers; Navi SDMA packet definitions; NBIO HDP flush and doorbell hooks; SDMA common helpers; and firmware files for navi10, navi12, navi14, and cyan_skillfish2.

## Integration Points
AMDGPU discovers this block through `sdma_v5_0_ip_block`. The memory manager uses `adev->mman.buffer_funcs` and `buffer_funcs_ring` for SDMA copies/fills. VM code uses registered SDMA PTE schedulers. IRQ processing feeds `amdgpu_fence_process()` for SDMA0/SDMA1 ring 0 trap events. KFD is coordinated during per-queue reset. NBIO programs the doorbell aperture and provides HDP flush offsets. RLC safe mode protects queue stop/restore sequences.

## Risks
Several compute/page-queue branches are placeholders: `sdma_v5_0_rlc_stop()`, `sdma_v5_0_rlc_resume()`, illegal instruction IRQ processing, and top-level soft reset are effectively no-ops. The non-SRIOV disable path computes `inst_mask = GENMASK(num_instances - 1, 0)` and then calls `sdma_v5_0_gfx_stop(adev, 1 << inst_mask)`, which appears suspicious because the stop helper expects an instance mask. Queue stop relies on magic status bits `0x3FF` when freeze does not complete. Doorbell and pointer writes rely on byte/dword conversions and 64-bit writeback ordering. Golden-register selection is tightly coupled to IP versions and SR-IOV mode. Big-endian handling is marked with comments in pointer access paths.

## Test Signals
Strong signals include successful firmware request/loading for each supported ASIC, `amdgpu_ring_test_helper()` passing on every SDMA instance, `sdma_v5_0_ring_test_ring()` and `sdma_v5_0_ring_test_ib()` writing `0xDEADBEEF`, fence interrupts advancing SDMA fences, VM PTE updates producing valid GPU page tables, copy/fill operations through TTM, queue reset recovery after a timed-out fence, preemption completing the trailing fence, suspend/resume preserving ring restart, SR-IOV VF ring setup, and clock-gating state reflecting MGCG/LS bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.h Research

## Purpose
`sdma_v5_0.h` is the public header for the AMDGPU SDMA 5.0 IP block implementation. It exposes the block descriptor used by the broader driver to register and instantiate the SDMA 5.0 hardware support code.

## Important APIs, Types, And Functions
The only exported symbol is `extern const struct amdgpu_ip_block_version sdma_v5_0_ip_block;`. The type comes from AMDGPU core headers included before or around this header by consumers.

## Control Flow
The header has no executable control flow. Its include guard prevents repeated declarations. Driver ASIC tables include this header when they need to reference the SDMA 5.0 block descriptor during device IP-block assembly.

## State, Persistence, And Dependencies
There is no mutable state. The header depends on consumers having visibility of `struct amdgpu_ip_block_version`. Persistent behavior is entirely in the C file behind the exported descriptor.

## Integration Points
This declaration is the compile-time link between ASIC selection code and `sdma_v5_0.c`. Any file that adds SDMA 5.0 to an AMDGPU IP block list uses this symbol rather than reaching into static implementation details.

## Risks
The header intentionally exports only the IP block descriptor, so tests or other subsystems cannot directly call internal SDMA 5.0 helpers without changing linkage. A mismatch between this declaration and the definition in `sdma_v5_0.c` would break the build.

## Test Signals
Useful signals are successful kernel compilation, correct linkage of `sdma_v5_0_ip_block`, and ASIC bring-up paths selecting the descriptor for the intended SDMA 5.0 IP versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c Research

## Purpose
`sdma_v5_2.c` implements AMDGPU SDMA 5.2 support for GC 10.3-era hardware. It is structurally similar to SDMA 5.0 but supports more SDMA instances, newer VM invalidation packet handling, larger copy/fill limits, firmware-version-dependent clock-gating workarounds, and explicit GFXOFF control while rings are active.

## Important APIs, Types, And Functions
The exported descriptor is `sdma_v5_2_ip_block`. Static callback tables include `sdma_v5_2_ip_funcs`, `sdma_v5_2_ring_funcs`, `sdma_v5_2_buffer_funcs`, `sdma_v5_2_vm_pte_funcs`, and `sdma_v5_2_sdma_funcs`. Key functions include `sdma_v5_2_get_reg_offset()`, `sdma_v5_2_gfx_resume_instance()`, `sdma_v5_2_start()`, `sdma_v5_2_soft_reset()`, `sdma_v5_2_stop_queue()`, `sdma_v5_2_restore_queue()`, `sdma_v5_2_ring_emit_vm_flush()`, `sdma_v5_2_seq_to_irq_id()`, `sdma_v5_2_seq_to_trap_id()`, and `sdma_v5_2_firmware_mgcg_support()`.

The MQD path uses `struct v10_sdma_mqd`, as in SDMA 5.0. Firmware declarations cover sienna_cichlid, navy_flounder, dimgrey_cavefish, beige_goby, vangogh, yellow_carp, and generic `sdma_5_2_6`/`sdma_5_2_7` images.

## Control Flow
Early init initializes microcode once with shared-firmware semantics, installs all SDMA callback tables, and registers SDMA VM PTE scheduling. SW init registers trap IRQs for each available SDMA instance using sequence-to-client/source mapping, creates one ring per instance, enables doorbells, allocates diagnostic dump storage, records reset support, and initializes SDMA reset-mask sysfs. HW init calls `sdma_v5_2_start()`.

Start halts engines for SR-IOV setup or loads direct firmware on bare metal, waits in emulation mode if needed, soft-resets all SDMA engines, enables engines, enables context switching/preemption, resumes all GFX rings, and returns the first ring-test failure. Ring resume programs queue size, rptr/wptr, writeback addresses, wptr polling, ring base, doorbell registers, NBIO doorbell range, UTC L1, MCBP, UTCL1 response/cache policy, F32 halt, RB enable, and IB enable. The doorbell path for IP 5.2.1 also writes RB wptr registers directly to recover from missed doorbells under power gating.

VM flush differs from SDMA 5.0: it writes VM context page-table base registers via SDMA SRBM writes, then emits an SDMA VM invalidation packet using the ring's invalidation engine. HDP flush delegates to `amdgpu_hdp_flush()` for SDMA instances greater than one and uses NBIO poll packets for lower instances. Reset support includes a top-level loop over all instances and per-queue reset through `amdgpu_sdma_reset_engine()` with KFD suspend/resume.

## State, Persistence, And Dependencies
State is stored in `adev->sdma` rings, firmware slots, function pointers, reset masks, IRQ sources, and diagnostic dump memory. Hardware state includes GC 10.3 SDMA registers, microcode RAM, doorbell ranges, queue rptr/wptr/writeback state, VM hub context registers, and clock/power-gating controls. Runtime ring-use state gates GFXOFF through `sdma_v5_2_ring_begin_use()` and `sdma_v5_2_ring_end_use()`.

Dependencies include AMDGPU ring/IB/fence/WB/KFD/reset/sysfs helpers, VM hub functions, SOC15 register macros, GC 10.3 register headers, SDMA0-3 interrupt source headers, Navi SDMA packet definitions, NBIO doorbell/HDP helpers, and SDMA common helpers.

## Integration Points
The descriptor integrates with AMDGPU IP discovery. IRQ registration supports up to four SDMA trap sources and routes ring 0 traps to `amdgpu_fence_process()` for the matching instance. VM code uses SDMA PTE functions for page-table manipulation. The memory manager uses SDMA 5.2 copy/fill callbacks with 1 GiB max operations. NBIO handles doorbell ranges, and GFXOFF control integrates with power management during active SDMA ring use.

## Risks
The code assumes correct `adev->sdma.num_instances` for instance loops; `sdma_v5_2_wait_for_idle()` reads four instances unconditionally, which is risky if a platform ever exposes fewer than four. Compute/page queues and illegal instruction IRQ handling remain placeholders. Firmware version checks mutate `adev->cg_flags`, so one unsupported instance can clear global SDMA MGCG/LS support. The 5.2.1 doorbell workaround depends on begin/end use keeping GFXOFF disabled while direct wptr writes are used. VM flush packet sizing must match `emit_frame_size`, and register-offset logic has special paths for hypervisor decode ranges and SDMA2/3 base offsets.

## Test Signals
High-value tests include firmware loading across all supported IP versions, ring and IB tests for every SDMA instance, VM flush correctness on page-table updates, SDMA2/3 HDP flush behavior, GFXOFF interaction on 5.2.1/5.2.3 systems, per-queue reset after a timed-out fence, trap IRQ routing for SDMA0-3, copy/fill stress up to boundary sizes, clock-gating enablement with older and newer firmware versions, SR-IOV VF ring startup, and suspend/resume cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.h Research

## Purpose
`sdma_v5_2.h` declares the AMDGPU SDMA 5.2 IP block descriptor for consumers that assemble GPU IP blocks.

## Important APIs, Types, And Functions
The header exports `extern const struct amdgpu_ip_block_version sdma_v5_2_ip_block;`. There are no inline helpers, macros beyond the include guard, or other public entry points.

## Control Flow
There is no runtime control flow. Inclusion gives ASIC selection code access to the SDMA 5.2 descriptor that points at the lifecycle functions implemented in `sdma_v5_2.c`.

## State, Persistence, And Dependencies
The header has no state and persists no configuration. It depends on the AMDGPU core definition of `struct amdgpu_ip_block_version` being visible to the including translation unit.

## Integration Points
This file is the public declaration boundary for SDMA 5.2. It prevents callers from coupling to static implementation helpers while still allowing GPU families with SDMA 5.2 hardware to register the block.

## Risks
The minimal surface is intentional, but it means any need to share SDMA 5.2 helper functionality would require a deliberate API expansion. Linkage failures would occur if the descriptor name or type diverges from the implementation.

## Test Signals
Build/link success and correct ASIC IP table selection are the main signals. Runtime confirmation comes indirectly from SDMA 5.2 lifecycle callbacks being invoked after the descriptor is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c Research

## Purpose
`sdma_v6_0.c` implements AMDGPU SDMA 6.0 support for GC 11/SOC21 hardware. It provides the SDMA IP block descriptor, ring packet emitters, queue register programming, firmware v2 loading, v11 MQD construction, user-queue integration, fence/trap IRQ handling, RAS registration for selected IP versions, reset/restart paths, diagnostic dump support, and copy/fill/VM PTE callbacks.

## Important APIs, Types, And Functions
The file exports both `sdma_v6_0_ip_funcs` and `sdma_v6_0_ip_block`. Static callback tables include `sdma_v6_0_ring_funcs`, `sdma_v6_0_buffer_funcs`, `sdma_v6_0_vm_pte_funcs`, `sdma_v6_0_trap_irq_funcs`, `sdma_v6_0_fence_irq_funcs`, and `sdma_v6_0_illegal_inst_irq_funcs`. Key routines include `sdma_v6_0_get_reg_offset()`, `sdma_v6_0_gfx_resume_instance()`, `sdma_v6_0_load_microcode()`, `sdma_v6_0_soft_reset()`, `sdma_v6_0_check_soft_reset()`, `sdma_v6_0_start()`, `sdma_v6_0_mqd_init()`, `sdma_v6_0_early_init()`, `sdma_v6_0_sw_init()`, `sdma_v6_0_set_userq_trap_interrupts()`, `sdma_v6_0_reset_queue()`, and `sdma_v6_0_process_fence_irq()`.

The implementation uses `struct v11_sdma_mqd`, `struct amdgpu_sdma_ras`, and `struct amdgpu_sdma_csa_info`. It declares firmware for SDMA 6.0.0-6.0.3 and 6.1.0-6.1.4.

## Control Flow
Early init interprets the `amdgpu_user_queue` policy into `no_user_submission` and `disable_uq`, initializes shared SDMA firmware, installs ring/buffer/IRQ/MQD/RAS callbacks, registers VM PTE functions, and exposes CSA sizing. SW init registers SOC21 GFX-client SDMA trap and fence IRQs, initializes one SDMA ring per instance, records reset support, initializes SDMA RAS, allocates diagnostic dump memory, conditionally enables MES user queue functions based on IP version and firmware thresholds, and initializes the sysfs reset mask.

Hardware init starts SDMA, then enables user-queue trap interrupts when user queue functions are active. Start handles SR-IOV by only programming rings after halting, otherwise optionally loads direct firmware, unhalts engines, enables context-empty interrupts for preemption/context switching, resumes rings, and starts RLC queues. Ring resume programs `QUEUE0_*` registers, writeback addresses, ring base, F32 wptr polling, doorbells, hang watchdog timeout, UTCL1 policy, F32 halt/thread reset bits, RB enable, and IB enable.

Firmware loading uses `struct sdma_firmware_header_v2_0` and defaults to broadcast mode, loading control-thread microcode through `BROADCAST_UCODE_*` then context-switch microcode at address `0x8000`. A legacy per-instance path remains but is disabled by a local `use_broadcast = true`. Soft reset stops GFX queues, freezes and halts each instance, asserts queue preempt low, toggles `GRBM_SOFT_RESET`, delays, and restarts the SDMA block. Per-queue reset uses MES legacy queue reset, reruns ring resume with restore semantics, and completes the ring reset helper sequence.

## State, Persistence, And Dependencies
Driver state lives in `adev->sdma` rings, firmware, RAS pointer, CSA info callback, IRQ sources, user queue flags, reset masks, and IP dump memory. The memory manager's global buffer function pointers are overwritten with SDMA 6.0 callbacks. Hardware state includes GC 11 `regSDMA0_QUEUE0_*` queue registers, doorbell routing, microcode RAM, UTCL1 policy, hang watchdog, SOC21 IRQ sources, and VM hub context registers.

Dependencies include Linux firmware/delay/module APIs; AMDGPU core ring, IB, fence, WB, VM, MES, user queue, user fence, RAS, reset, sysfs, and diagnostic helpers; SOC15/SOC21 register access macros; GC 11 register/default headers; HDP and NBIO 4.3 hooks; SDMA 6 packet definitions; `v11_structs.h`; `mes_userqueue.h`; and `amdgpu_userq_fence.h`.

## Integration Points
The block is selected through `sdma_v6_0_ip_block`, while `sdma_v6_0_ip_funcs` is also externally visible for code that needs the function table. Trap IRQs arrive through the SOC21 GFX client and are decoded by ring-id nibble into SDMA instance and queue. Fence IRQs for MES user queues call `amdgpu_userq_process_fence_irq()` using the doorbell offset. User queue support is exposed through `adev->userq_funcs[AMDGPU_HW_IP_DMA] = &userq_mes_funcs` only when firmware is new enough and user queues are not disabled. RAS late init is wired for IP 6.0.3. VM and TTM subsystems use the SDMA PTE and copy/fill callbacks.

## Risks
Clock- and power-gating callbacks are stubs, so gating state reporting is currently empty for this generation. `sdma_v6_0_ring_get_wptr()` only returns a meaningful value for doorbell rings, although rings are initialized with doorbells by default. Firmware loading always takes the broadcast path, so the legacy path is not normally exercised. `sdma_v6_0_wait_for_idle()` reads two SDMA instances directly, which assumes the supported platforms expose at least those instances and may not generalize. Soft reset restarts the IP block internally, so callers must tolerate reset side effects and repeated firmware/ring setup. User queue enablement is gated by firmware thresholds that must stay synchronized with firmware capabilities.

## Test Signals
Important signals include direct firmware load success using v2 headers, ring and IB tests for all instances, user queue enablement only at the expected firmware versions, SDMA trap IRQ fence processing, user fence IRQ processing from doorbell offsets, MES legacy queue reset recovery, soft reset followed by successful `check_soft_reset()`, copy/fill operations up to 1 GiB boundaries, VM flush packet correctness, RAS initialization on IP 6.0.3, suspend/resume cycling, SR-IOV VF setup, and diagnostic dump output for the expanded SDMA 6 register list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.h Research

## Purpose
`sdma_v6_0.h` declares the public symbols exported by the SDMA 6.0 implementation so AMDGPU ASIC and IP assembly code can reference the SDMA 6.0 function table and block descriptor.

## Important APIs, Types, And Functions
The header declares `extern const struct amd_ip_funcs sdma_v6_0_ip_funcs;` and `extern const struct amdgpu_ip_block_version sdma_v6_0_ip_block;`. Unlike the SDMA 5.x headers in this group, it exposes both the raw IP function table and the block-version wrapper.

## Control Flow
The header has no runtime control flow. Its include guard prevents duplicate declarations, and consumers use the symbols during static IP block registration or other compile-time linkage.

## State, Persistence, And Dependencies
There is no mutable state. The declarations depend on AMDGPU core definitions for `struct amd_ip_funcs` and `struct amdgpu_ip_block_version`. Runtime state is owned by `sdma_v6_0.c`.

## Integration Points
The `sdma_v6_0_ip_block` symbol integrates SDMA 6.0 into normal AMDGPU block enumeration. The separately declared `sdma_v6_0_ip_funcs` allows code to reference the function table directly when a full block-version wrapper is not the desired interface.

## Risks
Exporting the function table as well as the block descriptor creates a slightly wider linkage surface than the 5.x headers; external users can couple to the function table identity. Any signature/type mismatch with the implementation fails at build time.

## Test Signals
Compile/link success, correct IP table registration, and runtime invocation of SDMA 6.0 lifecycle methods through the selected descriptor are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.h -->
