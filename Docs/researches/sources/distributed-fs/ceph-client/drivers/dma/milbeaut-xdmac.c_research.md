<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/milbeaut-xdmac.c -->
# sources/distributed-fs/ceph-client/drivers/dma/milbeaut-xdmac.c

## Purpose
DMAEngine memcpy driver for Socionext Milbeaut M10V XDMAC channels.

## Important APIs, Types, And Functions
`milbeaut_xdmac_device` owns the DMA device, global register base, and flexible channel array. `milbeaut_xdmac_chan` stores a virt-dma channel, active descriptor, and channel register base. `milbeaut_xdmac_desc` carries length, source, and destination. `milbeaut_chan_start` programs byte count, source/destination addresses, default burst settings, and enables transfer/end interrupts. `milbeaut_xdmac_interrupt` acknowledges completion and starts the next queued descriptor. `enable_xdmac` and `disable_xdmac` gate the global engine bit.

## Control Flow
Probe counts IRQs, maps MMIO, initializes DMA_MEMCPY callbacks, creates one channel per IRQ, globally enables XDMAC, registers DMAEngine, and registers OF simple xlate. Prep allocates one descriptor for a memcpy request. Issue-pending moves the next vchan descriptor to `mc->md` and starts hardware if idle. IRQ clears status, completes the active descriptor, and starts the next one. Terminate clears channel enable, terminates the active vdesc, collects queued descriptors, and frees them. Remove terminates all channels, unregisters OF/DMAEngine, and disables XDMAC.

## State And Persistence
State consists of vchan queues, one active descriptor per channel, channel registers, and the global XDMAC enable register. There is no persistent storage.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, platform IRQ/MMIO resources, OF simple DMA xlate, and compatible `socionext,milbeaut-m10v-xdmac`. It advertises `DMA_MEMCPY` with 1/2/4/8-byte bus width capabilities.

## Risks And Edge Cases
The driver uses `md->len - 1` without guarding zero-length requests. It reports status through plain `dma_cookie_status`, so there is no residue calculation. It does not set an explicit DMA mask. Termination assumes clearing `CE` halts the channel promptly. Remove has the same terminate-failure resource-leak warning pattern as HDMAC.

## Test Signals
Use dmatest memcpy per channel, queue multiple descriptors to verify IRQ-driven chaining, terminate active copies, remove with idle and active channels, and check OF channel allocation through simple xlate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/milbeaut-xdmac.c -->
