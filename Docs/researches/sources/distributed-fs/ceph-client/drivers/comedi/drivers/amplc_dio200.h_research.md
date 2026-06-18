# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200.h Research

Defines the shared contract between Amplicon DIO200 ISA, PCI, and common helper code.

`enum dio200_sdtype` identifies supported subdevice descriptor types: none, interrupt, 8255, 8254, and timer. `DIO200_MAX_SUBDEVS` and `DIO200_MAX_ISNS` size board descriptor arrays. `struct dio200_board` carries board name, main PCI BAR, subdevice count, per-subdevice type/info arrays, and feature flags for interrupt-source registers, clock/gate selection, and PCIe enhanced behavior. It declares `amplc_dio200_common_attach()` and `amplc_dio200_set_enhance()`.

The header has no runtime control flow. Its structures determine how front-end drivers describe hardware to the common attach path. The bitfields become persistent per-board metadata in static descriptor tables.

Dependencies are Linux types and a forward declaration of `struct comedi_device`. It is included by `amplc_dio200.c`, `amplc_dio200_common.c`, and `amplc_dio200_pci.c`. Risks include descriptor array bounds and ABI coupling between front ends and common helper. Tests are compile-time and attach-time: every board descriptor should stay within max subdevices, valid interrupt source masks should fit `DIO200_MAX_ISNS`, and PCI front ends should provide `mainbar` only where common setup expects it.
