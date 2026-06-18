# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_sdma.c

## Purpose
`cik_sdma.c` implements the CIK System DMA engine support for the Radeon driver. CIK exposes two SDMA engines used for asynchronous graphics DMA and compute queues. This file handles SDMA ring pointer access, IB execution, fence/semaphore packets, engine stop/start, microcode loading, copy acceleration, ring and IB self-tests, lockup detection, VM page-table updates, and VM TLB flushing.

## Important APIs and functions
- Ring pointer operations: `cik_sdma_get_rptr`, `cik_sdma_get_wptr`, and `cik_sdma_set_wptr` read/write hardware or writeback-backed ring pointers for `R600_RING_TYPE_DMA_INDEX` and `CAYMAN_RING_TYPE_DMA1_INDEX`.
- Submission helpers: `cik_sdma_ring_ib_execute` pads to SDMA alignment and emits an `SDMA_OPCODE_INDIRECT_BUFFER`; `cik_sdma_fence_ring_emit` writes a fence, traps for interrupt generation, and emits an HDP flush; `cik_sdma_semaphore_ring_emit` emits wait/signal semaphore packets.
- Lifecycle: `cik_sdma_enable`, `cik_sdma_resume`, and `cik_sdma_fini` halt/unhalt engines, load firmware, initialize rings, test them, and tear them down.
- Internal setup: `cik_sdma_gfx_stop`, `cik_sdma_gfx_resume`, `cik_sdma_ctx_switch_enable`, `cik_sdma_load_microcode`, plus placeholder compute queue functions `cik_sdma_rlc_stop` and `cik_sdma_rlc_resume`.
- Copy and tests: `cik_copy_dma`, `cik_sdma_ring_test`, `cik_sdma_ib_test`, and `cik_sdma_is_lockup`.
- VM helpers: `cik_sdma_vm_copy_pages`, `cik_sdma_vm_write_pages`, `cik_sdma_vm_set_pages`, `cik_sdma_vm_pad_ib`, and `cik_dma_vm_flush`.

## Control flow
Resume loads SDMA microcode, enables both engines, initializes both graphics rings, and runs `radeon_ring_test` per ring. Ring setup programs semaphore timers, ring buffer size, read/write pointers, writeback address, base address, and IB enable bits before marking a ring ready. Stop disables RB/IB control, marks rings not ready, and uses an SDMA soft reset as a hibernation workaround. Copy and VM functions fill ring/IB dwords with SDMA packet sequences, then emit fences or pad IBs as required.

## State and persistence behavior
The file mutates persistent hardware state in SDMA registers (`SDMA0_*` plus `SDMA1_REGISTER_OFFSET`), microcode memory, ring buffer pointers, writeback slots, fence memory, VM context registers, and TLB invalidation registers. Driver state is updated in `rdev->ring[]`, `rdev->wb`, `rdev->fence_drv[]`, and synchronization structures. SDMA firmware is loaded from `rdev->sdma_fw`; both legacy big-endian blobs and newer firmware headers are supported.

## Dependencies and integration points
Includes `radeon.h`, `radeon_ucode.h`, `radeon_asic.h`, `radeon_trace.h`, `cik.h`, and `cikd.h`. It relies on Radeon ring, IB, fence, sync, TTM, VM, writeback, and MMIO helpers such as `radeon_ring_write`, `radeon_ring_lock`, `radeon_fence_emit`, `radeon_ib_schedule`, `RREG32`, and `WREG32`. It integrates with the ASIC copy callback through `cik_copy_dma` and with VM management through SDMA page-table update helpers.

## Risks and test signals
High-risk areas are packet sizing and alignment, firmware size/version handling, endian paths, writeback address programming, fence ordering, hibernation reset behavior, and VM flush correctness. Bugs manifest as DMA ring timeouts, fence stalls, corrupted BO moves, stale PTEs, VM faults, or GPU lockups. Direct test signals are `cik_sdma_ring_test`, `cik_sdma_ib_test`, `radeon_ring_test`, fence wait completion, BO move stress, VM map/unmap stress, suspend/hibernate/resume, and lockup reset recovery.
