# sources/distributed-fs/ceph-client/drivers/spi/spi-amd.h

## Purpose

`spi-amd.h` is the common private header for AMD SPI front-ends. It defines the hardware version enum, common private-data structure, and shared probe helper used by the platform and PCI wrappers.

## Important APIs, types, and functions

- `enum amd_spi_versions` distinguishes `AMD_SPI_V1`, `AMD_SPI_V2`, and `AMD_HID2_SPI`.
- `struct amd_spi` stores the remapped register base, HID2 DMA physical and virtual addresses, hardware version, and cached speed.
- `amd_spi_probe_common(struct device *dev, struct spi_controller *host)` is declared for front-ends to initialize and register a controller.

## Control flow

The header has no direct control flow. Front-end probes allocate a `spi_controller` with `sizeof(struct amd_spi)`, initialize version and MMIO address, then call `amd_spi_probe_common()`.

## State and persistence behavior

The structure fields persist for the lifetime of the SPI controller. `speed_hz` caches the selected hardware speed; `dma_virt_addr` and `phy_dma_buf` are only meaningful for HID2.

## Dependencies and integration points

The header depends on SPI controller types and DMA address types through included kernel headers in users. It is included by `spi-amd.c` and `spi-amd-pci.c`.

## Risks and edge cases

- Version values start at 1 and are used both as enum constants and ACPI match data; changing them would affect platform probe behavior.
- All front-ends must initialize `io_remap_addr` and `version` before calling the common probe.
- HID2 DMA fields must remain unused or NULL for non-HID2 versions.

## Test signals

Compile both AMD source files together and verify platform and PCI probes pass the expected `enum amd_spi_versions` values into the common code.
