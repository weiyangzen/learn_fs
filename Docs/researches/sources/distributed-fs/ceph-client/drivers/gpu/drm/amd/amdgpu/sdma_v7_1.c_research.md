# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1.c

## Purpose

`sdma_v7_1.c` is the AMDGPU SDMA 7.1 IP implementation for GC 12.1 devices. It is structurally similar to SDMA 7.0 but adapts register names, packet formats, instance addressing, interrupt routing, and lifecycle controls for multi-XCC/partitioned hardware. It exposes normal AMDGPU IP functions plus XCP suspend/resume hooks that can start or stop selected SDMA instance masks.

The file declares firmware dependency `amdgpu/sdma_7_1_0.bin`, uses GC 12.1 register and IRQ headers, uses `sdma_v7_1_0_pkt_open.h`, and includes `soc_v1_0.h` for XCC-normalized register offsets in SDMA register-write and register-wait packets.

## Important APIs, types, and functions

- `sdma_v7_1_ip_funcs` and `sdma_v7_1_ip_block` are the exported AMDGPU IP lifecycle descriptors for SDMA 7.1.
- `sdma_v7_1_xcp_funcs` exports XCP `suspend` and `resume` callbacks that call instance-mask-aware SDMA stop/start helpers.
- `sdma_v7_1_ring_funcs` supplies AMDGPU scheduler hooks for SDMA rings, including pointer access, IB/fence emission, VM flushes, tests, conditional execution, preemption, and queue reset.
- `sdma_v7_1_buffer_funcs` registers SDMA copy/fill emitters with the memory manager.
- `sdma_v7_1_vm_pte_funcs` registers copy/write/set page-table emitters.
- `sdma_v7_1_get_reg_offset()` maps a logical SDMA instance to a GC register aperture using `GET_INST(SDMA0, instance)`, `xcc_id`, `num_inst_per_xcc`, and the correct lower or second register base.
- Instance-mask helpers such as `sdma_v7_1_inst_gfx_stop()`, `sdma_v7_1_inst_enable()`, `sdma_v7_1_inst_gfx_resume()`, `sdma_v7_1_inst_load_microcode()`, and `sdma_v7_1_inst_start()` operate over `for_each_inst(i, inst_mask)`.
- `sdma_v7_1_process_trap_irq()` decodes `entry->node_id` through `ih_node_to_logical_xcc()` when available, combines it with ring_id instance bits, and maps the physical SDMA instance back to an AMDGPU SDMA ring index.

## Control flow

`sdma_v7_1_early_init()` sets user-queue policy more conservatively than v7.0: default and `-1` disable user submission and user queues, while `amdgpu_user_queue = 0` allows kernel submission but disables user queues. It initializes firmware metadata, installs ring/buffer/IRQ/MQD function tables, and registers VM PTE functions.

`sdma_v7_1_set_ring_funcs()` assigns the ring function table and records each instance's `xcc_id` based on the physical SDMA instance divided by `adev->sdma.num_inst_per_xcc`. `sw_init()` registers the trap IRQ, initializes each ring with doorbells, computes logical XCC ID, assigns `ring->vm_hub = AMDGPU_GFXHUB(xcc_id)`, names rings as `sdma<xcc>.<instance-within-xcc>`, initializes scheduler rings, sets reset capabilities, creates reset-mask sysfs state, allocates the IP dump buffer, and optionally enables DMA user queue functions under `CONFIG_DRM_AMDGPU_NAVI3X_USERQ`.

`hw_init()` builds an all-instances mask and calls `sdma_v7_1_inst_start()`. The start path handles SR-IOV by disabling requested instances and reprogramming their rings. Otherwise, direct firmware loading allocates and primes per-instance firmware BOs for the requested mask, then unhalts selected MCUs, sets UTCL1 timeout through the context-switch helper, resumes GFX rings, and leaves RLC resume as a no-op.

