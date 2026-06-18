# sources/distributed-fs/ceph-client/drivers/dma/hsu/hsu.c

## Purpose
`hsu.c` is the core dmaengine implementation for Intel High Speed UART DMA. It provides private slave SG channels for UART TX/RX using four hardware descriptor slots per channel and `virt-dma` queuing.

## Important APIs, Types, And Functions
Exports are `hsu_dma_probe()`, `hsu_dma_remove()`, `hsu_dma_get_status()`, and `hsu_dma_do_irq()`. Dmaengine methods include SG preparation, issue-pending, status/residue, config, pause/resume, terminate, and synchronize. `hsu_dma_chan_start()` programs burst size, minimum transfer size, descriptor address/length slots, and descriptor interrupt bits.

## Control Flow
Probe derives channel count from MMIO length and offset, creates one `virt_dma_chan` per channel, assigns even channels to TX and odd channels to RX, and registers the dmaengine device. IRQ glue read-clears status, distinguishes timeout-only events, and invokes descriptor/error handling. SG lists longer than four entries are run in batches.

## State And Persistence Behavior
State is runtime-only: active descriptor, SG array, active index, status, copied slave config, fixed direction, and MMIO channel registers. Stop clears channel and descriptor control.

## Dependencies And Integration Points
It depends on dmaengine slave SG, `virt-dma`, scatterlists, `hsu.h`, and public `linux/dma/hsu.h` bus glue.

## Risks And Test Signals
Risks include hardware errata around read-clear status and timeouts, residue accounting across batches, fixed channel direction, and 16-bit segment length. Test UART DMA TX/RX, SG lists over four entries, timeout paths, pause/resume, terminate, and residue reporting.
