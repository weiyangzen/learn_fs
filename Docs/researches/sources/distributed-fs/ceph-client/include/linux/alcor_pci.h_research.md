<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alcor_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/alcor_pci.h

## Purpose
`alcor_pci.h` defines register maps, constants, private state, and MMIO accessor prototypes for Alcor Micro AU6601/AU662x PCI card reader drivers.

## Important APIs, types, and functions
The header enumerates device IDs, driver names, clock/dma limits, SD/MS register offsets, command/data control bits, interrupt status/mask bits, bus width and power controls, PCIe capability offsets, and card-type identifiers. `struct alcor_dev_cfg` stores DMA configuration. `struct alcor_pci_priv` stores PCI devices, device pointer, MMIO base, IRQ, IDR ID, and config. Accessors include 8/16/32-bit writes, big-endian 32-bit write/read, and 8/32-bit reads.

## Control flow
Card reader drivers use register constants to program command/data transfers, DMA, clocks, resets, interrupts, card detection, and Memory Stick mode. Accessor functions centralize MMIO width/endian handling.

## State and persistence behavior
`alcor_pci_priv` is persistent per PCI function. Hardware register state persists in the controller until reset or reprogramming.

## Dependencies and integration points
It integrates PCI probing, MMIO, IRQ handling, MMC/MemoryStick card drivers, and DMA constraints.

## Risks and test signals
Risks include undocumented register assumptions, AU6601/AU6621 DMA differences, endian accessor misuse, interrupt mask errors, and card-detect races. Test signals include SD/MS card probe, DMA/PIO transfers, interrupt error paths, reset/power sequencing, and device-ID variant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alcor_pci.h -->
