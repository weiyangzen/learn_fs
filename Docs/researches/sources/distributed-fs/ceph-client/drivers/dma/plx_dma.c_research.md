# sources/distributed-fs/ceph-client/drivers/dma/plx_dma.c

## Purpose
`plx_dma.c` is a dmaengine memcpy provider for PLX/Microsemi ExpressLane PEX PCIe switch DMA hardware. It exposes one DMA channel backed by a coherent off-chip descriptor ring.

## Important APIs, Types, and Functions
- `struct plx_dma_hw_std_desc` is the hardware descriptor containing size/flags and 48-bit source/destination addresses split into low/high fields.
- `struct plx_dma_desc` wraps one dmaengine descriptor, points at its hardware ring entry, and stores original transfer size for residue/result calculation.
- `struct plx_dma_dev` owns the dmaengine device/channel, RCU-protected PCI device pointer, BAR mapping, completion tasklet, ring lock, active flag, head/tail indices, coherent hardware ring, and software descriptor ring.
- `plx_dma_prep_memcpy()` reserves a ring slot under lock, fills hardware address/size fields, and returns with the ring lock held for `tx_submit()`.
- `plx_dma_tx_submit()` assigns a cookie, uses a write barrier, sets the hardware valid bit, and releases the lock.
- `plx_dma_issue_pending()` starts the hardware ring after a barrier.
- `plx_dma_process_desc()` consumes completed write-back descriptors, computes residue/result, completes cookies, unmaps, and invokes result callbacks.
- `plx_dma_stop()`/`__plx_dma_stop()` gracefully pause and clear ring registers; `plx_dma_abort_desc()` reports queued work as aborted.

## Control Flow
PCI probe enables the device, negotiates 48-bit then 32-bit DMA mask, maps BAR 0, allocates an IRQ vector, sets bus mastering, and creates/registers the dmaengine device. Channel resource allocation allocates the coherent 2048-entry hardware ring, allocates matching software descriptors, programs ring base/count/prefetch registers, resets control, and marks the ring active. Prepare reserves a circular-buffer slot if the ring is active, space exists, and length fits the descriptor size mask. Submit sets the valid bit after descriptor writes are visible. Issue writes the start control value. Interrupt handling checks descriptor-done status and schedules a tasklet, which drains completed descriptors until the tail reaches a still-valid entry. Free/remove paths mark the ring inactive, stop hardware, synchronize IRQ/tasklet, abort remaining descriptors, and free rings.

## State and Persistence
The driver has only volatile ring state: `head`, `tail`, `ring_active`, hardware descriptor write-back flags, software descriptors, and an RCU PCI pointer used to prevent MMIO after removal. No persistent storage exists. Hardware state is the descriptor ring base/count/next registers, control registers, prefetch limit, and interrupt status/control.

## Dependencies and Integration Points
The driver integrates with PCI matching for vendor PLX device `0x87D0` with system-other class, dmaengine memcpy APIs, coherent DMA allocation, PCI IRQ vectors, RCU for removal synchronization, tasklets, and result-aware dmaengine callbacks. It uses `DMAENGINE_ALIGN_1_BYTE`.

## Risks and Edge Cases
- `plx_dma_prep_memcpy()` intentionally returns with `ring_lock` held and relies on `tx_submit()` to release it; any dmaengine API misuse that drops the descriptor without submitting would deadlock later users.
- Ring size is a power-of-two 2048 entries, and `CIRC_SPACE()` protects against full-ring overwrite, but no dynamic expansion exists.
- Completion depends on hardware clearing `PLX_DESC_FLAG_VALID` and writing result bits; malformed write-back can misclassify failures.
- Remove/free paths mix tasklet killing, IRQ synchronization, RCU pointer clearing, and abort completion; ordering is critical to avoid MMIO after device removal.
- Length is limited by `PLX_DESC_SIZE_MASK`, and addresses rely on the negotiated DMA mask fitting descriptor high fields.

## Test Signals
Test with PCI probe/remove, DMA mask fallback, dmatest memcpy with 1-byte alignment and max-size boundaries, ring-full prepare failures, interrupt-driven completion, read/write failure write-back bits, resource-free aborts, and hot-remove/unregister races.
