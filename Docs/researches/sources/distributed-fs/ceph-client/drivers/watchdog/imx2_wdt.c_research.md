<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx2_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/imx2_wdt.c`

Purpose: watchdog driver for i.MX2 and later NXP/Freescale watchdog blocks. It supports many OF compatibles, internal or external reset routing, optional pretimeout IRQs, suspend/resume handling, and restart.

Important APIs, types, and functions: `struct imx2_wdt_device` holds the clock, regmap, watchdog core device, match data, and policy flags. `imx2_wdt_setup()` writes WCR once-only low-power/reset bits and enables the watchdog; `imx2_wdt_ping()` writes the `0x5555`/`0xAAAA` service sequence; `imx2_wdt_set_pretimeout()` programs WICR; `imx2_wdt_restart()` writes WCR three times for the i.MX6Q SRS erratum.

Control flow: probe maps registers through regmap, gets/enables the clock, requests an IRQ when present to enable pretimeout reporting, reads reset status, parses `fsl,ext-reset-output` and `fsl,suspend-in-wait`, initializes watchdog core values, marks already-running hardware, clears WMCR, and registers. Start either updates a running watchdog or performs full setup; shutdown stretches timeout to the 128 second hardware maximum and pings; PM paths stretch/restart the watchdog around sleep depending on SoC behavior.

State and persistence: watchdog enable can persist from boot firmware and is marked with `WDOG_HW_RUNNING`. The hardware cannot be stopped through watchdog core because no stop op is provided. User timeout may exceed hardware heartbeat; the driver clamps actual hardware timeout to `IMX2_WDT_MAX_TIME` while retaining the requested logical timeout for core supervision.

Dependencies and integration points: depends on OF match data for WDW support, a clock, regmap MMIO, optional interrupt, watchdog core ping-on-suspend helpers, and restart priority 128. Reset routing is controlled by devicetree properties.

Risks and test signals: risks include incorrect low-power behavior, mismatched external reset wiring, pretimeout count conversion, and firmware-left-running watchdogs. Test all compatible data paths, IRQ pretimeout notification, suspend/resume for i.MX7D versus other SoCs, shutdown timeout extension, and restart reset assertion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx2_wdt.c -->
