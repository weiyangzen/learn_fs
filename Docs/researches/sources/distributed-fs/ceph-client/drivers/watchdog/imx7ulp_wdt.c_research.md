<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx7ulp_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/imx7ulp_wdt.c`

Purpose: watchdog driver for i.MX7ULP, i.MX8ULP, and i.MX93 style watchdogs with unlock/update handshakes, LPO clock selection, variant-specific prescaling, and noirq PM.

Important APIs, types, and functions: `struct imx7ulp_wdt_device` stores MMIO, clock, reset mode, watchdog core device, and `struct imx_wdt_hw_feature`. `imx7ulp_wdt_wait_ulk()` and `imx7ulp_wdt_wait_rcs()` poll unlock and reconfiguration completion. `_imx7ulp_wdt_enable()` and `_imx7ulp_wdt_set_timeout()` disable local IRQs around the unlock-write window. `imx7ulp_wdt_init()` configures CS/TOVAL with retry verification.

Control flow: probe maps registers, enables the clock, reads `fsl,ext-reset-output`, initializes core timeout bounds, associates match data, configures the hardware while preserving already-enabled state, and registers. Start/stop call the enable wrapper with retry; set_timeout writes `TOVAL`; restart enables the watchdog, sets a one-second timeout, then spins until reset. Suspend_noirq stops an active watchdog and disables the clock; resume_noirq reenables the clock and restores/feeds active watchdogs.

State and persistence: active hardware at probe is marked `WDOG_HW_RUNNING` and kept enabled. The CS update bits and TOVAL are verified after each retry, reducing exposure to missed unlock windows. Variant data changes clock-rate conversion, prescaler usage, and post-RCS delay.

Dependencies and integration points: depends on OF compatibles `fsl,imx7ulp-wdt`, `fsl,imx8ulp-wdt`, `fsl,imx93-wdt`, a clock, MMIO, watchdog core, and noirq system sleep callbacks.

Risks and test signals: risks include timeout conversion mismatches for i.MX93 prescaler, failing unlock/RCS polling, local IRQ latency requirements, and restart spinning if reset does not occur. Test repeated start/stop/set_timeout under load, suspend/resume, external reset configuration, already-running boot state, and retry failure paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imx7ulp_wdt.c -->
