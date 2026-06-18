<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rave-sp-wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rave-sp-wdt.c

Purpose: watchdog-core driver for the Zodiac Inflight Innovations RAVE Supervisory Processor MCU. It exposes the SP firmware watchdog through Linux watchdog APIs and also uses it as a high-priority restart handler.

Important APIs, types, and functions: `struct rave_sp_wdt_variant` captures protocol differences between legacy and RDU command layouts. `struct rave_sp_wdt` owns the `watchdog_device`, parent `struct rave_sp`, variant, and reboot notifier. Key functions are `rave_sp_wdt_exec()`, variant `configure()` and `restart()` helpers, `rave_sp_wdt_start()`, `rave_sp_wdt_stop()`, `rave_sp_wdt_ping()`, `rave_sp_wdt_set_timeout()`, `rave_sp_wdt_reboot_notifier()`, and `rave_sp_wdt_probe()`.

Control flow: probe allocates state, selects OF match data, reads an optional NVMEM `wdt-timeout`, initializes watchdog limits from the variant, registers a reboot notifier, starts the hardware unconditionally because previous state is unknown, then registers the watchdog. Start and timeout changes send SP configuration commands. Ping sends `RAVE_SP_CMD_PET_WDT`. Restart is split: a reboot notifier sends the UART/SP reset command during `SYS_DOWN`/`SYS_HALT`, while watchdog `.restart` only waits for the firmware-delayed reset.

State and persistence behavior: persistent runtime state is the watchdog core status, selected timeout, variant pointer, and SP transport handle. The optional NVMEM cell supplies an initial timeout. `WDOG_HW_RUNNING` is set after successful start, and `max_hw_heartbeat_ms` lets watchdog core keep the firmware-fed watchdog alive.

Dependencies and integration points: depends on the RAVE SP MFD command transport, OF match data, NVMEM consumer API, reboot notifier infrastructure, and watchdog core restart priority.

Risks and edge cases: reset cannot be issued from atomic restart context because SP communication may use UART, so notifier ordering is critical. Probe starts the watchdog before registration; registration failure must stop it. Variant command byte layouts differ, and the RDU timeout is 16-bit while legacy is 8-bit.

Test signals: boot with both compatibles, NVMEM and DT timeout override tests, watchdog start/stop/ping/set-timeout, registration-failure unwind, clean reboot/halt restart behavior, and SP command error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rave-sp-wdt.c -->
