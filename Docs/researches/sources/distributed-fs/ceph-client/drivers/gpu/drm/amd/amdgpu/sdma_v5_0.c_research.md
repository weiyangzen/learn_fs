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
