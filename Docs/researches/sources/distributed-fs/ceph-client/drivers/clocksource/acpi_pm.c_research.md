# sources/distributed-fs/ceph-client/drivers/clocksource/acpi_pm.c

Purpose: registers the ACPI PM timer as a 24-bit continuous clocksource using an I/O port discovered by platform setup or overridden on the command line.

Important APIs/types/functions: exports `pmtmr_ioport`, `acpi_pm_read_verified()`, suspend/resume callback registration helpers, `clocksource_acpi_pm`, `init_acpi_pm_clocksource()`, and `parse_pmtmr()`.

Control flow: early PCI fixups may lower rating and switch reads to a verified multi-read workaround. `fs_initcall` validates monotonicity, optional PIT-rate sanity, and then registers the clocksource at `PMTMR_TICKS_PER_SEC`.

State and persistence: global I/O port, optional callback pointer/data, and mutable clocksource read/rating fields persist for runtime. The hardware counter is free-running and not reset here.

Dependencies and integration points: depends on ACPI PM timer definitions, x86 I/O port access, PCI chipset fixups, optional PIT calibration, and clocksource suspend/resume hooks.

Risks: broken chipsets require triple-read verification and lower performance. Invalid BIOS timer rates disable the source. Callback registration is unguarded and assumes controlled users. `pmtmr=` can override firmware-provided ports.

Test signals: PM timer monotonicity checks at boot, `acpi_pm_good`/`pmtmr=` command-line paths, suspend/resume callback invocation, and chipset blacklist/graylist coverage.
