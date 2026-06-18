# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_init.c

## Purpose

`pm8001_init.c` is the module, PCI, SCSI-host, libsas-HA, interrupt, DMA-memory, and power-management initialization layer for the PMC-Sierra/Adaptec/ATTO PM8001/PM80xx SAS/SATA low-level driver. It binds supported PCI device IDs to chip families, allocates and initializes the driver-private `struct pm8001_hba_info`, wires libsas callbacks through `pm8001_transport_ops`, registers the host with SCSI and libsas, reads controller identity and PHY configuration from firmware/NVMD, and tears all of that down on remove, suspend, resume, or module exit.

The file is not the firmware command implementation itself. It delegates hardware-specific operations through `PM8001_CHIP_DISP`, whose function table is selected from `pm8001_chips[]` and implemented by the SPC and SPCv/PM80xx hardware files. This makes this file the common orchestration layer across the older `chip_8001` and later 8006/8008/8009/8018/8019/807x families.

## Important APIs, Types, and Functions

Module parameters define runtime knobs:

- `logging_level` selects the `PM8001_*_LOGGING` categories used by `pm8001_dbg`.
- `link_rate` controls advertised SAS link rates and is validated in `pm8001_pci_alloc`.
- `pm8001_use_msix` controls MSI-X use and is exported in the header.
- `pm8001_use_tasklet` selects interrupt bottom-half scheduling when MSI-X is active.
- `pm8001_read_wwn` chooses between controller-provided WWNs and a fixed fallback SAS address.
- `pcs_event_log_severity` configures PCS event log severity for newer hardware paths.

Driver registration surfaces are `pm8001_sht`, `pm8001_transport_ops`, `pm8001_pci_table`, `pm8001_pci_driver`, `pm8001_init`, and `pm8001_exit`. `pm8001_sht` derives from `LIBSAS_SHT_BASE` and supplies scan callbacks, queue limits, host and sdev sysfs groups, queue-depth tracking, and blk-mq queue mapping. `pm8001_transport_ops` supplies the libsas LLDD callbacks implemented mainly in `pm8001_sas.c`: device discovery/removal, task execution, PHY control, task abort/reset/query, port formation, and task-management completion hooks.

Initialization helpers are:

- `pm8001_phy_init` seeds each local `pm8001_phy` and embedded `asd_sas_phy` with link rates, role, frame buffer, SAS address pointer, and libsas back-pointers.
- `pm8001_prep_sas_ha_init` allocates `sas_phy` and `sas_port` pointer arrays and the private `pm8001_hba_info` object in `sas_ha_struct`.
- `pm8001_pci_alloc` fills the HBA identity, chip dispatch pointer, logging/link-rate state, IOMB size, tasklets, BAR mappings, IRQs, DMA regions, device slots, and queue metadata.
- `pm8001_alloc` initializes HBA locks, requests interrupts, builds per-queue memory-region descriptors, allocates coherent firmware event logs, inbound/outbound queues, queue index pages, NVMD/flash/forensic buffers, and the `devices[]` table.
- `pm8001_init_ccb_tag` sizes `shost->can_queue` from firmware `max_out_io`, reserves low tags for internal commands, allocates `ccb_info[]`, and allocates each CCB's PRD DMA buffer.
- `pm8001_init_sas_add`, `pm8001_get_phy_settings_info`, and `pm8001_configure_phy_settings` read SAS WWNs and PHY profile data or apply ATTO-specific 12G PHY profiles.

Interrupt helpers are `pm8001_setup_msix`, `pm8001_request_msix`, `pm8001_request_irq`, `pm8001_free_irq`, `pm8001_handle_irq`, `pm8001_interrupt_handler_msix`, and `pm8001_interrupt_handler_intx`. MSI-X uses one housekeeping vector plus queue vectors for non-SPC chips when available; INTx uses the libsas HA pointer as the IRQ cookie.

Lifecycle and PM entry points are `pm8001_pci_probe`, `pm8001_pci_remove`, `pm8001_pci_suspend`, and `pm8001_pci_resume`. The module entry and exit functions allocate/release the global workqueue, attach/release the SAS transport template, and register/unregister the PCI driver.

## Control Flow

Module load starts in `pm8001_init`. If tasklets are requested without MSI-X, tasklets are disabled, because the direct INTx path does not use the multi-vector tasklet model. The function creates the per-CPU workqueue `pm8001_wq`, attaches the libsas transport template, and registers the PCI driver.

PCI probe follows a layered sequence:

