# subset-b-001358 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_0.c -->
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
- `sdma_v7_0_ring_get_rptr()`, `sdma_v7_0_ring_get_wptr()`, and `sdma_v7_0_ring_set_wptr()` adapt AMDGPU ring pointers to SDMA's byte-addressed hardware pointers by shifting by two dwords and writing either a 64-bit doorbell or RB_WPTR registers.
- `sdma_v7_0_ring_emit_ib()`, `sdma_v7_0_ring_emit_fence()`, `sdma_v7_0_ring_emit_mem_sync()`, `sdma_v7_0_ring_emit_hdp_flush()`, and `sdma_v7_0_ring_emit_pipeline_sync()` are the main packet-generation entry points used by the scheduler and fence subsystem.
- `sdma_v7_0_ring_test_ring()` and `sdma_v7_0_ring_test_ib()` are runtime health tests that write `0xDEADBEEF` into a writeback slot directly or through an IB.
- `sdma_v7_0_start()`, `sdma_v7_0_gfx_resume_instance()`, `sdma_v7_0_load_microcode()`, `sdma_v7_0_hw_init()`, and `sdma_v7_0_hw_fini()` implement the main hardware bring-up and teardown path.
- IRQ functions include `sdma_v7_0_set_trap_irq_state()`, `sdma_v7_0_process_trap_irq()`, `sdma_v7_0_process_fence_irq()`, and the currently empty illegal-instruction handler.

## Control flow

Initialization starts in `sdma_v7_0_early_init()`. It derives user-queue policy from the global `amdgpu_user_queue` knob, initializes firmware metadata with `amdgpu_sdma_init_microcode()`, installs ring/buffer/IRQ/MQD function tables, registers VM PTE emitters, and publishes CSA sizing through `adev->sdma.get_csa_info`.

`sdma_v7_0_sw_init()` registers trap and user-fence IRQ source IDs, then initializes each `adev->sdma.instance[i].ring` with doorbells enabled, `me = i`, a GFXHUB VM hub, an engine-specific doorbell index, a name like `sdma0`, and `amdgpu_ring_init()`. It sets reset capabilities from `amdgpu_get_soft_full_reset_mask()` and adds per-queue reset support when not SR-IOV and not disabled by debug settings. It also creates sysfs reset-mask state, allocates the SDMA IP dump buffer, and conditionally enables DMA user queue MES functions when firmware version and IP version allow it.

Hardware initialization calls `sdma_v7_0_start()`. On SR-IOV VFs, it disables context switching and engines, programs ring-buffer registers, and returns after `sdma_v7_0_gfx_resume()`. On bare metal with direct firmware loading, it loads microcode into per-instance VRAM BOs, points IC registers at those BOs, primes icache, and waits for both `ICACHE_PRIMED` and `UCODE_INIT_DONE`. It then unhalts engines, enables context switching, resumes each GFX ring, and leaves RLC queue resume as a no-op.

Per-instance resume programs ring size, ring base, read/write pointers, writeback addresses, shadow write-pointer polling address, doorbell enable/offset, watchdog count, UTCL1 response mode/retry delay, default cache policies, MCU halt/reset bits, RB enable, IB enable, and finally marks `ring->sched.ready = true`. It then runs `amdgpu_ring_test_helper()` and clears readiness on failure.

Shutdown through `sdma_v7_0_hw_fini()` disables context switching and engines, then releases user queue trap IRQ references. `sw_fini()` finalizes each ring, destroys sysfs reset-mask and instance context state, frees direct-load firmware BOs, and frees the IP dump buffer.

Reset has two lanes. `sdma_v7_0_soft_reset()` stops rings, asserts HALT and RESET on every SDMA MCU, clears queue preemption, toggles `GRBM_SOFT_RESET`, delays between phases, and restarts SDMA. Per-queue reset uses `amdgpu_ring_reset_helper_begin()`, `amdgpu_mes_reset_legacy_queue()`, then `sdma_v7_0_gfx_resume_instance(..., restore = true)` before ending the reset helper.

## State and persistence behavior

Persistent runtime state is held in `adev->sdma`, its per-instance ring structs, firmware pointers/BOs, IP dump buffer, reset-mask sysfs objects, and the memory manager's selected buffer function/ring. The file does not persist state to disk; its persistence is hardware/MMIO state, writeback memory, doorbell state, and kernel objects that survive across IP lifecycle phases until freed.

