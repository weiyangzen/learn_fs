
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_wq.h

## Purpose
`hinic3_wq.h` defines generic hinic3 work queue structures and inline producer/consumer helpers used by SQ/RQ implementations.

## Important APIs, Types, And Functions
- `struct hinic3_sq_bufdesc` is the 16-byte SQ buffer descriptor used for additional SGEs.
- `struct hinic3_wq` stores queue pages, producer/consumer indices, queue depth/mask, and hardware WQ block address/table.
- `hinic3_wq_get_used()`, `hinic3_wq_free_wqebbs()`, `hinic3_wq_get_one_wqebb()`, `hinic3_wq_put_wqebbs()`, and `hinic3_wq_get_first_wqe_page_addr()` are hot-path helpers.
- `hinic3_wq_create()`, `hinic3_wq_destroy()`, `hinic3_wq_reset()`, `hinic3_wq_get_multi_wqebbs()`, and `hinic3_wq_is_0_level_cla()` are implemented in `hinic3_wq.c`.

## Control Flow
Producers call `hinic3_wq_get_one_wqebb()` or `hinic3_wq_get_multi_wqebbs()` to reserve descriptors and advance `prod_idx`. Completion paths call `hinic3_wq_put_wqebbs()` to advance `cons_idx`. Free space always subtracts one sentinel entry to avoid full/empty ambiguity.

## State And Persistence Behavior
The WQ object holds per-queue runtime state and coherent DMA memory pointers. Indices are 16-bit unmasked counters that naturally wrap; `idx_mask` maps them to ring slots.

## Dependencies And Integration Points
It includes `linux/io.h` and `hinic3_queue_common.h`, and it is included by NIC I/O, TX, and RX code.

## Risks And Edge Cases
- `hinic3_wq_free_wqebbs()` relies on unsigned 16-bit arithmetic and one unused entry; incorrect producer/consumer updates can report false free space.
- `hinic3_wq_get_one_wqebb()` performs no availability check.
- Hardware page address returned by `hinic3_wq_get_first_wqe_page_addr()` must match queue context expectations.

## Test Signals
Ring wraparound tests, descriptor reservation under near-full conditions, completion reclamation, and page-boundary multi-WQEBB reservations validate this header’s contract.
