# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dma.c

## Purpose
`rv770_dma.c` implements the RV7xx DMA copy callback used by the Radeon TTM memory manager to move GPU pages through the DMA ring instead of the graphics CP ring.

## Important APIs, Types, and Functions
The single exported function is `rv770_copy_dma(struct radeon_device *rdev, uint64_t src_offset, uint64_t dst_offset, unsigned num_gpu_pages, struct dma_resv *resv)`. It uses `struct radeon_sync`, `struct radeon_ring`, `struct radeon_fence`, DMA packet macros, reservation-object synchronization, and fence emission.

## Control Flow
The function creates a sync object, converts page count to DWORD count, splits the transfer into loops of at most `0xffff` DWORDs, locks the DMA ring for enough packet space, synchronizes against the reservation object and other rings, emits one DMA copy packet per chunk with low and high source/destination address fields, emits a fence, commits the ring, frees sync state, and returns the fence. Error paths undo the ring lock or free sync state and return `ERR_PTR`.

## State and Persistence
Persistent state is limited to ring write pointer advancement and emitted fences. The copy operation itself affects GPU memory at `dst_offset`. Reservation synchronization and the returned fence provide ordering state to callers.

## Dependencies and Integration Points
This file integrates with the radeon ring scheduler, TTM BO move path, DMA reservation objects, sync/fence subsystems, and RV770 DMA packet definitions from `rv770d.h`. The ring index comes from `rdev->asic->copy.dma_ring_index`.

## Risks
Address alignment is masked to 4-byte boundaries, so callers must provide page-aligned GPU addresses. Very large moves rely on correct loop chunking and ring-space accounting. Failure to synchronize reservations or emit fences correctly can cause memory corruption or use-before-copy races. If the DMA ring is not initialized, ring locking or fence emission fails.

## Test Signals
Signals include successful BO moves using the DMA ring, no `radeon: moving bo` errors, returned fences that signal, correct behavior for transfers larger than `0xffff` DWORDs, and memory validation after VRAM/GTT migration under rendering load.
