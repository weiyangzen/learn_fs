# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_admin.c

## Purpose
`ionic_admin.c` implements the Ionic RDMA admin/event queue infrastructure. It creates RDMA event queues, admin completion queues, and admin queues; posts and completes firmware admin WQEs; handles watchdog timeouts and LIF reset/kill; polls EQs and dispatches CQ/QP events into RDMA core callbacks.

## Important APIs, Types, And Functions
The central global is `ionic_evt_workq`. Key functions are `ionic_admin_post()`, `ionic_admin_wait()`, `ionic_create_rdma_admin()`, `ionic_destroy_rdma_admin()`, `ionic_kill_rdma_admin()`, and `ionic_rdma_reset_devcmd()`. Admin internals include `ionic_admin_poll_locked()`, `ionic_admin_dwork()`, `ionic_admin_work()`, `ionic_admin_busy_wait()`, and `ionic_admin_cancel()`. Queue construction uses `ionic_create_rdma_admincq()`, `ionic_create_rdma_adminq()`, `ionic_create_eq()`, and their destroy helpers. Event handling uses `ionic_poll_eq()`, `ionic_poll_eq_isr()`, `ionic_poll_eq_work()`, `ionic_cq_event()`, and `ionic_qp_event()`.

## Control Flow
Admin creation clamps requested EQ/AQ counts, requires minimum event/admin queues, creates EQs with interrupts and device queue commands, creates one admin CQ per admin queue, creates admin queues backed by host queue memory, attaches CQ context to AQ, and marks queues active. Posting selects an admin queue by CPU, queues a work request, and immediately polls if the queue was idle. Polling first completes CQEs, validates type/qid/command index, copies completion state to matching WQEs, consumes admin queue strides, rings CQ credits, arms CQ interrupts, then posts pending WQEs into available admin queue space and rings the admin doorbell. Waiting supports busy-wait, interruptible wait, uninterruptible wait, and teardown semantics. The delayed watchdog polls missed completions, warns after a threshold, and kills/resets RDMA on timeout. EQ ISR/work polling reads events with color bits, dispatches CQ notifications/errors and QP events, then re-arms interrupts or continues work.

## State And Persistence
Runtime state includes per-device `admin_state`, per-AQ `admin_state`, pending/posted WR lists, queue producer/consumer indexes, CQ color and arm state, watchdog stamp, interrupt masks/credits, xarray-backed QP/CQ lookup state owned elsewhere, and reset/admin delayed work. Admin kill transitions active queues through paused/killed states, completes pending admin WQEs locally as killed, flushes QPs/CQs, and may dispatch `IB_EVENT_DEVICE_FATAL`. There is no nonvolatile persistence.

## Dependencies And Integration Points
The file depends on shared Ionic net-driver device commands (`ionic_adminq_post_wait`, `ionic_intr_*`, LIF reset helpers), RDMA CQ/QP object helpers from `ionic_controlpath.c`, queue helpers, page-table/CQ creation helpers, workqueues, interrupts, DMA ordering barriers, and RDMA core event callbacks. Admin opcodes are consumed by the controlpath verbs operations for AH/MR/CQ/QP creation and modification.

## Risks
Admin timeout kills all admin queues and flushes QPs, so false timeouts or missed completions are disruptive. `ionic_admin_busy_wait()` can hold CPU with IRQs disabled for up to the configured retry window. Admin CQ validation drops malformed completions but still advances CQ producer/color, so hardware/software index mismatch handling is critical. Kill/reset uses local IRQ disabling and spin locks while flushing objects; lock ordering against CQ/QP datapath locks must be stable. Destroy assumes callers already killed/canceled work before freeing queues. Partial EQ/AQ creation is allowed above minimums, so later vector arithmetic must tolerate reduced counts.

## Test Signals
Test admin queue creation at min/max/partial counts, admin WQE stride splitting, CQE validation failures, missed event polling, watchdog warning and timeout reset, busy-wait AH paths, interruptible wait cancellation, teardown wait semantics after killed admin, EQ ISR budget overflow and work continuation, CQ notify/error events, QP event translations, LIF reset failure fallback, destroy after partial creation, and lockdep under kill/reset with active QPs.
