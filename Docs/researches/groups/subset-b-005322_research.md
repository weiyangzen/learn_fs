# Research: subset-b-005322

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_init.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_sas.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_sas.c

## Purpose

`pm8001_sas.c` implements the libsas low-level driver behavior for PM8001/PM80xx adapters after the PCI/module layer has created an HBA. It handles SAS task submission, CCB/tag allocation and freeing, DMA mapping for commands, local PHY control, SCSI scan startup, device registration and deregistration with firmware, open-reject retry completion, and SCSI/SAS error recovery callbacks such as abort task, query task, LUN reset, and I_T nexus reset.

The file is the bridge between libsas domain objects (`domain_device`, `sas_task`, `asd_sas_phy`, `asd_sas_port`) and firmware-facing driver objects (`pm8001_hba_info`, `pm8001_device`, `pm8001_ccb_info`, `pm8001_phy`). Like the init file, it avoids chip-specific IOMB construction by delegating command preparation and management operations through `PM8001_CHIP_DISP`.

## Important APIs, Types, and Functions

Tag and CCB support consists of `pm8001_find_tag`, `pm8001_tag_alloc`, `pm8001_tag_free`, `pm8001_ccb_task_free`, and the inline `pm8001_ccb_alloc`/`pm8001_ccb_free` helpers from `pm8001_sas.h`. Reserved tags are tracked in `pm8001_ha->rsvd_tags`; normal request-backed I/O uses `sas_task_find_rq(task)->tag + PM8001_RESERVE_SLOT`.

Command submission is centered on `pm8001_queue_command`. It validates device/port availability, handles controller fatal-error short-circuiting, allocates a CCB, maps SG lists for non-ATA tasks, stores `task->lldd_task`, increments `pm8001_dev->running_req`, and dispatches to `pm8001_deliver_command`. `pm8001_deliver_command` selects one of `smp_req`, `ssp_io_req`, `ssp_tm_req`, `sata_req`, or `task_abort` based on `task_proto` and `task->tmf`.

PHY and scan functions are `pm8001_phy_control`, `pm8001_scan_start`, and `pm8001_scan_finished`. PHY control implements link-rate changes, hard/link reset, spinup-hold release, disable, and event counter reads. Scan start optionally issues SAS reinitialization for SPC and starts every PHY; scan finish waits at least one second and drains libsas work.

Device lifecycle functions are `pm8001_dev_found`, `pm8001_dev_found_notify`, `pm8001_dev_gone`, `pm8001_dev_gone_notify`, `pm8001_alloc_dev`, `pm8001_init_dev`, `pm8001_find_dev`, and `pm8001_free_dev`. Discovery allocates a `pm8001_device`, attaches it to `domain_device->lldd_dev`, resolves attached PHY IDs for expander and direct SATA paths, sends firmware registration, and waits for completion. Removal aborts outstanding work if needed, deregisters firmware device ID, clears local PHY attachment for direct-attached devices, frees the slot, and clears `dev->lldd_dev`.

Error recovery functions are `pm8001_abort_task`, `pm8001_query_task`, `pm8001_lu_reset`, `pm8001_clear_task_set`, `pm8001_I_T_nexus_reset`, `pm8001_I_T_nexus_event_handler`, `pm8001_setds_completion`, and `pm8001_tmf_aborted`. They integrate libsas helpers such as `sas_abort_task`, `sas_query_task`, `sas_lu_reset`, `sas_clear_task_set`, `sas_phy_reset`, `sas_execute_internal_abort_single`, and `sas_execute_internal_abort_dev`.

Diagnostics and retry helpers include `pm80xx_get_tag_opcodes`, `pm80xx_show_pending_commands`, `pm80xx_get_local_phy_id`, `pm8001_open_reject_retry`, and tracepoint use in ATA completion cleanup. `pm8001_mem_alloc` is also defined here for coherent DMA allocation with alignment adjustment, even though init code is its heaviest user.

## Control Flow

