<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/init.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/init.c

Purpose: implements common MEI device lifecycle management: state string helpers, firmware-status formatting, work cancellation, reset/start/restart/stop flows, write-idle detection, and base `mei_device` initialization.

Important APIs and functions: exported functions are `mei_dev_state_str()`, `mei_pg_state_str()`, `mei_fw_status2str()`, `mei_cancel_work()`, `mei_reset()`, `mei_start()`, `mei_restart()`, `mei_stop()`, `mei_write_is_idle()`, and `mei_device_init()`. Internal `mei_reset_work()` retries resets asynchronously after IRQ-detected errors.

Control flow: `mei_start()` locks the device, clears interrupts, runs hardware config, repeatedly performs reset until success or disable, waits for HBM start, validates HBM version, and leaves the link established. `mei_reset()` logs unexpected reset context, clears interrupts, idles HBM, marks resetting, enforces a consecutive reset limit, calls hardware reset/start through ops, disconnects software clients except power-up/initialization cases, clears HBM/client/FW-version/read-header state, enters `MEI_DEV_INIT_CLIENTS`, and sends the HBM start request. `mei_restart()` is suspend/resume-oriented and schedules retry on partial failure. `mei_stop()` transitions through powering-down states, removes MEI bus devices, cancels work, synchronizes IRQs, resets to disabled, and disconnects clients.

State and persistence: initializes and mutates volatile `struct mei_device` state: device state, waitqueues, locks, work items, host/client lists, callback queues, tx queue limit, host client bitmap, reset count, PXP/GSC reset flags, PG event, ops pointer, parent device, and timeout values. No persistent storage beyond hardware state.

Dependencies and integration: calls generic hardware ops wrappers, HBM start/reset helpers, client disconnect and bus removal/rescan helpers, workqueues, waitqueues, and runtime-safe IRQ synchronization. Hardware backends call `mei_device_init()` during allocation.

Risks: reset flow is central and can race with IRQ handlers, runtime PM, and userspace file operations; most callers must hold `device_lock`. Reset loops are capped by `MEI_MAX_CONSEC_RESET`, after which the device is disabled. `mei_stop()` intentionally cancels work twice to catch HW-initiated reset during shutdown.

Test signals: probe/start success, forced reset recovery, suspend/resume via `mei_restart()`, shutdown/remove via `mei_stop()`, sysfs `dev_state` transitions, reset-count disable after repeated failures, and idle detection before runtime PM autosuspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/init.c -->