1. Enable the PCI device, set bus master, adjust the PCI command register, request BAR regions, and configure a 44-bit DMA mask with 32-bit fallback.
2. Allocate a `Scsi_Host` with enough private space to store a `sas_ha_struct *`, allocate `sas_ha_struct`, and populate its arrays/private HBA with `pm8001_prep_sas_ha_init`.
3. Store the HA as PCI driver data and call `pm8001_pci_alloc`, which sets chip identity, maps BARs, requests IRQs, initializes phys/ports, allocates all coherent MPI memory regions, and allocates the device table.
4. Soft-reset and initialize the chip through dispatch methods, then call `pm8001_init_ccb_tag` after firmware has populated `main_cfg_tbl`.
5. Run chip post-init. If MSI-X provided multiple vectors, set `shost->nr_hw_queues` to `number_of_intr - 1` and enable `host_tagset` so the midlayer respects shared tag limits.
6. Register the SCSI host with `scsi_add_host`, enable firmware interrupts, configure thermal settings on non-SPC chips, read SAS addresses, configure PHY profiles, finalize libsas HA pointers with `pm8001_post_sas_ha_init`, register the HA with libsas, add the HBA to `hba_list`, mark runtime state, and scan the host.

Error unwinding is mostly reverse-order: remove SCSI host if added, free HBA resources, free HA/host allocations, release PCI regions, and disable the device. One notable edge is the `pm8001_init_ccb_tag` failure path in probe, which jumps to `err_out_enable` rather than the later HBA-free labels. That path is worth auditing because it can bypass resources allocated before CCB setup.

Interrupt flow starts with `pm8001_request_irq`. If MSI-X is enabled and the device reports MSI-X capability, `pm8001_setup_msix` allocates one vector for SPC or 2..64 vectors with affinity for non-SPC chips. `pm8001_request_msix` then registers each vector and stores vector metadata in `irq_vector[]`. `pm8001_handle_irq` filters with `is_our_interrupt`, either calls the chip ISR directly or schedules the indexed tasklet, and tasklets call `PM8001_CHIP_DISP->isr(pm8001_ha, irq_id)`.

Remove calls `sas_unregister_ha`, `sas_remove_host`, removes the HBA from `hba_list`, disables interrupts in firmware, soft-resets the chip, frees IRQs, kills tasklets, drops the SCSI host reference, frees every CCB PRD buffer plus `ccb_info` and `devices`, releases coherent MPI regions and BAR mappings through `pm8001_free`, frees libsas arrays and HA, then releases PCI regions and disables PCI.

Suspend blocks new SCSI requests, suspends libsas, flushes workqueue work, disables firmware interrupts, soft-resets the chip, frees IRQs, and kills tasklets. Resume reapplies DMA mask, prepares libsas resume, reinitializes the chip, disables interrupt bits before requesting IRQs, initializes tasklets, re-enables vectors, applies a 500 ms delay for 8070/8072, restarts each PHY with completion waits, and calls `sas_resume_ha`.

## State and Persistence Behavior

Most state is in-memory, per-HBA state stored in `struct pm8001_hba_info`: PCI/device pointers, BAR mappings, DMA memory descriptors, firmware configuration tables, queues, PHY/port arrays, SAS address, CCB table, device table, IRQ vector metadata, queue counts, logging level, link rate, fatal/non-fatal error tracking, and workqueue-related locks. `hba_list`, `pm8001_id`, `pm8001_wq`, and `pm8001_stt` are process-wide module state.

Firmware-visible persistent or semi-persistent data is accessed through NVMD and profile commands. `pm8001_init_sas_add` reads WWN bytes from EEPROM, flash VPD, or NVMD depending on chip/device/subsystem, then derives per-PHY SAS addresses by copying the base address and incrementing every four PHYs. `pm8001_configure_phy_settings` may read board PHY profile values from NVMD or apply hard-coded ATTO 12G internal/external PHY settings with `pm8001_set_phy_profile_single`. The file reads and applies persistent controller data but does not itself update flash, except indirectly through dispatch functions used elsewhere.

DMA memory is persistent only for the lifetime of the HBA instance. `pm8001_mem_alloc` is used to allocate aligned coherent regions; the original DMA handle is stored as `phys_addr`, while `virt_ptr` may be alignment-adjusted. Free paths compensate by freeing `total_len + alignment` with the original `phys_addr`.

CCB tags are split between reserved low tags tracked by `rsvd_tags` and request tags for blk-mq-backed I/O. `pm8001_init_ccb_tag` sets `shost->can_queue` to firmware CCB count minus reserved slots, so queue depth and tag ownership are shared contracts with `pm8001_sas.h` inline CCB allocation.

## Dependencies and Integration Points

