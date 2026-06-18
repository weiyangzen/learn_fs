<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/keembay_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/keembay_wdt.c`

Purpose: Intel Keem Bay non-secure watchdog driver with separate timeout and threshold interrupts, secure-monitor interrupt clearing, and pretimeout support.

Important APIs, types, and functions: `struct keembay_wdt` holds watchdog core state, clock/rate, IRQs, and MMIO base. Writes go through `keembay_wdt_writel()`, which first writes `WDT_UNLOCK` to `TIM_SAFE`. Timeout and pretimeout registers are programmed from seconds times clock rate. Timeout ISR clears via SMC and calls `emergency_restart()`; threshold ISR disables pretimeout, clears via SMC, and notifies watchdog core.

Control flow: probe maps MMIO, gets clock rate, requests named `threshold` and `timeout` IRQs, initializes defaults, applies module timeout, writes timeout/pretimeout registers, registers watchdog, and stores drvdata. PM suspend stops an active watchdog, resume starts it.

State and persistence: timeleft is read from `TIM_WATCHDOG / rate`. Pretimeout register stores `timeout - pretimeout`; a threshold interrupt clears pretimeout to avoid repeated notifications. Clock is assumed enabled by default and is only read for rate.

Dependencies and integration points: depends on OF compatible `intel,keembay-wdt`, named IRQs, ARM SMCCC secure service `0x8200ff18`, watchdog core, emergency restart, and MMIO unlock protocol.

Risks and test signals: risks include secure monitor interrupt clearing failures, missing IRQ names, clock-rate mistakes, and pretimeout greater than timeout. Test threshold/timeout IRQ paths, SMC clear arguments, timeleft, suspend/resume, nowayout stop attempts, and timeout register overflow for high clock rates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/keembay_wdt.c -->
