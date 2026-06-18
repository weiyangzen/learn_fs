# sources/distributed-fs/ceph-client/drivers/acpi/acpi_watchdog.c

Purpose: parses ACPI WDAT and creates a `wdat_wdt` platform device when firmware advertises a usable ACPI watchdog. It also lets native watchdog drivers determine whether ACPI WDAT should take ownership.

Important APIs/functions: `acpi_has_watchdog` is exported to drivers; `acpi_watchdog_init` performs init-time platform-device creation; `acpi_watchdog_get_wdat` handles ACPI-disabled, boot-parameter, table lookup, and RTC-SRAM exclusion checks; `acpi_watchdog_uses_rtc` scans WDAT GAS entries for RTC I/O ports when `CONFIG_RTC_MC146818_LIB` is enabled; `disable_acpi_watchdog` handles `acpi_no_watchdog`.

Control flow: init obtains WDAT, quietly exits if absent, rejects BIOS-disabled tables, skips legacy PCI WDT descriptors, converts system-memory and system-I/O WDAT register regions to resources, merges overlapping resources, copies them to an array, registers `wdat_wdt`, and releases resources/table references.

State and persistence: `acpi_no_watchdog` persists the boot override. WDAT table pointers are temporary and should be released with `acpi_put_table`. The persistent result is a platform device with I/O or memory resources.

Dependencies and integration: depends on ACPI table APIs, resource-list helpers, `platform_device_register_simple`, IORESOURCE flags, and optional RTC port definitions. Native watchdog drivers can call `acpi_has_watchdog`; the watchdog subsystem binds the created `wdat_wdt` device.

Risks: `acpi_has_watchdog` obtains a WDAT pointer through `acpi_watchdog_get_wdat` but does not release it, so table reference semantics deserve audit. Unsupported address spaces abort registration. Without RTC library support, RTC-backed WDAT exclusion is compiled out. Resource merging must preserve separate I/O versus memory ranges.

Test signals: no WDAT, disabled WDAT, RTC-backed WDAT, legacy PCI WDAT, valid I/O and memory WDAT, overlapping resources, unsupported address spaces, platform-device registration failure, `acpi_no_watchdog`, and leak/refcount checks around repeated `acpi_has_watchdog` calls.
