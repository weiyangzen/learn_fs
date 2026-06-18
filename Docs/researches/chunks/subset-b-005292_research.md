# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_init.c lines 8854-15820

## Scope

This chunk covers the late and terminal portion of `lpfc_init.c`, from SLI4 RPI header setup through PCI probe/remove, power management, PCI error recovery, firmware update, congestion/RAS support, and module registration/exit. It is the code that turns previously defined low-level LPFC facilities into concrete PCI-device lifecycle behavior for both SLI3 (`LPFC_PCI_DEV_LP`) and SLI4 (`LPFC_PCI_DEV_OC`) adapters.

## Purpose

The code initializes and tears down Emulex/Broadcom LPFC Fibre Channel HBAs in the Linux SCSI/FC transport stack. In this chunk, initialization is organized around:

- Allocating `struct lpfc_hba` and creating the physical `struct lpfc_vport`/`Scsi_Host`.
- Mapping PCI BARs and SLI interface registers for SLI3 and SLI4 devices.
- Reading SLI4 firmware/device configuration, resource limits, FC4 capability, persistent topology, congestion signaling, function numbering, and SLI4 parameter descriptors.
- Allocating and creating SLI4 EQ/CQ/WQ/MQ/RQ queues and their lookup tables.
- Enabling interrupts with MSI-X/MSI/INTx fallback, including SLI4 CPU/vector/hardware-queue affinity mapping and CPU-hotplug handling.
- Handling removal, suspend/resume, PCI Advanced Error Reporting recovery, function reset, firmware download, congestion-buffer registration, OAS/RAS feature enablement, and final module registration.

## Important APIs, Types, and Functions

