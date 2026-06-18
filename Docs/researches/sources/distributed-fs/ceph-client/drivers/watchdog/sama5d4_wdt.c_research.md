<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sama5d4_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sama5d4_wdt.c

Purpose: watchdog-core driver for Atmel/Microchip SAMA5D4, SAM9X60, and SAMA7G5 watchdog timers, supporting hardware reset or software-reset interrupt modes.

Important APIs, types, and functions: `struct sama5d4_wdt` stores watchdog, MMIO base, mode and interrupt registers, last ping timestamp, IRQ need flag, and SAM9X60 capability flag. Key functions are timed `wdt_write()` helpers, start/stop/ping/set-timeout, IRQ handler, DT init, hardware init, probe, and suspend/resume.

Control flow: probe allocates state, detects SAM9X60-style hardware, maps registers, parses DT options (`atmel,watchdog-type`, idle/dbg halt), optionally requests IRQ for software reset, initializes timeout, detects already-running hardware, programs mode/load registers, sets nowayout and stop-on-unregister, registers, and stores drvdata. Writes respect a three-slow-clock delay after refresh. IRQ mode calls `emergency_restart()` on watchdog status. Suspend stops active watchdog; resume reinitializes registers and restarts if active.

State and persistence behavior: state includes cached mode/interrupt registers, last-ping jiffies, timeout, running bit from hardware, and suspend-time reinitialization. Hardware watchdog configuration may survive boot or suspend, and init tries to normalize it.

Dependencies and integration points: depends on AT91 watchdog register definitions, OF properties, IRQ mapping, watchdog core, jiffies delays, and emergency restart.

Risks and edge cases: writes too soon after ping violate hardware timing. Resume notes a FIXME because reinitialization also pings the watchdog. SAM9X60 and older WDT disable bits differ. Software-reset mode depends on IRQ availability.

Test signals: SAMA5D4 and SAM9X60 compatibles, software versus hardware reset mode, idle/dbg halt properties, write-delay compliance, already-running detection, suspend/resume, IRQ emergency restart, and timeout update while disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sama5d4_wdt.c -->
