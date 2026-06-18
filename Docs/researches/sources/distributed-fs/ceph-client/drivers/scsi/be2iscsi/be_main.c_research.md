# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_main.c

## Purpose

`be_main.c` is the main Linux kernel driver module for the Broadcom/Emulex `be2iscsi` enterprise iSCSI HBA. It registers an `iscsi_transport`, a PCI driver, and a SCSI host template, then owns adapter probe/remove, PCI BAR mapping, DMA memory layout, hardware queue creation, interrupt handling, libiscsi task submission/completion, boot-target sysfs export, error detection, and port recovery. It is not Ceph-specific; it is part of the kernel SCSI initiator stack used by storage clients when hardware iSCSI offload devices are present.

## Important APIs, Types, And Functions

The file exports and wires these major integration surfaces:

- `beiscsi_iscsi_transport`: the open-iscsi transport callback table. It connects libiscsi operations to driver methods such as `beiscsi_alloc_pdu`, `beiscsi_task_xmit`, `beiscsi_cleanup_task`, `beiscsi_parse_pdu`, endpoint callbacks from `be_iscsi.c`, interface parameter callbacks, stats, and `beiscsi_bsg_request`.
- `beiscsi_pci_driver`: PCI probe/remove and EEH/AER error-handler registration for supported BE2, BE3-R, and Skyhawk-R device IDs.
- `beiscsi_sht`: SCSI host template using libiscsi queueing and SCSI EH hooks, with driver-specific abort and device-reset handlers that invalidate firmware ICDs before delegating back to libiscsi.
- `alloc_wrb_handle`, `free_mgmt_sgl_handle`, `beiscsi_free_mgmt_task_handles`, `hwi_ring_cq_db`, and `beiscsi_process_mcc_cq`: non-static helper functions used by peer be2iscsi files.

Key lifecycle functions are `beiscsi_dev_probe`, `beiscsi_remove`, `beiscsi_enable_port`, `beiscsi_disable_port`, `beiscsi_recover_port`, and the EEH handlers. Hardware initialization is split across `be_ctrl_init`, `beiscsi_get_params`, `beiscsi_get_memory`, `hwi_init_controller`, `hwi_init_port`, `beiscsi_init_port`, `beiscsi_init_irqs`, and `hwi_enable_intr`. Queue and memory helpers include `beiscsi_find_mem_req`, `beiscsi_alloc_mem`, `beiscsi_init_wrb_handle`, `hwi_init_async_pdu_ctx`, `beiscsi_create_eqs`, `beiscsi_create_cqs`, default PDU queue creation, SGL page posting, template-header posting, and WRB ring creation.

The I/O path centers on `beiscsi_alloc_pdu`, `beiscsi_task_xmit`, `beiscsi_iotask` for BE2/BE3, `beiscsi_iotask_v2` for Skyhawk, `beiscsi_mtask` for non-SCSI iSCSI PDUs, `hwi_write_sgl`/`hwi_write_sgl_v2`, and `hwi_write_buffer`. Completion handling is driven by `be_isr`, `be_isr_msix`, `be_isr_mcc`, `be_iopoll`, `beiscsi_process_cq`, `hwi_complete_cmd`, and helpers that synthesize libiscsi completions for SCSI, logout, TMF, and NOP responses. Async/default-PDU handling is implemented by `beiscsi_hdl_get_handle`, `beiscsi_hdl_gather_pdu`, `beiscsi_hdl_fwd_pdu`, `beiscsi_complete_pdu`, and `beiscsi_hdq_post_handles`.

Boot and management-adjacent surfaces include `beiscsi_bsg_request`, `beiscsi_start_boot_work`, `beiscsi_boot_work`, boot-kset show/visibility callbacks, `beiscsi_eqd_update_work`, `beiscsi_hw_health_check`, and `beiscsi_hw_tpe_check`.

## Control Flow

Module initialization first registers the iSCSI transport and then the PCI driver. Probe enables the PCI device, allocates a SCSI host plus `struct beiscsi_hba`, selects generation-specific behavior and `iotask_fn`, maps BARs, allocates an aligned mailbox DMA buffer, initializes SLI/firmware configuration, computes device resource parameters, enables MSI-X if possible, allocates DMA memory pools, creates hardware queues, initializes SGL and CID tables, allocates the workqueue, registers IRQs, adds the SCSI host, sets the HBA online bit, starts optional boot-target discovery, creates default iSCSI interfaces, and arms EQ-delay plus hardware-health work.

I/O submission starts when libiscsi calls `alloc_pdu`; the driver allocates a DMA BHS buffer, an SGL handle, and a WRB handle. The task ITT encoded into the outgoing PDU combines WRB index and SGL/ICD index, while the original libiscsi ITT is stored in the per-task private data. For SCSI commands, `beiscsi_task_xmit` DMA maps the SCSI scatterlist and dispatches to the generation-specific iotask writer. Those writers populate hardware WRBs with BHS DMA address, LUN, CmdSN, ICD/SGL index, transfer length, inline first SGEs, SGL page entries, WRB type, WRB chaining metadata, and then ring the WRB doorbell. For login, text, NOP, TMF, and logout, `beiscsi_mtask` builds a management/direct-message WRB and maps task data with `dma_map_single` when present.

Completion flow begins in interrupt context. Legacy INTx reads the CEV ISR, consumes EQ entries, counts MCC versus I/O events, schedules `irq_poll` for I/O, and queues MCC work. MSI-X uses one vector per I/O EQ and a separate MCC vector. `be_iopoll` drains EQ entries, rings the EQ doorbell, processes CQEs up to budget, and rearms when done. `beiscsi_process_cq` decodes generation-specific CQE fields, resolves CID to CRI and endpoint, then dispatches solicited completions, firmware driver-message notifications, async/default-PDU notifications, digest errors, invalidation events, and connection-killed events. Solicited completions recover the original task from the WRB handle, translate firmware status into SCSI/libiscsi completion state, unmap DMA, copy sense data on check condition, and call libiscsi completion helpers. Default-PDU completions gather header/data handles until a complete PDU is available and then pass it to `__iscsi_complete_pdu`.