The normal I/O path begins when libsas calls `pm8001_queue_command`. If the task is not an internal abort and lacks a port, the driver completes it as `SAS_TASK_UNDELIVERED`/`SAS_PHY_DOWN`. If the controller is in fatal error, it completes the task as undelivered. Otherwise the function takes the HBA lock, verifies the target `pm8001_device` and `pm8001_port` are still valid and attached, allocates a CCB, maps non-ATA scatter/gather entries, links the CCB to `task->lldd_task`, records `n_elem`, increments `running_req`, and calls `pm8001_deliver_command`.

`pm8001_deliver_command` is a protocol switch. SMP tasks call the chip `smp_req`; SSP tasks call either `ssp_tm_req` for TMFs or `ssp_io_req` for normal I/O; SATA/STP tasks call `sata_req`; internal abort tasks call `task_abort`. If dispatch returns an error, `pm8001_queue_command` decrements `running_req`, unmaps any mapped SG list, frees the CCB, and returns the error to libsas.

Completion control flow is split across this file and MPI response handlers in other files. When firmware completes a command, those handlers call `pm8001_ccb_task_free` or `pm8001_ccb_task_free_done`. `pm8001_ccb_task_free` unmaps non-ATA SG lists, unmaps SMP request/response SGs, emits ATA completion trace data, clears `task->lldd_task`, and frees the CCB/tag. The `_done` helper then uses a memory barrier and calls `task->task_done`.

Discovery flow starts with `pm8001_dev_found_notify`. Under the HBA lock it allocates a device slot, links it to libsas, determines the local or expander-attached PHY, initializes a completion pointer, and sends `reg_dev_req`. It drops the lock before waiting for the registration completion. On device removal, `pm8001_dev_gone_notify` waits for outstanding `running_req` to drain by issuing `sas_execute_internal_abort_dev`, sends `dereg_dev_req`, clears direct local PHY attachment, frees the slot, and clears the libsas private pointer.

PHY control first rejects operations when firmware is in fatal-error state. Link-rate set, hard reset, and link reset start a disabled PHY before issuing the control operation. Disable synthesizes a libsas disconnect/loss-of-signal event when the PHY was linked, then sends `phy_stop_req`. Event reads lock the HBA, perform BAR4 window shifting for SPC, read counter registers from logical BAR2, restore BAR4 for SPC, and return.

Error recovery branches by protocol and chip. `pm8001_abort_task` marks the task aborted under the task state lock and installs a stack `sas_task_slow` completion if none exists. SSP uses `sas_abort_task` plus an internal abort. SATA/STP on `chip_8006` performs a multi-step recovery: set device state to recovery, hard reset the PHY, wait for PHY and port reset completions, abort all device tasks, wait for the target task's slow completion, and set device state back to operational. Other SATA/STP and SMP cases issue firmware/libsas internal aborts, with `ccb->task = NULL` for non-8006 SATA/STP to avoid racing a later completion against libsas task lifetime.

Open-reject retry handling walks all active CCBs while holding the HBA lock, optionally filters by task or device, forces task status to `SAS_OPEN_REJECT` with `SAS_OREJ_RSVD_RETRY`, decrements `running_req`, marks the task done, frees the CCB, and calls `task_done` outside the HBA lock unless the task is already aborted.

## State and Persistence Behavior

This file manages volatile runtime state only. The key state objects are:

- `task->lldd_task`, which points to a live `pm8001_ccb_info` while firmware owns the task.
- `pm8001_ccb_info`, which records task, device, tag, SG element count, PRD buffer, firmware-control context, and open-retry flag.
- `pm8001_device`, which records libsas domain device, firmware `device_id`, local/expander attached PHY, discovery and set-device-state completions, and `running_req`.
- `pm8001_phy`, which stores link state, completion pointers, reset completion/status, and local SAS PHY linkage.
- `pm8001_ha->rsvd_tags`, `devices[]`, `ccb_info[]`, and host-wide lock/bitmap lock.

Device slots are reused by zeroing and resetting `dev_type` to `SAS_PHY_UNUSED` and `device_id` to `PM8001_MAX_DEVICES`. CCB slots are considered active when `ccb_tag != PM8001_INVALID_TAG`; this convention is explicitly used by `pm8001_open_reject_retry` and pending-command diagnostics.

