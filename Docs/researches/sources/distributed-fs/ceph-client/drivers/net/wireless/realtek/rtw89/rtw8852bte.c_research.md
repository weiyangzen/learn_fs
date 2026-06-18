# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bte.c

Purpose: Registers the PCIe 8852BE-VT/8852BT-facing module and binds Realtek PCI id `0xb520` to `rtw8852bt_chip_info`.

Important APIs and types: `rtw8852bt_pci_ssid_quirks` enables `RTW89_QUIRK_THERMAL_PROT_110C` for a matching HP subsystem. `rtw8852bt_pci_info` supplies AX PCI descriptor, DMA, interrupt, LTR, RPP, and channel-mask settings. The driver info, PCI id table, and `pci_driver` wire generic RTW89 PCI callbacks.

Control flow: PCI match passes `rtw89_8852bte_info` to `rtw89_pci_probe`; shared PCI code initializes HCI, and core code uses `rtw8852bt_chip_info` for chip operations and RFK.

State and persistence: Immutable descriptors here. Runtime PCI/core state and hardware registers live elsewhere. SSID quirks become persistent driver behavior flags for matching systems.

Dependencies and integration points: Linux PCI/module APIs plus `pci.h`, `reg.h`, and `rtw8852bt.h`; integrates with `rtw8852bt.c` and shared PCI transport.

Risks: PCI descriptor drift can break HCI behavior. SSID quirk matching must be exact to avoid missing or over-applying thermal protection.

Test signals: Build, modalias autoload for `10ec:b520`, HP quirk detection, probe/remove, suspend/resume, AER recovery, DMA/interrupt traffic, and thermal-protection behavior.
