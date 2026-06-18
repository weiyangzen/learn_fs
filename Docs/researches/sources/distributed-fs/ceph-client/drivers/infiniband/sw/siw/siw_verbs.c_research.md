# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_verbs.c

Purpose: Implements the RDMA core verbs surface for SoftiWARP: userspace context allocation, device/port/GID queries, PD/QP/CQ/SRQ lifecycle, post-send/receive, CQ poll/notify, mmap of user queues, MR registration/deregistration/mapping, and asynchronous event dispatch.

Important APIs/types/functions: `siw_alloc_ucontext()`, `siw_query_device()`, `siw_query_port()`, and `siw_query_gid()` expose device capabilities and identity. `siw_create_qp()`, `siw_verbs_modify_qp()`, `siw_destroy_qp()`, `siw_post_send()`, and `siw_post_receive()` implement QP verbs. `siw_create_cq()`, `siw_poll_cq()`, and `siw_req_notify_cq()` implement CQ operations. MR functions include `siw_reg_user_mr()`, `siw_alloc_mr()`, `siw_map_mr_sg()`, `siw_get_dma_mr()`, and `siw_dereg_mr()`. SRQ functions cover create/modify/query/destroy/post. `siw_mmap()` maps vmalloc-backed queues via RDMA mmap entries.

Control flow: Userspace creates context, then PD/CQ/QP/SRQ/MR objects. User QPs/CQs/SRQs allocate `vmalloc_user` rings and return mmap offsets through SIW ABI responses. Kernel clients post WR lists directly; user-mapped queues are consumed from shared rings. Posting SEND validates state and queue space, converts IB WRs to SIW SQEs, marks them valid with barriers, and starts TX. Receive posting does the same for RQ/SRQ entries.

State and persistence behavior: Object counts are device atomics. QP/CQ/SRQ rings may be mmaped and synchronized through flags/barriers. MR state persists only as registered kernel objects and pinned memory until deregistration. Destroy paths remove mmap entries, suspend QPs, force error state, and wait for QP kref completion.

Dependencies/integration: Registered by `siw_main.c` in `ib_device_ops`; delegates state transitions to `siw_qp.c`, memory operations to `siw_mem.c`, completions to `siw_cq.c`, and events to RDMA core callbacks.

Risks: Uverbs ABI size checks, mmap entry lifetime, immediate post errors versus queued work, QP destroy with active callbacks, and user-mapped ring trust boundaries are high-risk. Some operations are intentionally unsupported and must return stable errors. MR deregistration while active relies on krefs and RCU.

Test signals: libibverbs smoke tests, rdma-core SIW tests, create/destroy loops, mmaped queues, kernel-client post paths, CQ notify missed events, MR reg/fast-reg/map/dereg, SRQ limit events, QP modify state matrix, drain SQ/RQ in error state, and fuzz invalid WR opcodes/flags/sge counts.
