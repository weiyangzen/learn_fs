# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad.c

## Purpose

`bfad.c` is the Linux PCI/module entry point for the QLogic/Brocade BR-series Fibre Channel/FCoE SCSI driver. It owns module parameters, firmware image loading, PCI probe/remove, PCI error recovery, interrupt setup, driver instance state transitions, BFA/FCS attach/start/stop, memory allocation for BFA modules, physical/vport setup, and top-level module init/exit.

The file integrates Linux kernel services with the BFA hardware abstraction and FCS stack. It claims supported PCI devices, loads the correct firmware blob for the ASIC family, maps PCI BARs, configures DMA and interrupts, attaches the BFA core, starts FC services, and exposes the adapter to the SCSI/FC transport through BFAD IM helpers.

## Important APIs, Types, And Functions

Module-scope configuration includes `num_rports`, `num_ios`, `num_tms`, `num_fcxps`, `num_ufbufs`, `reqq_size`, `rspq_size`, `num_sgpgs`, `rport_del_timeout`, `bfa_lun_queue_depth`, `bfa_io_max_sge`, `bfa_log_level`, `ioc_auto_recover`, `bfa_linkup_delay`, MSI-X disable knobs, FDMI/debugfs toggles, PCIe read request size, `max_xfer_size`, and `max_rport_logins`. Firmware globals hold image pointers and sizes for CB, CT, and CT2 firmware.

The BFAD instance state machine is implemented by `bfad_sm_uninit()`, `bfad_sm_created()`, `bfad_sm_initializing()`, `bfad_sm_operational()`, `bfad_sm_stopping()`, `bfad_sm_failed()`, and `bfad_sm_fcs_exit()`. Events drive creation, init success/failure, HAL init failure recovery, FCS exit, stop, and final cleanup.

BFA/FCS callbacks include `bfad_hcb_comp()`, `bfa_cb_init()`, `bfa_fcb_lport_new()`, `bfa_fcb_rport_alloc()`, and `bfa_fcb_pbc_vport_create()`. These complete HAL commands, respond to BFA init, allocate Linux/FCS port objects, allocate FCS rport wrappers, and create preboot vports.

Memory/configuration functions include `bfad_hal_mem_alloc()`, `bfad_hal_mem_release()`, and `bfad_update_hal_cfg()`. They obtain default BFA configuration, apply module-parameter overrides, request BFA memory descriptors, allocate KVA with `vzalloc()`, allocate DMA with `dma_alloc_coherent()`, and mirror resolved defaults back into module globals.

PCI and driver lifecycle functions include `bfad_pci_init()`, `bfad_pci_uninit()`, `bfad_drv_init()`, `bfad_drv_start()`, `bfad_fcs_stop()`, `bfad_stop()`, `bfad_cfg_pport()`, `bfad_uncfg_pport()`, `bfad_start_ops()`, `bfad_worker()`, `bfad_pci_probe()`, and `bfad_pci_remove()`.

Interrupt functions include `bfad_intx()`, `bfad_msix()`, `bfad_init_msix_entry()`, `bfad_install_msix_handler()`, `bfad_setup_intr()`, and `bfad_remove_intr()`. They select MSI-X or line interrupt mode, dispatch to BFA interrupt handlers, dequeue/process/free BFA completion callbacks, and clean up vectors.

PCI error recovery is implemented by `bfad_pci_error_detected()`, `restart_bfa()`, `bfad_pci_slot_reset()`, `bfad_pci_mmio_enabled()`, and `bfad_pci_resume()`, registered in `bfad_err_handler`.

Module and firmware functions include `bfad_init()`, `bfad_exit()`, `bfad_read_firmware()`, `bfad_load_fwimg()`, `bfad_free_fwimg()`, the PCI ID table, `bfad_pci_driver`, `MODULE_FIRMWARE()`, and module metadata declarations.

## Control Flow

Module load starts in `bfad_init()`: it logs driver version, remembers the SGPG module parameter, initializes the initiator-mode module, enables supported FC4 roles, propagates auto-recover and rport limits to BFA/FCS globals, and registers the PCI driver.

PCI probe allocates a `struct bfad_s`, trace module, AEN queues, firmware image, PCI resources, instance number, locks, lists, debugfs, BFA memory, and BFA/FCS attachment. It initializes the BFAD state machine to uninit and sends `BFAD_E_CREATE`.

The create/init state path creates `bfad_worker`, sets up interrupts, calls `bfa_iocfc_init()`, installs MSI-X handlers when enabled, starts the BFA timer, and waits for `bfa_cb_init()` to complete. On successful HAL init it stops the worker and calls `bfad_start_ops()`. On HAL init failure it initializes enough FCS/physical-port state to allow a deferred recovery path and marks the state failed.

`bfad_start_ops()` clamps transfer size, fills FCS driver info from module parameters and PCI name, initializes or updates FCS config, allocates the physical SCSI host, initializes FC host attributes, probes the initiator mode, starts IOC/FCS operations, completes preboot vport creation by creating FC transport vports, waits for rports online according to link-up delay policy, and logs device claim.

Interrupt flow is shared between INTx and MSI-X. The handler enters under `bfad_lock`, calls the appropriate BFA interrupt routine, dequeues completion callbacks, drops the lock, processes callbacks, then frees the completion list under lock.

The periodic BFA timer runs `bfa_timer_beat()`, drains and processes completion callbacks, and re-arms itself at `BFA_TIMER_FREQ`.

Remove sends `BFAD_E_STOP`, lets the state machine stop FCS and IOC, detaches BFA, releases HAL memory, removes debugfs, removes the instance from the global list, unmaps/release PCI resources, and frees trace and BFAD allocations.

