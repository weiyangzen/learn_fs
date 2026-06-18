# sources/distributed-fs/ceph-client/drivers/misc/cardreader/alcor_pci.c

## Purpose
`alcor_pci.c` is the PCI parent/MFD driver for Alcor Micro AU6601, AU6621, and AU6625 card readers. It maps PCI BAR registers, provides exported register access helpers, configures DMA, and creates SD/MMC and MemoryStick child devices.

## Important APIs, Types, and Functions
Exported helpers are `alcor_write8()`, `alcor_write16()`, `alcor_write32()`, `alcor_write32be()`, `alcor_read8()`, `alcor_read32()`, and `alcor_read32be()`. Driver lifecycle is `alcor_pci_probe()` and `alcor_pci_remove()`, with sleep PM callbacks `alcor_suspend()` and `alcor_resume()`. `alcor_pci_cells[]` declares child MFD cells for SDMMC and MS functions. PCI IDs select `struct alcor_dev_cfg` with a DMA capability flag.

## Control Flow
Probe enables the PCI device with managed helpers, allocates private state and an IDA ID, requests BAR regions, verifies BAR0 is memory, maps it, disables SD/MS interrupts, sets a 32-bit SDMA mask, enables bus mastering, stores driver data, passes the private structure as platform data to each child cell, adds MFD children, and disables PCIe L0s/L1 link states. Remove tears down MFD children, frees the ID, clears bus mastering and driver data. Resume disables L0s/L1 again.

## State and Persistence
Per-device state includes PCI device pointer, parent bridge pointer, device pointer, config pointer, IRQ, mapped BAR base, and IDA ID. Register state lives in hardware; driver state is volatile.

## Dependencies and Integration Points
The driver depends on PCI managed resource APIs, MFD core, DMA mask setup, `linux/alcor_pci.h` constants/shared structures, and child platform drivers that consume the exported MMIO helpers and platform data.

## Risks and Edge Cases
`alcor_pci_cells` is a global array whose `platform_data` and `pdata_size` are rewritten per probe; concurrent multiple devices could race or share stale platform data. The code disables link power states unconditionally, which may affect power consumption. DMA mask failure aborts even for configs with `.dma = 0`. The suspend callback does nothing beyond resume re-disabling link states.

## Test Signals
Test all PCI IDs, multi-device probe/remove, BAR type rejection, DMA-mask failure, MFD child creation failure cleanup, exported register helper endianness, interrupt disable at probe, and link-state policy after resume.
