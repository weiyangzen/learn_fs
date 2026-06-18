# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_pci_ids.h

## Purpose

`gpib_pci_ids.h` supplies fallback vendor/device IDs for PCI GPIB boards when the running kernel headers do not define them.

## Important APIs and Constants

- `PCI_VENDOR_ID_AMCC` is defaulted to `0x10e8`.
- `PCI_VENDOR_ID_CBOARDS` is defaulted to `0x1307`.
- `PCI_VENDOR_ID_QUANCOM` is defaulted to `0x8008`.
- `PCI_DEVICE_ID_QUANCOM_GPIB` is defaulted to `0x3302`.

## Control Flow and Integration

The file is preprocessor-only. `ines_gpib.c` includes it to build its PCI ID table and custom PCI search list.

## State and Persistence Behavior

No runtime state exists.

## Dependencies

The file has an include guard and relies on standard PCI macro naming. It avoids redefining IDs that the kernel already supplies.

## Risks and Test Signals

Incorrect IDs prevent device binding or make discovery match the wrong hardware. Test signals are `MODULE_DEVICE_TABLE(pci, ...)` contents, `lspci` matching on supported boards, and successful attach for Quancom/AMCC-backed INES boards.
