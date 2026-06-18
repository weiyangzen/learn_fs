# sources/distributed-fs/ceph-client/drivers/dma/hisi_dma.c

## Purpose
`hisi_dma.c` is the PCI dmaengine driver for HiSilicon Kunpeng HIP08/HIP09 DMA endpoints. It exposes memory-to-memory copy channels backed by per-channel submission/completion queues and MSI vectors.

## Important APIs, Types, And Functions
Core objects are `hisi_dma_dev`, `hisi_dma_chan`, `hisi_dma_desc`, `hisi_dma_sqe`, and `hisi_dma_cqe`. Revision helpers choose queue base, MSI count, channel count, and register layout. Dmaengine hooks are initialized by `hisi_dma_init_dma_dev()`, with `hisi_dma_prep_dma_memcpy()`, `hisi_dma_issue_pending()`, `hisi_dma_tx_status()`, `hisi_dma_terminate_all()`, and `hisi_dma_synchronize()`.

## Control Flow
Probe enables the PCI function, maps BAR 2, sets a 64-bit DMA mask, allocates MSI vectors, allocates coherent SQ/CQ rings, requests one IRQ per channel, initializes hardware queues, registers cleanup, registers the dmaengine device, and creates debugfs. Issue-pending starts one active descriptor by copying an SQE and updating SQ tail; IRQ advances CQ head, completes successful descriptors, and starts the next descriptor.

## State And Persistence Behavior
State is in coherent SQ/CQ rings, queue head/tail indices, current descriptor pointers, queue control registers, and revision-specific debugfs/register state. Reset pauses, disables, masks, polls FSM state, resets queue pointers, and optionally re-enables.

## Dependencies And Integration Points
It depends on PCI/MSI, `virt-dma`, coherent DMA memory, relaxed MMIO, `iopoll`, debugfs, and Huawei PCI ID `0xa122`.

## Risks And Test Signals
HIP08/HIP09 layout detection is critical. Failed CQ status logs an error without completing an error callback, and the driver keeps only one active descriptor per channel. Test with HIP08/HIP09 probe, MSI allocation, `dmatest`, CQ/SQ pointer movement, debugfs reads, and queue reset timeout absence.
