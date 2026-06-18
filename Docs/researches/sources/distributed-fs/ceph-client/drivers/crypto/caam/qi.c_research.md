<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.c

Purpose: implements the legacy DPAA1 CAAM Queue Interface backend using QMan frame queues, per-CPU response queues, NAPI polling, congestion groups, and a small hot-path kmem cache.

Important APIs and control flow: `caam_qi_init()` allocates a congestion group, response FQs for QMan-affine CPUs, dummy netdev/NAPI contexts, a `caamqicache`, debugfs, and a devm shutdown action. `caam_drv_ctx_init()` validates shared descriptor length, builds and DMA-maps preheader/shared descriptor memory, chooses a QMan-affine CPU, binds a response FQ, and creates a scheduled request FQ. `caam_qi_enqueue()` DMA-maps the request SGT, builds a compound FD, retries `qman_enqueue()`, and refcounts the driver context. Completion callbacks from ERN or DQRR translate FDs back to requests, unmap SGTs, decrement refcounts, report errors, and invoke caller callbacks. `caam_drv_ctx_update()` switches to a new parked request FQ, drains the old FQ, updates the shared descriptor, schedules the new FQ, and kills the old one. `caam_drv_ctx_rel()` kills the request FQ and unmaps descriptor memory.

State and persistence behavior: per-CPU `pcpu_qipriv` stores NAPI/netdev/response FQ; `last_cpu` spreads contexts; global `qipriv.cgr`, `caam_congested`, and `qi_cache` persist for the backend lifetime. Per-crypto context state is `caam_drv_ctx` with shared descriptor DMA address, request/response FQs, refcount, CPU, operation type, and device.

Dependencies and integration points: depends on QMan portals/FQs/CGRs, NAPI/netdev shims, controller IOMMU domain, CAAM descriptor sizes, debugfs QI congestion tracking, and QI algorithm modules using `caam_drv_req`.

Risks and test signals: risks include complex FQ teardown races, limited retries under QMan congestion, response lookup through IOVA-to-virt assumptions, refcount drain timeout warnings, global congestion state, and partial failure cleanup across per-CPU setup. Test signals include high-throughput crypto via QI, congestion callback/debugfs increments, context update while requests are in flight, CPU affinity fallback, NAPI polling/rescheduling, clean shutdown of all FQs/CGR/cache, and no DMA leaks on enqueue errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.c -->
