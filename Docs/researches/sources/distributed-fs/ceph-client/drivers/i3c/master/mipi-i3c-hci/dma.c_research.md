# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dma.c

## Purpose

`dma.c` implements the HCI DMA/ring-header I/O backend. It allocates command/response rings and IBI status/data rings, maps transfer buffers with the DMA API, queues descriptors into ring memory, processes completion and IBI interrupts, supports abort/dequeue recovery, and provides suspend/resume hooks for the core.

## Important APIs, Types, and Functions

- `struct hci_rh_data` represents one ring header: MMIO regs, coherent command/response/status memory, mapped IBI data memory, ring sizes, pointers, source-xfer mapping, and operation completion.
- `struct hci_rings_data` owns the DMA-capable system device and all ring headers.
- `hci_dma_init()` discovers ring count, chooses the DMA device (PCI parent when present), allocates coherent rings and IBI buffers, maps IBI data, and initializes hardware rings.
- `hci_dma_queue_xfer()` maps transfer data, writes command descriptors and data buffer descriptors to ring entries, stores source xfer pointers, and advances enqueue pointers.
- `hci_dma_dequeue_xfer()` aborts a running ring, replaces pending descriptors with no-op internal-control descriptors, unmaps buffers, and restarts the ring.
- `hci_dma_xfer_done()` consumes response ring entries, validates TID, unmaps data, stores responses, completes waiters, and updates software dequeue pointers.
- `hci_dma_process_ibi()` assembles IBI payloads from status and chunk rings and queues generic IBI slots.
- `mipi_i3c_hci_dma` exports the backend vtable.

## Control Flow

Initialization disables any old state, allocates software ring structures, reads hardware descriptor sizes, allocates coherent command/response/status rings, allocates and maps the IBI data chunk ring, registers a devm cleanup action, then writes base addresses and setup registers. Transfer queueing maps each data buffer, checks ring space under `hci->lock`, writes v1 or v2 descriptors, writes block size/IOC and DMA address fields, records each source xfer by ring entry, and updates `RING_OPERATION1.CR_ENQ_PTR`.

IRQ handling loops over rings. IBI-ready status calls `hci_dma_process_ibi()`. Transfer completion or transfer error calls `hci_dma_xfer_done()`, which drains all hardware-dequeued responses until `done_ptr == CR_DEQ_PTR`. Ring-operation status completes abort waiters. IBI processing scans status descriptors until a `LAST_STATUS` segment is found, validates address consistency and payload length, copies possibly wrapped chunk data into a generic IBI slot, advances IBI dequeue and chunk pointers, and releases chunks to hardware.

## State and Persistence Behavior

Ring memory and source-xfer arrays persist for the device lifetime and are freed by `hci_dma_free()`. Ring runtime pointers (`done_ptr`, `ibi_chunk_ptr`, `xfer_space`) are reset on init/resume. Individual `hci_xfer` objects remember their ring number and entry until completion or dequeue clears them.

## Dependencies and Integration Points

The backend depends on the HCI core for locking, resume signaling, and command descriptor format. It uses DMA mapping helpers from the I3C core (`i3c_master_dma_map_single()`), generic IBI pools, Linux coherent DMA APIs, and PCI parent detection for correct IOMMU context.

## Risks and Edge Cases

Only ring 0 is used despite possible hardware support for more rings. Ring abort failure logs a critical warning because hardware might still write memory. IBI zero-copy is avoided; payloads are copied due to ring wrap and delayed recycle issues. Short read buffers with IOMMU mapping can need bounce buffering when length is not word-aligned. TID mismatch is logged but not otherwise recovered in completion processing.

## Test Signals

Exercise DMA probe on platform and PCI-backed devices, ring-size boundary failures, queue full (`-EBUSY`), descriptor contents for v1/v2, timeout abort/dequeue, response TID mismatch, transfer-error recovery, IBI payload wraparound, oversized/unknown-device IBI drops, suspend/resume ring reinitialization, and DMA unmap leak checks.
