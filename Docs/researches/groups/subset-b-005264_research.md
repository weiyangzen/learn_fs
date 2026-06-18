# subset-b-005264 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_v3_hw.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_v3_hw.c

## Purpose

`hisi_sas_v3_hw.c` is the PCI hardware backend for HiSilicon SAS controller v3, exposed as the `hisi_sas_v3_hw` driver for Huawei/HiSilicon device `0xa230`. It supplies the v3 register map, queue programming, PHY control, interrupt handling, command-header construction, debugfs instrumentation, PCI reset, and power-management logic used by the common `hisi_sas` core and by libsas/SCSI. The file does not implement the whole driver alone: it binds a `struct hisi_sas_hw` callback table and a `struct scsi_host_template` to shared code in the rest of `drivers/scsi/hisi_sas/`.

## Important APIs, Types, and Functions

The local hardware-facing data types are `struct hisi_sas_complete_v3_hdr`, `struct hisi_sas_err_record_v3`, `struct hisi_sas_protect_iu_v3_hw`, `struct hisi_sas_debugfs_reg_lu`, and `struct hisi_sas_debugfs_reg`. They sit on top of shared structures from `hisi_sas.h`, especially `struct hisi_hba`, `struct hisi_sas_slot`, `struct hisi_sas_device`, `struct hisi_sas_phy`, `struct hisi_sas_cq`, `struct hisi_sas_dq`, `struct hisi_sas_hw`, and the generic DMA descriptors `struct hisi_sas_cmd_hdr`, `struct hisi_sas_itct`, `struct hisi_sas_iost`, SGE pages, and status buffers.

The key callback tables are `sht_v3_hw` and `hisi_sas_v3_hw`. `sht_v3_hw` connects the controller to the SCSI midlayer with libsas defaults, `sdev_configure_v3_hw()`, `hisi_sas_scan_start()`, `hisi_sas_scan_finished()`, `hisi_sas_map_queues()`, `hisi_sas_sdev_init()`, host and sdev sysfs groups, `hisi_sas_host_reset()`, host-wide blk-mq tags, and `queue_complete_v3_hw()` for poll queues. `hisi_sas_v3_hw` is the hardware operations table consumed by common `hisi_sas` code: ITCT setup/clear, wide-port bitmap lookup, SSP/SMP/STP/abort command preparation, delivery start, PHY init/start/disable/reset/link-rate callbacks, device deregistration, soft reset, event readout, SGPIO write, command-drain wait, and debugfs snapshot collection.

Initialization and lifecycle functions are `hisi_sas_v3_probe()`, `hisi_sas_shost_alloc_pci()`, `interrupt_preinit_v3_hw()`, `hisi_sas_v3_init()`, `hw_init_v3_hw()`, `reset_hw_v3_hw()`, `init_reg_v3_hw()`, `interrupt_init_v3_hw()`, `hisi_sas_v3_remove()`, `hisi_sas_v3_destroy_irqs()`, `hisi_sas_reset_prepare_v3_hw()`, `hisi_sas_reset_done_v3_hw()`, `suspend_v3_hw()`, and `resume_v3_hw()`. Register access is centralized through `hisi_sas_read32()`, `hisi_sas_write32()`, `hisi_sas_phy_read32()`, `hisi_sas_phy_write32()`, and the polling macros wrapping `readl_poll_timeout()`.

Command and completion functions are `setup_itct_v3_hw()`, `clear_itct_v3_hw()`, `dereg_device_v3_hw()`, `start_delivery_v3_hw()`, `prep_ssp_v3_hw()`, `prep_smp_v3_hw()`, `prep_ata_v3_hw()`, `prep_abort_v3_hw()`, `prep_prd_sge_v3_hw()`, `prep_prd_sge_dif_v3_hw()`, `fill_prot_v3_hw()`, `complete_v3_hw()`, `slot_complete_v3_hw()`, `slot_err_v3_hw()`, `is_ncq_err_v3_hw()`, `queue_complete_v3_hw()`, `cq_interrupt_v3_hw()`, and `cq_thread_v3_hw()`.

