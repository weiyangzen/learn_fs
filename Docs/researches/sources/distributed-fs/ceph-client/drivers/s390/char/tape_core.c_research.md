# sources/distributed-fs/ceph-client/drivers/s390/char/tape_core.c

Purpose: core s390 tape driver, owning ccw device probe/remove, online/offline transitions, tape device lifetime, request allocation, request queueing, interrupt dispatch, state/medium events, and module init/exit.

Important APIs/types/functions: exports `tape_generic_probe`, `tape_generic_remove`, `tape_generic_online`, `tape_generic_offline`, `tape_alloc_request`, `tape_free_request`, `tape_do_io`, `tape_do_io_async`, `tape_do_io_interruptible`, `tape_cancel_io`, `tape_open`, `tape_release`, `tape_mtop`, `tape_state_set`, `tape_med_state_set`, and `tape_dump_sense_dbf`.

Control flow: probe allocates `struct tape_device`, creates sysfs attributes, stores drvdata, and installs `__tape_do_irq`. Online installs a discipline, calls its setup, assigns minors, creates char devices, and moves to `TS_UNUSED`. Requests are added under the ccw device lock; the first request starts via `ccw_device_start`, later requests queue. Interrupts copy status into the request, update generic online status, call discipline `irq`, and then end, retry, cancel, or mark long-busy. Completion invokes callbacks, wakes waiters, drops queued refs, and starts the next request.

State and persistence: maintains global sorted `tape_device_list` under `tape_device_lock`, per-device request queues, state wait queues, delayed work for next request, long-busy timer, medium-state work and uevents, refcounts, mode byte, minor allocation, and debug areas. Runtime-only; sysfs attributes expose current state.

Dependencies and integration: integrates with ccw_device APIs, s390 debug feature, sysfs attributes, tape class/char/proc/3490 modules, Linux workqueues/timers/wait queues, and mtio status bits.

Risks: concurrency spans process, interrupt, timer, and workqueue contexts; request refcount drops must match queue insertion/removal; `TS_NOT_OPER` prevents state resurrection; interrupt handling of error-pointer IRBs and unsolicited long-busy ready events is fragile; module init does not unwind partial frontend/discipline registration failures in this source.

Test signals: ccw probe/remove while idle and in-use, online/offline busy rejection, sync/async/interruptible I/O completion and cancellation, long-busy timeout/ready interrupt handling, request queue ordering, sysfs state/operation/blocksize attributes, and module load/unload ordering.
