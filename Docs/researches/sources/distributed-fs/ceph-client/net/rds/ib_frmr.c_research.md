# sources/distributed-fs/ceph-client/net/rds/ib_frmr.c

## Purpose
`ib_frmr.c` implements RDS/IB fast memory registration (FRMR/FRWR) allocation, registration, invalidation, completion handling, and pool return behavior for RDMA memory regions.

## Important APIs, Types, And Functions
Externally used functions are `rds_ib_mr_cqe_handler()`, `rds_ib_unreg_frmr()`, `rds_ib_reg_frmr()`, and `rds_ib_free_frmr_list()`. Key helpers are `rds_transition_frwr_state()`, `rds_ib_alloc_frmr()`, `rds_ib_free_frmr()`, `rds_ib_post_reg_frmr()`, `rds_ib_map_frmr()`, and `rds_ib_post_inv()`. State is stored in `struct rds_ib_mr` and its `struct rds_ib_frmr` union member.

## Control Flow
Registration chooses the 8K or 1M MR pool based on page count, tries to reuse a clean MR, otherwise allocates a new `rds_ib_mr` and `ib_mr`. Mapping tears down old state, stores the scatterlist, DMA maps it, validates page-boundary constraints and pool page limits, posts an `IB_WR_REG_MR`, waits for registration completion, and returns the rkey. Work-request availability is throttled with `i_fastreg_wrs`; in-use registrations increment `i_fastreg_inuse_count`.

Invalidation posts `IB_WR_LOCAL_INV` for in-use MRs and waits for state to become free or stale before DMA unmap/teardown. Completion handling transitions state on errors, drops the RDS connection if needed, wakes registration/invalidation waiters, and returns a fastreg WR credit. Unregistration first posts invalidations for all mapped MRs, then tears down DMA mappings and either frees MRs up to a goal or leaves still-in-use entries. Freeing returns MRs to pool free/drop llist and queues pool flush work when pinned/dirty thresholds are exceeded.

## State And Persistence
FRMR state includes `fr_state`, registration/invalidation booleans and waitqueues, WR storage, DMA page count, sg byte length, rkey-generating remap count, associated connection/device/pool, scatterlist DMA mapping, and pool dirty/free/drop lists. State is memory-only and tied to MR pool/device/connection lifetime.

## Dependencies And Integration Points
The file integrates with IB verbs (`ib_alloc_mr`, `ib_map_mr_sg_zbva`, `ib_post_send`, `ib_update_fast_reg_key`, `ib_dereg_mr`, DMA mapping), RDS/IB send CQ MR completion dispatch in `ib_cm.c`, MR pool helpers in other IB RDMA files, and connection teardown wait conditions.

## Risks
The busy-wait loops around `i_fastreg_wrs` can spin if credits are never returned. Registration and invalidation deliberately wait for completions to avoid remote access and DMA teardown races. State transitions must decrement `i_fastreg_inuse_count` exactly once when leaving INUSE. Error completions mark MRs stale and may reconnect. Scatterlist boundary validation is strict; incorrect handling can expose invalid remote access or DMA bugs.

## Test Signals
Coverage should include MR reuse/allocation, 8K versus 1M pool selection, DMA map failure, page-boundary rejection, max-page rejection, registration post failure, registration completion wakeup, invalidation post failure, stale-state cleanup, CQ error reconnect, pool dirty/free threshold flush queuing, and teardown during connection shutdown.
