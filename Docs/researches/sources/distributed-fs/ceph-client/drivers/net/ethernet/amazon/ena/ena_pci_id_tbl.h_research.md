# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_pci_id_tbl.h

## Purpose
`ena_pci_id_tbl.h` defines the PCI vendor/device IDs supported by the ENA driver and builds the `ena_pci_tbl[]` device table consumed by the PCI driver and module device table.

## Important APIs, Types, And Functions
The file defines `PCI_VENDOR_ID_AMAZON` when absent, ENA PF/VF and LLQ PF/VF IDs, a reserved ID, `ENA_PCI_ID_TABLE_ENTRY(devid)`, and `static const struct pci_device_id ena_pci_tbl[]`. There are no functions.

## Control Flow, State, And Integration
The table is included by `ena_netdev.c`, which passes it to `MODULE_DEVICE_TABLE(pci, ena_pci_tbl)` and to `struct pci_driver ena_pci_driver.id_table`. Kernel PCI matching uses this static data to call `ena_probe()` for matching Amazon ENA devices. There is no runtime mutable state and no persistence beyond compiled module metadata.

## Dependencies
It depends on the kernel PCI ID structures/macros being visible through including source. It is coupled to actual ENA hardware IDs and to distribution/module autoload behavior.

## Risks And Test Signals
Risks are missing or incorrect IDs causing devices not to bind, or over-broad IDs binding unsupported hardware. Test signals include `modinfo` alias output, PCI probe on PF/VF and LLQ variants, SR-IOV VF creation, and verifying reserved ID handling remains intentional.
