# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_main.c

Purpose: implements QDIO runtime queue processing, SIGA/EQBS/SQBS operations, interrupt handling, exported queue API, and module lifecycle.

Important APIs/types/functions: exported APIs include `qdio_get_ssqd_desc()`, `qdio_shutdown()`, `qdio_free()`, `qdio_allocate()`, `qdio_establish()`, `qdio_activate()`, `qdio_inspect_input_queue()`, `qdio_inspect_output_queue()`, `qdio_add_bufs_to_input_queue()`, `qdio_add_bufs_to_output_queue()`, `qdio_start_irq()`, and `qdio_stop_irq()`. Internal core helpers handle SIGA read/write/sync, EQBS/SQBS state extraction, inbound/outbound frontier discovery, activation errors, cleanup cancellation, and PCI/thin interrupt delivery.

Control flow: consumers allocate QDIO storage, establish queues with CIW EQUEUE, optionally enable thin interrupts, wait for establish IRQ, query SSQD/QEBSM capability, initialize SLSB states, activate with CIW AQUEUE, then add/inspect buffers. Inbound processing returns CU-empty buffers, signals input if needed, inspects primed/error buffers, acknowledges batches, and lets polling restart IRQs safely. Outbound processing marks buffers CU-primed, handles IQDIO SIGA-W/WRITEM/WRITEQ, syncs or fast-requeues for non-IQDIO, and inspects completion/error/pending states.

State and persistence behavior: lifecycle state is `qdio_irq->state` from inactive through established/active/stopped/cleanup/error. Queue state is SLSB ownership/state bytes or QEBSM-managed state, `first_to_check`, `nr_buf_used`, input batch windows, poll-disabled bit, timers via CCW wait queues, and perf counters. All state is runtime memory and hardware queue state.

Dependencies and integration points: depends on CCW start/halt/clear APIs, CIWs from SENSE ID, QDIO setup/debug/thinint helpers, CHSC SSQD/SADC, adapter interrupts, IPL LGR logging, and upper-layer qdio handlers such as qeth/zfcp.

Risks and test signals: QDIO is concurrency-sensitive around poll-state transitions, adapter interrupts, buffer ownership, busy-bit retry loops, and shutdown while I/O is active. Tests should cover allocate/establish/activate/shutdown/free, missing CIWs, setup validation failures, establish timeout/error/retry, QEBSM and non-QEBSM buffer states, IQDIO AOB alignment, SIGA busy and ENOBUFS paths, pending/error SLSB states, and no-lost-interrupt `qdio_start_irq()` rescans.
