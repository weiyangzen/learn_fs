# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_common.c

## Purpose
Provides small shared hinic3 utility implementations: aligned coherent DMA allocation, matching free, polling with timeout through a callback, and command-buffer dword byte swapping.

## Important APIs And Functions
`hinic3_dma_zalloc_coherent_align()` allocates coherent DMA memory with a requested alignment, retrying with `size + align` if the first allocation is not aligned and recording both original and aligned addresses. `hinic3_dma_free_coherent_align()` releases the original allocation recorded in `struct hinic3_dma_addr_align`. `hinic3_wait_for_timeout()` wraps `read_poll_timeout()` around a caller-provided `wait_cpl_handler`. `hinic3_cmdq_buf_swab32()` calls `swab32_array()` for command-queue buffers.

## Control Flow And State
The aligned allocation path first attempts exact-size allocation, checks `ALIGN(paddr, align)`, and if necessary frees and reallocates a larger buffer so the aligned virtual address can be derived by offsetting from the original virtual address. The polling helper treats `HINIC3_WAIT_PROCESS_WAITING` as continue, returns `-EIO` for `HINIC3_WAIT_PROCESS_ERR`, and otherwise returns the polling timeout result. The byte-swap helper mutates a buffer in place.

## Dependencies And Integration Points
It depends on Linux DMA mapping, delay/iopoll helpers, and `hinic3_common.h`. It is a support library for modules that need aligned DMA blocks, polling waits, or command-queue buffer endian transformation.

## Risks And Test Signals
Risks include invalid `align` assumptions, pointer arithmetic on `void *` relying on compiler extension, freeing only through the recorded original allocation, and byte-swapping buffers whose length is not a multiple of 32 bits. Test signals include DMA-debug clean runs, allocations with already-aligned and misaligned DMA addresses, timeout and error polling paths, and command buffers verified before/after swap.
