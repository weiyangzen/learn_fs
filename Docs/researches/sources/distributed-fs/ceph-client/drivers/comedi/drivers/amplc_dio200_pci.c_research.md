# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_dio200_pci.c Research

Provides the PCI and PCIe front-end for Amplicon DIO200-series boards PCI215, PCI272, PCIe215, PCIe236, and PCIe296. It supplies board descriptors, maps PCI resources, performs PCIe setup, and delegates subdevice creation to the common helper.

`enum dio200_pci_model` indexes board variants. `dio200_pci_boards[]` defines per-board BAR, subdevice layout, offsets, feature flags, and PCIe enhanced status. `dio200_pcie_board_setup()` maps PCI BAR0 bridge registers, enables Avalon-MM to PCIe interrupt generation, and calls `amplc_dio200_set_enhance()`. `dio200_pci_auto_attach()` enables PCI, maps MMIO or I/O BARs, performs PCIe setup, and calls `amplc_dio200_common_attach()` with shared IRQ flags.

PCI probe passes match-table driver data to auto attach. Attach selects descriptor metadata, enables PCI, maps either memory or I/O resources from `mainbar`, configures PCIe boards when needed, then common code creates 8255/8254/timer/interrupt subdevices. Runtime state is mostly common-helper state; this file persists only `dev->board_ptr`, `dev->board_name`, and mapped `dev->mmio` or `dev->iobase`.

Dependencies are Comedi PCI helpers, Linux PCI BAR/MMIO APIs, IRQF_SHARED, and exported DIO200 common symbols. PCI IDs are conditional for legacy I/O-port boards under `CONFIG_HAS_IOPORT`. Risks include BAR selection mistakes, MMIO mapping failure, PCIe bridge interrupt setup assumptions, enhanced feature enable ordering, and conditional exclusion of I/O-port boards. Tests should cover each PCI ID mapping, MMIO and I/O resource paths, PCIe BAR0 size check, interrupt-enable write at offset 0x50, common attach propagation, and detach unmapping through Comedi PCI cleanup.
