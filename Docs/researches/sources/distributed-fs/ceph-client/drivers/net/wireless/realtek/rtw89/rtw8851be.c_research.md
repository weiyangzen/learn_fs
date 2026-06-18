# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851be.c

## Purpose
This file is the PCIe bus glue for the Realtek RTL8851BE 802.11ax chipset. It binds the generic RTW89 PCI framework to the 8851B chip description, declares the PCI device ID, and registers a Linux `pci_driver`.

## Important APIs, Types, and Data
- `rtw8851b_pci_info` is a `struct rtw89_pci_info` describing AX-generation PCI behavior: descriptor truncation modes, RXBD mode, multi-tag mode, burst sizes, DMA idle/active intervals, DMA stop/busy registers, interrupt callbacks, RPP format size, DMA channel mask, and BD RAM table.
- `rtw89_8851be_info` is a `struct rtw89_driver_info` that points `.chip` to `rtw8851b_chip_info` and attaches the PCI info under `.bus.pci`.
- `rtw89_8851be_id_table` matches Realtek vendor ID with device ID `0xb851` and stores a pointer to `rtw89_8851be_info` in `driver_data`.
- `rtw89_8851be_driver` wires Linux PCI callbacks to generic RTW89 PCI entry points: `rtw89_pci_probe`, `rtw89_pci_remove`, `rtw89_pm_ops`, and `rtw89_pci_err_handler`.

## Control Flow
At module load, `module_pci_driver()` registers `rtw89_8851be_driver`. When the PCI core matches device `10ec:b851`, `rtw89_pci_probe` receives the ID table entry, extracts `rtw89_8851be_info`, and initializes the common RTW89 device using `rtw8851b_chip_info` plus the PCI transport parameters in `rtw8851b_pci_info`. Removal, power management, and PCI error recovery are delegated to shared RTW89 PCI/core routines.

## State and Persistence
This wrapper stores only immutable module metadata and static config structures. Runtime state is allocated by the generic PCI probe path and RTW89 core. Persistent behavior includes PCI device binding through `MODULE_DEVICE_TABLE(pci, ...)`, which allows module auto-loading by modalias.

## Dependencies and Integration Points
- Linux PCI and module subsystems: `<linux/pci.h>`, `<linux/module.h>`.
- RTW89 PCI framework in `pci.h`, register definitions in `reg.h`, and chip-level RTL8851B metadata in `rtw8851b.h`.
- Shared PCI helper callbacks provide DMA setup, LTR, descriptor address filling, RPP parsing, interrupt mask programming, and interrupt recognition.
- Integrates with kernel PM through `rtw89_pm_ops` and PCI AER/error handling through `rtw89_pci_err_handler`.

## Risks
- Incorrect DMA channel masks, burst sizes, stop/busy registers, or tag settings can cause hangs, missed interrupts, or descriptor corruption.
- The ID table only binds `0xb851`; additional subsystem-specific IDs would not probe unless covered by this generic ID.
- `ssid_quirks = NULL` means no board-specific PCI quirks are applied here.

## Test Signals
- Kernel build with `CONFIG_RTW89_8851BE` or equivalent confirms API compatibility.
- `modinfo` should expose the PCI alias for `10ec:b851`.
- Runtime probe should create an RTW89 wireless PHY without DMA timeout, interrupt, or firmware download errors.
- Suspend/resume and PCI error-recovery tests exercise the `.driver.pm` and `.err_handler` paths delegated by this file.
