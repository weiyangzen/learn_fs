# sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse-smbus.c

`psmouse-smbus.c` bridges PS/2 devices to SMBus/I2C companion devices. It tracks pending/active companions, creates I2C clients on host-notify-capable adapters, suppresses PS/2 event reporting, and rescans serio when adapters or clients appear/disappear.

`struct psmouse_smbus_dev` stores board info, owner `psmouse`, client, list node, dead flag, and deactivation policy. Public APIs are `psmouse_smbus_init()`, `psmouse_smbus_cleanup()`, module init, and module exit. Init installs dummy packet/reconnect/disconnect callbacks, disables resync, scans current adapters, and optionally leaves breadcrumbs for future adapter notifications. Disconnect marks companions dead and schedules asynchronous I2C removal to avoid psmouse mutex deadlocks.

State is a global mutex/list/workqueue/notifier plus per-companion objects. Dependencies are I2C bus notifiers, host notify, device links, workqueues, serio rescans, and psmouse callbacks. Risks are opportunistic adapter scanning, I2C removal races, stale breadcrumbs, platform data cleanup, and non-fatal device-link failures. Test signals include delayed adapter arrival, client creation, `-EAGAIN` breadcrumb behavior, PS/2 suppression, async unregister, client-removal rescan, and failed-init cleanup.
