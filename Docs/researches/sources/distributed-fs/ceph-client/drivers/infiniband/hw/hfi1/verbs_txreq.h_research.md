# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs_txreq.h

Purpose: Defines the HFI1 verbs transmit request wrapper that bridges RDMA verbs send state to the HFI1 SDMA transmit machinery. `struct verbs_txreq` embeds an `hfi1_sdma_header` and `sdma_txreq`, then carries the owning `rvt_qp`, active WQE, optional memory region, SGE state, selected SDMA engine, send context, header dword count, and current send size.

Important APIs/types/functions: `get_txreq()` is the fast path allocator from `dev->verbs_txreq_cache` with `GFP_ATOMIC | __GFP_NOWARN`, requiring `qp->slock`; it falls back to `__get_txreq()` when the cache allocation fails. `get_waiting_verbs_txreq()` converts an `iowait_work` queue head from `sdma_txreq` back to `verbs_txreq`; `verbs_txreq_queued()` delegates queue-state checks to `iowait_packet_queued()`. The file declares `hfi1_put_txreq()`, `verbs_txreq_init()`, and `verbs_txreq_exit()` for lifecycle management.

Control flow: Callers under the QP send lock request a txreq, get initialized QP/private context pointers, zero descriptor count for later descriptor-existence tests, set header type from QP private state, and clear SDMA flags before filling the packet. Queued txreqs are recovered through the embedded `sdma_txreq`.

State and persistence: State is transient per-send kernel memory. Persistent resources are the driver kmem cache initialized and destroyed by the declared init/exit helpers. The txreq references QP, WQE, MR, and SGE state but does not own them except through the later `hfi1_put_txreq()` release path.

Dependencies and integration: Depends on HFI1 verbs, SDMA, and iowait internals plus RDMA core `rvt_qp`/`rvt_swqe` data. It integrates with HFI1 QP private fields `s_sde`, `s_sendcontext`, and `hdr_type`.

Risks: Allocation is atomic and can fail under pressure; slow-path locking must avoid deadlock with `qp->slock`. Stale embedded pointers would be dangerous if a txreq outlives its QP/WQE lifetime, so release and iowait queue ownership are critical. Test signals include stress sends under memory pressure, iowait wakeups, SDMA descriptor accounting, and lockdep around QP send locking.
