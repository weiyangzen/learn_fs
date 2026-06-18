## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822ce.c

Purpose: PCI module glue for RTL8822CE-class devices. It binds Realtek PCI IDs `0xC822` and `0xC82F` to the shared `rtw8822c_hw_spec` and delegates all behavior to the rtw88 PCI HCI layer.

Important APIs/types: `rtw_8822ce_id_table`, `struct pci_driver rtw_8822ce_driver`, `MODULE_DEVICE_TABLE(pci, ...)`, and `module_pci_driver()`. The driver uses `rtw_pci_probe`, `rtw_pci_remove`, `rtw_pci_shutdown`, `rtw_pci_err_handler`, and `rtw_pm_ops`.

Control flow and state: kernel PCI matching calls `rtw_pci_probe()` with `driver_data` pointing to the 8822C hardware spec. Removal, shutdown, runtime/system power management, and PCI error recovery are entirely handled by the shared PCI module.

Dependencies and integration: depends on `pci.h`, `rtw8822c.h`, Linux PCI core, and the common rtw88 PCI transport. It integrates with mac80211 only after the shared probe path allocates and registers the hardware.

Risks and test signals: risk is limited to PCI ID coverage and wrong hardware-spec pointer assignment. Test by building the module, checking `modinfo` aliases, probing matching hardware, exercising suspend/resume and PCI AER recovery.
