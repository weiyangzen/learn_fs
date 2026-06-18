# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/iowait.c

Purpose: implements the non-inline portions of the HFI1 I/O wait helper used by QPs/PQs and IPoIB queues to track SDMA/PIO resource waits, queued work, flags, and starvation priority.

Important APIs and functions: `iowait_set_flag()`, `iowait_flag_set()`, and `iowait_clear_flag()` manipulate wait flags with tracepoints. `iowait_init()` initializes the embedded wait structure, callback pointers, waitqueues, counters, list heads, and two send-engine work items. `iowait_cancel_work()` synchronously cancels IB and TID RDMA work items. `iowait_set_work_flag()` marks whether the IB or TID send engine has pending work. `iowait_priority_update_top()` compares starvation-adjusted priorities and returns the index of the higher-priority waiter.

Control flow: callers embed `struct iowait`, call `iowait_init()` with workqueue callbacks and resource callbacks, then use inline helpers from `iowait.h` and the functions here to schedule work, queue SDMA txreqs, mark pending legs, wait for drains, and wake waiters when resources become available. Cancellation is used during teardown to ensure queued restart work no longer references the parent object.

State and persistence: state lives entirely in the caller-owned `struct iowait`: flags, SDMA/PIO busy atomics, tx limit/count/descriptor count, priority/starvation counters, callback pointers, waitqueues, and per-send-engine `struct iowait_work` entries. `iowait_priority_update_top()` treats one priority unit as sixteen starvation-count units.

Dependencies and integration points: includes `iowait.h` and `trace_iowait.h`, depends on Linux workqueues/list/waitqueue/atomics through the header, and integrates with SDMA tx request lists and higher-level QP/PQ/IPoIB scheduling. The TID RDMA leg is optional; `iowait_cancel_work()` checks whether its work function is initialized.

Risks: flag bit `IOWAIT_PENDING_IB` is 0, so users must consistently use bit operations and not treat zero as "no flag". Work cancellation must happen before parent memory is freed. Priority comparison uses `u8` arithmetic after shifting priority; large values would wrap if callers exceed expected ranges. Callback locking rules from the header matter because sleep/wakeup callbacks may run with locks held.

Test signals: tracepoints for set/clear, scheduling of IB and TID work, pending flag selection from `iowait_set_work_flag()`, drain wait completion after SDMA/PIO decrements, cancellation during QP teardown, and fairness tests showing starved waiters rise in priority.