Error handling is layered. SCSI abort/device reset marks outstanding WRBs invalid, builds invalidation tables with CID/ICD pairs, calls `beiscsi_mgmt_invalidate_icds`, then delegates SCSI EH to libiscsi. Hardware-health polling checks for unrecoverable error or transient parity error. UE detection fails sessions and can switch the timer to TPE detection before recovery. Recovery disables the port, tears down IRQs and queues, then reinitializes the port resources. PCI EEH/AER paths set the PCI error bit, stop timers/work, fail sessions, disable the port, perform reset readiness checks, and resume by enabling the port.

Removal stops health and recovery work, destroys default iSCSI interfaces, removes the SCSI host, disables the port, destroys boot sysfs state, destroys the workqueue, frees DMA memory, unmaps BARs, frees mailbox memory, releases the PCI device reference and regions, and disables the PCI function.

## State And Persistence Behavior

The durable driver state is in `struct beiscsi_hba`, allocated as SCSI host private data. It tracks PCI mappings, firmware config, generation, resource parameters, online/error bits, CID-to-CRI maps, endpoint and connection tables, WRB/SGL pools, per-ULP default-PDU contexts, work/timer state, MCC tag state, and boot-session metadata. This state is volatile kernel memory; persistent settings such as firmware boot target, initiator name, flash access, IP/gateway/VLAN configuration, and boot session handles are obtained or modified via firmware mailbox commands implemented in `be_mgmt.c` and command helpers.

The code uses bit flags in `phba->state` for online, link-up, boot state, UER support, PCI error, firmware timeout, UE, and TPE. `beiscsi_hba_is_online` gates transmit and management paths. WRB handles and SGL handles are circular pools protected by spinlocks. MCC commands use mailbox locking, per-tag waitqueues, tag state bits, and optional async callbacks. Interrupt delay state is periodically recomputed from CQ counts in `beiscsi_eqd_update_work`.

Boot-target discovery is asynchronous once a boot session handle exists. The driver may reopen firmware boot sessions, fetch session info into `boot_struct.boot_sess`, logout the firmware session, then create an `iscsi_boot_kset` exposing target, initiator, and Ethernet attributes. Boot sysfs kobjects hold SCSI host references until release.

## Dependencies And Integration Points

The file depends on Linux PCI, DMA, interrupt, workqueue, timer, bsg, irq_poll, SCSI core, libiscsi, scsi_transport_iscsi, and iscsi_boot_sysfs. Local dependencies include `be_main.h` for driver structures and hardware layouts, `be_mgmt.h` for management commands, `be_cmds.h` for firmware mailbox and queue commands, `be_iscsi.h` for transport endpoint/session helpers, and `be.h` for chip generation and register definitions.

Hardware integration is through PCI BAR ioremaps, EQ/CQ/MCC/WRB/default-PDU queues, DMA coherent memory, doorbell writes, and firmware mailbox commands. Kernel storage integration is through SCSI host registration and libiscsi task/session callbacks. User-space integration appears through sysfs driver attributes, iSCSI boot sysfs, and SCSI BSG vendor firmware commands.

## Risks And Edge Cases

This file is high risk because it mixes interrupt context, softirq polling, workqueues, DMA, hardware queue ownership, and libiscsi locks. Races are explicitly handled around task cleanup with `session->back_lock`, task refcounts, and WRB invalidation, but the abort path still depends on correct task lifetime and firmware invalidation semantics. CQ processing assumes CID-to-CRI and endpoint arrays remain coherent while teardown can make endpoints null. Async PDU assembly has several defensive checks for stale firmware addresses, duplicate in-use handles, headerless data, incomplete PDUs, and overflow.

Resource unwinding is complex. Queue creation, DMA allocation, IRQ registration, and probe failure labels need to remain synchronized with initialization order. One notable risk signal is in `beiscsi_init_irqs`: the MSI-X failure cleanup loop frees `pci_irq_vector(pcidev, i)` while iterating `j`, which looks suspicious because the vector index should probably be `j`. Doorbell and bitfield code is generation-specific, so changes to BE2/BE3 versus Skyhawk layouts are easy to regress. Endianness conversion is also delicate: the code writes AMAP fields, then converts WRBs/CQEs as required by hardware.

The driver stores firmware-facing CHAP secrets in boot sysfs show paths when firmware reports them. That is expected for iSCSI boot interfaces but should be treated as sensitive. BSG vendor commands expose flash read/write behavior through firmware; validation is mostly delegated to command handling and firmware. Hardware health recovery fails all sessions, so recovery correctness depends on upper-layer reconnect behavior.

## Test Signals

Useful validation signals include kernel build coverage for `CONFIG_SCSI_BE2ISCSI`, probe/remove testing on supported adapters, `modprobe`/`rmmod` leak and warning checks, PCI BAR and DMA allocation failure injection, MSI-X and INTx interrupt modes, libiscsi login/logout/text/NOP/TMF/SCSI I/O tests, SCSI error-handler abort and device reset tests, iSCSI boot target sysfs validation, BSG vendor command error paths, firmware UE/TPE recovery, PCI EEH/AER recovery, and stress tests with session churn while I/O and async PDUs are active. Runtime checks should watch dmesg for `BM_`/`BG_` logs, WARN_ONs in async handle paths, DMA mapping errors, CQE connection-killed codes, and stuck MCC tag waiters.
