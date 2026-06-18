# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_0.c

## Purpose

`sdma_v7_0.c` is the AMDGPU System DMA IP implementation for SDMA 7.0 devices using GC 12.0 register definitions and `sdma_v6_0_0_pkt_open.h` packet encoders. It binds the SDMA hardware block into the AMDGPU IP lifecycle, exposes SDMA rings to the common scheduler, emits SDMA packets for indirect buffers, fences, VM page-table updates, buffer copies/fills, and handles firmware loading, reset, interrupt dispatch, diagnostics, and optional user queue support.

The file declares firmware dependencies for `amdgpu/sdma_7_0_0.bin` and `amdgpu/sdma_7_0_1.bin`. It assumes two SDMA register spaces via `SDMA1_REG_OFFSET`, with a special hyper-decode register range that uses a different base and stride.

## Important APIs, types, and functions

- `sdma_v7_0_ip_funcs` and `sdma_v7_0_ip_block` are the exported AMDGPU IP descriptors consumed by ASIC discovery/initialization code.
- `sdma_v7_0_ring_funcs` is the SDMA scheduler/ring contract: pointer access, doorbell writes, IB emission, fence emission, VM flush, tests, NOP padding, register wait/write packets, conditional execution, preemption, and per-queue reset.
- `sdma_v7_0_buffer_funcs` registers SDMA as the TTM/memory-manager copy/fill backend through `adev->mman.buffer_funcs` and `adev->mman.buffer_funcs_ring`.
- `sdma_v7_0_vm_pte_funcs` registers SDMA page-table update emitters through `amdgpu_sdma_set_vm_pte_scheds()`.
- `sdma_v7_0_mqd_init()` fills a `struct v12_sdma_mqd` for DMA MES/user-queue style queues, including ring base, read/write pointer writeback addresses, doorbell, CSA, and fence-address debug registers.
- `sdma_v7_0_get_reg_offset()` translates an SDMA instance plus internal register offset into a GC MMIO offset, including the SDMA1 regular-register offset and the special hyper-decode offset range.
- Ring pointer helpers adapt AMDGPU dword pointers to SDMA byte pointers, writing either a 64-bit doorbell or RB_WPTR registers.
- Packet emitters cover IBs, fences, memory sync, HDP flush, pipeline sync, VM flush, register waits/writes, PTE copy/write/set, buffer copy, and constant fill.
- Runtime health and reset hooks include direct ring tests, IB tests, full soft reset, reset-needed detection, and per-queue reset through MES legacy reset.

## Control flow

Initialization starts in `sdma_v7_0_early_init()`. It derives user-queue policy from `amdgpu_user_queue`, initializes firmware metadata, installs ring/buffer/IRQ/MQD function tables, registers VM PTE emitters, and publishes CSA sizing.

`sdma_v7_0_sw_init()` registers trap and user-fence IRQ source IDs, then initializes each SDMA ring with doorbells, `me = i`, a GFXHUB VM hub, an engine-specific doorbell index, a name like `sdma0`, and `amdgpu_ring_init()`. It sets reset capabilities, creates sysfs reset-mask state, allocates the SDMA IP dump buffer, and conditionally enables DMA user queue MES functions for supported firmware/IP versions.

Hardware initialization calls `sdma_v7_0_start()`. SR-IOV VFs disable context switching and engines, program ring-buffer registers, and return after GFX resume. Bare metal with direct firmware loading loads microcode into per-instance VRAM BOs, points IC registers at those BOs, primes icache, and waits for `ICACHE_PRIMED` and `UCODE_INIT_DONE`. It then unhalts engines, enables context switching, resumes each GFX ring, and leaves RLC queue resume as a no-op.

Per-instance resume programs ring size/base, read/write pointers, writeback addresses, shadow write-pointer polling address, doorbell enable/offset, watchdog count, UTCL1 response mode/retry delay, default cache policies, MCU halt/reset bits, RB enable, IB enable, and `ring->sched.ready`. It then runs `amdgpu_ring_test_helper()` and clears readiness on failure.

Reset has full-IP and per-queue lanes. The full soft reset stops rings, asserts HALT/RESET, clears queue preemption, toggles `GRBM_SOFT_RESET`, delays between phases, and restarts SDMA. Per-queue reset wraps `amdgpu_mes_reset_legacy_queue()` with ring reset begin/end helpers and restores the ring instance with saved pointers.

## State and persistence behavior

Persistent runtime state is held in `adev->sdma`, per-instance rings, firmware BO pointers/GPU addresses, IRQ sources, sysfs reset-mask state, and `adev->sdma.ip_dump`. The file does not persist to disk; it persists hardware/MMIO state, writeback memory, doorbells, and kernel objects across lifecycle phases.

Ring pointers are stored in writeback/shadow memory and represented as dword offsets in AMDGPU while SDMA hardware consumes byte offsets. Cold resume clears `ring->wptr`; reset restore writes both RPTR and WPTR from the saved `ring->wptr`. Direct firmware loading allocates one VRAM BO per SDMA instance and frees those BOs on error/finalization. Diagnostic dumps cache register snapshots in `adev->sdma.ip_dump`.

## Dependencies and integration points

The file integrates with AMDGPU core subsystems: rings, IBs, IRQs, fences, MES reset, SDMA helpers, GMC TLB flush, writeback allocation, BO allocation, firmware loading, sysfs reset masks, and memory manager buffer functions. It depends on GC 12.0 register headers, SDMA packet macros, NBIO HDP flush callbacks, SOC15 MMIO helpers, MES user queue functions, and v12 MQD structures.

Scheduler integration is through `amdgpu_ring_init()` and `amdgpu_ring_funcs`; VM integration is through `amdgpu_sdma_set_vm_pte_scheds()` and `amdgpu_gmc_emit_flush_gpu_tlb()`; memory-management integration is through `adev->mman.buffer_funcs`; interrupt integration uses `amdgpu_irq_add_id()`, `amdgpu_irq_get/put()`, and `amdgpu_fence_process()`. User-fence IRQ handling calls `amdgpu_userq_process_fence_irq()` when MES and a doorbell offset are present.

## Risks and edge cases

- Register offset translation is hardware-specific; wrong hyper-decode or SDMA1 offsets would program the wrong MMIO space.
- `sdma_v7_0_wait_for_idle()` reads only instances 0 and 1, unlike other loops over `adev->sdma.num_instances`.
- RLC stop/resume, context-switch enable, illegal-instruction handling, and clock/power gating hooks are placeholders.
- Direct firmware loading can partially allocate per-instance firmware BOs before a later instance fails, so cleanup paths matter.
- Pointer shadow memory still has comments about unresolved big-endian behavior.
- Fence emission uses `BUG_ON(addr & 0x3)`, making bad fence alignment fatal.
- Trap IRQ decoding assumes compact two-instance ring_id behavior.
- User queue behavior depends on module settings, firmware revision, MES enablement, and IP version.
- SDMA7 copy/fill compression and DCC fields are packet-format sensitive and high risk for memory-move corruption if mismatched.

## Test signals

Primary signals are `amdgpu_ring_test_helper()` during resume, direct ring write tests, scheduled IB write tests with fence waits, `check_soft_reset()` using IB-test failure, per-queue reset restore success, firmware init timeout logs, ring allocation/fence wait/IB timeout logs, invalid ring ID logs, and IP-state dumps. Valuable coverage should include direct and non-direct firmware loading, SR-IOV VF paths, doorbell and register WPTR paths, trap/fence IRQ dispatch, per-queue reset, compressed buffer copy flags, VM PTE packets, and suspend/resume.
