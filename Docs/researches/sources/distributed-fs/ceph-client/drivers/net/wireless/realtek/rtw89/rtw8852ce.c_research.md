# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852ce.c

## Purpose
This file is the PCIe bus binding for the RTL8852CE 802.11ax device. It connects the generic rtw89 PCI framework to `rtw8852c_chip_info`, supplies AX-generation PCI DMA/interrupt/register layout data, registers the Realtek PCI ID `0xc852`, and carries DMI quirks for specific Dell systems.

## Important APIs, Types, and Data
- `rtw8852c_bd_idx_addr_low_power` maps low-power TX/RX buffer descriptor index handshakes to `R_AX_DRV_FW_HSK_*` registers.
- `rtw8852c_pci_info` is the core bus descriptor. It selects `rtw89_pci_gen_ax`, `rtw89_pci_isr_ax`, AX HAXI registers, DMA stop/busy registers, RPWM/CPWM addresses, RPP format size, `rtw89_pci_ch_dma_addr_set_v1`, `rtw89_bd_ram_table_dual`, and v1 interrupt/LTR/TX-address helpers.
- `rtw8852c_pci_quirks` matches Dell Vostro 16 5640 and Inspiron 16 5640 DMI strings and applies `RTW89_QUIRK_PCI_BER`.
- `rtw89_8852ce_info` points the bus layer at `rtw8852c_chip_info`, the PCI info, and the DMI quirk table.
- `rtw89_8852ce_id_table` binds vendor `PCI_VENDOR_ID_REALTEK` and device `0xc852`.
- `rtw89_8852ce_driver` uses `rtw89_pci_probe`, `rtw89_pci_remove`, `rtw89_pm_ops`, and `rtw89_pci_err_handler`.

## Control Flow
At module load, `module_pci_driver()` registers the PCI driver. During device discovery, the PCI core matches the ID table and passes `rtw89_8852ce_info` through `driver_data` to the common rtw89 PCI probe path. Probe then uses the chip info for MAC/PHY behavior and `rtw8852c_pci_info` for PCI DMA rings, interrupts, power-management registers, and descriptor parsing. Remove, runtime/system PM, and PCI error recovery are delegated to common rtw89 handlers.

## State and Persistence
All state in this file is static const configuration or kernel driver registration metadata. Runtime state is allocated and owned by the common rtw89 core and PCI layers. DMI quirk results persist for the lifetime of the probed device through the driver info/quirk path.

## Dependencies and Integration Points
The file depends on Linux PCI/module/DMI matching, rtw89 `pci.h`, `reg.h`, and `rtw8852c.h`. It integrates with common PCI DMA channel configuration, interrupt recognition, low-power HCI handshakes, PM ops, and PCI Advanced Error Reporting recovery.

## Risks
- Register-field mismatches in `rtw8852c_pci_info` can break DMA start/stop, interrupt masking, or low-power transitions.
- The Dell DMI quirk is highly specific; SKU or product-name drift can leave affected systems without BER handling.
- `check_rx_tag = false` and `rx_ring_eq_is_full = false` are behavioral assumptions that must match 8852C PCI hardware semantics.

## Test Signals
- Kernel module builds and exposes `MODULE_DEVICE_TABLE(pci, ...)`.
- `lspci -nn` device `10ec:c852` binds to `rtw89_8852ce`; probe completes without HAXI/DMA busy timeout.
- Suspend/resume, PCI error recovery, RX/TX DMA, and Dell quirked systems should be exercised.
