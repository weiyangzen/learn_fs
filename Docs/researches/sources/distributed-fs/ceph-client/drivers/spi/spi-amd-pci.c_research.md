# sources/distributed-fs/ceph-client/drivers/spi/spi-amd-pci.c

## Purpose

`spi-amd-pci.c` is a PCI front-end for the AMD HID2 SPI controller. It discovers the SPI register window through an AMD LPC bridge PCI configuration register, maps the HID2 SPI aperture, sets version/bus metadata, and delegates registration to the shared AMD SPI implementation.

## Important APIs, types, and functions

- PCI ID table matches AMD vendor ID and LPC bridge device ID `0x1682`.
- `amd_spi_pci_probe()` allocates a SPI controller, reads config dword `0xA0`, masks the base address, adds `AMD_HID2_PCI_BAR_OFFSET`, maps `AMD_HID2_MEM_SIZE`, sets `AMD_HID2_SPI`, assigns bus number 2, and calls `amd_spi_probe_common()`.
- The module is registered with `module_pci_driver()`.

## Control flow

PCI core invokes probe for the LPC bridge. The probe path creates the controller and private `struct amd_spi`, maps the hardware, marks it as HID2, and reuses the common AMD SPI setup from `spi-amd.c`.

## State and persistence behavior

The front-end holds no independent mutable state after probe. Mapped IO and controller allocation are device-managed. Hardware state is managed by common AMD SPI code.

## Dependencies and integration points

The file depends on PCI, SPI framework, and `spi-amd.h`. It integrates with `amd_spi_probe_common()` exported by `spi-amd.c`, and is built together with it by `CONFIG_SPI_AMD`.

## Risks and edge cases

- The base address is read from PCI config rather than a normal BAR resource, so platform firmware correctness is critical.
- `devm_ioremap()` maps a physical address directly after masking and offsetting; there is no request-region protection in this wrapper.
- The bus number is fixed to 2, unlike the ACPI platform path using bus 0.

## Test signals

PCI enumeration on supported AMD hardware should show the `amd_spi_pci` driver binding, a mapped HID2 aperture, and successful controller registration. Build tests should ensure `spi-amd.o` exports `amd_spi_probe_common()` for this object.