- `lpfc_sli4_create_rpi_hdr()` / `lpfc_sli4_remove_rpi_hdrs()` allocate and free 4 KiB DMA RPI header templates for SLI4 ports that do not use extents. They update `phba->sli4_hba.lpfc_rpi_hdr_list`, `next_rpi`, and `rpi_hdrs_in_use`.
- `lpfc_hba_alloc()` / `lpfc_hba_free()` own the main `struct lpfc_hba` lifetime and board-number allocation through `lpfc_get_instance()`/`idr_remove()`.
- `lpfc_create_shost()` / `lpfc_destroy_shost()` create or destroy the physical vport and SCSI host, initialize FC timers, attach debugfs, stash `Scsi_Host` in PCI driver data, set FDMI/SmartSAN masks, and handle NVMe target-only pport setup.
- `lpfc_sli_pci_mem_setup()` / `lpfc_sli_pci_mem_unset()` map SLI3 BAR0/BAR2, allocate SLI2 SLIM and HBQ DMA areas, and set register pointers such as `HAregaddr`, `CAregaddr`, `HSregaddr`, and `HCregaddr`.
- `lpfc_sli4_pci_mem_setup()` / `lpfc_sli4_pci_mem_unset()` map SLI4 config, control, doorbell, and DPP BARs according to `lpfc_sli_intf_if_type`. They select if-type-specific EQ/CQ doorbell handlers and populate SLI4 register pointers with helpers `lpfc_sli4_bar0_register_memmap()`, `lpfc_sli4_bar1_register_memmap()`, and `lpfc_sli4_bar2_register_memmap()`.
- `lpfc_sli4_post_status_check()` waits up to 30 seconds for POST readiness through the port semaphore/status registers, checks unrecoverable-error registers, records `work_status[]`, and flags PLDV state for supported adapters.
- `lpfc_create_bootstrap_mbox()` / `lpfc_destroy_bootstrap_mbox()` allocate a 16-byte-aligned coherent DMA bootstrap mailbox region and encode the SLI4 high/low 30-bit mailbox DMA address format.
- `lpfc_sli4_read_config()` issues `READ_CONFIG`, captures max/base XRI/VPI/VFI/RPI/FCFI and queue resource counts, lmt, link info, FA-PWWN, trunking, extents, encryption support, BB credit support, persistent topology, congestion-registration mode, forced link speed, PF/VF function config, and clamps queue depth/vport counts to driver limits.
- `lpfc_get_sli4_parameters()` issues `GET_SLI4_PARAMETERS` and fills `phba->sli4_hba.pc_sli4_params` plus driver feature knobs such as PHWQ, xPSGL, NVMe, suppress-response, EQDR, max segment size, embedded FCP I/O, expanded WQ/CQ page use, MDS diagnostics, and NSLER.
- `lpfc_sli4_queue_verify()`, `lpfc_sli4_queue_create()`, `lpfc_sli4_queue_setup()`, `lpfc_sli4_queue_unset()`, and `lpfc_sli4_queue_destroy()` split queue lifecycle into host-memory allocation, firmware creation, firmware destruction, and host-memory release.
- `lpfc_alloc_io_wq_cq()` creates per-hardware-queue I/O CQ/WQ objects, while `lpfc_create_wq_cq()` performs firmware-side CQ then WQ/MQ creation and binds WQs to rings.
- `lpfc_sli4_cq_event_pool_create()`, `lpfc_sli4_cq_event_pool_destroy()`, `lpfc_sli4_cq_event_alloc()`, and release variants manage a pool of `struct lpfc_cq_event` entries used by ISR/worker slow-path event handoff.
- `lpfc_pci_function_reset()` performs if-type-specific SLI4 function/port reset: mailbox reset for if-type 0, status/ready polling and control-register INIT_PORT for if-type 2/6.
- `lpfc_sli_enable_intr()` and `lpfc_sli4_enable_intr()` enable interrupts with fallback from MSI-X to MSI to INTx. SLI4 uses `request_threaded_irq()` for MSI-X EQ handlers and records `lpfc_hba_eq_hdl` state.
- `lpfc_cpu_affinity_check()`, `lpfc_find_cpu_handle()`, `lpfc_sli4_enable_msix()`, `lpfc_irq_rebalance()`, `lpfc_cpu_online()`, and `lpfc_cpu_offline()` build and maintain the SLI4 CPU/EQ/hardware-queue map, including NUMA/non-hyperthread modes and temporary EQ polling during CPU offline.
- `lpfc_pci_probe_one_s3()` and `lpfc_pci_probe_one_s4()` are the primary attach paths. `lpfc_pci_probe_one()` dispatches by reading `LPFC_SLI_INTF`.
- `lpfc_pci_remove_one_s3()` and `lpfc_pci_remove_one_s4()` perform complete detach. SLI4 additionally unregisters congestion buffers, tears down NVMe/NVMeT transport objects, destroys multixri pools, calls `lpfc_sli4_hba_unset()`, and unmaps SLI4 BARs.
- `lpfc_pci_suspend_one_*()`, `lpfc_pci_resume_one_*()`, `lpfc_io_error_detected_*()`, `lpfc_io_slot_reset_*()`, and `lpfc_io_resume_*()` integrate with PCI PM and AER callbacks.
- `lpfc_write_firmware()` and `lpfc_sli4_request_firmware_update()` implement synchronous or asynchronous `.grp` firmware download through Linux firmware APIs and LPFC object-write mailbox plumbing.
- `lpfc_init_congestion_buf()`, `lpfc_init_congestion_stat()`, `lpfc_reg_congestion_buf()`, and `lpfc_unreg_congestion_buf()` manage the CMF/FPIN congestion information buffer shared with firmware.
- `lpfc_sli4_oas_verify()` and `lpfc_sli4_ras_init()` gate optional OAS and RAS firmware logging based on adapter support and module parameters.
- `lpfc_init()` and `lpfc_exit()` register/unregister the misc management device, FC transport templates, CPU-hotplug state, PCI driver, and global HBA IDR.

## Control Flow

### SLI4 Probe

`lpfc_pci_probe_one()` reads `LPFC_SLI_INTF`; valid SLI4 devices go to `lpfc_pci_probe_one_s4()`, all others use the SLI3 path. The SLI4 probe path:

1. Allocates `phba`, initializes `poll_list`, enables the PCI device, and installs SLI API callbacks for `LPFC_PCI_DEV_OC`.
2. Maps SLI4 PCI memory with `lpfc_sli4_pci_mem_setup()`, which validates `SLI_INTF`, optionally reads `ASIC_ID`, maps BARs by if-type, and assigns doorbell/interrupt helper functions.
3. Allocates SLI4-specific and common driver resources, initializes RRQ and FCF-priority lists, and sets model strings.
4. Stops the port to a known state, initializes CPU map and EQ-handle arrays, enables interrupts, reduces to one IRQ/MRQ for non-MSI-X, and computes CPU affinity.
5. Creates the physical `Scsi_Host`/vport and sysfs attributes.
6. Calls `lpfc_sli4_hba_setup()` for the firmware/device bring-up, then records/logs interrupt mode, posts adapter-arrival event via `lpfc_post_init_setup()`, creates NVMe localport when configured, optionally requests firmware update, creates static vports, sets up the CPU-hotplug poll timer, and registers the hotplug instance.
7. On failure, unwinds in reverse order: sysfs, shost, interrupts, common resources, SLI4 resources, BAR mappings, PCI enablement, and `phba`.

