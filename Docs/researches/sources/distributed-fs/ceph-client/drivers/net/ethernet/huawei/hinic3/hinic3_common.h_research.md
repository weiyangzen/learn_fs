# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_common.h

## Purpose
Declares shared hinic3 utility types and helpers for aligned DMA memory, scatter-gather element programming, polling completion state, and command-buffer byte swapping.

## Important APIs And Types
`HINIC3_MIN_PAGE_SIZE` defines the 4 KiB minimum page size used by command queues and WQ logic. `struct hinic3_dma_addr_align` records original and aligned virtual/physical addresses plus allocation size. `enum hinic3_wait_return` defines polling callback outcomes: complete, waiting, or error. `struct hinic3_sge` is a little-endian SGE with high address, low address, length, and reserved dword. `hinic3_set_sge()` fills an SGE from a DMA address and little-endian length. Public prototypes cover aligned DMA allocation/free, timeout polling, and `hinic3_cmdq_buf_swab32()`.

## Control Flow And State
The inline `hinic3_set_sge()` is the only executable code here; it writes upper/lower DMA address halves with `cpu_to_le32()`, stores the provided length, and clears the reserved field. Other declarations describe utility state consumed by `hinic3_common.c` and command/queue modules.

## Dependencies And Integration Points
It includes `linux/device.h` for DMA types and device pointers. `hinic3_cmdq.h` embeds `struct hinic3_sge` in command WQEs, and many hinic3 command builders can use `hinic3_set_sge()` for firmware-visible descriptors.

## Risks And Test Signals
Risks include passing a CPU-endian length to `hinic3_set_sge()` despite its `__le32` parameter, changing SGE layout in a way that breaks firmware ABI, or using aligned DMA records without matching free. Signals include sparse endian warnings, static layout checks in command structures, successful command-queue detail responses, and DMA-debug clean teardown.
