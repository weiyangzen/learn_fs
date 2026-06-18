# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_verbs.c

## Purpose

`rxe_verbs.c` registers RXE as an RDMA core provider and implements device, port, context, PD, AH, SRQ, QP, CQ, MR, send, receive, and registration verbs.

## Important APIs, Types, and Functions

It provides RDMA device ops for query/modify device and port, alloc/dealloc ucontext and PD, AH/SRQ/QP/CQ lifecycle, post_send/post_recv/post_srq_recv, CQ poll/peek/notify/resize, MR registration/rereg/dereg/allocation, mmap, multicast, counters, and `rxe_register_device()`.

## Control Flow

RDMA core calls `rxe_dev_ops`. Creation methods validate inputs, add objects to pools, initialize object-specific state, then finalize lookup visibility. Kernel post-send writes WQEs into SQ and schedules send processing; user QPs rely on mmap queues and scheduling. Receive posting writes RQ WQEs. Registration installs ops, associates the backing netdev, sets node identity, and calls `ib_register_device()`.

## State and Persistence Behavior

The file creates persistent RDMA objects in RXE pools and queue buffers, updates CQ notification state, WQE contents, MR access/state, parent sysfs attribute, QP source port, and queue occupancy.

## Dependencies and Integration Points

It integrates RDMA core/uverbs with RXE queues, pools, QP/SRQ/CQ/MR/MW/mcast helpers, ODP, hardware counters, UAPI structures, and the backing netdev.

## Risks and Edge Cases

ABI udata checks, unsupported opcode rejection, queue trust boundaries for user QPs, CQ destroy while associated with WQs, MR deregistration with bound MWs, and object finalization ordering are key risks.

## Test Signals

Run libibverbs/RDMA core lifecycle coverage, post-send/recv for kernel and user QPs, CQ poll/notify/resize, MR registration including ODP, AH user provider compatibility, udata fault injection, parent sysfs read, and RC/UC/UD/GSI traffic.
