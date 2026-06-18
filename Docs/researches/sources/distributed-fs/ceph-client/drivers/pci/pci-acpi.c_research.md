# sources/distributed-fs/ceph-client/drivers/pci/pci-acpi.c

## Purpose
Implements PCI/ACPI integration: PCI Firmware Specification DSM support, host bridge resource handling, `_HPX/_HPP` configuration programming, wake and power management, ACPI companion lookup, ACPI-backed MSI domains, and generic ECAM root scanning on ARM64/RISC-V.

## APIs, Types, And Functions
Defines `pci_acpi_dsm_guid` and many PCI core hooks: `pci_acpi_preserve_config()`, `pci_acpi_program_hp_params()`, `pciehp_is_native()`, `shpchp_is_native()`, PM notifier helpers, `acpi_pci_choose_state()`, `pci_set_acpi_fwnode()`, `pci_dev_acpi_reset()`, ACPI power/wakeup helpers, bus add/remove hooks, companion lookup hook registration, `pci_host_bridge_acpi_msi_domain()`, and architecture ECAM functions such as `pci_acpi_scan_root()`. Internal `_HPX` support uses type 0, 1, 2, and 3 record structs.

## Control Flow
Boot initialization honors FADT `NO_MSI` and `NO_ASPM`, then initializes ACPI PCI slots and hotplug. Host bridge setup evaluates DSMs to preserve boot config and optimize reset delays. `_HPX/_HPP` programming walks bridge ACPI scopes, decodes package records, and applies allowed PCI/PCIe register changes. Power helpers translate ACPI sleep states to PCI D-states, coordinate `_REG` config-space availability around D3cold, propagate wake to bridges/root buses, and decide when resume is required. Companion lookup uses an optional registered hook under an rwsem, otherwise searches ACPI children by `_ADR`. ACPI MSI lookup uses a registered fwnode provider callback to find an IRQ domain.

## State And Persistence
State includes host bridge flags (`preserve_config`, `ignore_reset_delay`, native hotplug/AER ownership), PCI device delays and wake flags, ACPI companion pointers, notifier registrations, `pci_acpi_find_companion_hook`, and `pci_msi_get_fwnode_cb`. Firmware methods may change hardware config/power state, but no disk state is written.

## Dependencies And Integration
Depends on ACPI core, PCI hotplug/slot code, PCI ECAM, IOMMU reset coordination, runtime PM, irqdomain/MSI, and PCI resource assignment. It plugs into PCI enumeration, PM callbacks in `pci-driver.c`, MSI domain discovery, host bridge scanning, and platform-specific ARM64/RISC-V root creation.

## Risks And Test Signals
Risks include malformed ACPI packages, over-broad `_HPX` register writes, wake propagation mistakes, D3cold `_REG` ordering, companion lookup races, firmware quirks around bridge D3 and reset delays, MSI disabling via FADT, and ECAM resources not reserved in ACPI namespace. Test signals include ACPI root scan, `_HPX/_HPP` record decoding, DSM preserve-config and delay functions, bridge hotplug wake from D3, `_RST` reset success/failure with IOMMU coordination, companion hook set/clear concurrency, FADT MSI/ASPM disabling, and ARM64/RISC-V ECAM mapping failure paths.