PCI error recovery suspends or stops BFA/FCS depending on error severity. Frozen-channel recovery stops FCS, removes interrupts, deletes the timer, disables PCI, then slot reset re-enables PCI, restores state, verifies config space, restores DMA mask/mastering, reattaches BFA, initializes IOC, reinstalls interrupts/timer, and restarts driver operations.

Firmware loading is lazy and per ASIC family. `bfad_load_fwimg()` picks CB, CT, or CT2 image based on PCI device ID and calls `request_firmware()` only if the cached image size is zero. Module exit frees cached images.

## State And Persistence Behavior

Persistent external state comes from module parameters, PCI device IDs, firmware files, PCI config state saved with `pci_save_state()`, and hardware/firmware configuration. Driver state is in memory: global instance count/list protected by `bfad_mutex`, per-device flags, completions, kthread pointer, locks, timer, mapped BARs, DMA/KVA memory descriptors, FCS/BFA structs, vport lists, AEN queues, and firmware image caches.

`bfad_update_hal_cfg()` normalizes user-provided module parameters into BFA config, then writes resolved defaults back to globals so sysfs/module parameter views expose actual values rather than zero. `bfad_start_ops()` temporarily derives default link-up delay when `bfa_linkup_delay` is negative, then restores `-1`.

The firmware image cache is process/module lifetime state. Images are loaded on first matching probe and reused until `bfad_exit()` calls `bfad_free_fwimg()`.

State-machine flags are central to cleanup decisions: `BFAD_DRV_INIT_DONE`, `BFAD_HAL_START_DONE`, `BFAD_CFG_PPORT_DONE`, `BFAD_FC4_PROBE_DONE`, `BFAD_HAL_INIT_DONE`, `BFAD_HAL_INIT_FAIL`, `BFAD_MSIX_ON`, `BFAD_INTX_ON`, and EEH flags determine whether resources are active and what teardown path should execute.

## Dependencies And Integration Points

The file depends heavily on Linux kernel PCI, firmware, DMA, interrupt, timer, kthread, completion, module parameter, debugfs, and FC transport APIs. It includes `bfad_drv.h`, `bfad_im.h`, `bfa_fcs.h`, `bfa_defs.h`, and `bfa.h`.

It integrates downward with BFA core through `bfa_attach()`, `bfa_detach()`, `bfa_cfg_get_default()`, `bfa_cfg_get_meminfo()`, `bfa_iocfc_init()`, `bfa_iocfc_start()`, `bfa_iocfc_stop()`, `bfa_intx()`, `bfa_msix()`, `bfa_msix_getvecs()`, `bfa_msix_init()`, `bfa_timer_beat()`, and completion queue helpers.

It integrates with FCS through `bfa_fcs_attach()`, `bfa_fcs_init()`, `bfa_fcs_exit()`, `bfa_fcs_driver_info_init()`, `bfa_fcs_update_cfg()`, `bfa_fcs_fabric_modstart()`, `bfa_fcs_pbc_vport_init()`, `bfa_fcs_vport_create()`, `bfa_fcs_vport_start()`, and FCS rport/vport callbacks.

It integrates upward with Linux SCSI/FC transport through BFAD IM helpers such as `bfad_im_module_init()`, `bfad_im_probe()`, `bfad_im_probe_undo()`, `bfad_im_port_new()`, `bfad_im_port_delete()`, `bfad_im_scsi_host_alloc()`, `bfad_im_scsi_host_free()`, `bfad_fc_host_init()`, and `fc_vport_create()`.

## Risks And Edge Cases

Probe failure unwind is multi-stage and must stay aligned with allocation order. A missing unwind step can leak DMA, KVA, IRQs, debugfs entries, trace memory, or PCI mappings; an extra step can double free partially initialized resources.

`bfad_read_firmware()` always calls `release_firmware(fw)` on exit, even after `request_firmware()` failure leaves `fw` uninitialized in the local scope. That pattern is suspicious in isolation and should be checked against the exact kernel version/compiler behavior and any downstream patches.

The state machine mixes synchronous waits, kthread fallback, and callback completions. Races around `bfad->bfad_tsk`, `bfad->comp`, timer deletion, and interrupt removal are high-risk, especially during init failure, remove, and PCI error recovery.

MSI-X setup first enables vectors, then handlers are installed later in the state-machine path. Error handling must preserve whether vectors are merely enabled or handlers are installed. The code falls back to INTx when MSI-X allocation fails, and CT hardware can retry with one vector.

PCI error recovery reattaches and restarts BFA using existing memory/configuration. Any state not reset by `bfa_attach()` or `bfad_drv_start()` can leak across reset. Permanent failure intentionally defers cleanup to normal remove to avoid inconsistent state.

Module parameter bounds are partial. Some parameters are clamped or ignored if invalid, while others are passed through to deeper layers. Tests should verify invalid values do not produce undersized queues, unsupported speeds, or unsafe memory sizing.

## Test Signals

Static signals include successful kernel build, module parameter registration, firmware declarations, and no resource-leak warnings from static analysis on probe/remove paths. Runtime load tests should verify firmware request by ASIC family, successful PCI probe, DMA mask and BAR mapping, BFA attach/init/start, physical SCSI host registration, interrupt delivery in both MSI-X and INTx modes, timer-driven completion processing, and clean module unload.

Failure-path tests should inject firmware missing, memory allocation failure, `pci_enable_device()`/`pci_request_regions()`/DMA mask/BAR map failures, MSI-X allocation/handler failures, BFA init failure, BFAD IM probe failure, vport creation failure, and PCI EEH frozen/permanent failures. Good signals are correct state-machine transitions, no hangs on completions, no live timers/IRQs after remove, no leaked DMA/KVA memory, and successful recovery after slot reset.
