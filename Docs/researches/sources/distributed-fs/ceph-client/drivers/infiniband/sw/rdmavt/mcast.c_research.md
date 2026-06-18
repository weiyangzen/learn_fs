<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.c

## Purpose

Implements rdmavt multicast group tracking and QP attach/detach operations.

## Important APIs, Types, And Functions

Public functions are `rvt_driver_mcast_init()`, `rvt_mcast_find()`, `rvt_attach_mcast()`, `rvt_detach_mcast()`, and `rvt_mcast_tree_empty()`. Internal helpers allocate/free multicast groups and QP attachments and insert into the rb tree through `rvt_mcast_add()`.

## Control Flow

Multicast groups are keyed by MGID in an rb tree per port, with a required matching MLID. Attach rejects QP0/QP1 and RESET QPs, allocates a candidate group and QP link outside locks, then inserts or attaches under the port lock. Duplicate QP attach is treated as success. Detach finds the MGID/MLID, removes the QP link with RCU list deletion, removes the group if it was the last attachment, waits for readers through `refcount`/waitqueue, then frees structures and decrements global group count.

## State And Persistence Behavior

Per-port multicast state lives in `ibp->mcast_tree`, each `struct rvt_mcast` has a QP list, attach count, refcount, and waitqueue. Device state tracks allocated group count under `n_mcast_grps_lock`. QP refs are held for each attachment.

## Dependencies And Integration Points

Depends on rdmavt QP reference helpers, RDMA multicast attach/detach verbs, rb trees, RCU lists, waitqueues, and per-port locks.

## Risks And Edge Cases

MGID can have only one MLID; conflicting MLID returns `-EINVAL`. Readers using `rvt_mcast_find()` must decrement the reference and wake waiters as expected by broader rdmavt code. Detach waits for refcounts, so missing wakeups can hang teardown. Duplicate attach succeeds without adding state.

## Test Signals

Test attach/detach for valid QPs, duplicate attach, invalid QP0/QP1/RESET QP, max group and max QP attach limits, MGID/MLID conflict, tree-empty reporting, concurrent find/detach readers, and last-QP group deletion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.c -->
