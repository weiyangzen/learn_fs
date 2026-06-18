# sources/distributed-fs/ceph-client/drivers/soc/xilinx/zynqmp_power.c

## Purpose
Implements the Xilinx Zynq UltraScale+ MPSoC and Versal power-management platform driver. It receives firmware-originated suspend, shutdown, and subsystem-restart events through the Xilinx event manager, an IPI mailbox, or a legacy interrupt path, then translates those callbacks into Linux poweroff, suspend-to-RAM, or restart actions. It also exposes a `suspend_mode` sysfs knob that programs the platform firmware suspend mode.

## Important APIs, Types, and Functions
Important local types are `struct zynqmp_pm_work_struct`, which wraps a work item plus callback arguments, and `struct zynqmp_pm_event_info`, a devres-managed record for firmware event registrations. The central entry points are `zynqmp_pm_probe()` and `zynqmp_pm_remove()`. Callback and bottom-half paths include `suspend_event_callback()`, `subsystem_restart_event_callback()`, `ipi_receive_callback()`, `zynqmp_pm_isr()`, `zynqmp_pm_init_suspend_work_fn()`, and `zynqmp_pm_subsystem_restart_work_fn()`. Sysfs handlers are `suspend_mode_show()` and `suspend_mode_store()`. `register_event()` and `unregister_event()` wrap `xlnx_register_event()` / `xlnx_unregister_event()` for devres cleanup.

## Control Flow
Probe first checks the PM firmware API version against `ZYNQMP_PM_VERSION`. It prefers event-manager registration for `PM_INIT_SUSPEND_CB`; when that succeeds it also queries family info and registers `PM_NOTIFY_CB` for `EVENT_SUBSYSTEM_RESTART` on the correct ACPU node for Versal or Versal Net. If the event manager is unavailable with `-EACCES` or `-ENODEV`, probe falls back to a DT `mboxes` receive channel with `ipi_receive_callback()`, or a threaded IRQ with `zynqmp_pm_isr()`. Suspend/shutdown callbacks queue work on `system_dfl_wq`; the work function calls `orderly_poweroff(true)` for shutdown reasons and `pm_suspend(PM_SUSPEND_MEM)` for power requests. Subsystem restart work first narrows firmware shutdown scope with `zynqmp_pm_system_shutdown(...SETSCOPE_ONLY, ...SUBSYSTEM)` and then calls `kernel_restart(NULL)`.

## State and Persistence Behavior
Global runtime state is small: pointers to the suspend and restart work objects, one global mailbox receive channel, and the selected `suspend_mode`. Event-manager registrations persist through devres records and unregister automatically through `unregister_event()`. The sysfs `suspend_mode` value is in-memory only, but storing a new value immediately calls `zynqmp_pm_set_suspend_mode()` so the firmware state changes with it. Work items retain the last copied firmware callback arguments only until their queued bottom halves execute. The driver does not persist anything to disk.

## Dependencies and Integration Points
The driver depends on the Xilinx ZynqMP firmware API (`xlnx-zynqmp.h`), the Xilinx event manager, mailbox IPI messages, OF platform probing, Linux suspend/reboot APIs, and sysfs device attributes. Its DT match is `xlnx,zynqmp-power`. It integrates with system power management by converting PMU firmware callbacks into generic Linux `pm_suspend()`, `orderly_poweroff()`, and `kernel_restart()` requests.

## Risks
The removal path appears to call `mbox_free_channel(rx_chan)` only when `rx_chan` is false, which is likely inverted and can leak a requested channel or attempt to free `NULL`. The mailbox callback copies `sizeof(msg->len)` bytes from `msg->data` into the payload array rather than using the callback payload size, so callback parsing depends on the mailbox message layout. The global work pointers and global `rx_chan` make multiple instances unsafe. Event-manager callbacks drop events while work is already pending, so repeated firmware notifications may coalesce without payload queuing. Suspend/restart actions are privileged and system-wide; bad firmware callback data directly affects machine power state.

## Test Signals
Useful checks include probing with event manager available, probing through mailbox fallback, probing through interrupt fallback, sysfs show/store of `standard` and `power-off`, firmware callback delivery for `SUSPEND_SYSTEM_SHUTDOWN` and `SUSPEND_POWER_REQUEST`, subsystem restart event delivery on Versal and Versal Net node IDs, error paths for unsupported PM API/family, module remove with an active mailbox channel, and suspend/restart behavior under repeated callback storms.
