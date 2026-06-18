# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dma.c

## Purpose

`r600_dma.c` operates the asynchronous DMA engine present on R600 through Evergreen-era Radeon GPUs. It initializes and tears down the DMA ring, reads and writes hardware ring pointers, emits DMA fences and semaphores, schedules DMA indirect buffers, performs ring/IB self-tests, detects lockups, and implements the TTM copy callback used for BO moves.

## Important APIs, Types, and Functions

- `r600_dma_get_rptr`, `r600_dma_get_wptr`, and `r600_dma_set_wptr`: ring pointer callbacks for the Radeon ring framework, using writeback memory for RPTR when enabled and MMIO registers otherwise.
- `r600_dma_resume`, `r600_dma_stop`, and `r600_dma_fini`: lifecycle management for DMA registers, ring base, writeback address, IB enablement, ring readiness, and ring allocation cleanup.
- `r600_dma_is_lockup`: checks GPU soft-reset bits and delegates to generic Radeon ring lockup tracking.
- `r600_dma_ring_test` and `r600_dma_ib_test`: write a sentinel through the DMA engine and poll writeback memory to verify ring and IB execution.
- `r600_dma_fence_ring_emit` and `r600_dma_semaphore_ring_emit`: emit synchronization packets understood by the DMA ring.
- `r600_dma_ring_ib_execute`: writes an indirect-buffer packet, pads to the DMA ring alignment requirement, and optionally writes `next_rptr` into writeback memory.
- `r600_copy_dma`: copies GPU pages for TTM moves by emitting one or more DMA copy packets, synchronizing with a reservation object, and returning a fence.

## Control Flow

Resume starts by clearing semaphore timers, programming ring size, endian swap flags, RPTR/WPTR, writeback addresses, ring base, and DMA IB control. It disables context-empty interrupts, sets `DMA_MODE` on RV770+, zeros the software write pointer, enables `DMA_RB_ENABLE`, marks the ring ready, and immediately runs `radeon_ring_test`. If the test fails, readiness is cleared and the error is returned. If this DMA ring is the active copy engine, visible VRAM limits are relaxed to real VRAM size after successful startup and reduced again on stop.

Ring and IB tests both write `0xDEADBEEF` to writeback memory. The ring test emits a direct `DMA_PACKET_WRITE` into the ring and polls for up to `rdev->usec_timeout`. The IB test allocates a 256-byte IB, fills it with the same write packet, schedules it, waits for the IB fence, then polls the writeback slot.

IB execution has an R600-specific alignment rule: the indirect-buffer packet must end on an 8-DW boundary. The function pads with DMA NOPs until `ring->wptr & 7` equals 5, then emits the IB packet address and length. When writeback is enabled, it first emits a DMA write of the predicted next read pointer.

`r600_copy_dma` creates a `radeon_sync`, locks enough ring space for chunked copies plus fence overhead, syncs against the reservation object and other rings, emits copy packets of at most `0xFFFE` dwords, emits a fence, commits the ring, and attaches the fence to the sync object. Error paths undo the ring lock or free sync state.

## State and Persistence Behavior

Persistent state is held in `rdev->ring[R600_RING_TYPE_DMA_INDEX]`, DMA MMIO registers, writeback memory, and fence driver memory. `ring->ready` gates whether the engine is usable. `ring->wptr` is software state mirrored to `DMA_RB_WPTR`; `rptr` can be read from writeback or `DMA_RB_RPTR`. `r600_copy_dma` leaves a fence object representing copy completion and updates BO move synchronization through `radeon_sync_free`.

## Dependencies and Integration Points

The file integrates with the generic Radeon ring, fence, IB, sync, and TTM move infrastructure. It depends on DMA packet macros and register definitions from `r600.h`/`r600d.h`, writeback slots such as `R600_WB_DMA_RPTR_OFFSET`, reset detection from `r600_gpu_check_soft_reset`, and `radeon_ttm_set_active_vram_size` when DMA is selected as the copy engine. It is paired with the DMA CS parser in `r600_cs.c`, but this file emits trusted kernel packets rather than validating userspace packets.

## Risks and Edge Cases

- Startup success depends on the ring test; failure must leave `ring->ready` false to avoid later scheduling onto a dead engine.
- Writeback and no-writeback paths can diverge; RPTR behavior should be tested in both modes.
- IB alignment is hardware-specific and easy to regress if ring padding changes.
- Copy chunks are limited by a 16-bit packet count; page-count math must avoid undercounting large moves.
- Error paths in `r600_dma_ib_test` return after fence wait failures without freeing the IB in the negative/timeout branches in this snapshot, which is worth auditing.
- Endian swap flags are compile-time conditional and need big-endian coverage if that platform matters.

## Test Signals

Primary tests are ring startup/shutdown, direct ring writeback tests, DMA IB tests, BO move/copy stress, fence interrupt delivery, semaphore waits/signals across rings, suspend/resume, GPU reset/lockup recovery, and large VRAM/GTT move workloads that force multi-packet copies. Regression testing should include R600 and RV770-family packet layouts and both writeback-enabled and MMIO-RPTR modes.
