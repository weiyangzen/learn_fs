# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922ae.c

## Purpose
This file is the PCIe bus binding for RTL8922AE and RTL8922AE-VS Wi-Fi 7 devices. It connects Linux PCI enumeration to `rtw8922a_chip_info`, supplies BE-generation PCI parameters, applies an SSID thermal-protection quirk, and selects the VS variant for device `0x892B`.

## Important APIs, Types, and Data
- `rtw8922a_pci_ssid_quirks` applies `RTW89_QUIRK_THERMAL_PROT_120C` to a Dell-specific Realtek subsystem ID.
- `rtw8922a_pci_info` selects `rtw89_pci_gen_be`, `rtw89_pci_isr_be`, BE HAXI registers, v2 interrupt/LTR helpers, BE DMA address setup, RX tag checking, no RXBD FS, and equal-full ring behavior.
- `rtw89_8922ae_info` uses base `rtw8922a_chip_info`.
- `rtw89_8922ae_vs_info` adds `rtw8922ae_vs_variant`.
- PCI IDs: Realtek `0x8922` for base AE and `0x892B` for VS.
- Driver uses `rtw89_pci_probe`, `rtw89_pci_remove`, `rtw89_pm_ops_be`, and `rtw89_pci_err_handler`.

## Control Flow
`module_pci_driver()` registers the PCI driver. PCI ID matching selects base or VS driver info via `driver_data`; common rtw89 PCI probe uses that info to allocate the device, load 8922A chip ops, configure PCI DMA/interrupt behavior, and apply variant constraints. Removal, PM, and error recovery remain common-code responsibilities.

## State and Persistence
Static const tables provide registration and bus configuration. Runtime state is held by rtw89 core/PCI. Variant choice persists for the lifetime of the device and changes firmware/MCS behavior through `rtw8922ae_vs_variant`.

## Dependencies and Integration Points
Depends on Linux PCI/module support, `pci.h`, `reg.h`, and `rtw8922a.h`. It integrates with BE PCI HCI ops, BE PM ops, PCI error recovery, and SSID quirk handling.

## Risks
- BE PCI register selection differs from AX parts; using the wrong ISR or DMA busy masks causes probe or interrupt failures.
- VS devices require the variant to disable MCS 12/13 and enforce minimum firmware; incorrect ID mapping can expose unsupported rates.
- Thermal-protection quirk coverage depends on exact subsystem ID match.

## Test Signals
- PCI aliases bind `10ec:8922` and `10ec:892b`.
- Base and VS devices should request correct firmware, complete BE PCI probe, and pass suspend/resume and AER tests.
- VS devices should report no MCS 12/13 support and satisfy firmware minimum behavior.
