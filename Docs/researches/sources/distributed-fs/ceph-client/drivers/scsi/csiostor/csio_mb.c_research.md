# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_mb.c

## Purpose
`csio_mb.c` implements firmware mailbox command construction, response parsing, asynchronous mailbox queueing, polling-mode mailbox execution, mailbox interrupt handling, timeout/cancel behavior, and firmware event handling for generic port/debug events. It is the firmware control-plane encoder/transport for hardware setup, queue allocation, FCoE link/VNP/FCF/stats operations, and adapter state changes.

## Important APIs and Functions
- Basic helpers: `csio_mb_fw_retval()`, `csio_mb_hello()`, `csio_mb_process_hello_rsp()`, `csio_mb_bye()`, `csio_mb_reset()`, `csio_mb_params()`, `csio_mb_process_read_params_rsp()`, `csio_mb_ldst()`, `csio_mb_caps_config()`, `csio_mb_port()`, `csio_mb_process_read_port_rsp()`, and `csio_mb_initialize()`.
- Queue mailbox helpers: `csio_mb_iq_alloc_write()`, `csio_mb_iq_alloc_write_rsp()`, `csio_mb_iq_free()`, `csio_mb_eq_ofld_alloc_write()`, `csio_mb_eq_ofld_alloc_write_rsp()`, and `csio_mb_eq_ofld_free()`.
- FCoE helpers: `csio_write_fcoe_link_cond_init_mb()`, `csio_fcoe_read_res_info_init_mb()`, `csio_fcoe_vnp_alloc_init_mb()`, `csio_fcoe_vnp_read_init_mb()`, `csio_fcoe_vnp_free_init_mb()`, `csio_fcoe_read_fcf_init_mb()`, `csio_fcoe_read_portparams_init_mb()`, and `csio_mb_process_portparams_rsp()`.
- Interrupt control: `csio_mb_intr_enable()` and `csio_mb_intr_disable()`.
- Firmware debug support: `csio_mb_dump_fw_dbg()`, `csio_mb_debug_cmd_handler()`.
- Mailbox engine: `csio_mb_issue()`, `csio_mb_completions()`, `csio_mb_isr_handler()`, `csio_mb_tmo_handler()`, `csio_mb_cancel_all()`, `csio_mbm_init()`, and `csio_mbm_exit()`.
- Firmware event helper: `csio_mb_fwevt_handler()` processes async `FW_PORT_CMD` link/module changes and `FW_DEBUG_CMD`.

## Control Flow and State
Command builder functions initialize `struct csio_mb` using `CSIO_INIT_MBP()`, fill firmware command structures in big-endian format, and set optional callbacks/private pointers. `csio_mb_issue()` is the central path. For synchronous commands (`mb_cbfn == NULL`), it writes mailbox registers, gives ownership to firmware, then polls until ownership returns or timeout expires. For asynchronous commands, it requires host and hardware interrupts to be enabled, queues if another mailbox is current, otherwise writes the command, records `mbm->mcurrent`, arms the timer, and notifies firmware with interrupt request.

`csio_mb_isr_handler()` validates PL/CIM mailbox causes, clears low-level then high-level cause registers, copies the response into `mbm->mcurrent`, clears mailbox ownership, moves the command to `mbm->cbfn_q`, and enqueues a `CSIO_EVT_MBX` event for worker-thread completion. `csio_mb_tmo_handler()` marks the current command with `FW_ETIMEDOUT`; `csio_mb_cancel_all()` marks current, queued, and callback-pending commands with `FW_HOSTERROR` and moves them to a callback queue.

## State and Persistence Behavior
`struct csio_mbm` stores the active mailbox pointer, pending request queue, callback queue, timer, interrupt index, and stats. Command payloads persist in each `struct csio_mb` until the caller callback or synchronous issue path consumes the response. The module keeps no disk state; all persistence is firmware/hardware side effects and in-memory driver queues.

## Dependencies and Integration Points
The file depends on Linux delay/jiffies APIs and SCSI FC headers, plus driver-local `csio_hw`, `csio_lnode`, `csio_rnode`, `csio_wr`, and firmware API headers. Hardware initialization uses HELLO/BYE/RESET/PARAMS/CAPS/PORT/INITIALIZE helpers. Work-request queue setup uses IQ/EQ helpers. Lnode discovery uses FCoE link/VNP/FCF/stats helpers. ISR and event-worker code use mailbox engine functions for completions.

## Risks and Edge Cases
- `csio_mb_issue()` assumes callers hold `hw->lock`; misuse can corrupt `mbm->mcurrent` or request queues.
- Async mailbox issue fails if interrupts are not enabled, so initialization order is critical.
- Queuing behavior for async commands only works when an active mailbox exists; unavailable hardware ownership with no `mcurrent` logs an error.
- `csio_mb_iq_alloc()` assigns `fl0size` twice, once from `fl0size` and then from `fl1size`, which looks suspicious and should be checked against firmware structure expectations.
- `csio_mb_process_portparams_rsp()` copies stats in chunks by index; off-by-one mistakes in `idx`/`nstats` would corrupt the assembled stats view.
- Firmware debug commands can arrive during mailbox polling/ISR and are handled specially, but repeated debug commands can delay ordinary completion.

## Test Signals
Tests should cover synchronous mailbox success/error/timeout, async mailbox queuing and callback ordering, timer timeout race with ISR completion, cancellation on hardware teardown, firmware debug mailbox handling, port link/module event updates, queue allocation response parsing, and FCoE stats assembly over three reads. Runtime counters `n_req`, `n_rsp`, `n_activeq`, `n_cbfnq`, `n_tmo`, `n_cancel`, and `n_err` provide direct observability.
