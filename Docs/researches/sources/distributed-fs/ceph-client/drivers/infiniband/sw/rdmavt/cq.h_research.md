<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.h

## Purpose

Declares rdmavt completion-queue operation and lifecycle functions.

## Important APIs, Types, And Functions

Prototypes cover CQ create/destroy, notify, resize, poll, driver CQ init, and CQ exit.

## Control Flow

The header allows rdmavt core and drivers to install the CQ ops and manage the global completion workqueue lifecycle.

## State And Persistence Behavior

No state is defined here; the implementation manages `struct rvt_cq` and a global workqueue.

## Dependencies And Integration Points

Includes RDMA VT and rdmavt CQ public structures.

## Risks And Edge Cases

Signatures must remain aligned with RDMA core object-size and uverbs APIs.

## Test Signals

Compile tests catch mismatches; module init/exit tests should call init/exit exactly once around CQ use.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.h -->
