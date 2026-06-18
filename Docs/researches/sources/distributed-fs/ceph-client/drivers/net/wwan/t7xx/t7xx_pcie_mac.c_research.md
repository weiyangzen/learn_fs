# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pcie_mac.c

This file programs the T7xx PCIe MAC registers. Its main responsibilities are address translation region (ATR) setup, host interrupt enable/disable, per-interrupt mask manipulation, interrupt status clearing, and MSI-X configuration.

`t7xx_pcie_mac_atr_cfg` writes ATR source, translation, and parameter registers for selected ports; `t7xx_pcie_mac_atr_init` disables old ATR tables, programs BAR2 register translation and transparent device DMA windows, and stores the device register translation address. `t7xx_pcie_mac_interrupts_en`/`dis` toggle host interrupt control; `t7xx_pcie_mac_clear_int`, `t7xx_pcie_mac_set_int`, and `t7xx_pcie_mac_clear_int_status` operate on EXT_INT masks/status; `t7xx_pcie_set_mac_msix_cfg` writes the MSI-X vector count.

State is hardware register state plus `base_addr.pcie_dev_reg_trsl_addr`. Dependencies are `t7xx_reg.h`, PCI BAR mappings, and callers in PCI, MHCCIF, and modem RGU paths. Risks include wrong ATR alignment/size, programming a translation window before BARs are mapped, using a mask bit outside EXT_INT range, and interrupt enable order during resume. Test signals include BAR2 register reads through translated windows, DMA path validation, interrupt mask/status readback, RGU/MHCCIF interrupt delivery, and suspend/resume reinitialization.