PHY and interrupt logic is organized around `phy_up_v3_hw()`, `phy_down_v3_hw()`, `phy_bcast_v3_hw()`, `int_phy_up_down_bcast_v3_hw()`, `handle_chl_int0_v3_hw()`, `handle_chl_int1_v3_hw()`, `handle_chl_int2_v3_hw()`, `int_chnl_int_v3_hw()`, `fatal_axi_int_v3_hw()`, `fatal_ecc_int_v3_hw()`, and `multi_bit_ecc_error_process_v3_hw()`. User-visible tuning/debug entry points include sysfs attributes `intr_conv_v3_hw`, `intr_coal_ticks_v3_hw`, `intr_coal_count_v3_hw`, `iopoll_q_cnt_v3_hw`, plus debugfs dump, BIST, PHY-down-count, and trace-FIFO files.

## Control Flow

Probe starts by enabling the PCI device with managed PCI helpers, setting bus mastering, mapping BAR 5, and requiring a 64-bit coherent DMA mask. `hisi_sas_shost_alloc_pci()` allocates a SCSI host with private `struct hisi_hba`, attaches the hardware table, stores PCI/device pointers, wires `SHOST_TO_SAS_HA()`, applies the optional `prot_mask`, reads firmware-provided topology/queue data through `hisi_sas_get_fw_info()`, validates `n_phy` and `queue_count`, applies the optional poll-queue count, and allocates common DMA memory via `hisi_sas_alloc()`.

`hisi_sas_v3_probe()` then initializes the libsas `sas_ha_struct` arrays, populates SCSI host limits (`max_id`, `max_lun`, CDB length, queue depth, `nr_maps`), optionally enables DIF/DIX protection, allocates MSI vectors with affinity in `interrupt_preinit_v3_hw()`, calls `scsi_add_host()`, registers the SAS HA, initializes hardware and interrupts, scans the host, optionally creates debugfs, configures runtime PM autosuspend, ignores child count for suspend decisions, and drops the runtime PM usage count.

Hardware initialization resets the device first. `reset_hw_v3_hw()` disables delivery queues, stops PHYs, waits for AXI idle, and invokes ACPI `_RST`; missing ACPI reset support is a hard failure. `init_reg_v3_hw()` programs global queue enable, tag limits, retry/aging/timer/coalescing settings, interrupt masks, QoS/cache attributes, queue base/depth registers for every delivery and completion queue, ITCT/IOST/breakpoint/initial-FIS DMA addresses, RAS masks, and SGPIO/LED defaults. It also initializes every PHY with link-rate masks, OOB/link timers, channel interrupt state, PHY masks, STP timers, 12G tuning for older revisions, and saved FFE defaults for BIST.

Normal I/O is prepared by protocol-specific callbacks. `prep_ssp_v3_hw()` builds SSP or TMF command headers, sets direction, command frame length, response buffer size, device id, transfer tag, command table and status buffer DMA addresses, CDB/LUN/task attribute fields, optional T10 PI protection IU, and data plus protection SGEs. `prep_smp_v3_hw()` points the command table directly at the SMP request DMA buffer and sizes the SMP response. `prep_ata_v3_hw()` emits direct SATA or STP command headers, handles forced PHY for directly attached SATA, sets ATA protocol and reset/unconstrained bits, injects the NCQ tag into the FIS, builds data SGEs, and copies the host-to-device FIS. `prep_abort_v3_hw()` emits abort commands keyed by abort type, device type, device id, and target tag.

The common core adds prepared slots to a delivery list. `start_delivery_v3_hw()` walks the DQ list until the last contiguous ready slot, uses a read memory barrier so descriptor writes from other CPUs are visible, and advances the hardware DQ write pointer. Completions are interrupt-driven or polled. The hard IRQ `cq_interrupt_v3_hw()` acknowledges the OQ source bit and wakes `cq_thread_v3_hw()`, which drains the completion queue with `complete_v3_hw()`. Poll mode calls `queue_complete_v3_hw()` under `cq->poll_lock`. Completion draining reads the hardware CQ write pointer, processes each CQE from `cq->rd_point`, decodes IPTT/device id/status words, handles SATA disk/NCQ error special cases, dispatches ordinary completions to `slot_complete_v3_hw()`, advances the local and hardware read pointers, and returns the number of CQEs processed.

