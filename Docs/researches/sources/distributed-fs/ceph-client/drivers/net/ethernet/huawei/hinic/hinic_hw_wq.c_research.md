# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wq.c

## Purpose
Implements the original HiNIC work-queue allocator and WQE access layer. It owns DMA page allocation for normal SQ/RQ work queues and command queues, tracks blocks inside shared WQ-set pages, and provides producer/consumer helpers that hide ring wraparound and multi-page WQE layout.

## Important APIs And Functions
Public allocation APIs are `hinic_wqs_alloc()`, `hinic_wqs_free()`, `hinic_wq_allocate()`, `hinic_wq_free()`, `hinic_wqs_cmdq_alloc()`, and `hinic_wqs_cmdq_free()`. WQE access APIs are `hinic_get_wqe()`, `hinic_return_wqe()`, `hinic_put_wqe()`, `hinic_read_wqe()`, `hinic_read_wqe_direct()`, and `hinic_write_wqe()`. Internal helpers allocate coherent pages (`queue_alloc_page()`, `alloc_wq_pages()`), manage the free block ring (`wqs_next_block()`, `wqs_return_block()`), and copy wrapped WQEs through shadow buffers (`copy_wqe_to_shadow()`, `copy_wqe_from_shadow()`).

## Control Flow And State
`hinic_wqs_alloc()` aligns the requested queue count to four blocks per page, allocates DMA pages plus VM shadow arrays, initializes the free-block ring, and exposes blocks to `hinic_wq_allocate()`. Each `hinic_wq` stores DMA block address, shadow page addresses, queue depth, WQEBB size, page sizing shifts, and atomics for `prod_idx`, `cons_idx`, and free-space `delta`. `hinic_get_wqe()` reserves WQEBBs by subtracting `delta`, advances `prod_idx`, and returns either a direct WQE pointer or a per-page `shadow_wqe` when the WQE crosses a page/ring boundary. `hinic_write_wqe()` copies such shadow WQEs back to DMA memory. Consumers use `hinic_read_wqe()` and release space with `hinic_put_wqe()`.

## Dependencies And Integration Points
The file depends on PCI coherent DMA, vmalloc, atomics, semaphores, `hinic_hw_if`, `hinic_hw_wqe`, and command-queue constants. `hinic_hw_qp.c`, Rx, Tx, and command-queue code rely on its ring accounting and DMA address tables. Hardware consumes the big-endian page-address table written here.

## Risks And Test Signals
High-risk areas are off-by-one ring wrap logic, power-of-two assumptions, mismatched WQE size accounting, and shadow-copy handling when a WQE straddles page boundaries. Stress tests should exercise full rings, fragmented Tx WQEs, jumbo Rx, command queues, repeated interface up/down, DMA allocation failures, and concurrency between Tx submission and completion. KASAN/KCSAN and DMA debug are useful signals for stale shadow pointers, leaks, or invalid unmaps.