Ring read/write pointers are stored in writeback/shadow memory and represented as dword offsets in the AMDGPU ring while SDMA hardware consumes byte offsets. Resume either restores both RPTR and WPTR from `ring->wptr` during queue reset or clears them on cold start. Doorbell writes also update `ring->wptr_cpu_addr` atomically, which provides host-visible shadow state.

Direct firmware loading allocates one VRAM BO per SDMA instance and stores the object, GPU address, and mapped pointer in `adev->sdma.instance[i]`. Those BOs are freed on direct-load errors and during software finalization.

The IP dump path persists a snapshot into `adev->sdma.ip_dump`; `dump_ip_state()` disables gfxoff, reads every register in `sdma_reg_list_7_0` for every instance, then re-enables gfxoff. `print_ip_state()` only prints the cached snapshot.

## Dependencies and integration points

The file is tightly integrated with the AMDGPU core: `amdgpu_ring`, `amdgpu_ib`, `amdgpu_irq`, `amdgpu_fence`, `amdgpu_mes`, `amdgpu_sdma`, `amdgpu_gmc`, `amdgpu_device_wb`, `amdgpu_bo`, and `amdgpu_ucode` APIs. It depends on GC 12.0 register headers, SDMA packet macros, NBIO HDP flush callbacks, SOC15 MMIO helpers, MES user queue functions, and v12 MQD structures.

Scheduler integration is through `amdgpu_ring_init()` and `amdgpu_ring_funcs`; VM integration is through `amdgpu_sdma_set_vm_pte_scheds()` and `amdgpu_gmc_emit_flush_gpu_tlb()`; memory-management integration is through `adev->mman.buffer_funcs`; interrupt integration uses `amdgpu_irq_add_id()`, `amdgpu_irq_get/put()`, and `amdgpu_fence_process()`; reset integration uses global and per-queue AMDGPU reset helpers. User-fence IRQ handling also calls `amdgpu_userq_process_fence_irq()` when MES is enabled and an SDMA fence doorbell offset is present.

## Risks and edge cases

- Register offset translation is hardware-specific. Mistakes in the hyper-decode range or SDMA1 offsets would silently program the wrong register space.
- `sdma_v7_0_wait_for_idle()` explicitly reads only instances 0 and 1, while other paths loop over `adev->sdma.num_instances`; this is safe only if v7.0 devices covered here expose exactly two instances.
- The code has several empty or placeholder paths: RLC stop/resume, context-switch enable, illegal-instruction handling, and clock/power gating hooks. If hardware later requires those controls, lifecycle and error handling would be incomplete.
- Direct firmware loading allocates firmware BOs per instance; if a later instance fails, already allocated earlier instance BOs depend on caller cleanup paths.
- Ring pointer handling assumes little-endian semantics except for selected register-swap fields; comments still note unresolved big-endian questions for writeback/doorbell shadow memory.
- Fence emission uses `BUG_ON(addr & 0x3)`, so invalid fence alignment becomes a kernel BUG rather than a recoverable error.
- `process_trap_irq()` rejects `instances > 1`, reflecting a two-instance assumption and a compact ring_id encoding.
- User queue enablement is gated by firmware version and module parameters. Regressions can surface only on combinations of IP version, firmware revision, MES enablement, and `amdgpu_user_queue`.
- Buffer copy/fill emitters include SDMA7 compression/DCC fields; packet-format mismatches could corrupt memory moves or compressed-resource metadata.

## Test signals

Primary built-in test signals are `amdgpu_ring_test_helper()` during resume, `sdma_v7_0_ring_test_ring()` direct ring writes, `sdma_v7_0_ring_test_ib()` scheduled IB writes plus fence wait, `sdma_v7_0_check_soft_reset()` which treats IB-test failure as a reset signal, and per-queue reset success from restored ring tests. Runtime diagnostics include DRM errors for firmware init timeout, ring allocation failure, IB timeout, fence wait failure, invalid ring IDs, and IP-state dumps via the SDMA register list. Useful integration tests should cover direct firmware load and non-direct firmware paths, SR-IOV VF behavior, doorbell and non-doorbell writes, trap/fence IRQ dispatch, per-queue reset, compressed buffer copy flags, VM PTE update packets, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_0.h

## Purpose

`sdma_v7_0.h` is the public header for the SDMA 7.0 AMDGPU IP block implementation. It provides the include guard and exposes the two global descriptors that other AMDGPU ASIC/IP discovery code needs to register or reference the SDMA 7.0 block.

## Important APIs, types, and functions

