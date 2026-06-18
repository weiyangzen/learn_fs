
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-iop32x.h

## Purpose
This header defines Intel IOP32x/IOP ADMA data structures shared by platform code and the ADMA DMAengine driver. It covers hardware ids, descriptor slot management, DMAengine embedding, and async transaction metadata.

## Important APIs And Types
Constants define descriptor slot size, threshold, paranoia checks, and hardware ids `DMA0_ID`, `DMA1_ID`, and `AAU_ID`. `struct iop_adma_device` wraps a platform device, hardware selector, descriptor pool DMA/CPU addresses, and embedded `dma_device`. `struct iop_adma_chan` tracks pending operations, spinlock, MMIO base, descriptor chain, parent device, embedded `dma_chan`, slot allocation lists, and IRQ tasklet. `struct iop_adma_desc_slot` represents software descriptors with list nodes, hardware descriptor pointer, transaction grouping, async_tx descriptor, and result pointers for XOR/CRC/PQ checks. `struct iop_adma_platform_data` supplies hardware id, capabilities, and descriptor pool size.

## Control Flow, State, And Persistence
The runtime model is descriptor-slot based: channels allocate slots from `all_slots`, chain operations, batch pending hardware submissions, and clean up from a tasklet after interrupts. The header stores no persistence; all state is in memory.

## Dependencies And Integration Points
It depends on Linux types, DMAengine, interrupts/tasklets, platform devices, lists, and async_tx consumers. Integration points are RAID/XOR/CRC/PQ acceleration and DMAengine clients on Intel IOP platforms.

## Risks And Test Signals
Risks include descriptor pool sizing, slot leaks, incorrect grouping for multi-slot transactions, races on `lock`, and misuse of hardware descriptor pointer macros. Test signals include memcpy/XOR/CRC/PQ DMAengine capability tests, interrupt cleanup, transaction dependency ordering, pool exhaustion, and DEBUG paranoia assertions.
