<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cq.c

## Purpose
Implements the mlx5 InfiniBand completion queue provider. It translates hardware CQEs into `struct ib_wc`, handles CQ creation for kernel and uverbs users, manages CQ arming, polling, resizing, software-generated completions, cleanup during QP/SRQ teardown, and mlx5-specific CQ uAPI attributes.

## Important APIs, Types, And Functions
- CQ callbacks: `mlx5_ib_cq_comp()` routes completion EQ events to the RDMA core CQ completion handler, and `mlx5_ib_cq_event()` reports CQ error events as `IB_EVENT_CQ_ERR`.
- CQE access helpers: `get_cqe()`, `get_sw_cqe()`, `next_cqe_sw()`, and `sw_ownership_bit()` implement mlx5 ownership-bit based CQ ring traversal.
- Completion decoding: `handle_good_req()`, `handle_responder()`, `mlx5_handle_error_cqe()`, `get_sig_err_item()`, and `handle_atomics()` map requestor, responder, error, signature, and atomic CQEs into RDMA work completions and driver state.
- Polling APIs: `mlx5_ib_poll_cq()` is the provider `poll_cq` method; `poll_soft_wc()` and `mlx5_ib_poll_sw_comp()` drain software completions and synthesize flushed completions during internal device error.
- Notification API: `mlx5_ib_arm_cq()` programs the CQ arm doorbell and reports missed software completions when requested.
- Creation/destruction: `mlx5_ib_create_user_cq()`, `mlx5_ib_create_cq()`, `mlx5_ib_pre_destroy_cq()`, `mlx5_ib_post_destroy_cq()`, and `mlx5_ib_destroy_cq()` allocate doorbells, UMEM or fragment buffers, create the core mlx5 CQ, and tear it down.
- Resize and moderation: `mlx5_ib_modify_cq()`, `mlx5_ib_resize_cq()`, `resize_user()`, `resize_kernel()`, and `copy_resize_cqes()` implement moderation commands and firmware CQ resize.
- Cleanup and software completion: `__mlx5_ib_cq_clean()`, `mlx5_ib_cq_clean()`, and `mlx5_ib_generate_wc()` remove stale CQEs and enqueue driver-generated WCs.
- uAPI: `mlx5_ib_create_cq_defs` adds optional `MLX5_IB_ATTR_CREATE_CQ_UAR_INDEX` to CQ creation.

## Control Flow
Polling takes `cq->lock`, drains pending software completions first, then loops over hardware CQEs until either the caller's budget is reached or `next_cqe_sw()` reports no software-owned entry. `mlx5_poll_one()` advances `mcq.cons_index`, executes a read barrier after the ownership check, handles resize CQEs specially, finds the QP by QPN in `dev->qp_table.tree`, and fills the caller's `ib_wc`. Successful requestor completions update SQ tail state; responder completions consume RQ or SRQ entries; error completions map mlx5 syndromes to IB WC status and update UMR recovery state for UMR QPs.

CQ creation validates the requested entry count against firmware `log_max_cq_sz`, rounds to a power-of-two ring plus one spare entry, initializes locks/lists, builds a `create_cq_in` command, gets an EQ number for the requested completion vector, and calls `mlx5_core_create_cq()`. User CQs pin a userspace CQ buffer, map the userspace doorbell page with `mlx5_ib_db_map_user()`, choose a UAR index from either the new attribute, legacy command field, or context default, and may enable CQE compression or real-time timestamps. Kernel CQs allocate a kernel doorbell record and a fragment buffer, initialize all CQEs to invalid, and use the device UAR.

CQ resize serializes with `resize_mutex`, allocates either a new user UMEM or kernel fragment buffer, builds `modify_cq_in` with new PAS/page-size/log-size fields, and calls `mlx5_core_modify_cq()` with resize opmod. User resize swaps `ibcq.umem` after firmware success; kernel resize copies CQEs up to the resize CQE under the CQ spinlock and frees the old buffer after the swap.

## State And Persistence
All state is in-memory and hardware-backed. Persistent per-CQ fields include `mcq.cqn`, `mcq.cons_index`, doorbell DMA addresses, CQE size, `ibcq.cqe`, private CQ flags, user UMEM or kernel frag buffer, resize buffers, software WC list, notification state, and QP linkage lists for send/receive CQs. CQE ownership, consumer index doorbells, and firmware CQ context persist in hardware until destroyed. Software-generated WCs are list entries owned by the CQ and freed after polling.

## Dependencies And Integration Points
The file depends on RDMA core CQ, WC, uverbs, UMEM, and cache helpers; mlx5 core CQ commands; mlx5 fragment-buffer and doorbell helpers; QP/SRQ private structures; device capabilities; and the uverbs named-ioctl framework. It integrates with `doorbell.c` for user DB mapping, with QP and SRQ teardown through `mlx5_ib_cq_clean()`, with integrity/signature MR state through `dev->sig_mrs`, with completion EQs through mlx5 core callbacks, and with provider device ops registered elsewhere in the mlx5 driver.

## Risks And Edge Cases
CQ polling is concurrency-sensitive: CQ lock coverage must match QP table removal, SRQ WQE reclamation, software WC insertion, and resize buffer swaps. Error unwinds in user CQ creation must not release `ibcq.umem` directly because ib_core owns it after assignment, while DB and command buffers remain local driver resources. CQE compression, 128-byte padding, UAR-index selection, and page-offset quantization are all capability-dependent and should reject unsupported combinations. Resize must preserve CQE ownership bits exactly or completions can be lost or duplicated. The source as read contains syntax-level risk signals, including a duplicated local `ret` declaration in `mlx5_ib_destroy_cq()` and an extra brace-looking sequence in `handle_responder()`; build coverage should catch whether these are real defects in this source snapshot.

## Test Signals
Useful signals include provider build tests with `CONFIG_INFINIBAND_MLX5`, CQ create/destroy tests for user and kernel CQs, CQE-size and compression matrix tests, UAR-index uAPI compatibility tests, CQ polling with send/recv/RDMA/atomic/UMR/error CQEs, RoCE and IB responder metadata checks, SRQ/XRC receive completion tests, internal-error flushing tests, CQ resize under load, CQ moderation changes, KASAN/KCSAN runs around resize and cleanup, and leak tests for doorbell, UMEM, software WC, and frag-buffer unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cq.c -->
