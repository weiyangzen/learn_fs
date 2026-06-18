# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_intr.c

Purpose: provides wait helpers for MFC firmware command completion at device and context scope.

Important APIs and functions: `s5p_mfc_wait_for_done_dev` waits on `dev->queue` for a device interrupt type matching the requested command or an error return. `s5p_mfc_wait_for_done_ctx` does the same for `ctx->queue`, using either interruptible or non-interruptible waits according to its `interrupt` argument. `s5p_mfc_clean_dev_int_flags` and `s5p_mfc_clean_ctx_int_flags` clear interrupt condition, type, and error fields.

Control flow: callers clear flags before issuing firmware commands, then wait until the interrupt handler sets `int_cond` and `int_type` and wakes the queue. Timeout uses `MFC_INT_TIMEOUT`; timeout, signal interruption, or firmware error return all map to a nonzero failure result. Successful matching commands return zero.

State and persistence: state is transient interrupt state in `struct s5p_mfc_dev` and `struct s5p_mfc_ctx`: `int_cond`, `int_type`, and `int_err`. The helpers do not touch hardware registers directly and do not persist state beyond clearing these fields.

Dependencies and integration points: depends on Linux wait queues, timeout conversion, errno values, and MFC debug/common definitions. It is used by command, scheduler, stream-on/off, and volatile-control paths that need synchronous confirmation from the firmware after an asynchronous hardware command.

Risks: all failure modes return `1`, so callers cannot distinguish timeout, signal, or firmware error without logs and saved `int_err`. A stale interrupt flag can satisfy a later wait unless the caller cleaned flags first. The interruptible path only handles `-ERESTARTSYS`, while other negative wait returns would be treated as success if ever introduced. Timeout-sensitive paths depend on firmware, clock, and IRQ delivery.

Test signals: fault-injection tests for no interrupt, error interrupt, and signal interruption; hardware tests around open instance, sequence done, frame done, sleep/wake, and abort; and lockdep/runtime tests ensuring waits are not made from atomic context.