The only persistence-like interaction is firmware registration state. `pm8001_dev_found_notify` creates firmware-visible device registration and receives a firmware device ID asynchronously. `pm8001_dev_gone_notify` deregisters that ID. Device state transitions such as `DS_IN_RECOVERY` and `DS_OPERATIONAL` are firmware state changes, but they are not stored persistently by this file.

Concurrency is managed with the HBA spinlock for CCB/device/port operations, `bitmap_lock` for reserved tag allocation, task state locks for libsas task flags, atomics for per-device running request counts, and completions for firmware responses. Several waits occur after dropping the HBA lock, but some completion pointers are stack variables stored in shared structures, so missed or late completions are lifetime-sensitive.

## Dependencies and Integration Points

The file depends on libsas for task/domain/PHY abstractions and error recovery helpers, libata for STP/SATA queued command metadata and NCQ tags, DMA mapping APIs for SG lists, and PM8001 hardware dispatch functions for actual firmware IOMB construction and control commands.

Major dispatch dependencies are `smp_req`, `sata_req`, `ssp_io_req`, `ssp_tm_req`, `task_abort`, `phy_start_req`, `phy_stop_req`, `phy_ctl_req`, `reg_dev_req`, `dereg_dev_req`, `set_dev_state_req`, `hw_event_ack_req`, `fatal_errors`, and the BAR4 shift helpers for PHY counters. MPI response handlers elsewhere must complete `dcompletion`, `setds_completion`, `enable_completion`, `reset_completion`, and task slow completions for these paths to make progress.

This file is registered with libsas through `pm8001_transport_ops` in `pm8001_init.c`. Its prototypes and shared structures live in `pm8001_sas.h`. It also emits `pm80xx_tracepoints.h` trace events for ATA request completion. Hardware-specific files consume CCB state and PRD buffers prepared here when building inbound IOMBs.

## Risks and Edge Cases

Task lifetime races are the main risk. The code deliberately clears `ccb->task` for some abort paths to avoid completions touching a task after libsas may free it. Any new completion path must honor NULL `ccb->task` and the `SAS_TASK_STATE_ABORTED`/`DONE` flags, or it can double-complete or dereference freed tasks.

The use of stack completions stored in `pm8001_device` and `pm8001_phy` fields is safe only if firmware response handlers complete before the function returns or if timeout paths clear the pointer. Some paths wait without timeout (`pm8001_dev_found_notify`, `pm8001_lu_reset` set-device-state wait, `pm8001_setds_completion`, PHY starts in scan) and can hang if firmware does not respond.

`pm8001_dev_gone_notify` waits in a loop until `running_req` becomes zero after an internal abort. If completions are lost or `running_req` accounting becomes unbalanced, removal can stall. `pm8001_open_reject_retry` decrements `running_req` while walking CCBs, so it must stay consistent with every CCB free and completion path.

The device allocator scans for `SAS_PHY_UNUSED` without its own lock; callers currently hold the HBA lock in discovery. Future callers must preserve that locking rule. `pm8001_find_dev` scans by firmware `device_id` and logs failure, so duplicate or stale device IDs would return the first match.

`pm8001_phy_control(PHY_FUNC_GET_EVENTS)` reads fixed register offsets with BAR4 window manipulation for SPC. Incorrect chip detection or concurrent BAR4 users could corrupt register access if not protected by `pm8001_ha->lock`.

For direct-attached SATA device-not-present paths, `pm8001_queue_command` temporarily drops the HBA lock before calling `task_done` and then reacquires it. That avoids callback-under-lock behavior for ATA, but makes this branch sensitive to task and device state changes while unlocked.

## Test Signals

Data-path validation should cover SSP, SMP, SATA, STP, NCQ, and internal abort submission. Useful checks are correct CCB tag assignment for request-backed and reserved-tag commands, SG DMA map/unmap balance, `task->lldd_task` cleanup, `running_req` increments/decrements, and command completion tracepoints.

Discovery tests should exercise direct SAS, direct SATA, and expander-attached devices, including failure of `sas_find_attached_phy_id`, registration completion, deregistration, and removal with outstanding I/O. Hotplug and expander topology changes are especially relevant because they stress device slot reuse and local-vs-expander PHY handling.