Per-instance resume programs RB size/base, RPTR/WPTR registers or restoration values, WPTR polling and RPTR writeback addresses, doorbell enable/offset, NBIO doorbell range for instance 0, minor pointer update sequencing, watchdog count, UTCL1 response/cache policy registers, MCU halt/reset bits, RB/IB enables, `ring->sched.ready`, SR-IOV-specific enable sequence, and `amdgpu_ring_test_helper()`.

Reset flow includes full SDMA soft reset and per-queue reset. The soft reset derives an instance mask, stops selected rings, asserts HALT/RESET, clears preemption, toggles `GRBM_SOFT_RESET`, and restarts masked instances. Per-queue reset uses the common MES legacy queue reset helper followed by restoring only the timed-out ring's instance. XCP resume/suspend call the same instance-mask helpers for partition-scoped lifecycle.

## State and persistence behavior

Runtime state lives in `adev->sdma.instance[]`, including rings, firmware BOs, firmware GPU addresses, mapped firmware pointers, and each instance's `xcc_id`. It also owns `adev->sdma.ip_dump`, reset-mask sysfs state, and the memory manager's selected SDMA buffer functions.

Ring pointer state follows the same dword-versus-byte conversion as v7.0. Cold resume clears `ring->wptr`; queue reset restore writes RPTR and WPTR from saved `ring->wptr`. Doorbell writes update both host write-pointer shadow memory and the 64-bit doorbell. Direct-load firmware BOs are allocated and freed by instance mask, which is important for XCP and partitioned start/stop paths.

## Dependencies and integration points

This file integrates with AMDGPU's IP block framework, ring scheduler, VM update path, MES reset path, memory manager, interrupt handling, firmware loader, BO allocator, writeback allocator, NBIO doorbell range programming, and XCP partition framework. It depends on GC 12.1 register headers, SOC15 MMIO helpers, SOC v1 register-offset normalization, SDMA 7.1 packet macros, `v12_sdma_mqd`, and `userq_mes_funcs` under the relevant build option.

The ring register-write and register-wait emitters normalize XCC register offsets before emitting SDMA packets. Trap IRQ processing integrates with `adev->gfx.funcs->ih_node_to_logical_xcc()` to route interrupts from hardware node IDs to logical SDMA ring indices.

## Risks and edge cases

- Instance masks can be confused with instance numbers; the SR-IOV branch in `sdma_v7_1_gfx_resume_instance()` passes `i` to helpers that expect masks, so instance 0 would pass mask 0.
- `sdma_v7_1_soft_reset()` derives `inst_mask = GENMASK(NUM_XCC(adev->sdma.sdma_mask) - 1, 0)`, which may not select every SDMA instance if the intended mask is per-SDMA rather than per-XCC.
- `sdma_v7_1_get_reg_offset()` depends on valid `xcc_id` and `num_inst_per_xcc`, so lifecycle ordering before register access matters.
- Trap IRQ routing may misroute on multi-XCC hardware if `ih_node_to_logical_xcc()` is unavailable.
- RLC stop/resume, illegal-instruction handling, and clock/power gating hooks are placeholders.
- `sdma_v7_1_vm_copy_pte()` advertises `copy_pte_num_dw = 8` but visibly emits seven dwords; `buffer_funcs.copy_num_dw` similarly reserves eight while copy emits seven.
- DCC/compression fields present in v7.0 copy/fill emitters are absent here and should be checked against SDMA 7.1 packet requirements.
- Fence alignment still uses `BUG_ON(addr & 0x3)`.

## Test signals

Built-in validation includes `amdgpu_ring_test_helper()` during instance resume, direct ring write tests, IB scheduling tests with fence waits, reset-trigger tests via `check_soft_reset()`, and diagnostic register snapshots. High-value coverage should exercise multi-XCC instance mapping, XCP suspend/resume with nontrivial masks, trap IRQ routing from `node_id`, direct firmware load by mask, SR-IOV VF paths, per-queue reset restore, VM PTE packet sizes, XCC-normalized register waits/writes, and suspend/resume across all SDMA instances.