- `extern const struct amd_ip_funcs sdma_v7_0_ip_funcs;` exports the lifecycle callback table implemented in `sdma_v7_0.c`.
- `extern const struct amdgpu_ip_block_version sdma_v7_0_ip_block;` exports the IP block metadata, including block type and version.

The header deliberately does not expose implementation-private helpers such as ring emitters, reset functions, register offset helpers, or IRQ handlers. Those remain `static` inside `sdma_v7_0.c`.

## Control flow

There is no runtime control flow in this header. Its role is compile-time linkage: a translation unit includes it to gain declarations for the SDMA 7.0 IP function table and block-version record. At runtime, control enters the implementation through the function pointers stored in `sdma_v7_0_ip_funcs`.

## State and persistence behavior

The header declares global const objects but owns no state. State is created and managed in the C implementation through `adev->sdma`, rings, firmware BOs, IRQ sources, and IP dump buffers.

## Dependencies and integration points

The declarations depend on `struct amd_ip_funcs` and `struct amdgpu_ip_block_version` being visible from surrounding AMDGPU headers before or alongside this header. It integrates with AMDGPU IP registration code that selects an IP block descriptor based on discovered hardware version.

## Risks and edge cases

- The header's ABI surface is intentionally tiny; adding private helper declarations here would increase coupling and make internal SDMA implementation details callable from unrelated code.
- The include guard must remain unique to avoid collisions with other SDMA version headers.
- The exported declarations must stay synchronized with the definitions in `sdma_v7_0.c`; changing symbol names in one file without the other would produce link errors or stale references.

## Test signals

Build coverage is the primary signal. A successful kernel/module build verifies that the exported symbols match their definitions and that any file including this header sees compatible structure declarations. Runtime validation belongs to `sdma_v7_0.c` through IP block initialization, ring tests, reset tests, and interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1.c

## Purpose

`sdma_v7_1.c` is the AMDGPU SDMA 7.1 IP implementation for GC 12.1 devices. It is structurally similar to the SDMA 7.0 implementation but adapts register names, packet formats, instance addressing, interrupt routing, and lifecycle controls for multi-XCC/partitioned hardware. It exposes normal AMDGPU IP functions plus XCP suspend/resume hooks that can start or stop a selected SDMA instance mask.

The file declares firmware dependency `amdgpu/sdma_7_1_0.bin`, uses GC 12.1 register and IRQ headers, uses `sdma_v7_1_0_pkt_open.h`, and includes `soc_v1_0.h` for XCC-normalized register offsets in SDMA register-write and register-wait packets.

## Important APIs, types, and functions

- `sdma_v7_1_ip_funcs` and `sdma_v7_1_ip_block` are the exported AMDGPU IP lifecycle descriptors for SDMA 7.1.
- `sdma_v7_1_xcp_funcs` exports XCP `suspend` and `resume` callbacks that call instance-mask-aware SDMA stop/start helpers.
- `sdma_v7_1_ring_funcs` supplies AMDGPU scheduler hooks for SDMA rings, including pointer access, IB/fence emission, VM flushes, tests, conditional execution, preemption, and queue reset.
- `sdma_v7_1_buffer_funcs` registers SDMA copy/fill emitters with the memory manager.
- `sdma_v7_1_vm_pte_funcs` registers copy/write/set page-table emitters.
- `sdma_v7_1_get_reg_offset()` maps a logical SDMA instance to a GC register aperture using `GET_INST(SDMA0, instance)`, the instance's `xcc_id`, `adev->sdma.num_inst_per_xcc`, the lower register window, and the hyper-decode-style second register base.
- Instance-mask helpers such as `sdma_v7_1_inst_gfx_stop()`, `sdma_v7_1_inst_enable()`, `sdma_v7_1_inst_gfx_resume()`, `sdma_v7_1_inst_load_microcode()`, and `sdma_v7_1_inst_start()` are the central difference from v7.0. They operate over `for_each_inst(i, inst_mask)` rather than always touching all instances.
- `sdma_v7_1_process_trap_irq()` decodes `entry->node_id` through `ih_node_to_logical_xcc()` when available, combines it with ring_id instance bits, and maps the physical SDMA instance back to an `adev->sdma.instance[]` index.

## Control flow

`sdma_v7_1_early_init()` sets user-queue policy more conservatively than v7.0: default and `-1` disable user submission and user queues, while `amdgpu_user_queue = 0` allows kernel submission but disables user queues. It then initializes firmware metadata, installs ring/buffer/IRQ/MQD function tables, and registers VM PTE functions.

