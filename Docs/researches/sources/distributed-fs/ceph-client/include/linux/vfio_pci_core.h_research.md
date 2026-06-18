# sources/distributed-fs/ceph-client/include/linux/vfio_pci_core.h

## Purpose
This header defines shared VFIO PCI core structures and helpers used by VFIO PCI variant drivers to expose PCI BARs, config space, IRQs, reset, SR-IOV, DMA-buf, and region extensions.

## Important APIs, types, and functions
Key definitions include VFIO PCI offset/index macros, `vfio_pci_eventfd`, `vfio_pci_regops`, `vfio_pci_region`, `vfio_pci_device_ops`, and `vfio_pci_core_device`. APIs register device regions, set module parameters, initialize/release/register/unregister devices, handle ioctl/read/write/mmap/request/match, enable/disable PCI devices, setup BAR maps, handle AER, perform IO read/write with width helpers, test memory enablement, check range intersections, and map DMA-buf physical vectors.

## Control flow, state, and persistence
Variant drivers embed `vfio_pci_core_device`, initialize common state, register the VFIO device, and delegate user file operations to core helpers. The core tracks BAR mappings, config permission maps, IRQ/eventfd contexts, MSI/MSI-X state, reset/PM flags, SR-IOV token/PF state, memory locks, dynamic regions, and DMA-buf lists. State is runtime device and userspace attachment state; persistent PCI config is saved/restored through PCI core helpers.

## Dependencies and integration points
It depends on PCI, VFIO, IRQ bypass, RCU, UUIDs, notifiers, DMA-buf/P2PDMA, and UAPI VFIO region structures. It integrates VFIO PCI drivers with PCI reset/AER/PM, KVM irqbypass, SR-IOV, and userspace VMM memory mapping.

## Risks and test signals
Risks include BAR mmap permission errors, config-space access leakage, eventfd RCU lifetime mistakes, SR-IOV token misuse, reset/PM restore regressions, and width/alignment bugs in IO paths. Tests should cover BAR read/write/mmap, region capabilities, MSI/MSI-X and INTx, AER, reset, SR-IOV configure, DMA-buf paths, and range intersection edge cases.