### SLI3 Probe

`lpfc_pci_probe_one_s3()` follows the older SLI3 sequence: allocate HBA, enable PCI, set LP API table, map SLIM/control BARs and coherent SLIM/HBQ DMA, set up SLI3 resources and IOCB lists, create common resources, create shost/sysfs, then loop through interrupt modes. Each interrupt mode is validated by `lpfc_sli_hba_setup()` plus an active interrupt counter check before accepting the mode. It then posts init setup and creates static vports.

### Queue Lifecycle

SLI4 queue management is two-phase:

- `lpfc_sli4_queue_create()` allocates host queue descriptors and DMA-backed queue pages, initializes hardware-queue lock/list state, creates per-vector EQ descriptors, per-HDWQ I/O CQ/WQ pairs, NVMeT MRQ arrays when enabled, slow-path mailbox/ELS/NVMe-LS queues, unsolicited RQs, and clears per-HDWQ protocol stats.
- `lpfc_sli4_queue_setup()` creates firmware queues in dependency order: query firmware config, create EQs, create I/O CQ/WQs, create mailbox MQ/CQ, optional NVMeT CQ sets/MRQs, ELS WQ/CQ, NVMe LS WQ/CQ, unsolicited RQ, tune EQ delay, and build `cq_lookup`.
- `lpfc_sli4_queue_unset()` destroys firmware-side objects in reverse-ish dependency order.
- `lpfc_sli4_queue_destroy()` marks `LPFC_QUEUE_FREE_INIT`, waits for `LPFC_QUEUE_FREE_WAIT` users to drain, cleans poll lists, frees queue descriptors and backing resources, clears `lpfc_wq_list`, and drops the free-init flag.

### Interrupt and Affinity Flow

SLI4 MSI-X allocation starts with `cfg_irq_chann`, optionally constrained by NUMA/non-hyperthread affinity masks. Each allocated vector gets an `lpfc_hba_eq_hdl`, handler name, IRQ number, and threaded interrupt. The CPU map records first-IRQ CPUs and later `lpfc_cpu_affinity_check()` fills in missing CPU-to-EQ and CPU-to-HDWQ assignments, preferring same package/core, then package, then round-robin. CPU-hotplug callbacks rebalance affinities and switch affected EQs into or out of polling when an IRQ-affinitized CPU goes offline or online.

### Removal and Reset Flow

SLI4 remove marks the vport unloading, unregisters congestion buffers, removes sysfs and NPIV vports, removes FC/SCSI hosts, runs node and NVMe/NVMeT cleanup, frees I/O and IOCB resources, calls `lpfc_sli4_hba_unset()`, unsets driver resources, unmaps BARs, releases PCI resources, and frees the HBA. `lpfc_sli4_hba_unset()` itself stops timers, blocks async mailboxes, waits for or force-completes an active mailbox, aborts IOCBs, waits for XRI exchange-busy lists to drain when PCI is still online, removes CPU-hotplug state, disables interrupts/SR-IOV, stops the worker thread, stops RAS logging, unsets and destroys queues, resets the function, frees RAS DMA, and clears port work events.

PCI AER paths split by generation. For SLI4 frozen errors, `HBA_PCI_ERR` prevents duplicate reset preparation, management and SCSI I/O are blocked/flushed, queues and interrupts are destroyed/disabled, and PCI is disabled. Slot reset re-enables the PCI device, restores and re-saves config state, clears `LPFC_SLI_ACTIVE`, reinitializes CPU mapping, reenables interrupts, recomputes affinity, and returns recovered. Actual SLI restart is deferred to `lpfc_io_resume_s4()` because the function reset mailbox needs DMA enabled.

## State and Persistence Behavior