Error recovery tests should cover SSP abort/query/LU reset, SATA/STP abort on `chip_8006` and non-8006 chips, I_T nexus reset/event handling for SATA and SSP, open-reject retry by task and by device, and controller fatal-error short-circuiting. Timeout/failure injection for PHY reset, port reset, internal abort, and set-device-state completions would expose hang and stale-pointer risks.

PHY-control tests should cover link-rate changes from disabled and enabled states, hard/link reset, disable notifications, spinup-hold release, and event counter reads on SPC and non-SPC chips. Lockdep, KASAN, DMA API debug, and tracing are appropriate because this file combines spinlocks, atomics, completions, task callbacks, and DMA mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_sas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_sas.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_sas.h

## Purpose

`pm8001_sas.h` is the central shared contract header for the PM8001/PM80xx SAS/SATA driver. It defines the driver name/version, logging masks, hardware dispatch interface, chip metadata, HBA/PHY/port/device/CCB/queue structures, DMA memory descriptors, firmware/NVMD/flash/forensic payload structures, device-state constants, external globals, function prototypes, and inline CCB allocation/free helpers.

The header is the glue between common libsas-facing code, PCI/module initialization, chip-specific hardware implementation, MPI response handling, sysfs/ctl support, firmware update support, and diagnostic dump support. Its structure layouts are both kernel-internal APIs and firmware/hardware-facing ABI descriptions for DMA rings, config tables, status tables, and PRDs.

## Important APIs, Types, and Constants

Top-level constants are `DRV_NAME` (`pm80xx`), `DRV_VERSION`, logging masks (`PM8001_FAIL_LOGGING` through `PM8001_EVENT_LOGGING`), `IS_SPCV_12G`, `PM8001_NAME_LENGTH`, and `PM8001_INVALID_TAG`. `pm8001_info` and `pm8001_dbg` standardize logging and use `pm8001_hba_info->logging_level` to gate debug categories.

`struct pm8001_dispatch` is the most important API in the header. It is the per-chip operations table used through `PM8001_CHIP_DISP`. It contains chip lifecycle hooks, BAR mapping/unmapping hooks, ISR and interrupt-control hooks, command builders for SMP/SSP/SATA/TMF/abort, PHY control and device register/deregister hooks, NVMD/flash hooks, device-state and SAS diagnostic hooks, SAS reinit, fatal-error detection, and hardware-event ACK.

Core topology/runtime structures are:

- `struct pm8001_chip_info`: encryption support flag, number of phys, and dispatch table pointer.
- `struct pm8001_port`: embedded `asd_sas_port`, attachment state, wide-port PHY map, port state/id, and list linkage.
- `struct pm8001_phy`: back-pointer to HBA, port pointer, embedded `asd_sas_phy`, SAS identity, optional SCSI device pointer, SAS address, PHY type/state, enable/reset completion pointers, received frame buffer, attached flag, link-rate bounds, reset status, and reset success.
- `struct pm8001_device`: libsas device type and `domain_device` pointer, attached PHY, local slot id, discovery and set-device-state completions, firmware device ID, and atomic running request count.
- `struct pm8001_ccb_info`: live `sas_task`, SG element count, CCB tag, PRD DMA handle, device pointer, PRD buffer, firmware-control context, and open-retry flag.
- `struct pm8001_hba_info`: the full HBA state object tying together PCI/device pointers, BARs, coherent memory map, encryption/forensic state, firmware tables, MPI queues, PHY attributes, SAS/libsas/SCSI state, chip identity, completions, tag bitmap, phys/ports, device and CCB arrays, IRQ/tasklet metadata, logging/link-rate settings, fatal/non-fatal status, queue counts, offsets, and IOP log tracking.

DMA and firmware-table structures include `pm8001_prd`, `pm8001_prd_imt`, `mpi_mem`, `mpi_mem_req`, `inbound_queue_table`, `outbound_queue_table`, `pm8001_hba_memspace`, `union main_cfg_table`, `union general_status_table`, and `sas_phy_attribute_table`. These encode PRDs, coherent memory regions, queue base/index metadata, BAR mappings, firmware main config table variants for SPC and PM80xx, and general status table variants.

