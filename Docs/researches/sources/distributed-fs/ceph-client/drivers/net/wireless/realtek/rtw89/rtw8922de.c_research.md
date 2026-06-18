# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922de.c

## Purpose
This file is the PCIe bus binding for RTL8922DE and RTL8922DE-VS Wi-Fi 7 devices. It supplies BE-generation PCI v1 parameters, maps Realtek device IDs to base or VS chip variants, and registers the PCI driver against common rtw89 probe/remove/PM/error handlers.

## Important APIs, Types, and Data
- `rtw8922d_pci_info` selects `rtw89_pci_gen_be`, `rtw89_pci_isr_be_v1`, BE HAXI registers, group BD addressing, RPP format v1, BE v1 DMA address setup, v3 interrupt helpers, v1 DMA busy/stop masks, and a TX DMA channel mask that excludes alternating ACH/high queues.
- `rtw89_8922de_vs_info` uses `rtw8922d_chip_info` with `rtw8922de_vs_variant`.
- `rtw89_8922de_info` uses base `rtw8922d_chip_info`.
- PCI IDs: `0x892D` and `0x882D` select VS, while `0x895D` selects base.
- Driver uses `rtw89_pm_ops_be` and `rtw89_pci_err_handler`.

## Control Flow
The PCI core matches one of the device IDs and passes the selected `rtw89_driver_info` pointer through `driver_data`. Common PCI probe then initializes PCI DMA/interrupt behavior from `rtw8922d_pci_info` and chip behavior from the base or VS chip descriptor. Removal, PM, and PCI error recovery are delegated to shared rtw89 code.

## State and Persistence
The file contains static const bus configuration and registration metadata only. Runtime device state is owned by the common rtw89 core/PCI layers. Variant selection persists for the device lifetime and can override firmware and capability behavior.

## Dependencies and Integration Points
Depends on Linux PCI/module APIs, rtw89 `pci.h`, `reg.h`, and `rtw8922d.h`. It integrates with BE PCI v1/v3 interrupt plumbing, DMA channel selection, PM, and AER recovery.

## Risks
- `group_bd_addr = true`, `rpp_fmt_size = sizeof(struct rtw89_pci_rpp_fmt_v1)`, and v3 interrupt helpers must match the 8922D PCI hardware revision.
- Device-ID to variant mapping affects firmware basename and MCS support; wrong mapping can request incompatible firmware or advertise unsupported rates.
- TX DMA channel mask must align with queue topology in `rtw8922d_chip_info`.

## Test Signals
- PCI aliases should bind `10ec:892d`, `10ec:882d`, and `10ec:895d`.
- Base and VS devices should complete probe, firmware load, DMA ring init, interrupt handling, suspend/resume, and PCI error recovery.
- VS devices should request the 8922DS firmware override and enforce variant capability limits.