`slot_complete_v3_hw()` clears the libsas pending bit, initializes a `task_status_struct`, decodes abort/TMF status from the completion header, handles hardware-error completions through `slot_err_v3_hw()`, copies SSP/SMP/SATA responses, marks tasks done unless already aborted, frees the slot through `hisi_sas_slot_task_free()`, respects frozen HA state for non-internal non-SMP tasks, and invokes `task_done()`. Error classification maps underflow, queue full, open reject, SATA FIS status, NCQ error, IO-in-target, and PHY-down cases into libsas task status, sometimes setting `slot->abort` and calling `sas_task_abort()` or `sas_ata_device_link_abort()`.

PHY interrupts split into link/broadcast and channel-error vectors. `phy_up_v3_hw()` acknowledges PHY enable, reads port id and link rate, distinguishes SATA from SAS using `PHY_CONTEXT`, builds attached addresses and frame-received data, records target protocol/device type, marks `phy_attached`, pairs runtime PM references with a PHY-up PM work item, and completes any reset waiter. `phy_down_v3_hw()` increments `down_cnt`, masks not-ready, notifies common code with current ready state, clears SL/CTA and TXID state, and unmasks. Broadcast-change handling checks `RX_PRIMS_STATUS` and calls `hisi_sas_phy_bcast()`. Channel interrupt 1 logs DMA/AXI/FIFO/ECC-style per-PHY fatal errors and queues reset work. Channel interrupt 2 accounts SAS error counters, handles identify and STP link timeouts, and has revision-specific invalid-DW handling.

Fatal global interrupts mask the relevant sources, log AXI/FIFO/poison/LM/abort errors, queue reset work, request AXI master shutdown on older revisions, process ECC multi-bit errors with address reporting, and complete ITCT clear operations. Soft reset disables interrupts, disables the host, reinitializes common memory, and reruns hardware init. PCI FLR prepare blocks until SCSI recovery is idle, takes `hisi_hba->sem`, sets reset state, calls common reset-prepare logic, disables interrupts, and disables the host. FLR done reinitializes memory and hardware, then calls common reset-done logic to thaw the controller.

Suspend sets PM/reset state, blocks SCSI requests, rejects new commands, flushes reset/event work, disables interrupts, validates runtime PM state, disables the host, reinitializes memory, releases tasks, and calls `sas_suspend_ha()`. Resume unblocks requests early, clears reject state, prepares libsas resume, reinitializes hardware, starts PHYs, resumes the HA without synchronous drain to avoid deadlock if a directly attached disk disappeared during suspend, and clears reset/PM bits.

## State and Persistence Behavior

Persistent runtime state is in `struct hisi_hba`, allocated as SCSI host private data. It owns MMIO base, PCI/device pointers, SAS address, firmware-provided PHY/queue counts, `struct Scsi_Host`, libsas HA, PHY/port arrays, DQ/CQ arrays, device table, coherent DMA memory for command headers, completion headers, ITCT, IOST, initial SATA FISes, SAS/SATA breakpoints, slot metadata, queue-vector counts, flags, reset work, interrupt coalescing settings, iopoll queue count, and debugfs/BIST/FIFO snapshots.

Device-specific hardware state is mirrored in ITCT entries written by `setup_itct_v3_hw()` and cleared by `clear_itct_v3_hw()`. Slot state is indexed by IPTT/slot id and uses DMA-backed command, status, data-SGE, and protection-SGE buffers. Queue state is split between host-side `wr_point`/`rd_point` fields and hardware read/write pointer registers. PHY state includes link attachment, type, port id, frame-received data, reset completion, timers, counters, and trace FIFO configuration.

State is not persisted across reboot or unload. Module parameters (`intr_conv`, `prot_mask`, `experimental_iopoll_q_cnt`) are read at module load/probe time. Sysfs changes to interrupt coalescing are stored in `hisi_hba->intr_coal_ticks` and `intr_coal_count` and immediately reprogram hardware after stopping and restarting PHYs, but they are not durable. Debugfs dump memory is allocated lazily per triggered dump and remains readable until driver teardown; BIST settings, PHY-down counters, and FIFO configuration live only in RAM/hardware registers.

Concurrency and lifetime are guarded by a mixture of SCSI/libsas locks, `hisi_hba->sem`, `task_state_lock`, per-device slot locks, `cq->poll_lock`, timers, workqueues, and runtime PM references. Reset and PM paths use `HISI_SAS_RESETTING_BIT`, `HISI_SAS_REJECT_CMD_BIT`, and `HISI_SAS_PM_BIT` to reject or block new work while draining in-flight commands and synchronizing interrupts.

