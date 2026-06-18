# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822be.c

## Purpose

`rtw8822be.c` is the PCIe module binding for Realtek RTL8822BE devices. It contains no chip logic itself; it identifies PCI device ID `10ec:b822`, attaches `rtw8822b_hw_spec` through `driver_data`, and delegates probe/remove/shutdown/error handling to the shared `rtw88` PCI transport layer.

## Important APIs and Types

- `rtw_8822be_id_table[]`: `struct pci_device_id` table with `PCI_DEVICE(PCI_VENDOR_ID_REALTEK, 0xB822)` and `.driver_data = (kernel_ulong_t)&rtw8822b_hw_spec`.
- `MODULE_DEVICE_TABLE(pci, rtw_8822be_id_table)`: exports modalias information for autoloading.
- `rtw_8822be_driver`: `struct pci_driver` using:
  - `.probe = rtw_pci_probe`
  - `.remove = rtw_pci_remove`
  - `.driver.pm = &rtw_pm_ops`
  - `.shutdown = rtw_pci_shutdown`
  - `.err_handler = &rtw_pci_err_handler`
- `module_pci_driver(rtw_8822be_driver)`: provides module init/exit registration.

## Control Flow and Integration

When the PCI core matches the device ID, `rtw_pci_probe()` receives the `pci_dev` and ID entry. The shared PCI probe path extracts `driver_data`, obtains the RTL8822B chip descriptor, maps PCI resources, allocates and initializes `struct rtw_dev`, loads firmware/tables, and registers with mac80211. Removal and shutdown reverse that work through common PCI callbacks. PCIe Advanced Error Reporting or reset handling flows through `rtw_pci_err_handler`.

## State and Persistence

This file owns only static module registration state. Device state is allocated by the common PCI probe path and chip-specific RTL8822B operations. Suspend/resume behavior is delegated to `rtw_pm_ops`; this module only wires the PM operations into the driver object.

## Dependencies

It depends on Linux PCI/module APIs plus rtw88 headers `pci.h` and `rtw8822b.h`. The real operational dependency is `rtw8822b_hw_spec`, which supplies all chip operations, firmware names, register tables, efuse layout, and capability flags.

## Risks

- Any incorrect PCI ID or `driver_data` pointer would bind the wrong hardware specification or fail autoloading.
- Because this file is deliberately thin, changes to shared PCI callbacks affect RTL8822BE behavior broadly.
- Error recovery depends on `rtw_pci_err_handler`; devices may behave poorly after bus reset if chip state cannot be rebuilt from the shared path.

## Test Signals

- Kernel module build and `modinfo` should expose the PCI alias for `10ec:b822`.
- On hardware, `lspci -nnk` should show this driver bound, and probe logs should enter the common `rtw88_pci` path.
- Suspend/resume, shutdown, and PCI error injection tests validate that this binding supplies the common callbacks correctly.
