# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/pm.c

## Purpose

`pm.c` implements the MHI host power-management and device-state machine. It validates PM state transitions, drives READY/M0/M2/M3/SYS_ERR/disable transitions, manages device wake doorbells, schedules execution-environment transition work, handles mission-mode entry, powers controllers up and down, exports suspend/resume APIs, and sends execution-environment uevents.

## Important APIs, Types, And Functions

- Transition validation: `dev_state_transitions[]` and `mhi_tryset_pm_state()`.
- Device state writes: `mhi_set_mhi_state()`.
- MHI transitions: `mhi_ready_state_transition()`, `mhi_pm_m0_transition()`, `mhi_pm_m1_transition()`, `mhi_pm_m3_transition()`, `mhi_pm_mission_mode_transition()`, `mhi_pm_disable_transition()`, and `mhi_pm_sys_error_transition()`.
- Work scheduling: `mhi_queue_state_transition()`, `mhi_pm_st_worker()`, and `mhi_pm_sys_err_handler()`.
- Exported PM APIs: `mhi_pm_suspend()`, `mhi_pm_resume()`, `mhi_pm_resume_force()`, `mhi_async_power_up()`, `mhi_sync_power_up()`, `mhi_power_down()`, `mhi_power_down_keep_dev()`, `mhi_force_rddm_mode()`, `mhi_device_get_sync()`, and `mhi_device_put()`.

## Control Flow

`mhi_async_power_up()` supplies default wake callbacks if needed, initializes PM to POR, validates the current execution environment, recovers from initial SYS_ERR if possible, enables IRQs, and queues either PBL firmware loading or READY processing. READY processing waits for reset clear and READY set, transitions to POR, initializes MMIO, primes software event rings, and asks the device to enter M0.

M0 transition updates host state, asserts wake, rings event/cmd/channel doorbells as needed, handles doorbell-mode reset requests, then releases wake and wakes waiters. M1 events move to M2 and either notify idle or immediately wake the device if resources are pending. Suspend moves from M0/M1 to M3_ENTER, writes M3, waits for M3 completion, and notifies LPM-capable clients. Resume moves from M3 to M3_EXIT, writes M0, waits for M0/M2, and notifies clients of LPM exit.

Mission-mode transition verifies the device EE, destroys devices from the previous EE, notifies controller and userspace, forces M0, primes hardware event rings, creates channel devices, and drops wake. SYS_ERR transition notifies the controller, moves to SYS_ERR_PROCESS, optionally resets hardware, kills tasklets, destroys channel devices, resets event/cmd contexts, and queues PBL or READY recovery. Disable transition optionally destroys devices, resets hardware unless in RDDM, kills IRQ/tasklets, resets rings, and moves to DISABLE.

## State And Persistence Behavior

`mhi_cntrl->pm_state` is a single-bit internal PM state protected by `pm_lock` and `pm_mutex` depending on scope. `dev_state`, `ee`, transition-list entries, wake counters, `pending_pkts`, M0/M2/M3 counters, and `state_event` waitqueue coordinate asynchronous hardware and software transitions. Device wake is reference counted in `dev_wake`; the wake doorbell is only written when PM-state predicates allow it.

## Dependencies And Integration Points

`pm.c` depends on register/ring helpers in `main.c`, context/MMIO setup in `init.c`, firmware loader functions, public MHI states from `common.h`, controller callbacks such as `status_cb`, `runtime_get`, `runtime_put`, and optional `wake_get`/`wake_put`, plus tracepoints in `trace.h`. PCI glue calls these APIs for power-up, runtime PM, recovery, reset, and removal.

## Risks

Transition correctness depends on `mhi_tryset_pm_state()` receiving valid bitmask states under the right lock. Error and shutdown paths drop `pm_mutex` while destroying devices and waking waiters, which is necessary but creates interleaving sensitivity. Wake reference imbalance is guarded by warnings in disable/SYS_ERR paths but can still cause suspend failures. RDDM support intentionally skips normal SYS_ERR handling, so controller configuration changes can alter crash recovery behavior. Suspend rejects pending packets and wake refs, making runtime PM sensitive to client drivers that hold wake references too long.

## Test Signals

Trace `mhi_tryset_pm_state` and `mhi_pm_st_transition` through full power-up, firmware download, mission-mode, runtime suspend/resume, SYS_ERR recovery, RDDM entry, graceful power-down, and non-graceful link-down. Check uevents for `EXEC_ENV`, controller callbacks for idle, mission mode, SYS_ERROR, fatal error, and RDDM, and warnings for nonzero wake or pending packet counts during teardown.