- The persistent driver object is `struct lpfc_hba`; this chunk mutates fields across PCI lifecycle: `sli_rev`, `pci_dev_grp`, BAR addresses, register pointers, `intr_type`, `intr_mode`, `cfg_irq_chann`, queue-resource counts, SLI4 capability descriptors, link/topology settings, congestion settings, NVMe support, and feature flags.
- SLI4 READ_CONFIG values persist in `phba->sli4_hba.max_cfg_param`, `lnk_info`, `bbscn_params`, `fawwpn_flag`, `conf_trunk`, `extents_in_use`, and queue-related config. These values drive later queue allocation and XRI/IOCB reservations.
- Persistent topology support sets `HBA_PERSISTENT_TOPO` and can override `cfg_topology` from firmware state. Invalid or unsupported persistent topology falls back to module parameters.
- Forced link speed from READ_CONFIG sets `HBA_FORCED_LINK_SPEED` and rewrites `cfg_link_speed`.
- Congestion management initializes a coherent `lpfc_cgn_info` buffer, atomics, timestamps, frequency defaults, and CRC. Registration is firmware-visible through `REG_CONGESTION_BUF`; unregister stops CMF first.
- Queue state spans firmware queue IDs, host descriptors, child lists, `lpfc_wq_list`, `cq_lookup`, CPU maps, per-HDWQ stats, and the queue-free flags used to coordinate teardown.
- Interrupt state persists in `phba->intr_type`, `phba->intr_mode`, `phba->sli.slistat.sli_intr`, `sli4_hba.hba_eq_hdl[]`, and affinity masks. CPU-hotplug registration is per-HBA and must be removed before full teardown.
- The firmware update path persists firmware to the adapter by streaming `.grp` file contents through DMA buffers to `lpfc_wr_object()`. It skips update when image revision matches current firmware.
- Module-level state includes the PCI driver registration, FC transport templates, misc device `lpfcmgmt`, dynamic CPU-hotplug state ID, `lpfc_pldv_detect`, `lpfc_present_cpu`, and `lpfc_hba_index`.
- The debug ring buffer state uses atomics `dbg_log_idx`, `dbg_log_cnt`, and `dbg_log_dmping`; `lpfc_dmp_dbg()` drains it to dev_info and resets the count.

## Dependencies and Integration Points

- Linux PCI core: `pci_register_driver`, `pci_alloc_irq_vectors`, `pci_irq_vector`, `pci_irq_get_affinity`, `pci_enable_device_mem`, `pci_restore_state`, `pci_save_state`, `pci_disable_device`, `pci_disable_sriov`, AER callbacks, PCI BAR resource APIs, and config-space reads/writes.
- Linux interrupt and CPU-hotplug APIs: `request_irq`, `request_threaded_irq`, `free_irq`, affinity masks, `irq_set_affinity`, `cpuhp_setup_state_multi`, per-HBA cpuhp instances, RCU synchronization, and timers.
- Linux DMA/I/O mapping APIs: `dma_set_mask_and_coherent`, `dma_set_max_seg_size`, `dma_alloc_coherent`, `dma_free_coherent`, `ioremap`, `iounmap`, `readl`, `writel`, and ordered PCI config reads for flushes.
- SCSI and FC transport layers: `Scsi_Host`, `scsi_host_set_prot`, `scsi_host_set_guard`, `fc_attach_transport`, `fc_release_transport`, `fc_remove_host`, `scsi_remove_host`, `fc_host_post_vendor_event`, NPIV vport termination, and host/vport sysfs/debugfs integration.
- LPFC internal subsystems: SLI mailbox commands (`lpfc_sli_issue_mbox`, `lpfc_sli_issue_mbox_wait`, `lpfc_sli4_config`), queue create/destroy functions, ring/IO abort/flush paths, worker thread `lpfc_do_work`, memory pools, debugfs, NVMe/NVMeT transport hooks, RAS firmware logging, CMF/FPIN congestion management, and vport/static-vport helpers.
- Linux firmware loader: `request_firmware_nowait`, `request_firmware`, `release_firmware`; image validation depends on LPFC group-header format and ASIC generation magic constants.
- Kernel module integration: `module_init`, `module_exit`, `MODULE_DEVICE_TABLE`, `MODULE_LICENSE`, `MODULE_DESCRIPTION`, `MODULE_AUTHOR`, and `MODULE_VERSION`.

## Risks and Edge Cases

