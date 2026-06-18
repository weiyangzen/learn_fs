# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00pci.h

## Purpose
`rt2x00pci.h` is the public header for the generic rt2x00 PCI bus library. It lets chip-specific PCI drivers call shared probe/remove code and attach shared PM operations.

## Important APIs, Types, And Functions
It declares `rt2x00pci_probe(struct pci_dev *pci_dev, const struct rt2x00_ops *ops)`, `rt2x00pci_remove(struct pci_dev *pci_dev)`, and `extern const struct dev_pm_ops rt2x00pci_pm_ops`. It includes Linux I/O and PCI headers.

## Control Flow
Chip drivers define a `struct pci_driver`, set `.probe` to a small wrapper that passes their `struct rt2x00_ops` into `rt2x00pci_probe()`, set `.remove = rt2x00pci_remove`, and wire `.driver.pm = &rt2x00pci_pm_ops`. All real PCI resource handling is implemented in `rt2x00pci.c`.

## State And Persistence
The header owns no runtime state. It defines the compile-time interface by which chip modules share the PCI bus implementation.

## Dependencies And Integration Points
The declarations depend on `struct rt2x00_ops` from the rt2x00 core and Linux PCI/PM types. `rt61pci.c` is a direct consumer.

## Risks
Because this is only a declaration header, risks are ABI-style within the kernel tree: signature changes must be applied to all chip drivers. Missing inclusion of the matching rt2x00 core header before this header would leave `struct rt2x00_ops` undefined.

## Test Signals
Test signals are successful compilation of PCI rt2x00 drivers, module load binding through their PCI tables, remove calling the shared cleanup path, and suspend/resume symbols resolving when PM is enabled.
