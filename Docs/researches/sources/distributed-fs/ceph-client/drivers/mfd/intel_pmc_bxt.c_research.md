# sources/distributed-fs/ceph-client/drivers/mfd/intel_pmc_bxt.c

Purpose: Intel Broxton/Apollo Lake PMC MFD driver. It exposes PMC GCR helpers, registers SCU IPC, and creates child devices for P-unit IPC, iTCO watchdog, and telemetry resources described by a single ACPI device.

Important APIs/types/functions: exported `intel_pmc_gcr_read64()`, `intel_pmc_gcr_update()`, `intel_pmc_s0ix_counter_read()`, `intel_pmc_probe()`, sysfs stores `simplecmd` and `northpeak`, `struct intel_pmc_dev`, and MFD cells `intel_punit_ipc`, `iTCO_wdt`, `intel_telemetry`.

Control flow: probe allocates PMC state, parses ACPI platform resources into SCU IPC/GCR/P-unit/TCO/telemetry resources, registers SCU IPC, stores drvdata, then adds available child devices. GCR helpers serialize MMIO access with `gcr_lock`.

State and persistence: GCR MMIO state lives in hardware. The driver stores mapped GCR base, optional telemetry base, and SCU IPC handle. S0ix residency is read from hardware counters and converted from 19.2 MHz ticks.

Dependencies and integration: relies on ACPI ID `INT34D2`, SCU IPC core, MFD core, iTCO watchdog platform data, telemetry child driver, and platform resources exported by IFWI.

Risks: resource index assumptions are firmware-contract sensitive. TCO registration is skipped when ACPI WDAT exists. `intel_pmc_gcr_update()` reads back to verify masked writes, so hardware side effects or locking bugs surface as `-EIO`.

Test signals: ACPI resource parsing, sysfs IPC commands, S0ix counter reads, child device enumeration, watchdog presence/absence with WDAT, and concurrent GCR helper callers.
