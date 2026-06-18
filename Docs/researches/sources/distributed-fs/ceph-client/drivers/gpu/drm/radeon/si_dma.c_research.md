# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dma.c

## Purpose

`si_dma.c` implements Southern Islands DMA-ring helpers for lockup detection, VM page-table updates, VM TLB flushes through the DMA engine, and buffer-object page copies. It complements the broader SI ASIC setup in `si.c` and is registered as the SI DMA ring/copy backend through Radeon ASIC tables.

## Important APIs, Types, and Functions

- `si_dma_is_lockup(struct radeon_device *rdev, struct radeon_ring *ring)` maps DMA ring index to `RADEON_RESET_DMA` or `RADEON_RESET_DMA1`, checks `si_gpu_check_soft_reset`, updates lockup tracking when idle, and delegates suspected hangs to `radeon_ring_test_lockup`.
- `si_dma_vm_copy_pages(...)` emits SI `DMA_PACKET_COPY` packets that copy page-table entries from a GART source to a page-entry destination in chunks capped at `0xFFFF8` bytes.
- `si_dma_vm_write_pages(...)` emits `DMA_PACKET_WRITE` packets and writes PTE values inline, using `radeon_vm_map_gart` for system pages, raw `addr` for valid VRAM pages, or zero for invalid entries, then ORs in PTE flags.
- `si_dma_vm_set_pages(...)` emits `DMA_PTE_PDE_PACKET` packets for physically contiguous VRAM updates, carrying mask, value, and increment so the DMA engine generates PTE/PDE entries.
- `si_dma_vm_flush(...)` writes VM page table base registers through `DMA_PACKET_SRBM_WRITE`, flushes HDP, invalidates the selected VM context, and emits `DMA_PACKET_POLL_REG_MEM` to wait for invalidate completion.
- `si_copy_dma(...)` synchronizes a reservation object, locks the configured DMA ring, emits chunked `DMA_PACKET_COPY` packets for GPU-page movement, emits a fence, commits the ring, and returns the fence.

## Control Flow

VM page updates are chosen by the common Radeon VM layer based on flags and contiguity. `si_dma_vm_copy_pages` copies prebuilt PTEs; `si_dma_vm_write_pages` writes individual PTE values for system or sparse/non-contiguous mappings; `si_dma_vm_set_pages` uses the hardware PTE/PDE generation packet for contiguous mappings. All three append packet dwords to a caller-supplied IB and advance `ib->length_dw`.

`si_dma_vm_flush` is a ring-emission path rather than an IB builder. It updates the per-VM page table base, flushes HDP cache, requests invalidation for `vm_id`, then polls `VM_INVALIDATE_REQUEST` with mask `1 << vm_id` until the bit clears.

`si_copy_dma` computes total bytes from GPU pages, reserves enough ring space for all copy packets plus sync/fence overhead, syncs against the supplied reservation object, emits copy packets capped at `0xFFFFF` bytes, emits a fence, commits the ring, and frees sync state. Lock or fence errors undo/unwind the ring and return `ERR_PTR(r)`.

## State and Persistence Behavior

The file mutates command buffers (`radeon_ib::ptr` and `length_dw`) and DMA rings (`radeon_ring` write pointer through `radeon_ring_write`). It updates persistent GPU VM context base registers and invalidation state through ring packets, but does not directly write MMIO except through emitted commands. `si_copy_dma` creates a fence whose lifetime is owned by the caller and synchronization subsystem.

Lockup detection updates per-ring lockup bookkeeping when the DMA engine is not reported busy. Page-table update helpers rely on caller-provided `pe`, `addr`, `src`, `count`, `incr`, and `flags` and do not store state between calls.

## Dependencies and Integration Points

- Includes `radeon.h`, `radeon_asic.h`, `radeon_trace.h`, `si.h`, and `sid.h`.
- Depends on SI DMA packet macros and register definitions from `sid.h`, PTE flags from `radeon.h`, and reset status from `si_gpu_check_soft_reset`.
- Integrated through `radeon_asic.c` as SI DMA ring functions, VM update callbacks, and copy callbacks.
- Uses common Radeon ring, fence, sync, reservation, and VM helpers such as `radeon_ring_lock`, `radeon_ring_write`, `radeon_sync_resv`, `radeon_sync_rings`, `radeon_fence_emit`, and `radeon_vm_map_gart`.

## Risks and Edge Cases

- Chunk-size limits are hardware encoded. Off-by-one mistakes can generate invalid packet lengths; this file caps copy at `0xFFFF8` for PTE copies and `0xFFFFF` for BO copies, and write/set paths cap dwords at `0xFFFFE`.
- `si_dma_vm_write_pages` stores 64-bit `pe` and `value` into `u32` IB slots by implicit truncation for the low dword; this matches the packet format but relies on readers understanding the following upper dword writes.
- `si_dma_vm_flush` uses `1 << vm_id`; SI has 16 VM contexts, so callers must keep `vm_id < 16` to avoid invalid shifts and hardware requests.
- The helpers assume the caller reserved enough IB space. They do not check `ib->ptr` bounds.
- `si_copy_dma` calculates ring space as `num_loops * 5 + 11`; changes to sync/fence emission requirements or packet format must keep this reservation accurate.
- Lockup detection depends on `si_gpu_check_soft_reset`; false negatives there will mark the DMA ring healthy and only update lockup tracking.

## Test Signals

- VM tests should cover copy/write/set page update paths for system, valid VRAM, invalid, contiguous, and non-contiguous mappings, including counts crossing chunk caps.
- DMA VM flush tests should validate context base selection for VM IDs below and above 7, HDP flush emission, invalidate request emission, and poll packet fields.
- BO move tests should cover `si_copy_dma` with zero, one, and multi-chunk transfers, reservation synchronization, fence emission failure, and ring lock failure.
- Lockup tests should simulate reset masks for DMA0 and DMA1 and verify idle rings call `radeon_ring_lockup_update` while busy rings call `radeon_ring_test_lockup`.
