# sources/distributed-fs/ceph-client/drivers/dma/idma64.c

## Purpose
`idma64.c` is the platform/dmaengine driver for Intel integrated DMA 64-bit controllers, commonly LPSS-attached. It provides private slave SG channels using linked-list hardware descriptors.

## Important APIs, Types, And Functions
It uses `idma64`, `idma64_chan`, `idma64_desc`, `idma64_hw_desc`, and `idma64_chip`. Core helpers power the controller, initialize/start/stop channels, handle IRQs, allocate/free descriptors, fill LLIs, compute residue, and implement pause/resume/terminate.

## Control Flow
Platform probe gets IRQ/MMIO, coerces the parent to a 64-bit DMA mask, and calls core probe. The core powers off hardware, requests the shared IRQ, creates two virt-dma channels, and registers a private slave dmaengine device. SG preparation allocates one DMA-pool LLI per SG entry, links LLIs, and enables interrupt on the last block. Issue-pending starts the active descriptor by programming LLP and enabling the channel.

## State And Persistence Behavior
State includes virt-dma queues, active descriptor, DMA-pool LLIs, copied slave config, controller enable bits, and interrupt masks. Suspend powers off; resume powers on, and channel init re-enables the controller because context is lost.

## Dependencies And Integration Points
It depends on platform devices named `LPSS_IDMA64_DRIVER_NAME`, dmaengine slave SG, `virt-dma`, DMA pools, 64-bit lo-hi MMIO, and peripheral dmaengine clients.

## Risks And Test Signals
Only two channels are supported. Burst values are converted to log2 encoding, residue depends on current LLP/CTL_HI, and terminate has bounded FIFO drain. Test bidirectional SG DMA, residue, pause/resume, terminate, suspend/resume, and shared IRQ filtering.
