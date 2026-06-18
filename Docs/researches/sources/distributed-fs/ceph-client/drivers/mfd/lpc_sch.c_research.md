# sources/distributed-fs/ceph-client/drivers/mfd/lpc_sch.c

Purpose: this PCI MFD driver supports Intel Poulsbo SCH, Tunnel Creek, Centerton, and Quark X1000 LPC/ILB devices, exposing SMBus, GPIO, and watchdog children from LPC decode registers.

Important APIs, types, and functions: `sch_chipset_info[]` provides per-chipset I/O sizes. `lpc_sch_get_io()` reads a config dword, checks the enable bit, and fills an I/O resource. `lpc_sch_populate_cell()` allocates a resource, calls `lpc_sch_get_io()`, and fills an `mfd_cell`. `lpc_sch_probe()` builds up to three cells: `isch_smbus`, `sch_gpio`, and `ie6xx_wdt`.

Control flow: probe attempts each possible child in order. Return `LPC_NO_RESOURCE` or `LPC_SKIP_RESOURCE` skips a cell without failing; negative errors abort. If every cell is skipped, probe returns `-ENODEV`. Remove calls `mfd_remove_devices()`.

State and persistence: there is no long-lived private data. Resources are devm-allocated and cell arrays are stack-local during registration. Hardware decode register state is only read, not modified.

Dependencies and integration points: PCI IDs, MFD core, ACPI headers, and child drivers for Intel SCH SMBus, GPIO, and watchdog. Cells set `ignore_resource_conflicts = true`, reflecting legacy firmware/ACPI overlap expectations.

Risks: decode-disabled or zero base registers lead to missing child devices; the driver intentionally tolerates that until all resources are absent. Stack-local `mfd_cell` data must be fully copied by MFD core, which is the expected API contract but a point worth remembering. Tests should exercise each chipset's resource sizes, disabled decode warnings, zero-base skips, all-disabled failure, and remove cleanup.
