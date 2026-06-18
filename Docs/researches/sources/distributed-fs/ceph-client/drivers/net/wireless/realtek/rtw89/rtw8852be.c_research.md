# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852be.c

Purpose: Registers the PCIe RTL8852BE driver and supplies PCI HCI parameters for the generic RTW89 PCI probe path. It binds Realtek PCI ids `0xb852` and `0xb85b` to `rtw8852b_chip_info`.

Important APIs and types: `rtw8852b_pci_info` configures AX PCI descriptor modes, bursts, tags, DMA stop/busy registers, channel masks, interrupt hooks, LTR, RPP parsing, and DMA address programming. `rtw89_8852be_info` packages chip and bus data. The PCI id table and `module_pci_driver()` define module registration.

Control flow: PCI core matches an id, calls `rtw89_pci_probe`, and passes `rtw89_8852be_info`. Shared PCI code initializes rings, interrupts, DMA, PM, and error recovery from `rtw8852b_pci_info`.

State and persistence: Only const descriptors here. Runtime state lives in `rtw89_dev` and PCI objects; descriptor-derived settings persist after hardware register writes.

Dependencies and integration points: Linux PCI/module APIs plus `pci.h`, `reg.h`, and `rtw8852b.h`. Integrates with `rtw8852b.c` and shared RTW89 PCI transport.

Risks: Wrong DMA masks or register fields can break RX/TX and PM. No SSID quirks are configured, so platform exceptions require explicit additions.

Test signals: Build, modalias autoload, probe/remove, suspend/resume, AER recovery, interrupt handling, DMA ring traffic, and RX/TX throughput.
