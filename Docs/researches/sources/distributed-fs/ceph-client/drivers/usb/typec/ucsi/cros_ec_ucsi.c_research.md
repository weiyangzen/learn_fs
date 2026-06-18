# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/cros_ec_ucsi.c

Purpose: Implements a UCSI transport for ChromeOS EC devices that expose a Platform Policy Manager through EC host commands and PD event notifications.

Important APIs/types/functions: `struct cros_ucsi_data` stores the EC device, UCSI core instance, notifier, work items, timeout counter, and completion/flag fields. `cros_ucsi_read`, `cros_ucsi_async_control`, and `cros_ucsi_sync_control` implement `ucsi_operations`. `cros_ucsi_event` receives ChromeOS PD notifications, `cros_ucsi_work` reads CCI and calls `ucsi_notify_common`, and `cros_ucsi_write_timeout` attempts recovery from stuck/busy PPM writes.

Control flow and state: probe finds the parent EC, creates a UCSI core instance, stores private data, registers a ChromeOS USB-PD notifier, and calls `ucsi_register`. EC `PD_EVENT_PPM` schedules work to read CCI and notify the core. `PD_EVENT_INIT` is treated like resume to re-enable PPM communication. Synchronous control delegates to `ucsi_sync_control_common` and schedules timeout recovery on `-EBUSY` or `-ETIMEDOUT`.

Persistence behavior: state is in memory only: timeout counter, pending delayed work, and UCSI core state. It does not persist commands across unload; resume and late init rebuild notification state through `ucsi_resume`.

Dependencies/integration points: integrates with `cros_ec_cmd`, ChromeOS EC platform data, `cros_usbpd_register_notify`, platform/ACPI/OF matching, UCSI core ops, Type-C mode selection for partner altmodes, and PM callbacks.

Risks: EC messages are capped at 256 bytes, so future larger UCSI payloads would need changes. Timeout recovery depends on detecting CCI busy/complete state and may leave the PPM unresponsive after five retries. Work flushing in the notifier prevents stale reads but can add latency. Parent-device discovery differs for firmware-described and subdevice cases.

Test signals: EC command success/failure logs, notifier delivery for `PD_EVENT_PPM` and `PD_EVENT_INIT`, timeout recovery logs, suspend/complete resume behavior on LPC-backed ECs, altmode mode-selection start/delete, and hotplug role/power updates through the UCSI core.
