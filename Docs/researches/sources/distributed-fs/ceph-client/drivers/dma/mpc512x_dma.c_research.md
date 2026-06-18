<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mpc512x_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mpc512x_dma.c

## Purpose
DMAEngine driver for Freescale MPC512x and MPC8308 DMA controllers using eDMA-style transfer control descriptors. It supports memory-to-memory copies and limited peripheral slave SG.

## Important APIs, Types, And Functions
`mpc_dma_regs` and `mpc_dma_tcd` model the hardware register block and transfer descriptors. `mpc_dma` owns the DMAEngine device, channel array, register/TCD MMIO, IRQs, and saved error status. `mpc_dma_chan` keeps free/prepared/queued/active/completed lists plus peripheral configuration. `mpc_dma_desc` wraps a software descriptor and coherent TCD. Important functions include `mpc_dma_execute`, `mpc_dma_irq_process`, `mpc_dma_process_completed`, `mpc_dma_tx_submit`, resource allocation/free, memcpy/slave SG prep, `mpc_dma_device_config`, and terminate.

## Control Flow
Probe maps IRQs and MMIO, identifies MPC8308 versus MPC512x, requests one or two IRQs, initializes DMAEngine callbacks and channel lists, configures arbitration/error/interrupt registers, registers DMAEngine, and optionally registers OF xlate by channel id. Allocating channel resources allocates a coherent TCD array and software descriptors, populates the free list, and enables error interrupts. Memcpy prep chooses the largest aligned transfer size, fills one TCD, and puts it on the prepared list. Slave SG prep currently accepts only one SG element, validates peripheral config and alignment, fills TCD fields for peripheral flow or MPC8308 software start, and prepares it. Submit moves the descriptor to queued, starts execution immediately if idle, and assigns a cookie. Execution moves queued descriptors to active, chains mem-to-mem TCDs through scatter/gather, marks final interrupt, copies the first TCD into hardware, and starts by software request or external request. IRQ captures error state, clears per-channel interrupt/error bits, marks active descriptors as error on error IRQs, moves active to completed, and starts more queued descriptors. The tasklet logs detailed error reasons, invokes callbacks/dependencies, recycles completed descriptors, and updates completed cookies.

## State And Persistence
State includes coherent TCD pools per allocated channel, descriptor lists, peripheral FIFO addresses/burst widths, active error status, channel cookies, and DMA controller registers. No filesystem persistence exists.

## Dependencies And Integration Points
Depends on DMAEngine core, OF address/IRQ/DMA helpers, platform devices, big-endian MMIO accessors, coherent DMA memory, and compatible strings `fsl,mpc5121-dma` and `fsl,mpc8308-dma`. Slave clients configure peripheral addresses and maxburst through `dma_slave_config` and request channels by OF channel id.

## Risks And Edge Cases
Slave SG refuses `sg_len != 1`, matching the file header limitation. It calls `list_first_entry(&mchan->free, ...)` before checking whether the free list is empty, which can dereference an invalid list head under descriptor exhaustion. Terminate splices prepared/queued/active back to free after clearing requests but does not handle completed callbacks. `mpc_dma_issue_pending` is a no-op because submit starts hardware immediately, which may surprise clients expecting delayed issue semantics. Error status is global and only the first pending hardware error is preserved until the tasklet drains it.

## Test Signals
Use dmatest memcpy across alignments and lengths, peripheral slave single-SG transfers with invalid and valid bus widths/maxburst, descriptor exhaustion tests, MPC8308 dual-IRQ path, error injection for DMAES decoding, terminate while active, and OF channel id lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mpc512x_dma.c -->