## Dependencies and Integration Points

This file depends on PCI managed resource APIs, ACPI reset/DSM methods, DMA masks and coherent allocations performed by common code, MSI/MSI affinity, Linux IRQ/threaded IRQ APIs, runtime PM, debugfs, sysfs attributes, blk-mq queue maps and poll hooks, SCSI host templates, libsas HA registration, libata/SATA helpers, T10 PI/SCSI protection helpers, and common `hisi_sas` core routines declared in `hisi_sas.h`.

External kernel integration points include `scsi_host_alloc()`, `scsi_add_host()`, `scsi_scan_host()`, `sas_register_ha()`, `sas_unregister_ha()`, `sas_remove_host()`, `scsi_block_requests()`, `scsi_unblock_requests()`, `blk_mq_map_hw_queues()`, `blk_mq_map_queues()`, `sas_ssp_task_response()`, `hisi_sas_sata_done()`, `sas_ata_device_link_abort()`, `sas_task_abort()`, `sas_suspend_ha()`, and `sas_resume_ha_no_sync()`. User-facing integration is through the PCI driver, SCSI host sysfs attributes, SAS/ATA transport attributes, runtime PM behavior, and the optional debugfs hierarchy under the common hisi_sas debugfs root.

## Risks and Edge Cases

Probe requires 64-bit coherent DMA and ACPI reset support; systems without either fail rather than falling back. Firmware data is trusted after range checks only for `n_phy <= 8` and `queue_count <= 16`, so queue/vector assumptions should stay aligned with hardware limits and `HISI_SAS_MAX_QUEUES`. MSI vector allocation requests all 32 vectors to avoid reinsertion issues, and queue mapping assumes at least one interrupt CQ after subtracting base vectors and poll queues.

Reset and PM paths are high risk because they stop PHYs, disable delivery queues, reinitialize host memory, and release tasks while SCSI, libsas, IRQ threads, and runtime PM may all be active. Error paths that call `scsi_remove_host()` during resume failure or queue reset work from IRQ context must be checked for races with remove, debugfs dumps, and libsas event work. `debugfs_snapshot_prepare_v3_hw()` blocks SCSI requests, waits for command-count quiescence by sampling `CQE_SEND_CNT`, sets reject state, synchronizes CQs, and disables delivery; if command completion keeps moving or a reset races the dump, the snapshot may fail or perturb I/O latency.

Debugfs BIST and FIFO controls directly manipulate PHY registers and can disable PHYs, loopback traffic, change FFE, disable ALOS, and read trace data. They are root/debugfs-only surfaces but can disrupt live links if used incorrectly. Interrupt coalescing sysfs stores stop all PHYs while reprogramming coalescing registers, so it is not a trivial passive tuning knob.

Completion handling trusts IPTT values below `HISI_SAS_COMMAND_ENTRIES_V3_HW` and maps them into `slot_info`; invalid or stale CQEs are discarded only if the tag is out of range. SATA/NCQ error paths may call link abort before normal slot completion, and `slot_complete_v3_hw()` returns early when it triggers abort, leaving final cleanup to the abort path. Underflow and response-IU logic depends on precise hardware status bits and status-buffer layout.

Several paths have hardware revision branches (`pdev->revision < 0x30`, `> 0x20`, `== 0x20`, `< 0x21`) that need regression coverage on affected chips. The use of ACPI `_DSM` for MSI error handling is advisory when absent, while `_RST` is mandatory in reset. Device links added in `sdev_configure_v3_hw()` disable runtime PM if they fail while PM is enabled, changing power behavior for the whole host.

## Test Signals

Build coverage should include this file with `CONFIG_SCSI_HISI_SAS_PCI`, `CONFIG_PM`, debugfs, libsas, libata, blk-mq, and T10 PI paths enabled. Probe tests should verify BAR 5 mapping, 64-bit DMA mask, firmware-derived `n_phy` and `queue_count` validation, MSI vector counts, CQ affinity masks, SCSI host registration, SAS HA registration, `scsi_scan_host()`, runtime PM autosuspend, and cleanup on every failure label.

Functional tests should cover SSP reads/writes with and without protection information, SMP expander management, direct SATA and STP-through-expander devices, NCQ success/error cases, ATA device reset, TMF abort/query/reset behavior, internal aborts, wide-port discovery, hotplug PHY up/down, broadcast change events, queue polling via `mq_poll`, and queue mapping when `experimental_iopoll_q_cnt` is nonzero.

