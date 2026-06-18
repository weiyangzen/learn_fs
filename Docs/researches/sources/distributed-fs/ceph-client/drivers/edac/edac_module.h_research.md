# sources/distributed-fs/ceph-client/drivers/edac/edac_module.h

## Purpose
This internal EDAC core header declares cross-file interfaces used within the EDAC subsystem: memory-controller sysfs helpers, device sysfs helpers, core workqueue operations, debugfs wrappers, and PCI parity/sysfs helpers.

## Important APIs and Types
The memory-controller declarations include `edac_mc_sysfs_init()`, `edac_mc_sysfs_exit()`, `edac_create_sysfs_mci_device()`, `edac_remove_sysfs_mci_device()`, logging policy getters, panic policy getters, polling period getters, and DIMM location formatting. Device helpers expose EDAC device sysfs registration and removal. Workqueue helpers include `edac_workqueue_setup()`, `edac_workqueue_teardown()`, `edac_queue_work()`, `edac_stop_work()`, and `edac_mod_work()`.

## Control Flow
The header does not implement runtime flow, but it defines build-time flow through `CONFIG_EDAC_DEBUG` and `CONFIG_PCI`. With debug enabled, debugfs functions are real declarations; otherwise inline no-op stubs are compiled. With PCI enabled, PCI parity functions are declared; otherwise preprocessor no-ops allow non-PCI EDAC builds to compile.

## State and Persistence
No state is owned here. The declarations expose runtime state managed by other translation units: sysfs kobjects, EDAC workqueue delayed work, debugfs dentries, and PCI parity policy/counters.

## Dependencies and Integration
The header includes `acpi/ghes.h`, `edac_mc.h`, `edac_pci.h`, and `edac_device.h`, making it a central private contract among EDAC core files and EDAC PCI/GHES code. It also maps debugfs remove calls directly to kernel `debugfs_remove*` helpers.

## Risks
Because this is an internal umbrella header, adding declarations here expands coupling across EDAC components. The non-PCI macros intentionally erase calls, but several are function-like macros without return values; code using return values must match the macro shapes. Debugfs stubs return `NULL`, so callers must tolerate unavailable debugfs.

## Test Signals
Build coverage is the main signal: EDAC should compile with and without `CONFIG_PCI`, and with and without `CONFIG_EDAC_DEBUG`. Runtime tests should confirm debugfs-dependent drivers degrade cleanly when debugfs support is disabled.
