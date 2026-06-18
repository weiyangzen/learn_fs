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