Fault-injection signals include fatal AXI/FIFO interrupts, multi-bit ECC interrupts for DQE/IOST/ITCT/CQE/NCQ/OOO RAM, channel interrupt 1 errors, identify timeout, STP link timeout, invalid dword/code/disparity counters, invalid IPTT CQEs, SATA disk error CQEs, ITCT clear timeout, AXI idle timeout in reset/disable, and ACPI `_RST` failure. Reset coverage should include `hisi_sas_host_reset()`, controller reset work, PCI FLR prepare/done, suspend/resume, runtime suspend with active usage count, and device removal during suspend.

User-interface tests should verify sysfs attributes report and validate `intr_conv`, `intr_coal_ticks`, `intr_coal_count`, and `iopoll_q_cnt`; `intr_coal_*` reject out-of-range values and reprogram hardware; debugfs dump generation creates `global`, `port`, `cq`, `dq`, `iost`, `itct`, cache, `axi`, and `ras` files; BIST controls reject writes while enabled and restore PHY state; FIFO configuration validation rejects invalid modes; and `phy_down_cnt` can be read and reset to zero only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_v3_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hosts.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/hosts.c

## Purpose

`hosts.c` is SCSI midlayer infrastructure for allocating, publishing, looking up, reference-counting, removing, and iterating `struct Scsi_Host` instances. It is the common bridge between low-level SCSI drivers and the driver core, transport classes, procfs/sysfs exposure, runtime PM, blk-mq tag sets, error handling, and host workqueues. Low-level drivers such as the HiSilicon SAS v3 PCI backend ultimately flow through this file when they call `scsi_host_alloc()`, `scsi_add_host()` or `scsi_add_host_with_dma()`, `scsi_scan_host()`, `scsi_remove_host()` or `sas_remove_host()`, and `scsi_host_put()`.

## Important APIs, Types, and Functions

The exported host lifecycle API is `scsi_host_alloc()`, `scsi_add_host_with_dma()`, `scsi_remove_host()`, `scsi_host_lookup()`, `scsi_host_get()`, `scsi_host_put()`, `scsi_host_busy()`, `scsi_queue_work()`, `scsi_flush_work()`, `scsi_host_complete_all_commands()`, and `scsi_host_busy_iter()`. Module/core lifecycle functions are `scsi_init_hosts()` and `scsi_exit_hosts()`, and `scsi_is_host_device()` identifies generic SCSI host devices.

The host state model is enforced by `scsi_host_set_state()`, which accepts transitions among `SHOST_CREATED`, `SHOST_RUNNING`, `SHOST_RECOVERY`, `SHOST_CANCEL`, `SHOST_DEL`, `SHOST_CANCEL_RECOVERY`, and `SHOST_DEL_RECOVERY`. Internal release and lookup helpers are `scsi_host_cls_release()`, `scsi_host_dev_release()`, `__scsi_host_match()`, `scsi_host_check_in_flight()`, `complete_all_cmds_iter()`, and `__scsi_host_busy_iter_fn()`.

Global state includes the `eh_deadline` module parameter stored in `shost_eh_deadline`, the `host_index_ida` allocator used for host numbers, and `shost_class`, the device class named `scsi_host` with `scsi_shost_groups` attributes. The file relies on `struct scsi_host_template` to seed `struct Scsi_Host` limits and callbacks.

## Control Flow

`scsi_host_alloc()` allocates one `struct Scsi_Host` plus driver private bytes, initializes locks, lists, waitqueues, the scan mutex, host state, default transport template, SCSI limits, DMA/segment constraints, active mode, host-blocked behavior, and blk/SCSI template-derived fields. It allocates a stable host number with `ida_alloc()`, sets up `shost_gendev` on `scsi_bus_type` with `scsi_host_type`, initializes the class device `shost_dev` under `shost_gendev`, starts the per-host error-handler kthread `scsi_eh_%d`, creates a TMF workqueue, and creates the per-template proc host directory. Failure while still in `SHOST_CREATED` drops the generic device reference so `scsi_host_dev_release()` handles partial cleanup.

