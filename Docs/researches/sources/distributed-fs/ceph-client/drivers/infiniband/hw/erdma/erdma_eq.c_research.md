# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_eq.c

Implements ERDMA event queues: common EQ allocation and notification, AEQ handling, CEQ handling, CEQ IRQ/tasklet setup, firmware create/destroy EQ commands, and CEQ array lifecycle.

Important functions include `notify_eq`, `get_next_valid_eqe`, `erdma_eq_common_init`, `erdma_eq_destroy`, `erdma_aeq_init`, `erdma_aeq_event_handler`, `erdma_ceq_completion_handler`, `erdma_set_ceq_irq`, `erdma_ceq_init_one`, `erdma_ceq_uninit_one`, `erdma_ceqs_init`, and `erdma_ceqs_uninit`.

Common init allocates coherent EQ memory and a DMA-pool DB record. AEQ init writes AEQ queue address/depth/DB record registers. CEQ init creates one EQ per completion vector via CMDQ, sets BAR doorbell address, then requests IRQs whose handlers schedule tasklets. CEQ handling drains bounded EQE chunks, looks up CQs, advances kernel CQ command serial, and calls completion handlers. AEQ maps CQ error events to `IB_EVENT_CQ_ERR` and other QP events to `IB_EVENT_QP_FATAL`.

Persistent state includes EQ DMA memory, CI, depth, DB address and record, counters, and `erdma_eq_cb.ready`. Dependencies include CMDQ, IRQ/tasklet APIs, RDMA event callbacks, QP/CQ lookups, and BAR doorbell registers.

Risks include interrupt/tasklet races with object destruction, leaked EQ memory if destroy-EQ command fails, and bounded polling leaving pending events for later interrupts. Test signals include CQ interrupts across vectors, CQ/QP async events, CEQ partial-failure unwind, tasklet cleanup on unload, EQ counters, and destroy-EQ failure injection.