`sdma_v7_1_set_ring_funcs()` assigns the ring function table and records each instance's `xcc_id` based on the physical SDMA instance divided by `adev->sdma.num_inst_per_xcc`. `sw_init()` registers the trap IRQ, initializes each ring with doorbells, computes the ring's logical XCC ID, assigns `ring->vm_hub = AMDGPU_GFXHUB(xcc_id)`, names rings as `sdma<xcc>.<instance-within-xcc>`, initializes scheduler rings, sets reset capabilities, creates reset-mask sysfs state, allocates the IP dump buffer, and optionally enables DMA user queue functions under `CONFIG_DRM_AMDGPU_NAVI3X_USERQ`.

`hw_init()` builds an all-instances mask with `GENMASK(adev->sdma.num_instances - 1, 0)` and calls `sdma_v7_1_inst_start()`. The start path handles SR-IOV by disabling the requested instances and reprogramming their rings; otherwise direct firmware loading allocates and primes per-instance firmware BOs for the requested mask, then unhalts the requested MCUs, sets UTCL1 timeout in the context-switch helper, resumes GFX rings for those instances, and leaves RLC resume as a no-op.

Per-instance resume mirrors v7.0 but uses GC 12.1 register names. It programs RB size/base, RPTR/WPTR registers or restoration values, WPTR polling and RPTR writeback addresses, doorbell enable/offset, NBIO doorbell range for instance 0, minor pointer update sequencing, watchdog count, UTCL1 response and cache policy registers, MCU halt/reset bits, RB/IB enables, `ring->sched.ready`, SR-IOV-specific enable sequence, and an `amdgpu_ring_test_helper()` validation.

Reset flow includes both full SDMA soft reset and per-queue reset. `sdma_v7_1_soft_reset()` derives an instance mask from `NUM_XCC(adev->sdma.sdma_mask)`, stops selected rings, asserts HALT/RESET, clears preemption, toggles `GRBM_SOFT_RESET`, and restarts the masked instances. Per-queue reset uses the common MES legacy queue reset helper followed by restoring only the timed-out ring's instance.

XCP resume/suspend call the same instance-mask helpers as the normal lifecycle. This allows partition-level operations to suspend/resume only the SDMA engines belonging to a GPU partition.

## State and persistence behavior

The implementation stores runtime state in `adev->sdma.instance[]`, including rings, firmware BOs, firmware GPU addresses, mapped firmware pointers, and each instance's `xcc_id`. It also owns `adev->sdma.ip_dump`, reset-mask sysfs state, and the memory manager's selected SDMA buffer functions.

Ring pointer state follows the same dword-versus-byte conversion as v7.0. Cold resume clears `ring->wptr`; queue reset restore writes RPTR and WPTR from the saved `ring->wptr`. Doorbell writes update both host write-pointer shadow memory and the 64-bit doorbell.

The IP dump buffer contains a cached register snapshot across all instances using `sdma_reg_list_7_1`. Dumps disable gfxoff around MMIO reads. Direct-load firmware BOs are allocated and freed by instance mask, which is important for XCP and partitioned start/stop paths.

## Dependencies and integration points

This file integrates with AMDGPU's IP block framework, ring scheduler, VM update path, MES reset path, memory manager, interrupt handling, firmware loader, BO allocator, writeback allocator, NBIO doorbell range programming, and XCP partition framework. It depends on GC 12.1 register headers, SOC15 MMIO helpers, SOC v1 register-offset normalization, SDMA 7.1 packet macros, `v12_sdma_mqd`, and `userq_mes_funcs` under the relevant build option.

The ring register-write and register-wait emitters normalize XCC register offsets before emitting SDMA packets, which is a critical integration detail for multi-XCC devices. Trap IRQ processing integrates with `adev->gfx.funcs->ih_node_to_logical_xcc()` to route interrupts from hardware node IDs to logical SDMA ring indices.

## Risks and edge cases

