<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/lpc32xx_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/lpc32xx_ts.c

Purpose: platform driver for the NXP LPC32xx built-in resistive touchscreen controller. It programs the controller for automatic four-sample X/Y acquisition, reports single-touch coordinates through the input core, and manages controller clocking on open/close and suspend/resume.

Important APIs/types/functions: `struct lpc32xx_tsc` holds input, MMIO base, IRQ, and clock. `tsc_readl()`/`tsc_writel()` wrap raw MMIO. `lpc32xx_fifo_clear()`, `lpc32xx_ts_interrupt()`, `lpc32xx_setup_tsc()`, `lpc32xx_stop_tsc()`, `lpc32xx_ts_open()`, `lpc32xx_ts_close()`, `lpc32xx_ts_probe()`, `lpc32xx_ts_suspend()`, and `lpc32xx_ts_resume()` make up the lifecycle.

Control flow: probe maps registers, gets the clock, allocates input, requests IRQ, registers input, and marks the device wake-capable. Open enables the clock, configures FIFO threshold/sample size/timing/ranges, clears stale FIFO entries, and enables automatic capture. The IRQ handler detects FIFO overrun, otherwise pops up to four samples, normalizes inverted 10-bit X/Y values, and reports the average of samples 2 and 3 if the fourth sample still says pen-down; otherwise it reports release. Close disables auto mode and the clock. PM either enables IRQ wake or stops/restarts the controller depending on wake capability.

State and persistence: the only persistent host state is device handles and whether the input device is enabled. Hardware registers are reprogrammed on every open/resume. FIFO contents are intentionally discarded on overflow and setup.

Dependencies/integration: integrates with platform resources, MMIO, clock framework, OF compatible `nxp,lpc3220-tsc`, Linux input, IRQ wake, and LPC32xx controller register layout.

Risks and test signals: the handler reads `rv[3]` even when fewer than four samples were collected, so pen-up short FIFO paths should be scrutinized. Test clock enable failure, FIFO overrun clearing, coordinate inversion/range, suspend with no users, wake-enabled suspend, register timing values, and IRQ behavior under noisy pen-up transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/lpc32xx_ts.c -->
