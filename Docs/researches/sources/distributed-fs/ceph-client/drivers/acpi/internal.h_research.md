# sources/distributed-fs/ceph-client/drivers/acpi/internal.h

Purpose: `internal.h` is the private ACPI subsystem header for infrastructure code, not general drivers. It declares cross-file initialization hooks, scan/hotplug helpers, power-resource APIs, EC internals, sleep hooks, property parsing, watchdog/LPIT hooks, and MIPI CSI-2 graph helpers.

Important APIs, types, and functions: notable declarations include ACPI init functions (`acpi_scan_init()`, `acpi_processor_init()`, `acpi_platform_init()`), PCI/IOAPIC hooks, hotplug scheduling functions, device-object setup/removal functions, power-resource operations, EC definitions (`enum acpi_ec_event_state`, `struct acpi_ec`, `first_ec`, EC helper prototypes), sleep/NVS hooks, property helpers, and MIPI helpers such as `acpi_mipi_check_crs_csi2()` and `acpi_graph_ignore_port()`.

Control flow: the header has no runtime flow, but conditional compilation selects real declarations or inline stubs based on configuration. This lets ACPI core files call optional subsystem hooks without scattering ifdefs through call sites.

State and persistence: it exposes internal shared state such as `acpi_root`, `acpi_bus_id_list`, `first_ec`, and per-device structures managed elsewhere. `struct acpi_ec` defines the EC driver's mutex, spinlock, waitqueue, current transaction pointer, work item, event counters, query counters, and polling state.

Dependencies and integration: this file is the internal contract among ACPI scan, PCI, processor, EC, thermal, sleep, property, watchdog, LPIT, IOAPIC, and MIPI DisCo code. It depends on kernel ACPI and ID allocator definitions.

Risks: because it is private but widely included, changes can silently affect many ACPI compilation units. Stub behavior must match real behavior enough that callers remain correct across configs. The EC struct couples `ec.c` tightly to declarations here, so layout changes need full EC lifecycle review.

Test signals: build matrix coverage across ACPI feature configs, especially `CONFIG_ACPI_EC`, `CONFIG_PM_SLEEP`, `CONFIG_PCI`, `CONFIG_X86`, `CONFIG_ACPI_HOTPLUG_IOAPIC`, and MIPI-related paths. Static analysis should catch stale prototypes and mismatched stubs.
