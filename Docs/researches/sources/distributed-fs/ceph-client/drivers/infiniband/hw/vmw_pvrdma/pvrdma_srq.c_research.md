<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_srq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_srq.c

## Purpose

Implements PVRDMA shared receive queue verbs: create, query, modify, destroy, and local resource teardown.

## Important APIs, Types, And Functions

Public handlers are `pvrdma_create_srq()`, `pvrdma_query_srq()`, `pvrdma_modify_srq()`, and `pvrdma_destroy_srq()`. `pvrdma_free_srq()` clears the device table, waits for references, releases umem and page directories, and decrements counters.

## Control Flow

Create is userspace-only and supports only `IB_SRQT_BASIC`. It validates WR/SGE limits, reserves an SRQ counter, copies user command data, pins the user buffer, builds a page directory from umem, posts `PVRDMA_CMD_CREATE_SRQ`, stores the returned handle in `dev->srq_tbl`, and copies the SRQN back to userspace. Query posts `PVRDMA_CMD_QUERY_SRQ` and returns limit/max fields. Modify supports only `IB_SRQ_LIMIT`. Destroy posts backend destroy and then frees local state regardless of command result.

## State And Persistence Behavior

SRQs hold pinned user memory, page directory, backend handle, lock, refcount, completion, WQE sizing, and the device table entry. There is no kernel-client SRQ support in this implementation.

## Dependencies And Integration Points

Depends on RDMA SRQ APIs, user ABI structs, page-directory helpers, command posting, PD handles, and async SRQ event dispatch from `pvrdma_main.c`.

## Risks And Edge Cases

Create ignores the return value of `pvrdma_page_dir_insert_umem()`, so a failed insertion would be discovered only later by backend behavior. Table clearing uses raw handle indexing while insertion uses modulo. Destroy returns 0 even when backend destroy fails. Only limit modification is accepted, so resize-like semantics are unsupported.

## Test Signals

Test no-udata rejection, unsupported SRQ type, max WR/SGE bounds, umem/page-dir failures, create/destroy command failures, query responses, limit modification, userspace copyback failure cleanup, and SRQ async event refcounting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_srq.c -->