Diagnostic and maintenance structures include `pm8001_ioctl_payload`, `forensic_data`, fatal-dump table offsets/status values, `fatal_error_reporter`, `pm8001_work`, `pm8001_fw_image_header`, `fw_flash_updata_info`, `fw_control_info`, and `fw_control_ex`. Device-state constants define firmware states such as `DS_OPERATIONAL`, `DS_IN_RECOVERY`, and `DS_NON_OPERATIONAL`; flash update status constants describe firmware update results.

Function prototypes expose the cross-file driver API: tag management, CCB/task cleanup, PHY control, scan callbacks, task queue/abort/reset/query, device found/gone, open-reject retry, memory allocation, chip/NVMD/flash/MPI helpers, event and response handlers, BAR shifting, PHY profile setup, dump accessors, fatal-error signaling, sysfs attribute groups, and diagnostics.

The inline helpers `pm8001_ccb_alloc`, `pm8001_ccb_free`, and `pm8001_ccb_task_free_done` are key shared behavior. Allocation chooses either a blk-mq/libsas request tag offset by `PM8001_RESERVE_SLOT` or a reserved low tag, initializes the matching `ccb_info[]` entry, and records task/device context. Freeing clears fields so manual scans can detect inactive CCBs, then frees low reserved tags when applicable. `_done` frees task resources and calls `task_done` after a memory barrier.

## Control Flow and Integration

This header does not run control flow directly, but it defines the data and callbacks that all runtime paths use:

1. `pm8001_init.c` selects a `pm8001_chip_info`, stores it in `pm8001_hba_info`, and uses `PM8001_CHIP_DISP` for chip init, reset, ISR, interrupt enable/disable, NVMD reads, PHY starts, and profile setup.
2. `pm8001_sas.c` uses the same dispatch table to build and send SMP/SSP/SATA/TMF/internal-abort commands, control phys, register/deregister devices, and change firmware device state.
3. Hardware-specific files implement the dispatch functions and consume `pm8001_hba_info`, `inbound_queue_table`, `outbound_queue_table`, `main_cfg_tbl`, `gs_tbl`, CCBs, PRDs, and device records to construct and process MPI messages.
4. MPI response/event files use the prototypes and structure fields to complete commands, update device IDs, complete discovery and reset completions, handle fatal/non-fatal dumps, and free CCBs.
5. sysfs/ctl paths use host/sdev attribute groups, firmware-control structures, dump functions, and NVMD/flash request prototypes.

The CCB inline flow is especially important. A submitted `sas_task` maps to one `ccb_info[tag]`; the tag comes from blk-mq when available or from the reserved bitmap for internal work. The chip-specific request builder receives the CCB and uses its task, device, PRD buffer, and tag to build firmware commands. Completion handlers free the CCB and call the task callback through the helpers.

## State and Persistence Behavior

`pm8001_sas.h` defines volatile in-memory state; it does not persist state itself. Some structures describe hardware or firmware state that may be persistent or long-lived outside the driver:

- `main_cfg_tbl`, `general_status_table`, queue tables, and PRDs mirror firmware-visible DMA/BAR state.
- `pm8001_ioctl_payload`, `fw_control_ex`, and flash/NVMD prototypes represent requests that may read or modify controller nonvolatile memory or firmware images.
- Fatal/non-fatal forensic fields in `pm8001_hba_info` track dump progress, offsets, preserved transfer counts, and fatal table BAR/shift data.
- `pm8001_device->device_id` is assigned by firmware during registration and remains valid until deregistration.

State ownership conventions are encoded in the structures. `pm8001_hba_info->lock` is the host-wide lock for CCB/device/port operations, while `bitmap_lock` protects reserved tags. `running_req` is atomic because command completion and removal/error-recovery paths coordinate on it. Completion pointers in `pm8001_phy`, `pm8001_device`, and `pm8001_hba_info` are borrowed pointers to stack or caller-owned completions, so users must set/clear them carefully around waits.

The layout of many structures is ABI-sensitive. `pm8001_prd` is explicitly packed, firmware image headers are packed/aligned, endian annotations are used in PRDs and queue indices, and main/general table unions preserve different SPC and PM80xx layouts. Changes to these fields can break firmware communication even if C code still compiles.

