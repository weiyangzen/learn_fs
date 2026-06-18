# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wq.h

## Purpose
Declares the original HiNIC work-queue data structures and public APIs used by command queues, SQ/RQ queue-pair setup, Tx, and Rx. It is the driver-internal interface for allocating queue memory and producing or consuming hardware WQEs.

## Important APIs And Types
`struct hinic_wq` describes a single hardware work queue: backing block location inside a WQ set, WQEBB and page sizing, DMA block address, page-address arrays, shadow WQE storage, ring atomics, and index mask. `struct hinic_wqs` owns a pool of WQ blocks over one or more coherent pages, with page-address arrays and a semaphore-protected free-block ring. `struct hinic_cmdq_pages` is the command-queue-specific page container. Public functions cover WQS lifecycle, individual WQ lifecycle, command-queue WQS allocation, WQE reservation/return/read/write, and direct reads by consumer index.

## Control Flow And State
The header does not implement behavior, but it exposes the state machine used by `hinic_hw_wq.c`: `prod_idx` reserves WQEBBs for new WQEs, `cons_idx` releases completed WQEs, `delta` tracks available WQEBBs, and `mask` implements power-of-two ring wrapping. `shadow_wqe` and `shadow_idx` persist temporary copies of WQEs that cannot be represented as a single contiguous DMA-memory span.

## Dependencies And Integration Points
It includes Linux types, semaphores, atomics, `hinic_hw_if.h`, and `hinic_hw_wqe.h`. Higher layers use `struct hinic_hw_wqe` unions from `hinic_hw_wqe.h` while queue-pair code maps `hinic_wq` addresses into firmware queue contexts. Rx and Tx code consume this API through `hinic_hw_qp` wrappers.

## Risks And Test Signals
The exposed fields are tightly coupled to queue implementation; callers that manipulate atomics or address arrays directly can break ring invariants. API tests should check allocation failure unwinding, power-of-two validation, WQE wraparound, and queue depths at boundary values. Integration signals are successful interface open/close, no DMA-debug complaints, and stable Tx/Rx under ring pressure.
