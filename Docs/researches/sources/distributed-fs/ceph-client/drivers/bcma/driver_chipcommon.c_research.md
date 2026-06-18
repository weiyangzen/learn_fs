# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon.c

Purpose: this file implements the BCMA ChipCommon core driver, handling common chip capabilities, flash detection, PMU handoff, GPIO register helpers, watchdog registration, LED timing, and MIPS UART discovery.

Important APIs, types, and functions: exported or cross-file APIs include `bcma_chipco_get_alp_clock`, `bcma_chipco_watchdog_register`, `bcma_core_chipcommon_early_init`, `bcma_core_chipcommon_init`, `bcma_chipco_watchdog_timer_set`, `bcma_chipco_irq_mask`, `bcma_chipco_irq_status`, `bcma_chipco_gpio_in`, `bcma_chipco_gpio_out`, `bcma_chipco_gpio_outen`, `bcma_chipco_gpio_control`, `bcma_chipco_gpio_intmask`, `bcma_chipco_gpio_polarity`, `bcma_chipco_gpio_pullup`, `bcma_chipco_gpio_pulldown`, and conditionally `bcma_chipco_serial_init`.

Control flow: early init initializes the GPIO spinlock, reads ChipCommon status/capability registers, initializes PMU early when present, detects flash for SoC hosts, and guards with `early_setup_done`. Full init calls early init, configures pullup/pulldown defaults for selected chips, initializes PMU and reports unimplemented power-control support, writes LED duty-cycle timing from SPROM or defaults, computes watchdog ticks per millisecond, and marks setup done. Watchdog registration builds `struct bcm47xx_wdt` callbacks and registers a platform device unless the chip has a known broken watchdog. Flash detection dispatches to serial, parallel, or NAND init based on capability bits and revision/chip ID. GPIO helpers use a shared masked-write helper under `gpio_lock` for mutable GPIO registers.

State and persistence: `struct bcma_drv_cc` stores capabilities, status, PMU state, flash descriptors, GPIO spinlock, watchdog platform device, serial port descriptors, and setup flags. Hardware registers persist the configured pullups, LED timer, IRQ masks, GPIO state, and watchdog value.

Dependencies and integration points: it integrates with PMU code, flash platform devices, bcm47xx watchdog platform data, GPIO driver code, SPROM data, MIPS serial init, BCMA register accessors, and SoC host detection.

Risks: chip-specific watchdog and clock quirks are easy to regress. Flash init is deliberately early and only prepares platform devices because full device registration is not safe yet. GPIO masked writes require locking to avoid read/modify/write races. Serial init is limited by ChipCommon revision and assumes UART register spacing.

Test signals: boot logs for flash detection, watchdog device registration, GPIO operation, serial console availability on MIPS, and absence of timeout/error logs during PMU/watchdog setup are key signals.
