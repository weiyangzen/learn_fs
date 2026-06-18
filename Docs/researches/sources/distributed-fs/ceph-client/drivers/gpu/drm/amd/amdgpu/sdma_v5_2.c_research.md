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
