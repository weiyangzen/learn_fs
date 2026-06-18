# sources/distributed-fs/ceph-client/drivers/spi/spi-intel-pci.c

## Purpose

`spi-intel-pci.c` is the PCI front-end for the Intel PCH/PCU SPI flash controller. It matches Intel PCI IDs, maps BAR 0, provides board-specific controller type data, optionally exposes a PCI config-space write-protect override, and delegates all real SPI flash behavior to `intel_spi_probe()` in `spi-intel.c`.

## Important APIs, Types, and Functions

`intel_spi_pci_set_writeable()` toggles the BIOS Control Register write-protect-disable bit (`BCR_WPD`) when the core requests write access. `bxt_info` and `cnl_info` are `struct intel_spi_boardinfo` instances carrying controller type and the set-writeable callback. `intel_spi_pci_probe()` enables the PCI device, duplicates matched boardinfo, stores the PCI device in `info->data`, maps BAR 0 with `pcim_iomap_region()`, and calls `intel_spi_probe()`.

## Control Flow

The PCI ID table maps many Intel device IDs to BXT or CNL-style controller info. On probe, pcim/devm management handles device and mapping lifetime. The shared core then initializes registers, registers a spi-mem controller, and creates SPI NOR child devices. PCI driver `dev_groups` points at `intel_spi_groups`, so sysfs attributes from the core appear on PCI devices.

## State and Persistence Behavior

This file has no independent long-lived state beyond devm-duplicated boardinfo and PCI-managed mappings. Persistent effects are possible only through the core's flash writes and through setting `BCR_WPD` in PCI config space, which can make BIOS flash writeable until firmware/platform policy changes it.

## Dependencies and Integration Points

The file depends on PCI core managed APIs, Intel PCI IDs, `spi-intel.h`, and platform data definitions from `linux/platform_data/x86/spi-intel.h`. It exports no SPI callbacks itself; all SPI integration is delegated to `spi-intel.c`.

## Risks and Edge Cases

Writeability depends on platform firmware honoring `BCR_WPD`; if the bit cannot be set, the core reports BIOS lock state. Device ID to controller-type mapping is critical because register offsets differ between BXT and CNL. BAR mapping failures or incorrect resource sizing stop probe before the core sees the device.

## Test Signals

Test representative BXT and CNL PCI IDs, BAR0 mapping failure, `writeable=1` with BCR_WPD settable and locked cases, sysfs attribute presence via `dev_groups`, and smoke tests that `intel_spi_probe()` receives the correct boardinfo type and PCI device data.
