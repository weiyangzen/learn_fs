# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_dma.c

## Purpose
`evergreen_dma.c` contains DMA-ring operational helpers for Evergreen through Southern Islands style Radeon ASIC support. Unlike the DMA command-stream parser in `evergreen_cs.c`, this file emits trusted kernel DMA ring packets for fences, indirect-buffer execution, TTM buffer moves, and lockup detection.

## Important APIs, Types, And Functions
`evergreen_dma_fence_ring_emit()` writes a DMA fence packet to the selected DMA ring, followed by a trap packet for interrupt generation and an SRBM write that flushes HDP coherency. `evergreen_dma_ring_ib_execute()` emits a DMA indirect-buffer packet, with optional writeback of the next read pointer and padding so the IB packet lands on the hardware-required 8-DW boundary. `evergreen_copy_dma()` is the copy callback used by Radeon TTM memory movement; it emits one or more DMA copy packets and returns a `struct radeon_fence *`. `evergreen_dma_is_lockup()` checks soft-reset status and updates or tests ring lockup state.

## Control Flow
Fence emission takes the fence ring, obtains the fence GPU address from `rdev->fence_drv`, writes the DMA fence packet/address/sequence, emits a trap, then writes `HDP_MEM_COHERENCY_FLUSH_CNTL` through an SRBM write packet.

IB execution optionally writes `ring->next_rptr_gpu_addr` when writeback is enabled, pads the ring write pointer until the DMA IB packet will end on the required modulo-8 position, then emits `DMA_PACKET_INDIRECT_BUFFER` with the IB base address and length. `evergreen_copy_dma()` creates a `radeon_sync`, computes the transfer length in dwords, splits the transfer into chunks no larger than `0xfffff` dwords, locks enough ring space, syncs against the reservation object and other rings, writes copy packets, emits a fence, commits the ring, and releases sync state. Error paths undo the ring lock when a fence cannot be emitted and return `ERR_PTR(r)`.

## State And Persistence Behavior
The functions mutate the DMA ring write stream and therefore persist work in GPU-visible ring memory until consumed by the engine. They update synchronization state through emitted fences and optional read-pointer writeback. No private static state is kept in this file. `evergreen_copy_dma()` advances source and destination offsets per emitted chunk and leaves completion state represented by the returned fence.

## Dependencies And Integration Points
The file depends on core Radeon ring, fence, sync, writeback, and ASIC reset helpers from `radeon.h`, `radeon_asic.h`, `evergreen.h`, and `evergreend.h`. It integrates with the ASIC copy callback (`rdev->asic->copy.dma_ring_index`), TTM reservation synchronization (`struct dma_resv`), fence drivers, and ring lock/unlock infrastructure. Hardware register and packet macros include `DMA_PACKET_*`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, and `RADEON_RESET_DMA`.

## Risks
DMA packet formatting is low-level and alignment-sensitive. Incorrect padding in `evergreen_dma_ring_ib_execute()` can hang the DMA engine. Copy chunk sizing must match the packet count field width; the loop correctly caps at `0xfffff` dwords. Fence emission depends on a valid fence GPU address and ring index. Error handling around ring locks is important because a partially written but uncommitted ring could corrupt subsequent work if not undone.

## Test Signals
Tests should cover DMA ring fence signaling, interrupt delivery after trap packets, IB execution alignment, writeback-enabled and writeback-disabled execution, copy sizes at 0, one page, exactly `0xfffff` dwords, and multi-chunk transfers. Lockup tests should simulate soft-reset masks with and without `RADEON_RESET_DMA`. Runtime signals include ring test failures, fence timeouts, DMA reset events, and TTM buffer move errors.