- The instance-mask design reduces blast radius for XCP operations but creates correctness risk if masks are confused with instance numbers. In `sdma_v7_1_gfx_resume_instance()` the SR-IOV branch passes `i` to `sdma_v7_1_inst_ctx_switch_enable()` and `sdma_v7_1_inst_enable()` even though those helpers expect masks; this is worth auditing because instance 0 would pass mask 0.
- `sdma_v7_1_soft_reset()` derives `inst_mask = GENMASK(NUM_XCC(adev->sdma.sdma_mask) - 1, 0)`, which may not select every SDMA instance if the intended mask is per-SDMA rather than per-XCC.
- `sdma_v7_1_get_reg_offset()` depends on valid `xcc_id` and `num_inst_per_xcc`; these are set in `set_ring_funcs()`, so lifecycle ordering matters before any register access.
- Trap IRQ routing depends on `ih_node_to_logical_xcc()` availability. Without it, the code warns and may use XCC 0, which can misroute fences on multi-XCC hardware.
- As in v7.0, RLC stop/resume, illegal-instruction handling, and clock/power gating hooks are placeholders.
- `sdma_v7_1_vm_copy_pte()` advertises `copy_pte_num_dw = 8` but emits seven dwords in the visible path, unlike v7.0's eight-dword copy packet. This may be intentional packet-format change or a sizing mismatch that warrants validation.
- `sdma_v7_1_buffer_funcs.copy_num_dw` remains 8 while `sdma_v7_1_emit_copy_buffer()` emits seven dwords. Over-reservation is generally safe, but consumers may assume exact sizing in tight IB accounting.
- DCC/compression fields present in v7.0 copy/fill emitters are absent here; compressed copy behavior should be checked against SDMA 7.1 packet requirements.
- Fence alignment still uses `BUG_ON(addr & 0x3)`, which converts invalid caller input into a kernel BUG.

## Test signals

Built-in validation includes `amdgpu_ring_test_helper()` during instance resume, direct ring write tests, IB scheduling tests with fence waits, reset-trigger tests via `check_soft_reset()`, and diagnostic register snapshots through `dump_ip_state()`/`print_ip_state()`. High-value integration coverage should exercise multi-XCC instance mapping, XCP suspend/resume with nontrivial instance masks, trap IRQ routing from `node_id`, direct firmware load by mask, SR-IOV VF paths, per-queue reset restore, VM PTE update packet sizes, XCC-normalized register waits/writes, and suspend/resume across all SDMA instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1.h

## Purpose

`sdma_v7_1.h` is the public header for the SDMA 7.1 AMDGPU IP block. It exposes the standard IP lifecycle descriptors plus the XCP-specific function table used to suspend and resume selected SDMA instance masks on partitioned devices.

## Important APIs, types, and functions

- `extern const struct amd_ip_funcs sdma_v7_1_ip_funcs;` declares the lifecycle callback table implemented in `sdma_v7_1.c`.
- `extern const struct amdgpu_ip_block_version sdma_v7_1_ip_block;` declares the SDMA 7.1 IP block metadata.
- `extern struct amdgpu_xcp_ip_funcs sdma_v7_1_xcp_funcs;` declares the XCP suspend/resume hook table implemented at the end of `sdma_v7_1.c`.

The header exposes no private ring, register, firmware, IRQ, or packet-emission helpers. Those remain static to the implementation file.

## Control flow

There is no executable control flow in the header. Consumers include it to wire SDMA 7.1 into device/IP discovery and, when relevant, XCP partition management. Runtime control enters the implementation through `sdma_v7_1_ip_funcs` for normal device lifecycle and through `sdma_v7_1_xcp_funcs` for partition-scoped suspend/resume.

## State and persistence behavior

The header owns no state. It declares global descriptor objects that point to implementation functions. Runtime state is held in the C file through `adev->sdma` instances, rings, firmware BOs, XCC IDs, reset-mask sysfs state, and IP dump buffers.

## Dependencies and integration points

The declarations depend on AMDGPU structure definitions for `struct amd_ip_funcs`, `struct amdgpu_ip_block_version`, and `struct amdgpu_xcp_ip_funcs`. The XCP declaration is the key difference from `sdma_v7_0.h`; it lets partition-aware AMDGPU code call SDMA 7.1 instance-mask suspend/resume without exposing lower-level helpers.

## Risks and edge cases

- The XCP function table is non-const in this header and implementation, so accidental mutation by external code would affect partition lifecycle behavior.
- Include ordering must provide the struct definitions or forward declarations expected by these extern declarations.
- The header must stay synchronized with implementation symbol names and storage qualifiers; mismatches would fail builds or break XCP registration.
- Keeping the public surface small is important because the SDMA 7.1 implementation has many hardware-specific assumptions around XCC and instance masks.

## Test signals

Build coverage verifies symbol declaration/definition consistency and correct include dependencies. Runtime validation is indirect: successful IP registration, normal SDMA lifecycle tests, and XCP suspend/resume tests prove that the exported descriptors are correctly consumed by the rest of AMDGPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1.h -->
