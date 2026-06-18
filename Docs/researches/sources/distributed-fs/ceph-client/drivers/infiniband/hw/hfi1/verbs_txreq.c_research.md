# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs_txreq.c

## Purpose
`verbs_txreq.c` manages the slab cache and lifecycle of `struct verbs_txreq` objects used by verbs send paths. It allocates txreqs, handles low-memory/resource waits by queueing QPs on `dev->txwait`, cleans SDMA state and MR references on release, and wakes a waiting QP when a txreq becomes available.

## Important APIs and Functions
`hfi1_put_txreq(struct verbs_txreq *tx)` releases a tx request, drops an attached MR with `rvt_put_mr()`, cleans SDMA descriptor state with `sdma_txclean()`, frees the slab object, then wakes one QP from the txwait list. `__get_txreq(struct hfi1_ibdev *dev, struct rvt_qp *qp)` allocates from `dev->verbs_txreq_cache` while `qp->s_lock` is held; on failure it marks the QP `RVT_S_WAIT_TX`, queues its `s_iowait`, traces sleep, and takes a QP reference. `verbs_txreq_init()` creates a per-device slab cache named by unit. `verbs_txreq_exit()` destroys it.

## Control Flow
Send builders call `get_txreq()`/`__get_txreq()` before constructing a packet. If allocation succeeds, normal send logic owns the txreq until PIO completion or SDMA callback calls `hfi1_put_txreq()`. If allocation fails and the QP is in a receive-capable state, the QP is placed on `dev->txwait`, marked not busy, and later woken by `hfi1_put_txreq()` after another txreq is freed. The wait list is protected by `txwait_lock` seqlock and QP references are held until wakeup.

## State, Persistence, and Dependencies
Persistent state is the per-device `verbs_txreq_cache`, `txwait` list, `txwait_lock`, and `n_txwait` counter in `struct hfi1_ibdev`. Per-QP state includes `RVT_S_WAIT_TX`, `RVT_S_BUSY`, private `s_iowait`, and QP refcount. Dependencies include `hfi.h`, `verbs_txreq.h`, `qp.h`, `trace.h`, rdmavt MR/QP helpers, and SDMA cleanup.

## Integration Points
`uc.c`, `ud.c`, RC send code, and `verbs.c` consume txreqs for packet construction and send. `hfi1_put_txreq()` is called from PIO send completion/error paths and SDMA callbacks. QP wakeups integrate with `hfi1_qp_wakeup()` and tracepoint `hfi1_qpsleep`.

## Risks and Test Signals
Risks include wait-list corruption under seqlock misuse, missed wakeups, leaking QP references when queued, freeing txreqs with live SDMA descriptors, MR reference leaks, and destroying the cache while txreqs remain. Test signals include forced slab allocation failure, high-concurrency send pressure, txwait list drain on release, QP state transitions around `RVT_S_WAIT_TX`, SDMA cleanup after aborted sends, and unregister checks that wait lists are empty.
