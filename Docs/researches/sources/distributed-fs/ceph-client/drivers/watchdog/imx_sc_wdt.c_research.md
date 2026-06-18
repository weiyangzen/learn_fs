<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx_sc_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/imx_sc_wdt.c`

Purpose: NXP i.MX system-controller watchdog driver that delegates watchdog operations to SC firmware through ARM SMCCC calls and uses SCU IRQ notifications for pretimeout.

Important APIs, types, and functions: `struct imx_sc_wdt_device` embeds `watchdog_device` and a notifier block. `imx_sc_wdt_start()`, stop, ping, timeout, and pretimeout functions send `IMX_SIP_TIMER` SMC subcommands. `imx_sc_wdt_is_running()` probes by attempting start and undoing it when Linux successfully started it. `imx_sc_wdt_notify()` maps SCU watchdog IRQ events to `watchdog_notify_pretimeout()`.

Control flow: probe initializes the watchdog, sets default timeout in firmware, detects running firmware state, enables stop-on-reboot/unregister, attempts to enable SCU watchdog IRQ group and register a notifier, conditionally advertises pretimeout, then registers the watchdog. Operations are thin firmware RPCs and convert nonzero firmware return values to `-EACCES`.

State and persistence: the authoritative watchdog state is in SC firmware, not Linux registers. Firmware may already have the watchdog running, represented with `WDOG_HW_RUNNING`. Pretimeout programming uses `timeout - pretimeout` because firmware interprets the value relative to current timestamp.

Dependencies and integration points: depends on ARM SMCCC, NXP SCU firmware/IRQ APIs, OF compatible `fsl,imx-sc-wdt`, watchdog core, and firmware support for the timer SIP service.

Risks and test signals: risks include firmware semantic changes, probing by start/stop causing side effects, inability to stop due to permission, and pretimeout conversion errors. Test SMC failure handling, already-running detection, notifier registration cleanup, pretimeout delivery, and stop-on-reboot/unregister with firmware traces.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx_sc_wdt.c -->
