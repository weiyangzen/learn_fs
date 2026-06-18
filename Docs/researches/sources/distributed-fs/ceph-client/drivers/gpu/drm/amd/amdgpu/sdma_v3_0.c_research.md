# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v3_0.c

## Purpose
Implements the AMDGPU SDMA v3.0/v3.1 IP block for VI-era ASICs. It loads SDMA firmware, applies per-ASIC golden registers, initializes SDMA gfx rings, exposes SDMA packet emitters for IBs, fences, VM page table updates, HDP/VM flushes, and buffer copy/fill, and plugs the block into the AMDGPU IP lifecycle.

## APIs, Types, And Functions
The exported objects are `sdma_v3_0_ip_block` and `sdma_v3_1_ip_block`. Important internal tables include `sdma_v3_0_ip_funcs`, `sdma_v3_0_ring_funcs`, `sdma_v3_0_vm_pte_funcs`, `sdma_v3_0_buffer_funcs`, and IRQ handler tables. Key functions are firmware loading/freeing, `sdma_v3_0_gfx_resume()`, `sdma_v3_0_start()`, ring pointer helpers, packet emitters, `sdma_v3_0_ring_test_ring()`, `sdma_v3_0_ring_test_ib()`, lifecycle callbacks, soft-reset callbacks, clock-gating helpers, and trap/illegal-instruction interrupt handlers.

## Control Flow
`early_init` chooses one or two SDMA instances, requests chip-specific firmware, installs ring/buffer/VM/IRQ function tables, and records firmware versions and burst-NOP capability. `sw_init` registers legacy interrupt IDs and creates one gfx SDMA ring per instance, using doorbells on bare metal and pollmem for SR-IOV VF. `hw_init` programs golden registers and starts the block. Start disables context switching and halts SDMA, programs each gfx ring base, rptr/wptr writeback, doorbell or polling, enables RB/IB, unhalts engines, enables context switching, then tests every ring. Suspend/fini paths disable context switching and halt the engines.

## State And Persistence
Runtime state lives in `adev->sdma`: instance count, firmware pointers/versions, ring structs, `burst_nop`, and `srbm_soft_reset`. Ring state persists in GPU-visible ring buffers and writeback slots for rptr/wptr; firmware blobs are retained in memory until `sw_fini`. There is no filesystem persistence beyond kernel firmware loading. Soft reset caches the SRBM reset mask in `adev->sdma.srbm_soft_reset`; post reset reinitializes gfx rings. Compute/RLC queue state is not implemented in this file.

## Dependencies And Integration
This file depends on AMDGPU core ring, IB, VM, fence, IRQ, firmware, and TTM buffer movement helpers, plus VI/GMC/GFX/BIF register definitions and `tonga_sdma_pkt_open.h` packet macros. It integrates with `amdgpu_sdma_set_vm_pte_scheds()` for VM updates, `adev->mman.buffer_funcs` for DMA copy/fill, `amdgpu_irq_add_id()` for trap and illegal instruction events, `amdgpu_gmc_emit_flush_gpu_tlb()` for VM flushes, and `amdgpu_ring_test_helper()` for bring-up validation.

## Risks And Test Signals
Important risks are ASIC-specific firmware name selection, one-instance Stoney behavior, doorbell versus pollmem write-pointer paths, alignment requirements for IBs and fences, incomplete RLC compute queue support, and soft-reset recovery that only restores gfx rings. Big-endian swapping paths are conditional and likely low-coverage. Test signals include successful firmware load, ring tests writing `0xDEADBEEF`, IB fence completion, VM PTE update stress, trap IRQ fence processing, illegal instruction scheduler faults, suspend/resume, SR-IOV VF pollmem behavior, and clock-gating flag checks.
