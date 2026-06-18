<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.h

## Purpose

Declares rdmavt protection-domain allocation and deallocation handlers.

## Important APIs, Types, And Functions

Prototypes cover `rvt_alloc_pd()` and `rvt_dealloc_pd()`.

## Control Flow

The functions are installed in rdmavt RDMA device ops and called by RDMA core during PD lifecycle.

## State And Persistence Behavior

No state is declared here; count and PD flags are managed in `pd.c`.

## Dependencies And Integration Points

Includes RDMA VT public definitions.

## Risks And Edge Cases

Signatures must match RDMA core PD op expectations.

## Test Signals

Compile coverage and PD lifecycle tests validate the contract.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.h -->
