<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se30_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se30_wdt.c`

Purpose: Lenovo SE30 watchdog driver for DMI-matched systems using an NCT6692-based shared-memory host interface discovered through Super I/O.

Important APIs, types, and functions: Super I/O helpers enter/exit config mode and read chip/base registers. `shm_get_ready()` programs module/cmd/select fields, issues read control, and waits for ID change. `read_shm_win()` and `write_shm_win()` access the SHM data window. `lenovo_se30_wdt_enable()` writes reset config and watchdog count; ping disables, writes count, then re-enables because active refresh is unsupported.

Control flow: module init creates a platform device from DMI matches. Probe verifies chip ID mask, reads SHM base from LDN 0x0F, reserves and maps the SHM region, initializes watchdog register descriptors, sets bounds and nowayout, installs stop-on-reboot/unregister, and registers.

State and persistence: watchdog timeout is an 8-bit count in the board controller, with no bootstatus tracking. The active watchdog cannot be refreshed in-place; ping briefly disables and re-enables it. If SHM readiness times out, read returns zero timeleft or write returns error.

Dependencies and integration points: depends on Lenovo DMI product names 11NA/11NB/11NC/11NH/11NJ/11NK, Super I/O ports, MMIO SHM window, watchdog core, and NCT6692 host-interface semantics.

Risks and test signals: risks include ping disable/enable race, SHM ready timeout, invalid base address, DMI matching drift, and no `.set_timeout` op despite advertising `WDIOF_SETTIMEOUT`. Test DMI platform creation, SHM base validation, start/stop/ping sequences, timeleft reads, and behavior during reboot/unregister.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se30_wdt.c -->
