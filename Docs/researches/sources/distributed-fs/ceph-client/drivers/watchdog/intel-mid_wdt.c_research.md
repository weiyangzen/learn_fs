<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/intel-mid_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/intel-mid_wdt.c`

Purpose: Intel MID SCU watchdog driver for Merrifield-like platforms where watchdog control is performed through Intel SCU IPC and a warning IRQ panics the kernel.

Important APIs, types, and functions: `struct mid_wdt` stores watchdog core state, device pointer, and SCU IPC device. `wdt_command()` wraps `intel_scu_ipc_dev_command_with_size()`. `wdt_start()` sends `SCU_WATCHDOG_START` with pretimeout and timeout dwords, `wdt_ping()` sends keepalive, and `wdt_stop()` sends stop. `mid_wdt_irq()` calls `panic("Kernel Watchdog")`.

Control flow: probe requires platform data, runs optional platform probe hook, initializes watchdog core bounds, forces nowayout, obtains the SCU IPC device, requests the warning IRQ with `IRQF_NO_SUSPEND`, starts the watchdog immediately to override firmware/U-Boot defaults, marks `WDOG_HW_RUNNING`, and registers the watchdog.

State and persistence: firmware may leave the watchdog running with unknown thresholds, so probe deliberately restarts it with deterministic values. There is no set_timeout op even though `WDIOF_SETTIMEOUT` is advertised; timeout range is fixed in the device structure. Nowayout is always forced.

Dependencies and integration points: depends on Intel MID platform data, SCU IPC platform APIs, watchdog core, panic path, and IRQ routing for warning/pretimeout.

Risks and test signals: risks include IPC command size quirks, panic-on-warning behavior, missing platform data, and inability to read hardware state. Test SCU IPC start/stop/ping returns, IRQ panic delivery, probe-defer for SCU IPC, deterministic restart after firmware, and watchdog daemon interaction under nowayout.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/intel-mid_wdt.c -->
