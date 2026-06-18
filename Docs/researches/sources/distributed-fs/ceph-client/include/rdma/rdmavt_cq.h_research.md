# sources/distributed-fs/ceph-client/include/rdma/rdmavt_cq.h

Purpose: rdmavt completion queue structures and memory-ordering helpers for kernel and mmaped userspace CQ rings.

Important APIs/types/functions: `RVT_CQ_NONE`, `RDMA_READ_UAPI_ATOMIC`, `RDMA_WRITE_UAPI_ATOMIC`, `struct rvt_k_cq_wc`, `struct rvt_cq`, `ibcq_to_rvtcq`, and `rvt_cq_enter`.

Control flow: Completion producers call `rvt_cq_enter` to append an `ib_wc`, update queue state under lock, and handle notification/triggered/full conditions. Shared head/tail indices use acquire/release barriers for userspace mmap visibility.

State and persistence behavior: Runtime ring-buffer state. `rvt_cq` embeds the core `ib_cq`, work item, lock, notify flags, queue pointers, device pointer, CPU vector, and mmap info.

Dependencies and integration points: Depends on kthread/work support, uverbs CQ ABI, `ib_verbs.h`, and `rvt-abi.h`. Integrates with rdmavt QP completion generation and user/kernel polling.

Risks: Missing memory barriers can expose stale CQEs to userspace. Full queues must not overwrite unpolled completions. Notify arming races are common.

Test signals: CQE insertion, solicited notification, sentinel notify state, full queue behavior, mmaped userspace polling, completion-vector CPU behavior, and producer/consumer stress.