This file depends on kernel PCI, DMA, IRQ, blk-mq, SCSI host, and libsas APIs. It includes `pm8001_sas.h`, `pm8001_chips.h`, and `pm80xx_hwi.h`, and uses constants/types from `pm8001_defs.h` through the header. Hardware operations are exclusively dispatched through `PM8001_CHIP_DISP`: chip reset/init/post-init, interrupt enable/disable, ISR entry, BAR unmap, NVMD read, PHY profile write, thermal config, fatal-error checks, and PHY start/control operations.

Important peer files are:

- `pm8001_sas.c`, which implements the callbacks registered here in `pm8001_transport_ops`.
- hardware-specific files providing `pm8001_8001_dispatch` and `pm8001_80xx_dispatch`.
- sysfs/ctl files that define `pm8001_host_groups` and `pm8001_sdev_groups`.
- MPI response/event handlers that complete the `nvmd_completion`, PHY completions, CCBs, and set-device-state completions initialized here.

The PCI ID table maps both generic `PCI_VDEVICE` IDs and subsystem-specific Adaptec/ATTO IDs to chip enum values. ATTO 8070/8072 subsystem IDs are also used later to choose internal/external PHY masks, so probe matching and PHY tuning are coupled.

## Risks and Edge Cases

Resource unwinding is a high-risk area. `pm8001_pci_alloc` requests IRQs before coherent memory and later calls `pm8001_free` on failure, but `pm8001_free` does not call `pm8001_free_irq` or kill tasklets; callers must ensure IRQ state is handled. The probe failure after `pm8001_init_ccb_tag` appears to jump to `err_out_enable`, which can skip host/HBA/PCI cleanup for failures after a substantial allocation sequence.

`pm8001_request_msix` has an error loop that iterates `j` but frees `pci_irq_vector(..., i)` with `irq_vector[i]` instead of the already registered `j` entries. That should be checked because partial MSI-X registration failure may leak or incorrectly free IRQs.

Completion waits can be long or unbounded. NVMD WWN reads use a 60-second timeout, but PHY profile reads use `wait_for_completion` without a timeout. Resume and scan paths wait on per-PHY completions and can block if firmware fails to respond. The code tries to avoid known fatal-error no-response states before some NVMD/PHY operations, but not every wait has a fatal-error guard.

The module parameter descriptions for `use_msix`, `use_tasklet`, and `read_wwn` use `MODULE_PARM_DESC(zoned, ...)`, which looks like a copy/paste bug. It is documentation-facing rather than data-path critical, but it can confuse module parameter metadata.

Interrupt/tasklet indexing assumes the chip ISR vector id and tasklet index are bounded by the arrays and requested vectors. Non-SPC chips may allocate fewer than `PM8001_MAX_MSIX_VEC` vectors, while tasklet initialization initializes all max vectors when MSI-X is present. The requested/free paths use `number_of_intr`, so unused tasklets are harmless but should stay consistent with vector routing.

BAR mapping uses logical BARs and skips PCI BAR 1 and 3 for paired 64-bit resources. Any hardware generation with different BAR layout must be reflected in the chip dispatch ioremap/unmap expectations.

## Test Signals

Useful validation signals include successful module load/unload with no leaks or IRQ warnings, PCI probe and remove on each supported chip family, MSI-X and INTx fallback paths, `use_tasklet=0` direct-ISR mode, `use_msix=0` INTx mode, and queue mapping with one versus multiple interrupt vectors.

Initialization tests should cover WWN reading from each selector path: fixed `read_wwn=0`, SPC 8081 offset `0x704`, SPC device `0x0042` offset `0x010`, ATTO 8070/8072 subsystem offset `0x010`, and default PM80xx offset `0x804`. PHY profile tests should cover ATTO 6G no-op, ATTO 12G internal/external masks by subsystem ID, Adaptec/no-subsystem no-op, and generic NVMD profile read.

Failure-injection points are `pci_alloc_irq_vectors*`, `request_irq`, `dma_alloc_coherent`, `kzalloc`, `chip_init`, `scsi_add_host`, `sas_register_ha`, NVMD timeout/failure, and PHY start completion loss. KASAN/KCSAN/lockdep plus DMA API debugging are relevant because the file mixes coherent allocation, IRQ teardown, tasklets, spinlocks, completions, and libsas registration.

Runtime tests should watch `/proc/interrupts` vector naming, SCSI scan completion, libsas discovery events, sysfs host/sdev group presence, suspend/resume with active devices, and removal while I/O and discovery work are pending. Logs gated by `PM8001_INIT_LOGGING`, `PM8001_FAIL_LOGGING`, and `PM8001_EVENT_LOGGING` are the primary built-in observability.
