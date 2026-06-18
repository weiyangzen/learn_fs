# Research: sources/distributed-fs/ceph-client/include/linux/pci-acpi.h

Purpose: `pci-acpi.h` bridges PCI core code with ACPI root bridges, power management, MCFG/ECAM lookup, slot and hotplug enumeration, device companions, and PCI-specific ACPI DSM functions.

Important APIs/types/functions: ACPI-enabled APIs include PM notifier add/remove helpers, `acpi_pci_root_get_mcfg_addr()`, `pci_mcfg_lookup()`, bridge-handle helpers, `struct acpi_pci_root_info`, `struct acpi_pci_root_ops`, resource probing, root bus creation, bus add/remove hooks, `pci_acpi_setup()`, slot/hotplug helpers, EDR notifier helpers, and companion lookup hook registration. `_DSM` function constants include preserve boot config, device name, power-on reset delay, and readiness durations.

Control flow and state: root bridge discovery builds `acpi_pci_root_info`, prepares resources, creates a PCI bus, and registers ACPI/PCI associations. Bus add/remove hooks manage companion and slot/hotplug state. Many functions compile to no-ops when relevant config options are disabled.

Dependencies and integration points: depends on `linux/acpi.h`, PCI root/host bridge code, ECAM ops, ACPI PM notifier infrastructure, hotplug, EDR, slot code, and DSM GUID handling.

Risks and test signals: risks include stale ACPI handles, wrong root-bus traversal, MCFG quirks not applied, no-op behavior hiding missing config, and hotplug slot leaks. Tests should cover ACPI and non-ACPI builds, root resource parsing, MCFG lookup quirks, companion setup/cleanup, hotplug enumeration/removal, and EDR notifier lifecycle.
