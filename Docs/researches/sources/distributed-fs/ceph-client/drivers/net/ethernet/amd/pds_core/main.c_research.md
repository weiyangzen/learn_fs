# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/main.c

## Purpose
`main.c` owns the AMD/Pensando core driver's module, PCI, devlink, PF/VF, SR-IOV, reset, AER, BAR-mapping, workqueue, timer, and high-level lifecycle logic. It distinguishes PF from VF behavior, initializes PF firmware/core services, creates auxiliary devices for clients, and registers the `pci_driver`.

## Important APIs, Types, And Functions
Important functions include `pdsc_probe`, `pdsc_remove`, `pdsc_init_pf`, `pdsc_init_vf`, `pdsc_sriov_configure`, `pdsc_map_bars`, `pdsc_unmap_bars`, `pdsc_map_dbpage`, `pdsc_wdtimer_cb`, `pdsc_reset_prepare`, `pdsc_reset_done`, `pdsc_pci_error_detected`, `pdsc_pci_error_resume`, `pdsc_get_pf_struct`, module init/exit, and helper health timer stop/restart functions. Static objects include the PCI ID table, PF/VF devlink ops, devlink params, firmware health reporter ops, IDA for unique ids, and PCI error handlers.

## Control Flow
Module init verifies `KBUILD_MODNAME` matches `PDS_CORE_DRV_NAME`, creates debugfs root, and registers the PCI driver. Probe allocates a devlink instance with PF or VF ops, stores `pdsc`, marks initialization, sets PCI drvdata, creates debugfs device state, allocates a unique id, sets a coherent DMA mask, enables the PCI device, and dispatches to PF or VF init.

PF init requests PCI regions, maps BAR0 register windows and BAR1 doorbells, creates a single-threaded workqueue, initializes health and reset work, sets the watchdog timer, initializes locks, marks firmware dead, runs `pdsc_setup`, starts interrupts, creates the FWCTL aux device, registers devlink params and firmware health reporter, registers devlink, and starts the watchdog timer. VF init obtains PF driver data, records VF id, registers VF devlink, stores the VF pointer in PF `vfs[]`, and creates a vDPA aux device if enabled/supported.

Remove unregisters devlink first to block new users. PF remove destroys health reporter and params, disables SR-IOV and aux devices before AdminQ teardown, stops the watchdog/workqueue, marks stopping, masks interrupts, tears down core/device state, unmaps BARs, releases PCI regions, disables PCI, frees IDA/debugfs/devlink. VF remove unregisters its aux device from the PF and clears the PF VF pointer.

Reset prepare stops health checks, marks firmware down, deletes aux devices, unmaps BARs, releases regions, and disables PCI. Reset done re-enables PCI, remaps PF BARs, runs firmware-up recovery, restarts health checks, and recreates aux devices. AER frozen-channel handling requests reset; resume triggers locked function reset if firmware remains dead.

## State And Persistence
Per-device runtime state is `struct pdsc` allocated as devlink private data. Persistent kernel-lifetime state includes the PCI driver registration, debugfs root, and `pdsc_ida`. PF runtime state includes BAR mappings, workqueue, watchdog timer, locks, aux-device pointers, devlink reporter/params, and SR-IOV VF array. No disk persistence is used.

## Dependencies And Integration Points
The file integrates with PCI core, SR-IOV, AER/FLR reset callbacks, devlink allocation/registration/params/health, debugfs, DMA mask setup, workqueues, timers, auxiliary bus, firmware/core setup from `core.c`/`dev.c`, and Kbuild/module macros. `pdsc_get_pf_struct` is exported for VF/client paths.

## Risks
Lifecycle ordering is the main risk. Aux devices must be removed before AdminQ teardown so clients can cleanly issue firmware commands. Devlink must unregister before stopping internals to avoid new callbacks during teardown. BAR mapping currently maps only the first memory BAR fully and records later BAR metadata; doorbell mapping relies on the recorded BAR index. Reset paths differ for PF and VF and must avoid workqueue/timer use after destruction. SR-IOV configuration allocates `vfs` before enabling VFs and must free it on all disable/error paths.

## Test Signals
Validate PF and VF probe/remove, module load/unload, SR-IOV enable/disable, devlink registration, FWCTL/vDPA aux-device creation, FLR and AER reset flows, firmware health watchdog recovery, BAR signature failure handling, DMA mask failure, and remove while VFs and aux clients are active.
