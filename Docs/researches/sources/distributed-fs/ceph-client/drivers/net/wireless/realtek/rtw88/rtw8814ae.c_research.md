# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814ae.c

`rtw8814ae.c` is the PCIe binding for RTL8814AE. It matches Realtek PCI device `0x8813`, stores `&rtw8814a_hw_spec` in `driver_data`, exports the PCI modalias table, and registers a `pci_driver` that delegates probe, remove, shutdown, and PM to the common rtw88 PCI layer.

Control flow is kernel PCI enumeration to `rtw_pci_probe()`, where common code retrieves the chip-info pointer and initializes the RTL8814A hardware. This file stores no per-device runtime state; its persistent behavior is driver registration and modalias generation. Hardware state is owned by shared PCI/core code and the chip ops behind `rtw8814a_hw_spec`.

Dependencies are Linux PCI/module APIs, `pci.h`, and `rtw8814a.h`. Risks are wrong device ID or wrong chip-info pointer. Test signals are module build, `modinfo` aliases, probe on `10ec:8813`, suspend/resume through `rtw_pm_ops`, shutdown, and clean remove.
