# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cq.c

Purpose: Implements completion queue reaping and CQ flush for SoftiWARP. It translates internal `siw_cqe` records produced by QP completion paths into standard `ib_wc` work completions consumed by kernel clients and CQ polling.

Important APIs/types/functions: `map_wc_opcode[]` maps SIW opcodes to `IB_WC_*` opcodes. `map_cqe_status[]` maps internal SIW completion statuses to `ib_wc_status`. `siw_reap_cqe()` pops one valid CQE under `cq->lock`, fills an `ib_wc`, clears the CQE valid flag, and advances `cq_get`. `siw_cq_flush()` drains all currently valid CQEs by repeatedly reaping.

Control flow: TX/RX completion producers write CQEs into the ring and set `SIW_WQE_VALID`. Pollers call `siw_poll_cq()` in `siw_verbs.c`, which delegates here. During CQ destroy or queue flush, this file clears outstanding entries so backing memory can be released.

State and persistence behavior: CQ state is an in-memory ring with `cq_put`, `cq_get`, `num_cqe`, and a queue that may be mmaped to userspace. No state persists outside the kernel object. `READ_ONCE`/`WRITE_ONCE` protect against concurrent userspace-visible flag changes.

Dependencies/integration: Depends on `ib_verbs.h` and `siw.h`. Completion producers are in `siw_qp.c`; consumers are `siw_verbs.c` poll/destroy paths. Kernel CQs carry `base_qp` references and invalidate metadata; user CQs may have CQE fields modified by userspace, so this file validates opcode/status before array lookup.

Risks: CQE flag ordering and bounds checking are critical. User-mapped CQEs are adversarial; missing opcode/status validation could cause out-of-bounds reads. CQ overflow is handled by producers with CQ error events, so tests need to cover producer/consumer race behavior.

Test signals: Poll empty and non-empty CQs, kernel and user CQ modes, invalid user-written opcode/status, remote-invalidation completions, CQ flush on destroy, CQ overflow events, and concurrent producer/poller stress with KCSAN.
