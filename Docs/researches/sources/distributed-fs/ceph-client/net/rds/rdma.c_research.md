# sources/distributed-fs/ceph-client/net/rds/rdma.c

## Purpose
`rdma.c` implements generic RDS RDMA and atomic socket-control behavior above any specific transport. It manages user MR registration/freeing, socket MR lookup trees, use-once invalidation, RDMA/atomic send operation construction from control messages, page pinning, ODP fallback setup, and operation cleanup.

## Important APIs, Types, and Functions
Public functions include `rds_get_mr()`, `rds_get_mr_for_dest()`, `rds_free_mr()`, `rds_rdma_drop_keys()`, `rds_rdma_unuse()`, `rds_rdma_extra_size()`, `rds_cmsg_rdma_args()`, `rds_cmsg_rdma_dest()`, `rds_cmsg_rdma_map()`, `rds_cmsg_atomic()`, `rds_rdma_free_op()`, `rds_atomic_free_op()`, and `__rds_put_mr_final()`. Key helpers are `rds_pages_in_vec()`, `rds_mr_tree_walk()`, `rds_destroy_mr()`, `rds_pin_pages()`, `__rds_rdma_map()`, and `rds_rdma_pages()`.

## Control Flow
MR registration validates that the socket is bound and has a transport with `get_mr`, checks address/length overflow, requires `can_do_mlock()`, calculates page count, limits MR size to the 1 MiB RDS message bound plus alignment, allocates an `rds_mr`, pins pages with `pin_user_pages_fast(FOLL_LONGTERM|FOLL_WRITE)`, builds an SG table, and calls the transport `get_mr` callback. If long-term pinning is unsupported, it requests ODP registration instead. On success it stores the transport-private MR, builds the 64-bit cookie from rkey and offset, optionally copies the cookie to user space, inserts the MR into the socket RB tree, and returns with refcounts balanced.

MR freeing handles a zero-cookie flush-all special case, otherwise removes the keyed MR from the RB tree under `rs_rdma_lock`, applies invalidate if requested, and drops the reference. `rds_rdma_drop_keys()` removes all socket MRs during socket teardown and flushes transport MRs. `rds_rdma_unuse()` reacts to incoming RDMA extension headers by syncing the MR and freeing use-once or forced MRs.

`rds_cmsg_rdma_args()` parses sendmsg RDMA control messages, validates vector count, preallocates notifier state, calculates and pins local pages, supports a single-vector ODP fallback by registering a local ODP MR, fills SG entries, checks local byte count against remote vector capacity, and marks the RDMA op active. `rds_cmsg_rdma_dest()` attaches an existing local MR cookie for delivery to the remote and syncs it for device reads. `rds_cmsg_rdma_map()` registers a new MR and embeds its cookie into the outgoing message. `rds_cmsg_atomic()` parses masked/nonmasked FADD and CSWP requests, validates 8-byte alignment, pins the local result page, and fills the atomic op.

## State and Persistence
Socket MR state is in `rs->rs_rdma_keys`, an RB tree keyed by rkey. Each `rds_mr` is kref-managed, holds transport-private state, flags for use-once/invalidate/write, and a back pointer to the owning socket. RDMA and atomic send ops live inside `struct rds_message` until completion or message purge. Pinned user pages persist until op or MR cleanup; ODP MRs avoid explicit page arrays.

## Dependencies and Integration Points
Transport callbacks in `struct rds_transport` provide actual MR registration, sync, free, and flush behavior. `ib_rdma.c` is the IB implementation. `message.c` allocates SG space and calls cleanup. `recv.c` processes RDMA extension headers and invokes `rds_rdma_unuse()`. User ABI structs come from `<linux/rds.h>`.

## Risks
Long-term page pinning has security/resource implications and depends on `can_do_mlock()`. Error paths must release partially pinned pages and SG arrays exactly once. RB-tree lookup/insertion assumes rkeys are unique; duplicate behavior is guarded by BUG assumptions. ODP fallback changes cleanup ownership and only supports a single local vector in this code. Atomic control messages require strict 8-byte alignment and correct result buffer dirtying. User-controlled vector lengths need overflow checks throughout.

## Test Signals
Test MR get/free/drop, duplicate/invalid cookies, zero-cookie flush, use-once RDMA unuse, invalidation, RDMA read/write vectors with unaligned addresses, ODP supported and unsupported paths, mlock permission failures, atomic variants, notifier generation, and socket teardown with outstanding MRs. Watch for leaked pins, RB tree corruption, and RDMA status control messages.
