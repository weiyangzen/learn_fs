# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_pci.c

## Purpose

This file is the PCI wrapper for the ComputerBoards PCI-DAS08. It binds the PCI ID, enables the device, chooses the correct BAR-derived I/O base, allocates common private state, and delegates all board behavior to the shared DAS08 implementation.

## Important APIs, Types, and Functions

`das08_pci_boards[]` describes the PCI-DAS08 as a 12-bit bipolar 5 V AI board with standard DAS08 encoding, 3 DI lines, 4 DO lines, an 8254 at offset 4, and 8 I/O ports. `das08_pci_auto_attach()` allocates `struct das08_private_struct`, sets `dev->board_ptr`, calls `comedi_pci_enable()`, assigns `dev->iobase` from `pci_resource_start(pdev, 2)`, and calls `das08_common_attach()`. `das08_pci_probe()`, `das08_pci_table`, and `module_comedi_pci_driver()` provide PCI binding.

## Control Flow, State, and Persistence

PCI probe calls `comedi_pci_auto_config()`, which invokes auto-attach. The Comedi detach path is `comedi_pci_detach()` and PCI remove is `comedi_pci_auto_unconfig()`. Runtime state is the enabled PCI device, selected I/O BAR, and common DAS08 private state; no persistent configuration is written.

## Dependencies and Integration Points

The file depends on `linux/comedi/comedi_pci.h` and `das08.h`. It integrates with PCI vendor `PCI_VENDOR_ID_CB`, device `0x0029`, the Comedi PCI auto-config framework, and common DAS08 subdevice setup.

## Risks and Test Signals

The primary risks are using the wrong BAR index, failing to handle PCI enable errors, and assuming only one PCI-DAS08 board descriptor. Test with a matching PCI card, verify BAR 2 maps valid I/O registers, confirm AI/DI/DO/8254 subdevices, run AI single reads, and unload/reload to ensure PCI resources are released.