`scsi_add_host_with_dma()` publishes an allocated host. It validates that `can_queue` is nonzero and that reserved commands have a `queue_reserved_command` method, clamps `cmd_per_lun` to `can_queue`, initializes the sense cache, chooses the generic parent and DMA device, caps `max_sectors` using the DMA device's maximum mapping size, sets up blk-mq tags through `scsi_mq_setup_tags()`, initializes the tag-set refcount and completion, enables runtime PM on `shost_gendev`, adds the generic device, transitions the host to `SHOST_RUNNING`, takes a parent reference, adds the class device, allocates transport-private `shost_data`, optionally allocates a transport workqueue, adds sysfs host attributes, creates a pseudo sdev for reserved commands, adds proc host entries, and runtime-idles the host.

If publish fails after `device_add()`, the function unwinds in reverse: delete `shost_dev`, release its reference when needed, delete `shost_gendev`, disable async suspend and runtime PM, mark runtime suspended, drop the temporary PM reference, and drop the tag-set refcount with `scsi_mq_free_tags()`. Any allocations owned by the host are left for `scsi_host_dev_release()`.

`scsi_remove_host()` cancels an already published host. It serializes with scanning through `scan_mutex`, attempts to transition to `SHOST_CANCEL` or `SHOST_CANCEL_RECOVERY` under `host_lock`, gets a runtime PM reference, flushes the TMF workqueue, calls `scsi_forget_host()` to remove devices, drops proc entries, releases the tag-set reference and waits for `tagset_freed` so command private destructors can still use the host pointer, transitions to `SHOST_DEL` or `SHOST_DEL_RECOVERY`, unregisters the transport device, unregisters the class device, and deletes the generic device.

`scsi_host_dev_release()` is the final memory release path for `shost_gendev`. It waits for pending RCU command callbacks, destroys the TMF workqueue, stops the error-handler kthread, destroys the optional transport workqueue, handles the special never-added `SHOST_CREATED` cleanup for proc hostdir and `shost_dev` name, frees transport-private data, releases the host number to the IDA, drops the parent device reference for published hosts, and frees the `Scsi_Host`.

Lookup and reference handling use the class device. `scsi_host_lookup()` finds the `scsi_host` class device by host number, converts it to `Scsi_Host`, attempts `scsi_host_get()`, and then drops the class lookup reference. `scsi_host_get()` refuses hosts already in `SHOST_DEL` and otherwise references `shost_gendev`; `scsi_host_put()` drops that reference.

Busy/iteration helpers are blk-mq tag-set walks. `scsi_host_busy()` counts requests whose `struct scsi_cmnd` has `SCMD_STATE_INFLIGHT`. `scsi_host_complete_all_commands()` iterates all busy tags, unmaps DMA, clears the result, sets a caller-supplied host byte, and calls `scsi_done()`; the caller must stop concurrent submission/completion. `scsi_host_busy_iter()` adapts a caller callback over `struct scsi_cmnd` to `blk_mq_tagset_busy_iter()`. `scsi_queue_work()` and `scsi_flush_work()` operate on a transport-created host workqueue and warn with stack dumps if the transport did not request one.

## State and Persistence Behavior

The durable runtime object is `struct Scsi_Host`. Its state persists only while device references exist. Host numbering is process-wide kernel state managed by `host_index_ida`; host numbers are freed only in `scsi_host_dev_release()`. `shost_state` is the gate for legal host lifecycle transitions and for refusing late references after deletion starts.

Resource ownership is split between driver-private memory appended to the host allocation, the generic device `shost_gendev`, the class device `shost_dev`, blk-mq tag-set resources, runtime PM state, workqueues, the error-handler kthread, transport-private `shost_data`, proc/sysfs/transport registrations, pseudo sdev state, and parent device references. The release path intentionally centralizes most cleanup in the generic device release callback so partial allocation and failed add paths can be handled consistently.

The only module parameter in this file is `eh_deadline`. It is copied into each host at allocation time, converted from seconds to jiffies if the low-level template has `eh_host_reset_handler`, clamped to `INT_MAX`, and disabled with `-1` otherwise. Changing the module parameter affects later allocations, not already allocated hosts.

## Dependencies and Integration Points

`hosts.c` depends on the Linux driver core (`struct device`, classes, device types, `device_add()`, `device_del()`, `device_unregister()`), runtime PM, async suspend, IDA allocation, kthreads, workqueues, completions, RCU, blk-mq tag iteration, SCSI sysfs/proc/transport helpers, and the SCSI error handler. It includes `scsi_priv.h` and `scsi_logging.h` for internal midlayer operations and logging.