## Dependencies and External Contracts

The header includes kernel primitives (`spinlock`, `delay`, DMA mapping, PCI, interrupt, workqueue, atomics, blk-mq) and SCSI/SAS interfaces (`libsas`, `scsi_tcq`, `sas_ata`). It includes `pm8001_defs.h` for array sizes, memory-region indices, queue limits, link-rate constants, chip enums, and other hardware constants.

External symbols declared here are defined across the driver:

- `pm8001_8001_dispatch` and `pm8001_80xx_dispatch` in chip-specific implementations.
- `pm8001_wq`, `hba_list`, `pm8001_use_msix`, and `pcs_event_log_severity` in init/common code.
- MPI builders, response handlers, event handlers, BAR shift helpers, PHY profile helpers, fatal dump functions, and sysfs attribute groups in companion pm8001/pm80xx files.

The libsas contract is represented by prototypes for `pm8001_queue_command`, `pm8001_dev_found`, `pm8001_dev_gone`, `pm8001_phy_control`, scan callbacks, and error recovery functions. The firmware contract is represented by dispatch callbacks, queue table structures, config/status table layouts, PRDs, NVMD/flash control structures, and dump/forensic definitions.

## Risks and Edge Cases

Because this header centralizes shared structure definitions, small changes can have broad effects. Reordering or resizing fields in firmware-visible structs, changing packing/alignment, or altering endian types can corrupt DMA communication. Even purely internal fields such as `ccb_tag`, `device`, completion pointers, and `running_req` are used by multiple files and concurrency contexts.

The CCB inline allocator assumes `ccb_info` is large enough for either `rq->tag + PM8001_RESERVE_SLOT` or a reserved low tag. That relies on `pm8001_init_ccb_tag` sizing `shost->can_queue`, host tagset behavior, and firmware `max_out_io` consistently. Any mismatch can produce out-of-bounds CCB access.

`pm8001_ccb_free` always calls `pm8001_tag_free`, but `pm8001_tag_free` ignores tags at or above `PM8001_RESERVE_SLOT`. This split is intentional; callers must not separately release request tags through the reserved bitmap. Active CCB detection depends on `ccb_tag == PM8001_INVALID_TAG`, so all completion and abort paths must use the common free helpers or maintain the same cleanup convention.

Completion pointer fields are non-owning and can point at stack completions in caller functions. Late firmware responses after timeout or teardown can complete stale pointers unless timeout paths clear them. The header cannot enforce this; users of `enable_completion`, `reset_completion`, `dcompletion`, `setds_completion`, and `nvmd_completion` must be audited together with response handlers.

`pm8001_hba_info` mixes many concerns: PCI/BAR state, DMA memory, firmware tables, topology, command slots, interrupts, error dumps, queue offsets, and logging. That breadth makes it easy for cross-file changes to introduce hidden dependencies. Locking rules are mostly conventional rather than encoded in type boundaries.

## Test Signals

Compile-time test signals include sparse/endian checking, structure packing/size checks where available, and warnings from all files that include the header. Runtime validation should focus on the contracts encoded here: CCB allocation/free under normal I/O and internal aborts, reserved-tag exhaustion, blk-mq tag offsets, device registration IDs, queue table setup, PRD DMA correctness, and firmware table decoding for both SPC and PM80xx layouts.

Fault injection should target allocation failures for `ccb_info`, PRD buffers, device arrays, and coherent queue regions; firmware response loss for every completion pointer type; and fatal-error transitions while requests are active. DMA API debug, KASAN, KCSAN, lockdep, and tracing are useful because the header-defined objects are shared by interrupt handlers, tasklets, workqueue work, SCSI callbacks, and libsas error recovery.

Hardware coverage should include `chip_8001` and newer PM80xx/SPCv devices, MSI-X and INTx modes, request-backed SCSI I/O and reserved-tag internal commands, NVMD/flash operations, fatal/non-fatal dump retrieval, and sysfs host/sdev attribute access through `pm8001_host_groups` and `pm8001_sdev_groups`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_sas.h -->
