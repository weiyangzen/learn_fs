# sources/distributed-fs/ceph-client/drivers/edac/edac_pci_sysfs.c

## Purpose
This file owns EDAC PCI sysfs exposure and generic PCI parity scanning. It creates `/sys/devices/system/edac/pci`, per-instance `pciN` kobjects, global policy attributes, per-controller counters, and helpers to clear/report PCI parity and non-parity errors.

## Important APIs and Functions
Policy getters include `edac_pci_get_check_errors()` and `edac_pci_get_poll_msec()`. Sysfs creation/removal APIs are `edac_pci_create_sysfs()` and `edac_pci_remove_sysfs()`. PCI scanning helpers include `get_pci_parity_status()`, `edac_pci_dev_parity_clear()`, `edac_pci_dev_parity_test()`, `edac_pci_do_parity_check()`, and `edac_pci_clear_parity_errors()`. Exported event handlers are `edac_pci_handle_pe()` and `edac_pci_handle_npe()`.

## Control Flow
Creating a controller sysfs instance first bumps/creates the top-level PCI kobject under the EDAC bus, then creates `pciN`, then links the controller kobject to the underlying device. Removal deletes the symlink, drops the instance kobject, and tears down the top-level kobject when the refcount reaches zero. Parity checks iterate all PCI devices, read and clear primary status, inspect bridge secondary status when applicable, increment global counters, and optionally panic if policy requests panic on new parity errors.

## State and Persistence
Static module state includes `check_pci_errors`, logging/panic policy booleans, `edac_pci_poll_msec`, global parity counters, `edac_pci_top_main_kobj`, and `edac_pci_sysfs_refcount`. Per-controller counters live in `struct edac_pci_ctl_info`.

## Dependencies and Integration
The file integrates with the EDAC bus from `edac_module.c`, PCI core iteration/config access, sysfs/kobject APIs, module reference counting, and `edac_pci.c` registration flow.

## Risks
Sysfs integer stores accept only buffers beginning with a digit and use `simple_strtoul`, so negative or malformed writes are silently ignored/partially accepted. PCI config access failures are mostly inferred from `0xffff`/`0xffffffff` sanity reads. Parity scans use `for_each_pci_dev()` and may sleep, so they deliberately do not disable interrupts across the whole scan.

## Test Signals
Signals include global sysfs attributes, `pciN/pe_count`, `pciN/npe_count`, device symlink creation, parity counter increments on injected/configured PCI errors, and panic behavior only when `edac_pci_panic_on_pe` is set.