Low-level drivers integrate by filling `struct scsi_host_template`, calling `scsi_host_alloc()` with private size, setting host limits or transport pointers, publishing through `scsi_add_host()`/`scsi_add_host_with_dma()`, scanning, removing the host, and releasing their reference with `scsi_host_put()`. Transport classes integrate through `transportt->host_size`, `transportt->create_work_queue`, and `transport_unregister_device()`. blk-mq integration is through `scsi_mq_setup_tags()`, `scsi_mq_free_tags()`, `tagset_refcnt`, and `tagset_freed`.

User-visible integration is indirect: successful host add creates `/sys/class/scsi_host/hostN`, a generic `hostN` device under the SCSI bus, transport/sysfs attributes, proc host entries when configured, runtime PM state, and SCSI error-handler threads/workqueues named per host.

## Risks and Edge Cases

Lifecycle ordering is the main risk. `scsi_remove_host()` must prevent new devices by changing host state before forgetting existing devices, and it must wait for the tag-set refcount to drop before freeing tags because low-level `.exit_cmd_priv` callbacks may need the host pointer. Illegal state transitions only log and return `-EINVAL`; callers that ignore failures can leave a host in a surprising state, although remove handles recovery-state alternatives.

`scsi_host_complete_all_commands()` is deliberately unsafe against concurrent queue changes; callers must quiesce submission/completion before using it or risk double completion or stale request access. `scsi_host_busy_iter()` similarly delegates locking requirements to its caller. Busy counting only checks `SCMD_STATE_INFLIGHT`, so it is a snapshot rather than a full synchronization primitive.

Runtime PM setup in `scsi_add_host_with_dma()` temporarily increments usage and then calls `scsi_autopm_put_host()` after proc/sysfs setup. Error unwinds must preserve runtime PM balance. Parent references are only dropped in release when the host left `SHOST_CREATED`, so incorrect state changes could affect parent lifetime.

The `eh_deadline` parameter is global and copied at allocation time; extremely large values are clamped, and hosts without a host-reset handler get deadline disabled. Drivers setting `nr_reserved_cmds` without `queue_reserved_command` are rejected at add time. Drivers with `can_queue == 0` are rejected because zero queue depth is no longer supported.

Workqueue helpers assume `transportt->create_work_queue` was set before add. Calling `scsi_queue_work()` or `scsi_flush_work()` on a host without `work_q` returns/logs errors and dumps the stack, which is useful diagnostically but noisy if callers do not check transport capabilities.

## Test Signals

Lifecycle tests should cover successful `scsi_host_alloc()` plus `scsi_add_host_with_dma()`, allocation failures before and after host-number assignment, error-handler kthread creation failure, TMF workqueue failure, `scsi_add_host_with_dma()` failures at sense cache, tag setup, generic device add, class device add, transport-private allocation, workqueue allocation, sysfs add, and pseudo-sdev allocation, verifying release of IDA numbers, PM references, tag sets, device names, proc hostdirs, and parent references.

State-machine tests should verify every legal transition accepted by `scsi_host_set_state()` and representative illegal transitions logged and rejected. Remove tests should cover hosts in `SHOST_RUNNING` and `SHOST_RECOVERY`, active scans guarded by `scan_mutex`, runtime PM reference handling, TMF workqueue flush, device forgetting, tag-set refcount wait, transport unregister, class unregister, and final generic device release.

Integration tests should validate `/sys/class/scsi_host/hostN` creation/removal, proc host entry lifecycle, transport-private `shost_data` allocation, transport-created workqueue use through `scsi_queue_work()` and `scsi_flush_work()`, lookup/reference behavior with `scsi_host_lookup()` during and after removal, and `scsi_is_host_device()` for generic host devices.

Command-iteration tests should exercise `scsi_host_busy()` with in-flight and completed commands, `scsi_host_busy_iter()` callback ordering/early-stop behavior, and `scsi_host_complete_all_commands()` only under quiesced queues, checking DMA unmap, host-byte result, and `scsi_done()` completion. Parameter tests should allocate hosts with `eh_deadline = -1`, valid positive values, overflow-sized values, and templates with and without `eh_host_reset_handler`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hosts.c -->
