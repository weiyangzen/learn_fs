# sources/distributed-fs/ceph-client/include/linux/io_uring_types.h

Purpose: This header defines the main internal io_uring data structures shared across core implementation units: task state, rings, context, submission state, request flags, request objects, and completion overflow records.

Important APIs, types, and functions: Key types include `io_uring_task`, `io_rings`, `io_ring_ctx`, `io_submit_state`, `io_alloc_cache`, `io_file_table`, `io_hash_table`, `io_mapped_region`, `io_restriction`, `io_tw_state`, `io_kiocb`, `io_cqe`, and `io_overflow_cqe`. It defines issue flags (`IO_URING_F_*`), context flags (`IO_RING_F_*`), request flag bit positions, and bitwise `io_req_flags_t` values.

Control flow: The structure layout separates hot submission, completion, task-work, timeout, and cleanup cachelines. User and kernel share `io_rings` through mmap with documented ownership of SQ/CQ heads, tails, flags, drops, and overflow counters. Requests carry opcode, fixed/provided buffer state, CQE data, context/task links, poll/task-work nodes, async data, credentials, and workqueue state through their lifecycle.

State and persistence: Ring context state persists for the life of an io_uring instance and owns resource tables, wait queues, xarrays, mmap regions, restrictions, personalities, and cleanup work. Per-task state tracks registered rings and inflight counters. Requests persist until completion, cancellation, or cache recycling.

Dependencies and integration points: Depends on block, task_work, bitmaps, llist, xarray, UAPI ring layouts, optional futex and network busy-poll support, BPF filter hooks, and io-wq.

Risks: These layouts are concurrency-sensitive and cacheline-sensitive. Ring head/tail ownership and memory barriers are critical. Request flag space is bounded by `__REQ_F_LAST_BIT`. RCU, xarray, waitqueue, and lock nesting mistakes can lead to UAF, lost completions, or stuck cancellation.

Test signals: Stress SQ/CQ mmap ownership, overflow accounting, cancellation, linked requests, poll and IOPOLL, buffer selection, registered file/buffer tables, restrictions and BPF filters, resize-vs-mmap locking, task exit cleanup, and optional futex/NAPI paths.
