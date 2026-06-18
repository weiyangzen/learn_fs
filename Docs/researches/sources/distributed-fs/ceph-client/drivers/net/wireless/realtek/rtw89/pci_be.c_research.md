# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci_be.c

## Purpose
`pci_be.c` implements BE-generation PCIe behavior that differs from the AX path in `pci.c`. It supplies BE-specific ASPM/L1SS/CLKREQ programming, IO-recovery watchdog setup, DMA stop/start and idle polling, descriptor index clearing, BE mode configuration, BDRAM reset, debounce/LDO/link/SER hardware setup, LTR v2, interrupt mitigation, level-1 recovery DMA reset, EQ/OOBS calibration workaround, suspend/resume hooks, BE ISR definitions, and the exported `rtw89_pci_gen_be` generation dispatch table.

## Important APIs, types, and functions
- `rtw89_pci_aspm_set_be()`, `rtw89_pci_l1ss_set_be()`, and `rtw89_pci_clkreq_set_be()` are the BE generation callbacks for PCIe link power features.
- `_patch_pcie_power_wake_be()` toggles BE wake control in `R_BE_HCI_OPT_CTRL` and is used both locally and as the generation `power_wake` callback.
- `rtw89_pci_set_io_rcy_be()` programs or disables the BE watchdog/IO recovery timers across AON, MDIO, LA mode, WLAN, AXIDMA, local, and AXI read/write channels.
- `rtw89_pci_ctrl_wpdma_pcie_be()` and `rtw89_pci_ctrl_trxdma_pcie_be()` control BE WPDMA, TXDMA, RXDMA, and AXI master stop bits.
- `rtw89_pci_clr_idx_all_be()`, `rtw89_pci_poll_txdma_ch_idle_be()`, `rtw89_pci_poll_rxdma_ch_idle_be()`, and `rtw89_pci_poll_dma_all_idle_be()` reset and validate BE descriptor/DMA state.
- `rtw89_pci_mode_op_be()` maps `rtw89_pci_info` descriptor/burst/tag/watchdog settings into BE HAXI init, RX append, and expansion-control registers.
- `rtw89_pci_ops_mac_pre_init_be()`, `rtw89_pci_ops_mac_pre_deinit_be()`, and `rtw89_pci_ops_mac_post_init_be()` are the BE MAC init/deinit phases used through `rtw89_pci_gen_be`.
- `rtw89_pci_ltr_set_v2()` exports the BE LTR programming sequence with chip-specific latency values for RTL8922A versus later BE chips.
- `rtw89_pci_lv1rst_stop_dma_be()` and `rtw89_pci_lv1rst_start_dma_be()` implement BE level-1 recovery DMA stop/start.
- `rtw89_pci_disable_eq_be()` is a RTL8922A EQ/OOBS/offset calibration workaround.
- `rtw89_pci_suspend_be()` and `rtw89_pci_resume_be()` define `rtw89_pm_ops_be`.
- Exported `rtw89_pci_isr_be`, `rtw89_pci_isr_be_v1`, and `rtw89_pci_gen_be` are consumed by BE chip `rtw89_pci_info` tables.

## Control flow and state behavior
BE pre-init starts by configuring IO recovery from `rtwdev->pci_info`, forcing PCI wake on, stopping WPDMA and all TRX/IO DMA, clearing descriptor indexes, and polling until TX/RX DMA are idle. It then programs descriptor/burst/tag/watchdog mode, resets common software/hardware PCI rings through `rtw89_pci_ops_reset()`, resets BDRAM, applies debounce and LDO low-power policy, sets BE PCIe link/autoload/aux-clock behavior, configures PCIe SER PL1 behavior, disables normal TXDMA queues while enabling the firmware-command channel, and finally reenables TRX/IO DMA for firmware download. This mirrors the AX pre-init contract but uses BE HAXI and BE power/reset registers.

BE post-init enables LTR through the selected `info->ltr_set` callback, releases IO stop while leaving TX/RX state alone, enables WPDMA, enables normal TXDMA and firmware TXDMA channels, and configures interrupt mitigation. MIT setup chooses a 1 ms RX timer unit and a RX count threshold of half the maximum RXBD count. BE pre-deinit turns wake off, checks WLAN MAC power state, and only disables TRX/IO DMA plus clears indexes if the MAC is still powered.

