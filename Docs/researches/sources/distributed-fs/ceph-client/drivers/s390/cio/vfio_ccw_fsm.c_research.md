## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_fsm.c

Purpose: implements the vfio-ccw device finite-state machine. It validates user I/O requests, translates and starts channel programs, handles halt/clear async commands, processes interrupts, and controls open/close transitions.

Important APIs/types/functions: the exported dispatch table is `vfio_ccw_jumptable`. Major actions are `fsm_io_request()`, `fsm_io_helper()`, `fsm_async_request()`, `fsm_do_halt()`, `fsm_do_clear()`, `fsm_irq()`, `fsm_open()`, `fsm_close()`, and error/retry/busy handlers. States and events are defined in `vfio_ccw_private.h`.

Control flow: writes to the I/O region generate `VFIO_CCW_EVENT_IO_REQ`. In IDLE, `fsm_io_request()` copies the SCSW, rejects transport mode and halt/clear on the legacy I/O region, builds the channel program via `cp_init()` and `cp_prefetch()`, then calls `ssch()` through `fsm_io_helper()`. Success moves to `CP_PENDING`; translation or start errors free the CP and return IDLE. Async command-region writes dispatch HSCH or CSCH. Interrupts copy the per-CPU IRB and queue deferred work, optionally completing a quiesce waiter.

State and persistence: device state moves among NOT_OPER, STANDBY, IDLE, CP_PROCESSING, and CP_PENDING. The active channel program persists in CP_PENDING until the deferred interrupt path frees it. Close disables or quiesces the subchannel and frees any active CP.

Dependencies and integration: uses s390 `ssch/hsch/csch`, `cio_enable_subchannel()`, `cio_disable_subchannel()`, `vfio_ccw_sch_quiesce()`, tracepoints, and channel-program APIs.

Risks and test signals: high-risk paths are error unwind after partial CP translation, simultaneous async commands while pending, close during pending I/O, and not-oper recursion. Test expected return codes: `-EOPNOTSUPP` for transport/halt/clear in the I/O region, `-EAGAIN` while processing, `-EBUSY` while pending, and successful IRQ-driven IDLE return.
