# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852ae.c

Purpose: This file is the PCIe bus glue module for RTL8852AE. It binds Realtek PCI device IDs to the generic RTW89 PCI probe/remove paths and supplies the 8852A-specific PCI host-controller configuration used by the common bus layer.

Important APIs, types, and data: `rtw8852a_pci_info` is the key data object. It fills `struct rtw89_pci_info` with AX-generation PCI definitions, BD truncation/tag/burst modes, DMA idle/active intervals, RPP format size, register addresses and bit masks for HCI enable, BD modes, DMA stop/busy checks, RPWM/CPWM/MIT registers, DMA address setup, BD RAM table, interrupt callbacks, LTR setup, TX address filling, and RPP parsing. `rtw89_8852ae_info` is a `struct rtw89_driver_info` pointing at `rtw8852a_chip_info` and `rtw8852a_pci_info`. The PCI ID table matches vendor `PCI_VENDOR_ID_REALTEK` with device IDs `0x8852` and `0xa85a`, then stores `rtw89_8852ae_info` in `driver_data`. `rtw89_8852ae_driver` registers `rtw89_pci_probe`, `rtw89_pci_remove`, `rtw89_pm_ops`, and `rtw89_pci_err_handler`.

Control flow: Module loading registers the `pci_driver` through `module_pci_driver()`. When the PCI core matches one of the IDs, `rtw89_pci_probe()` receives the driver info, allocates/initializes the RTW89 device, loads `rtw8852a_chip_info`, and configures PCI rings, DMA, interrupts, power management, and firmware around the static `rtw8852a_pci_info` parameters. Removal and PCI error recovery are delegated to common RTW89 PCI callbacks.

State and persistence: This file owns no mutable state beyond kernel driver registration. Persistent runtime state is held by the PCI core, `struct pci_dev`, and RTW89 device allocation performed by the common probe. The static config remains read-only and shared across devices.

Dependencies and integration points: Includes Linux module and PCI headers plus RTW89 `pci.h`, `reg.h`, and `rtw8852a.h`. It integrates with the Linux PCI bus, module autoloading through `MODULE_DEVICE_TABLE(pci, ...)`, RTW89 PCI DMA/interrupt helpers, RTW89 PM ops, and the RTL8852A chip info exported by the chip-specific implementation.

Risks: The static PCI register map and DMA/HCI parameters must match RTL8852AE hardware. Incorrect stop/busy registers, BD mode bits, tag settings, or interrupt callbacks can cause failed probe, stuck DMA, interrupt storms, suspend/resume failures, or packet loss. Device ID additions must use the right chip info; because `driver_data` is a raw pointer cast to `kernel_ulong_t`, a wrong pointer type would fail at runtime rather than through strong typing.

Test signals: Compile/link checks include `rtw8852a_chip_info` availability and PCI helper prototypes. Runtime signals are PCI modalias autoload, successful probe for IDs `10ec:8852` and `10ec:a85a`, firmware load, ring setup, TX/RX traffic, interrupt delivery, suspend/resume, PCI AER recovery paths, and clean module unload.
