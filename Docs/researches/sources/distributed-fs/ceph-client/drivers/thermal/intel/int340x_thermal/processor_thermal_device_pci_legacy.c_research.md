# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device_pci_legacy.c

## Purpose

`processor_thermal_device_pci_legacy.c` is the PCI frontend for older Processor Thermal Devices. It combines the common ACPI processor thermal zone with optional legacy SoC DTS sensors and optional MMIO RAPL/workload support.

## Important APIs, Types, and Functions

`proc_thermal_pci_probe()` enables the PCI device, allocates `struct proc_thermal_device`, calls `proc_thermal_add()`, optionally initializes IOSF DTS sensors for Braswell, and calls `proc_thermal_mmio_add()`. `proc_thermal_pci_msi_irq()` forwards MSI interrupts to `intel_soc_dts_iosf_interrupt_handler()`. PM callbacks delegate to common suspend/resume.

## Control Flow

Probe must complete the common ACPI path first. For BSW, it attempts auxiliary IOSF DTS enumeration and MSI IRQ registration but does not fail the whole driver if auxiliary DTS support is absent. MMIO features are added after DTS setup. Remove exits DTS/MSI, removes MMIO features, and unregisters the common thermal zone.

## State and Persistence Behavior

Per-device state is the common `proc_thermal_device`; auxiliary DTS state lives in `proc_priv->soc_dts`. MSI IRQ state is tied to the PCI device and freed on remove. No file persistence exists.

## Dependencies and Integration Points

It depends on PCI, ACPI processor thermal core, optional IOSF SoC DTS, MSI, and feature flags from `processor_thermal_device.h`. PCI IDs cover Haswell/Broadwell/Baytrail/Braswell/Broxton/Cannonlake/CoffeeLake/GeminiLake/IceLake/JasperLake/Skylake/TigerLake.

## Risks and Test Signals

Risks include auxiliary DTS failure being intentionally nonfatal, an empty `else` branch for non-BSW devices, ordering of `pci_set_drvdata()` relative to common setup, and MMIO add failure after DTS setup. Test signals include BSW MSI DTS interrupt handling, non-BSW probe, MMIO RAPL feature IDs, suspend/resume delegation, and remove cleanup after partial auxiliary setup.
