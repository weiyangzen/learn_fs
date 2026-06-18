<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.c

## Purpose

Implements rdmavt protection-domain allocation and deallocation accounting.

## Important APIs, Types, And Functions

`rvt_alloc_pd()` increments the device PD count if below `max_pd` and records whether the PD belongs to userspace. `rvt_dealloc_pd()` decrements the count.

## Control Flow

Allocation is called by RDMA core after object allocation. It locks `n_pds_lock`, checks `n_pds_allocated` against `dparms.props.max_pd`, increments, unlocks, and sets `pd->user = !!udata`. Deallocation decrements under the same lock and returns success.

## State And Persistence Behavior

Persistent state is the per-device allocated PD count and each `struct rvt_pd`'s `user` flag. No hardware state is programmed.

## Dependencies And Integration Points

Depends on RDMA VT public structs. MR logic uses `pd->user` to reject user DMA MRs and lkey zero access.

## Risks And Edge Cases

PD count underflow is possible if deallocation is called without a matching successful allocation; RDMA core lifecycle should prevent that. The implementation does not track per-PD resources beyond the user flag.

## Test Signals

Test max-PD exhaustion, user versus kernel PD flag, balanced count increment/decrement, and MR behavior differences for user/kernel PDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.c -->