- Initialization/unwind ordering is critical. Many routines assume partially initialized fields are either valid or NULL; mismatched cleanup can double-free queues, unmap uninitialized BARs, or leave interrupts active against freed state.
- SLI4 queue teardown waits indefinitely while `LPFC_QUEUE_FREE_WAIT` remains set. Bugs in queue users can hang remove/reset/suspend paths.
- `lpfc_sli4_xri_exchange_busy_wait()` waits forever after the initial timeout, logging periodically. This prevents unsafe reset/unload while exchange-busy lists are non-empty, but it can make device removal hang if completions never arrive.
- `lpfc_pci_function_reset()` treats port-not-ready and RN-after-reset as fatal and logs a board-mode firmware reset hint. Register-read failures or stale status on if-type 2/6 abort the bring-up path.
- `lpfc_sli4_read_config()` computes `qmin -= 4` after using firmware max WQ/CQ counts; extremely small queue-count responses would underflow as an unsigned value unless firmware guarantees enough slow-path resources.
- CPU affinity mapping depends on present/possible CPU masks, PCI managed affinity, NUMA masks, and hyperthread detection. Hotplug code must not race with unload; `FC_UNLOADING` and cpuhp removal/synchronize_rcu are used to reduce this risk.
- In SLI4 MSI-X setup, partial vector allocation failure must unwind only already requested IRQs and clear affinity flags. Any stale `eqhdl->irq` or handler state risks freeing the wrong IRQ later.
- Firmware update validates magic values by adapter generation and logs detailed failures, but the async `request_firmware_nowait()` callback carries `phba` as context. The broader driver must ensure the HBA is not freed while an internal firmware update callback may still run.
- Congestion-buffer CRC and endian fields must match firmware expectations. Any structure layout/version drift affects CMF/FPIN behavior.
- Suspend/resume paths restart worker threads and interrupts but are intentionally minimal; failures after worker-thread creation can leave partially resumed state unless higher-level PM recovery handles it.
- SLI3 and SLI4 dispatch wrappers depend on `phba->pci_dev_grp`. Corruption or incomplete probe setup routes removal/PM/AER to the wrong generation path.

## Test Signals

- Successful SLI4 probe should log PCI memory setup, interrupt mode, CPU affinity assignments (`3333`/`3335`/`3336` style messages), queue setup messages for EQ/CQ/WQ/MQ/RQ, SCSI scan (`0428`), adapter-arrival vendor event, and optional NVMe localport registration.
- SLI3 probe should show accepted interrupt mode only after active interrupt testing; fallback messages indicate MSI-X/MSI problems but can be valid if INTx succeeds.
- READ_CONFIG and GET_SLI4_PARAMETERS logs should show sane resource counts, topology selection, congestion registration choices, firmware NVMe support, embedded I/O settings, and no mailbox status/add-status failures.
- Queue failure testing should verify `lpfc_sli4_queue_create()` and `lpfc_sli4_queue_setup()` unwind through `queue_destroy`/`queue_unset` without leaked DMA memory, leaked IRQs, or stale `cq_lookup`.
- Removal tests should confirm sysfs/debugfs removal, vport termination, FC/SCSI host removal, NVMe/NVMeT teardown, congestion unregister, interrupt disable, queue destroy, BAR unmap, PCI disable, and HBA free complete without use-after-free warnings.
- PCI AER tests should exercise normal, frozen, permanent, and unknown states for both SLI3 and SLI4 and verify returned `pci_ers_result_t` values, `HBA_PCI_ERR` gating, slot-reset reinitialization, and `io_resume` online behavior.
- CPU-hotplug tests should verify EQ polling starts when the last CPU for an IRQ vector is going offline, stops when its mapped CPU returns online, and affinity is restored for NUMA/non-hyperthread modes.
- Firmware-update tests should cover matching revision skip, unsupported magic/generation, administrative lockout, DMA allocation failure, object-write failure, and async callback completion.
- Congestion/RAS tests should validate buffer CRC updates, register/unregister mailbox success/failure handling, CMF stop on unregister, and RAS enablement only for supported generations/functions.

## Unresolved Cross-Chunk References

- The actual implementations of `lpfc_sli4_hba_setup()`, `lpfc_sli4_driver_resource_setup()`, mailbox builders, queue create/destroy helpers, NVMe/NVMeT transport handlers, and most constants/bitfield macros are outside this chunk. This chunk shows how they are sequenced and how their results are persisted, but full semantics require the earlier declarations and helper definitions in neighboring files/chunks.
- The beginning of `lpfc_init.c` defines device IDs, module parameters, global state, and common resource setup/cleanup used heavily here.
