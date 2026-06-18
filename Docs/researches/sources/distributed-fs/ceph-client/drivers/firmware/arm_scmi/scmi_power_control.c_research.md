# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/scmi_power_control.c

Purpose: This SCMI driver consumes System Power notifications and turns platform-originated graceful shutdown, reboot, and suspend requests into Linux system transitions.

Important APIs/types/functions: `enum scmi_syspower_state` tracks idle, in-progress, and rebooting. `struct scmi_syspower_conf` stores device pointer, state mutex, requested transition, SCMI userspace notifier, reboot notifier, delayed forceful work, and suspend work. Key functions are `scmi_userspace_notifier()`, `scmi_request_graceful_transition()`, `scmi_reboot_notifier()`, `scmi_forceful_work_func()`, `scmi_request_forceful_transition()`, `scmi_syspower_probe()`, and `scmi_system_power_resume()`.

Control flow: Probe acquires the SCMI System protocol, allocates driver state, initializes suspend work, and registers an event notifier for `SCMI_EVENT_SYSTEM_POWER_STATE_NOTIFIER`. On notification, the driver rejects unsupported states and forceful platform requests, ignores duplicate or late events, records the requested transition, and invokes orderly poweroff/reboot or schedules suspend. If firmware provided a timeout for graceful shutdown, it registers a reboot notifier and schedules delayed work at 75 percent of the timeout; if a matching reboot begins, the delayed work is canceled, otherwise the worker unregisters the notifier and calls the kernel forceful transition path.

State and persistence: State is per driver instance and protected by `state_mtx`. The SCMI core is expected to instantiate only one System Power device. Resume resets state to idle. No state is persisted across reboot or suspend beyond normal kernel memory.

Dependencies and integration points: It uses the SCMI bus driver model, SCMI notify ops, reboot notifier chain, orderly power APIs, `pm_suspend()`, delayed work, and emergency sync in built-in builds. It integrates with `system.c`, which supplies the protocol event decoder.

Risks and edge cases: Forceful notifications from firmware are ignored by design. The timeout path unregisters the reboot notifier while holding state mutex; the code comments call this out to avoid deadlock. If userspace is unavailable, `orderly_poweroff(true)` can still force shutdown. Duplicate notifications are ignored once state is not idle. Suspend is scheduled asynchronously and does not use the forceful timeout mechanism.

Test signals: Use synthetic System Power notifications for shutdown, cold reset, warm reset, suspend, unsupported states, duplicate events, and forced notifications. Verify reboot notifier cancellation, delayed forceful fallback timing, resume resetting state, and that only one SCMI system-power driver binds.
