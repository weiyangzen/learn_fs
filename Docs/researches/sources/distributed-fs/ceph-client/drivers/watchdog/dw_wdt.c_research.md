# sources/distributed-fs/ceph-client/drivers/watchdog/dw_wdt.c

## Purpose
`dw_wdt.c` is the Synopsys DesignWare watchdog driver. It supports fixed or device-tree-provided TOP values, reset and pretimeout interrupt modes, optional reset control for stopping, debugfs register exposure, suspend/resume save-restore, and restart handling.

## Important APIs, types, and functions
`struct dw_wdt` holds registers, clocks, reset control, response mode, sorted timeout table, watchdog object, saved PM registers, and optional debugfs directory. Key functions include `dw_wdt_init_timeouts`, `dw_wdt_handle_tops`, `dw_wdt_set_timeout`, `dw_wdt_set_pretimeout`, `dw_wdt_start`, `dw_wdt_stop`, `dw_wdt_restart`, `dw_wdt_get_timeleft`, `dw_wdt_irq`, and `dw_wdt_drv_probe`.

## Control Flow
Probe maps MMIO, enables timer/APB clocks, obtains optional reset, sets reset mode, optionally registers a rising-edge IRQ for pretimeout, deasserts reset, builds timeout ranges, initializes the watchdog, and either adopts already-running hardware or programs a default timeout. Start selects a TOP, kicks the counter, and enables the watchdog. Pretimeout switches response mode to two-stage IRQ mode. Stop resets the block if reset control exists; otherwise it marks hardware running so the core keeps feeding.

## State and Persistence
The watchdog cannot always be stopped once started. Runtime state includes current response mode, sorted hardware timeout table, saved PM register values, and optional `WDOG_HW_RUNNING`. Hardware registers persist through software close unless reset is available.

## Dependencies and Integration Points
It depends on platform/OF binding `snps,dw-wdt`, timer and optional APB clocks, optional reset controller, optional IRQ, debugfs, PM callbacks, and watchdog pretimeout/restart framework.

## Risks and Test Signals
Risks include malformed `snps,watchdog-tops`, timeout sorting/rounding errors, two-stage timeleft accounting, IRQ status not cleared until ping, stop semantics without reset control, and clock/reset ordering. Tests should cover fixed/custom TOPs, running-at-probe adoption, pretimeout IRQ notification, restart, suspend/resume, debugfs registration, and no-reset nowayout-like behavior.
