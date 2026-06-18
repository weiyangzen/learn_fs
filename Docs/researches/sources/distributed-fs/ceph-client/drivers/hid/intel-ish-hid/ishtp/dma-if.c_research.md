# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/dma-if.c

## Purpose
`dma-if.c` manages the shared coherent DMA buffers used for ISHTP-over-DMA transfers. It allocates one host TX buffer and one host RX buffer, tracks 4 KiB TX slots with a bitmap-like byte array, and releases slots when firmware sends DMA transfer acknowledgments.

## Important APIs, types, and functions
`ishtp_cl_alloc_dma_buf()` allocates 1 MiB TX/RX coherent buffers and initializes `ishtp_dma_tx_map` and `ishtp_dma_tx_lock`. `ishtp_cl_free_dma_buf()` releases those buffers and the map. `ishtp_cl_get_dma_send_buf()` finds a contiguous run of free 4 KiB slots for a requested payload and marks them used. `ishtp_cl_release_dma_acked_mem()` validates an acknowledged address and length, then marks the corresponding slots free.

## Control flow and integration points
HBM enables DMA after client enumeration by calling `ishtp_cl_alloc_dma_buf()` and notifying firmware of the RX buffer address. Client transmit uses `ishtp_cl_get_dma_send_buf()` before writing a payload and sending a `DMA_XFER` HBM descriptor. HBM DMA ACK handling calls `ishtp_cl_release_dma_acked_mem()` after validating the acknowledged physical range. The RX buffer is consumed by `hbm.c` when firmware sends `DMA_XFER`.

## State and persistence behavior
DMA state is per `struct ishtp_device`: coherent TX/RX virtual addresses, physical addresses, sizes, slot count, TX slot map, and a spinlock. This is volatile kernel memory and is freed when clients are released or error paths tear down the ISHTP device.

## Dependencies
The file depends on Linux DMA coherent allocation, `DMA_SLOT_SIZE` from `client.h`, and ISHTP device fields from `ishtp-dev.h`. Correct operation also depends on HBM range validation and the client sender's DMA ACK state.

## Risks and edge cases
Allocation is partial-tolerant but does not unwind earlier allocations if a later allocation fails, leaving callers to operate with missing RX or map state. `ishtp_cl_release_dma_acked_mem()` accepts an 8-bit `size`, which can underrepresent larger messages if the protocol length is wider. Slot math must reject unaligned ACK addresses and out-of-range spans; any mismatch leaks TX slots or frees live ones. Cache coherency depends on the coherent allocation and explicit flushes elsewhere when firmware lacks snooping.

## Test signals
Exercise DMA allocation failure at each step, repeated allocate/free cycles, slot exhaustion and contiguous-slot fragmentation, ACKs with unaligned/out-of-range addresses, ACK length edge cases around 4 KiB boundaries, concurrent send/ACK under lockdep, DMA fallback to IPC, and suspend/remove teardown with live outstanding DMA messages.
