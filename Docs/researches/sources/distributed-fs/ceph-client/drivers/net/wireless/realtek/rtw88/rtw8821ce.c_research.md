<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821ce.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821ce.c

## Purpose

This file is the PCI bus binding module for Realtek RTW8821CE devices. It does not implement chip behavior itself; it matches PCI device IDs, passes `&rtw8821c_hw_spec` to the shared `rtw88` PCI probe path, and registers a `struct pci_driver` with standard remove, power-management, shutdown, and PCI error-recovery hooks.

## Important APIs, Types, and Functions

- `rtw_8821ce_id_table[]`: PCI ID table with Realtek vendor ID and device IDs `0xB821` and `0xC821`. Each entry stores `(kernel_ulong_t)&rtw8821c_hw_spec` in `.driver_data`.
- `MODULE_DEVICE_TABLE(pci, rtw_8821ce_id_table)`: exports aliases so module autoload can bind matching PCI hardware.
- `rtw_8821ce_driver`: `struct pci_driver` with `.name = KBUILD_MODNAME`, `.id_table = rtw_8821ce_id_table`, `.probe = rtw_pci_probe`, `.remove = rtw_pci_remove`, `.driver.pm = &rtw_pm_ops`, `.shutdown = rtw_pci_shutdown`, and `.err_handler = &rtw_pci_err_handler`.
- `module_pci_driver(rtw_8821ce_driver)`: emits module init/exit registration boilerplate.

## Control Flow

At module load, `module_pci_driver` registers the driver with the PCI core. When a matching Realtek PCI function appears, the PCI core calls `rtw_pci_probe`. The common PCI probe reads the matched ID's `driver_data` and uses the `rtw8821c_hw_spec` chip description to allocate/configure the shared `rtw_dev`, firmware, MAC/PHY tables, efuse parsing, and mac80211 integration. Removal and shutdown are delegated to the shared PCI helpers.

PCI Advanced Error Reporting or similar recovery paths enter through `rtw_pci_err_handler`, so this small file also integrates 8821CE devices into common PCI error handling.

## State and Persistence Behavior

This file owns only static module registration data. Runtime device state is allocated and managed by the common PCI and core `rtw88` layers. Persistent effects are kernel driver binding and module alias metadata. Power-management state is not stored here; suspend/resume behavior is controlled by `rtw_pm_ops` and shared chip operations.

## Dependencies and Integration Points

- Linux PCI and module frameworks: `<linux/pci.h>`, `<linux/module.h>`, `struct pci_driver`, module alias generation.
- `pci.h`: common `rtw88` PCI probe/remove/shutdown/error handlers.
- `rtw8821c.h`: declares `rtw8821c_hw_spec`.
- `rtw8821c.c` and `rtw8821c_table.c`: provide chip operations and tables selected by this bus binding.
- mac80211/cfg80211 integration occurs in shared core code after probe.

## Risks

- Incorrect or missing PCI IDs prevent module autoload or leave supported devices unbound.
- A wrong `.driver_data` pointer would bind hardware to the wrong chip description and break efuse parsing, register tables, and firmware selection.
- Because all real behavior is delegated, this file relies on shared PCI code correctly interpreting `driver_data` and handling runtime PM/error recovery for 8821CE.
- The file has no per-ID quirks; if one PCI ID requires a different RFE, firmware, or power-management workaround, it must be represented elsewhere.

## Test Signals

- `modinfo` should show PCI aliases for `10ec:b821` and `10ec:c821`.
- Boot/probe on both IDs should call `rtw_pci_probe` and load `rtw88/rtw8821c_fw.bin`.
- Suspend/resume, shutdown, and PCI error recovery tests validate the delegated hooks.
- Build tests catch signature drift in common PCI helpers or `rtw8821c_hw_spec`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821ce.c -->