DMA recovery uses the common `rtw89_pci_ctrl_dma_all()` wrapper but BE-specific idle status. If stopping DMA fails because `B_BE_HAXI_MST_BUSY` remains set, it toggles MAC HCI DMA TRX off/on and polls again. Restart toggles MAC HCI DMA, clears indexes, resets BDRAM, and reenables DMA. These generation callbacks are plugged into `rtw89_pci_ops_mac_lv1_recovery()` in `pci.c`.

Link-power state is set directly in BE registers. ASPM first programs PCI config ASPM delay to 16 us and then toggles `B_BE_ASPM_CTRL_L1`. L1SS has an extra RTL8922D CID7090 branch enabling ASPM/PCIPM L1.1/L1.2 bits before toggling `B_BE_L1SUB_ENABLE`. CLKREQ programs BE latency and toggles `B_BE_CLK_PM_EN`; the disable path clears through `R_AX_L1_CLK_CTRL`, which is an alias-like constant reused with a BE bit and should be verified against register definitions when porting.

SER setup is chip/CV dependent. RTL8922A CAV/CBV leave PL1 SER disabled with selected masks; CCV/default clears ISR, enables PL1 SER, and masks/unmasks PM/LTSSM sources. RTL8922D uses BE2 flow: toggle SER flush reset, manipulate RAC PHY error mask/flag registers on both G1/G2 lanes, clear PL1 ISR, program masks and timer unit, enable PL1 SER, and optionally enable SER detect for CID7090. Suspend/resume temporarily changes PL1 timer units for WoW, freezes/unfreezes PCIe register reset, manipulates PRST gating, clears SER/PHY ISR state, and calls `rtw89_pci_basic_cfg()` on resume.

## Dependencies and integration points
The file includes Linux PCI plus rtw89 `mac.h`, `pci.h`, and `reg.h`. It relies on common PCI helpers from `pci.c`: `rtw89_pci_ops_reset()`, `rtw89_pci_ltr_is_err_reg_val()`, `rtw89_pci_ctrl_dma_all()`, `rtw89_pci_clr_idx_all()`, `rtw89_pci_basic_cfg()`, and the generation dispatch contract declared in `pci.h`. It calls MAC-level DMA reset helpers `rtw89_mac_ctrl_hci_dma_trx()` and uses chip metadata (`chip_id`, `hal.cv`, `hal.cid`, and `rtw89_pci_info`) to select RTL8922A/RTL8922D behavior. Its exported symbols are selected by BE chip bus-info tables and by PM wiring in BE PCI modules.

## Risks and edge cases
- BE hardware setup is highly chip-revision specific. RTL8922A CV branches and RTL8922D CID7090 branches must match the actual silicon, or SER/L1SS/LDO settings can be wrong.
- IO recovery timer defaults use different analog/MAC/AUX timer values; a wrong `io_rcy_tmr` or scale can either miss stuck IO or trigger false recovery.
- `rtw89_pci_mode_op_be()` only touches `R_BE_RX_APPEND_MODE` for RTL8922A; future BE chips with different append behavior need explicit handling.
- Grouped descriptor-address mode and unsupported channel masks are handled elsewhere through `pci.c` and `pci.h`; BE stop masks must remain consistent with those tables.
- SER and EQ workaround code directly manipulates RAC analog registers and temporarily disables ASPM/EQ state. Restore ordering is important to avoid link instability.
- Resume clears PHY ISR flags by toggling `PHY_ERR_FLAG_EN` only on RTL8922D; missing this can leave stale PHY error state after system sleep.
- LTR v2 rejects dead register reads before programming. This prevents writing through invalid bus state but can abort MAC post-init and prevent the device from starting.

## Test signals
BE probe should complete pre-init through DMA idle polling, BDRAM reset, debounce/LDO/link/SER setup, firmware-command DMA enablement, post-init LTR, WPDMA enable, TXDMA enable, and MIT configuration. RTL8922A and RTL8922D should be tested separately, including RTL8922D CID7090 L1SS/SER paths. Suspend/resume tests should confirm PRST gating is restored, PL1 timer unit returns to the normal value, SER/PHY ISR clear polling does not warn, and `rtw89_pci_basic_cfg()` reestablishes ASPM/CLKREQ/L1SS. Recovery tests should force HAXI busy, exercise the fallback HCI DMA TRX toggle, and verify BDRAM/index reset plus DMA restart. Link-power tests should verify ASPM/L1SS/CLKREQ module parameters still gate the BE callbacks through the common wrappers in `pci.c`.
