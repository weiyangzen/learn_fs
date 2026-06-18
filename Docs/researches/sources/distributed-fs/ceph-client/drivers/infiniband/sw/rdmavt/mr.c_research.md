<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.c

## Purpose

Implements rdmavt software memory-region management: lkey table initialization, DMA/user/fast-reg MR allocation, MR deregistration with QP cleanup, scatterlist mapping, fast registration, rkey invalidation, and local/remote key validation.

## Important APIs, Types, And Functions

Public APIs include `rvt_driver_mr_init()`, `rvt_mr_exit()`, `rvt_get_dma_mr()`, `rvt_reg_user_mr()`, `rvt_dereg_mr()`, `rvt_alloc_mr()`, `rvt_map_mr_sg()`, `rvt_fast_reg_mr()`, `rvt_invalidate_rkey()`, `rvt_lkey_ok()`, and `rvt_rkey_ok()`. Core helpers include `rvt_init_mregion()`, `rvt_alloc_lkey()`, `rvt_free_lkey()`, `rvt_check_refs()`, and SGE/MR reference utilities.

## Control Flow

Initialization allocates an RCU-protected lkey table sized from driver parameters, with high bits indexing the table and lower bits carrying user/generation information. MR allocation initializes segment maps and publishes an lkey under the table lock. User MR registration pins umem, builds segment maps from pages, and stores user base/iova/length/access. DMA MR uses lkey 0 and is restricted to kernel PDs. Deregistration unpublishes the lkey, drops references, cleans matching QPs, synchronizes RCU, waits up to five seconds for MR refs to drain, and frees maps/umem.

Fast-reg and map-SG paths build or update page segments and key/access state. `rvt_lkey_ok()` validates local SGEs, compresses adjacent SGEs, checks PD/access/range/lkey generation, and takes MR refs. `rvt_rkey_ok()` performs equivalent remote-key validation for QP operations.

## State And Persistence Behavior

Persistent state includes the per-device lkey table, optional DMA MR pointer, generation counter, and each MR's segment maps, percpu refcount, completion, lkey publication flag, invalidation flag, PD, access flags, iova/user-base/offset/length, and optional umem. MR refs persist through in-flight QP SGEs and must drain before deregistration completes.

## Dependencies And Integration Points

Depends on RDMA umem, scatterlist page iteration, rdmavt QP iteration/cleanup, RCU, percpu refs, tracepoints, and driver device parameters. Exported functions are used by QP send/receive/RC paths to validate SGEs and remote access.

## Risks And Edge Cases

Deregistration can return `-EBUSY` after timeout and intentionally re-takes a reference, leaving cleanup to later handling. Lkey generation sizing must leave enough bits to avoid stale-key reuse. `rvt_lkey_ok()` and `rvt_rkey_ok()` must correctly handle lkey/rkey zero for kernel DMA MR while rejecting user PDs. Adjacent SGE compression must not hide overruns. User MR segment construction requires `page_address()` to succeed.

## Test Signals

Test lkey table sizing and generation wrap, DMA MR user rejection, user MR zero length and umem failures, deregistration with active QP refs, fast-reg key checks, invalidated rkey rejection, local and remote access flag enforcement, SGE boundary/offset calculations, adjacent SGE compression, scatterlist mapping, and RCU publication/unpublication races.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.c -->
