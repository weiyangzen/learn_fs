# sources/distributed-fs/ceph-client/include/trace/events/rdma_core.h

Purpose: Defines RDMA core tracepoints for completion queue scheduling/polling/allocation/free and memory-region allocation/deregistration. It supports diagnosing CQ workqueue behavior and MR resource lifecycle.

Important APIs/types/functions: CQ events include `cq_schedule`, `cq_reschedule`, `cq_process`, `cq_poll`, `cq_drain_complete`, `cq_modify`, `cq_alloc`, `cq_alloc_error`, and `cq_free`. MR events include `mr_alloc`, `mr_integ_alloc`, and `mr_dereg`. Symbolic maps decode `ib_poll_context` and `ib_mr_type`.

Control flow: RDMA core emits CQ events when work is scheduled, rescheduled, processed, polled, drained, modified, allocated, or freed. MR events fire when protection-domain memory regions are allocated, integrity MRs are allocated, or regions are deregistered.

State and persistence: No state is owned. It observes RDMA core objects such as `ib_cq`, `ib_device`, `ib_pd`, `ib_mr`, queue depths, poll contexts, completion counts, and return codes.

Dependencies and integration points: Depends on `rdma/ib_verbs.h` and tracepoints. It integrates with all RDMA providers and upper-layer protocols including RPC/RDMA and storage/network fabrics.

Risks and test signals: Risks include object lifetime races during destroy, provider-specific return code semantics, missing CQ context in errors, and high output under CQ load. Test CQ allocation/free, interrupt and workqueue polling, resize/modify, drain, MR alloc/dereg, provider error injection, and module unload.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rdma_core.h` completely for this pass (394 lines, 7193 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rdma_core.h_research.md`.
