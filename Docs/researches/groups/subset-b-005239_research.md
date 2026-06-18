# Research: subset-b-005239

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_main.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_main.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_main.h

## Purpose

`be_main.h` is the central private header for the `be2iscsi` Linux kernel driver. It defines driver identity, supported PCI IDs, resource limits, hardware register offsets, doorbell bit fields, memory descriptor indices, main HBA/session/connection/task structures, firmware-facing WRB/SGL/CQE/PDU layouts, async default-PDU bookkeeping, and prototypes shared with peer implementation files. It is the type contract that lets `be_main.c`, `be_mgmt.c`, `be_iscsi.c`, and command helpers share the same view of HBA state and hardware descriptors.

## Important APIs, Types, And Constants

Driver identity constants include `DRV_NAME`, `BUILD_STR`, `BE_NAME`, `DRV_DESC`, vendor IDs, and device IDs for BE2, BE3, OneConnect, and Skyhawk-R adapters. Capacity constants define queue and protocol limits such as `BE2_IO_DEPTH`, `BE2_MAX_SESSIONS`, `BE2_SGE`, default PDU sizes, max CPUs, SCSI host limits, sense-buffer sizing, minimum memory fragment size, and maximum command size.

Hardware-facing macros define PCI config offsets, host interrupt mask, CEV ISR register offsets, TX/RX doorbell offsets, EQ/CQ doorbell masks and shifts, default-PDU queue access, page-count calculations, and ULP/CID helpers. State macros define online/error bits and `beiscsi_hba_is_online`.

Important structures include:

- `struct beiscsi_hba`: the main adapter state, including resource parameters, hardware controller pointer, DMA memory descriptors, mapped BAR addresses, PCI device, IRQ/MSI-X names, SGL handle pools, endpoint/connection tables, firmware configuration, state bits, timers/work items, control/MCC state, generation, interface handle, AIC state, selected I/O writer, and boot-session state.
- `struct hwi_controller`, `struct hwi_context_memory`, `struct hwi_wrb_context`, and `struct wrb_handle`: WRB queue and context structures mapping firmware CIDs/CRIs to WRB rings and handles.
- `struct sgl_handle`, `struct iscsi_sge`, `struct mem_array`, and `struct be_mem_descriptor`: DMA memory and SGL bookkeeping used for I/O, management, and firmware-posted SGL pages.
- `struct beiscsi_conn`, `struct beiscsi_session`, and `struct beiscsi_io_task`: libiscsi private state for sessions, connections, and tasks.
- `struct hd_async_context`, `struct hd_async_entry`, `struct hd_async_buf_context`, and `struct hd_async_handle`: default-PDU header/data buffer state used to gather unsolicited or firmware-unprocessed iSCSI PDUs.
- Hardware-layout structures and pseudo-AMAP structures for PDU headers, SCSI/data-out BHS, NOP, SGL entries, offload params, solicited CQEs, default-PDU CQEs, EQ entries, CQ doorbells, WRBs, and target-context-update WRBs.

The header declares shared functions such as `alloc_wrb_handle`, `free_mgmt_sgl_handle`, `beiscsi_free_mgmt_task_handles`, `hwi_ring_cq_db`, `beiscsi_process_cq`, `beiscsi_process_mcc_cq`, and `beiscsi_start_boot_work`.

## Control Flow Role

This header does not execute control flow directly, but it shapes the driver lifecycle. Probe fills `struct beiscsi_hba`, creates `struct hwi_controller`, populates `struct hwi_context_memory`, builds memory descriptors indexed by `enum be_mem_enum`, and initializes WRB/SGL/default-PDU contexts described here. I/O submission allocates `struct beiscsi_io_task`, `struct wrb_handle`, and `struct sgl_handle`, fills `struct iscsi_wrb` using AMAP pseudo-layouts, and links completions back through `wrb_handle->pio_handle`. CQ processing decodes `struct sol_cqe` and default-PDU CQEs using the masks and pseudo-AMAP definitions. Recovery and cleanup use state bits and pointer ownership encoded in `struct beiscsi_hba`.

## State And Persistence Behavior

All structures in this header represent volatile kernel driver state or firmware DMA descriptors. `struct beiscsi_hba` is the root object attached to the SCSI host and PCI device. Its `fw_config` substructure is a cached view of firmware-provided resource assignments, including ULP support, CID/ICD ranges, chain ranges, physical port, features, and queue counts. Its `boot_struct` caches firmware boot session data until boot sysfs objects are created. Persistent configuration is not stored by the header itself; fields such as initiator name, IP configuration, gateway, VLAN, flash contents, and boot target are accessed through firmware commands defined elsewhere.

Pool state is tracked with circular indices and availability counters for IO SGLs, management SGLs, ULP CID arrays, and WRB handles. Error state is represented as bit positions in `phba->state`, with `BEISCSI_HBA_IN_ERR` grouping PCI, firmware timeout, UE, and TPE errors. Async PDU state includes per-CRI wait queues for in-progress header/data gather operations and CID-to-async-CRI mapping.

## Dependencies And Integration Points

The header includes Linux kernel, PCI, Ethernet/IP, module, SCSI, libiscsi, and scsi_transport_iscsi headers, then includes local `be.h` after defining ULP and HBA-related types. It depends on firmware command definitions from `be_cmds.h` indirectly through embedded command headers and response structures used by peer files. The AMAP pseudo-structures integrate with local AMAP bit helpers used throughout the driver.

External integration is with PCI device IDs, SCSI host configuration, libiscsi task/session/connection objects, hardware BAR doorbells, DMA memory, firmware queue descriptors, and iSCSI boot sysfs. The data layouts must match firmware ABI expectations; even small field-width or endianness changes can break hardware communication.

## Risks And Edge Cases

The biggest risk is ABI drift. Many pseudo-AMAP structures encode bit positions by field width rather than ordinary C layout semantics, so changes must be synchronized with the `AMAP_SET_BITS`/`AMAP_GET_BITS` users and firmware documentation. Several comments warn that variable-size arrays must remain last, that command-per-LUN must align with invalidation table size, and that async PDU buffers have hardware-required posting multiples.

`BE_MAX_SESSION` limits CID map arrays to 2048; any firmware generation exposing larger CID values would require coordinated changes. ULP support is represented as bits and indexed arrays of size two, so multi-ULP assumptions are hardcoded. `struct beiscsi_hba` is broad and shared across many contexts; modifications can introduce locking, lifetime, or initialization-order regressions.

## Test Signals

Header changes should be validated by full kernel compilation with `CONFIG_SCSI_BE2ISCSI`, sparse/endian warnings, structure size and field-offset review for firmware-facing descriptors, and runtime smoke tests covering BE2/BE3 and Skyhawk paths if hardware is available. Test focus should include CID/CRI mapping, WRB allocation, SGL page posting, async PDU gather, error-state gating, and boot sysfs object creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_mgmt.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_mgmt.c

## Purpose

`be_mgmt.c` implements management-plane firmware commands for the `be2iscsi` driver. It builds embedded and non-embedded MCC/mailbox requests for vendor BSG flash operations, TCP connect-and-offload, EQ delay tuning, initiator-name lookup, network interface IP/gateway/DHCP/VLAN configuration, NIC configuration lookup, firmware boot-session discovery/logout/reopen, connection invalidation/upload, ICD invalidation for SCSI error handling, and generation-specific iSCSI target-context-update WRB construction.

## Important APIs And Functions

Externally used functions include `mgmt_vendor_specific_fw_cmd`, `mgmt_open_connection`, `beiscsi_modify_eq_delay`, `beiscsi_get_initiator_name`, `beiscsi_if_get_handle`, `beiscsi_if_set_gw`, `beiscsi_if_get_gw`, `beiscsi_if_en_static`, `beiscsi_if_en_dhcp`, `beiscsi_if_set_vlan`, `beiscsi_if_get_info`, `mgmt_get_nic_conf`, boot helpers (`beiscsi_boot_logout_sess`, `beiscsi_boot_reopen_sess`, `beiscsi_boot_get_sinfo`, `__beiscsi_boot_get_shandle`, `beiscsi_boot_get_shandle`), sysfs display helpers, `beiscsi_offload_cxn_v0`, `beiscsi_offload_cxn_v2`, `beiscsi_invalidate_cxn`, `beiscsi_upload_cxn`, and `beiscsi_mgmt_invalidate_icds`.

Shared internal helpers provide the common non-embedded command pattern:

- `beiscsi_prep_nemb_cmd` allocates coherent DMA memory, sets size, and prepares the firmware header.
- `beiscsi_exec_nemb_cmd` allocates an MCC WRB under `mbox_lock`, attaches the non-embedded SGE, optionally records an async callback and DMA buffer ownership in the MCC tag state, notifies firmware, and waits for completion for synchronous commands.
- `beiscsi_free_nemb_cmd` frees the DMA command buffer unless ownership was deferred because the firmware/MCC path is busy.
- `__beiscsi_eq_delay_compl` handles async EQ delay completion and frees stored DMA memory.

Network functions manipulate the firmware iSCSI interface by retrieving the interface handle, clearing existing static IPs, releasing DHCP state, setting static IP/subnet, enabling DHCP, deleting/adding default gateways, setting VLAN through `be_cmd_set_vlan`, and fetching interface/NIC configuration. Boot functions operate as an async state machine coordinated with `be_main.c` boot work.

## Control Flow

Management command flow usually allocates a DMA command buffer, populates request fields, posts an MCC WRB, waits for or registers a completion, copies response data when needed, and frees the DMA buffer. `mgmt_open_connection` is invoked by endpoint connect logic: it validates address family, resolves the ULP/default header/data queues for the endpoint CID, builds `OPCODE_COMMON_ISCSI_TCP_CONNECT_AND_OFFLOAD`, assigns a completion queue in round-robin order, records endpoint destination address/port/type, sets template PDU address and queue IDs, and posts the command. For non-BE2/BE3 adapters it uses command version 1 and TCP window parameters.

Interface configuration flows are deliberately ordered. `beiscsi_if_en_static` gets current interface info, releases DHCP if active, clears any existing IP, then sets the provided static IP unless the call only wanted DHCP release. `beiscsi_if_en_dhcp` gets current interface info, returns if DHCP is already active, clears static IP, deletes gateway configuration, then posts a blocking DHCP configuration request. `beiscsi_if_set_gw` reads existing gateway, deletes it if nonzero, then adds the new gateway.

Boot-session flow is split between synchronous probe-time detection and async work. `beiscsi_boot_get_shandle` synchronously asks firmware whether boot targets exist and returns a valid session handle only when firmware logged in. Async boot work then calls `__beiscsi_boot_get_shandle`, possibly reopens boot sessions, fetches session info through a non-embedded command, logs out the firmware session, and asks `be_main.c` to create boot sysfs objects. `beiscsi_boot_process_compl` validates the expected tag/action, decodes the command-specific response, updates the boot action, handles retries, frees non-embedded session-info DMA memory, and reschedules boot work when progress should continue.

Connection cleanup commands split invalidation and TCP upload. `beiscsi_invalidate_cxn` posts an iSCSI driver invalidate request with cleanup type depending on whether the endpoint still has a live connection. `beiscsi_upload_cxn` posts common TCP upload with graceful or abort upload type. `beiscsi_mgmt_invalidate_icds` is used by SCSI EH to invalidate one or more firmware commands by CID/ICD table, then waits for MCC completion and frees the non-embedded buffer.

## State And Persistence Behavior

The file primarily mutates firmware state through mailbox commands. Driver-local state touched here includes `phba->interface_handle`, endpoint destination fields (`dst_addr`, `dst6_addr`, `dst_tcpport`, `ip_type`), `phba->nxt_cqid`, MCC tag state and waitqueues, async tag DMA ownership, and `phba->boot_struct`. Persistent or semi-persistent firmware state includes flash contents, initiator name, network interface configuration, default gateway, VLAN, boot target/session metadata, and active offloaded TCP/iSCSI sessions.

Non-embedded command buffers have careful ownership semantics: synchronous commands free after completion, async EQ-delay and boot session info defer or explicitly free through callbacks, and `-EBUSY` indicates the MCC completion path owns the buffer. Boot state is protected by tag/action checks rather than a separate lock; the work item and MCC callbacks communicate through `boot_struct.tag`, `boot_struct.action`, and the `BEISCSI_HBA_BOOT_WORK` bit.

## Dependencies And Integration Points

The file depends on Linux BSG, SCSI iSCSI transport headers, and local `be_mgmt.h`, `be_iscsi.h`, and `be_main.h`. It relies heavily on command helpers from `be_cmds`/`be_cmds.h` such as `alloc_mcc_wrb`, `free_mcc_wrb`, `be_wrb_hdr_prepare`, `be_cmd_hdr_prepare`, `embedded_payload`, `nonembedded_sgl`, `be_mcc_notify`, `beiscsi_mccq_compl_wait`, `__beiscsi_mcc_compl_status`, and `be_cmd_set_vlan`.

User-visible integrations are SCSI BSG vendor commands, sysfs attributes for driver/firmware/session counts/adapter family/physical port, and iSCSI boot sysfs data consumed by userspace iSCSI tooling. Hardware/firmware integration is through MCC WRBs and command opcodes in common, iSCSI, and iSCSI initiator subsystems.

## Risks And Edge Cases

Because this is the firmware management plane, return-code semantics and DMA buffer ownership are critical. Several functions return `0` both as a failure-to-post tag and as a valid nonpositive status pattern, so callers must distinguish tag-returning functions from `int` status functions. `mgmt_vendor_specific_fw_cmd` returns `-EPERM` through an unsigned return type on unsupported commands, which can be surprising to callers expecting tag-or-zero behavior.

Network configuration is stateful and multi-step; failures after clearing an IP or gateway can leave firmware configuration partially changed. `beiscsi_if_get_info` resizes its response buffer on `-EAGAIN`, which depends on firmware filling `actual_resp_len` correctly. Boot work relies on a single outstanding boot tag and retries; unexpected callbacks, tag mismatch, or missing boot-work bit are logged and ignored. CHAP names and secrets can be exposed through boot sysfs callbacks if firmware supplies them.

Generation-specific offload WRB construction must match the hardware layouts in `be_main.h`. The v0 path also writes a pad-buffer address from global-header memory; memory descriptor layout changes can break it. ICD invalidation accepts up to `BE_INVLDT_CMD_TBL_SZ` entries and waits synchronously; SCSI EH latency can be affected by firmware/MCC stalls.

## Test Signals

Validation should include firmware mailbox success and failure paths, BSG flash read/write command handling, IPv4 and IPv6 TCP connect-and-offload, static IP to DHCP and DHCP to static transitions, gateway replacement, VLAN set failures, interface-info insufficient-buffer retry, initiator-name retrieval, boot target discovery with and without configured boot sessions, boot-session reopen/get-info/logout retry behavior, connection invalidate/upload on live and half-torn-down endpoints, and ICD invalidation during SCSI abort/device reset. Runtime signals include `BG_` and `BS_` logs, MCC timeout/busy statuses, leaked coherent DMA buffers, stuck boot work bits, and incorrect interface handle caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_mgmt.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_mgmt.h

## Purpose

`be_mgmt.h` declares the `be2iscsi` management-plane ABI between driver files and firmware command helpers. It defines management constants, firmware command payload structures for ICD invalidation, controller/HBA attributes, BSG vendor flash commands, endpoint state, and prototypes for connection management, network interface management, boot-session commands, sysfs display helpers, offload WRB population, and firmware session cleanup.

## Important APIs, Types, And Constants

Constants include IP add/delete actions, IPv4/IPv6 byte lengths, UE status/mask PCI config offsets, `BE_INVLDT_CMD_TBL_SZ`, and BSG flash operation IDs. `GET_MGMT_CONTROLLER_WS` and `ISCSI_GET_PDU_TEMPLATE_ADDRESS` are helper macros used by management/open-connection paths.

Important structures include:

- `struct invldt_cmd_tbl`, `struct invldt_cmds_params_in`, `struct invldt_cmds_params_out`, and `union be_invldt_cmds_params`: packed firmware payloads for invalidating outstanding iSCSI commands by ICD and CID.
- `struct mgmt_hba_attributes`, `struct mgmt_controller_attributes`, `struct be_mgmt_controller_attributes`, and response variants: packed controller/HBA inventory and firmware version data structures.
- `struct be_bsg_vendor_cmd`: BSG vendor flash command request header with region, offset, and sector fields.
- `struct beiscsi_endpoint`: driver endpoint state tying an open-iscsi endpoint to HBA, connection pointer, destination IPv4/IPv6 address, TCP port, endpoint CID, firmware session handle, and validity flags.

The header declares management entry points for `mgmt_open_connection`, `mgmt_vendor_specific_fw_cmd`, `beiscsi_mgmt_invalidate_icds`, initiator-name retrieval, DHCP/static IP/gateway/NIC/VLAN/interface-info operations, boot session helpers, sysfs display functions implemented in `be_mgmt.c`, connection offload WRB population, connection invalidation/upload, EQ delay modification, and firmware-session logout.

## Control Flow Role

The header is consumed by `be_main.c`, `be_mgmt.c`, and related transport files. Endpoint connect paths allocate/populate `struct beiscsi_endpoint` and call `mgmt_open_connection`. SCSI error handlers build `struct invldt_cmd_tbl` arrays and call `beiscsi_mgmt_invalidate_icds`. Interface parameter callbacks use the declared network configuration functions. Probe and boot work use boot helper prototypes. Completion and recovery paths use connection invalidation/upload prototypes to coordinate firmware state with libiscsi endpoint teardown.

## State And Persistence Behavior

`struct beiscsi_endpoint` is the main stateful type in this header. It persists for the lifetime of a driver/open-iscsi endpoint and records both host-side pointers and firmware-side identifiers. The packed command structures are transient DMA or embedded mailbox payloads. Management operations can update persistent firmware state such as flash contents, configured initiator name, network IP/gateway/VLAN configuration, and boot session data, but the header itself only defines the data shapes and function contracts.

## Dependencies And Integration Points

The header includes `scsi/scsi_bsg_iscsi.h`, `be_iscsi.h`, and `be_main.h`, so it is tightly coupled to SCSI BSG, libiscsi transport types, the main HBA definition, and local firmware command structures. Packed structures must match firmware command ABI. Prototypes bridge user-facing transport callbacks, BSG handling, boot sysfs, and low-level MCC command submission.

## Risks And Edge Cases

The header contains packed firmware structures with fixed-size strings and reserved fields; layout changes are risky. `BE_INVLDT_CMD_TBL_SZ` must remain aligned with SCSI command-per-LUN behavior in `be_main.h`. `struct beiscsi_endpoint` mixes IPv4 `unsigned long` storage with IPv6 byte arrays and firmware/session identifiers, so users must respect `ip_type` and validity fields. Several prototypes return unsigned tags where zero means failure; callers need careful error handling.

## Test Signals

Any changes should trigger build coverage for all be2iscsi files, packed layout review, sparse/endian checks, and runtime management tests for endpoint connect/disconnect, ICD invalidation, interface configuration, boot session discovery, and BSG vendor command handling. ABI-sensitive changes should be verified against firmware command documentation or existing command helper expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/Makefile

## Purpose

This Makefile integrates the Brocade/BFA Fibre Channel SCSI driver into the kernel build. It defines the composite `bfa.o` object that is built when `CONFIG_SCSI_BFA_FC` is enabled and lists the constituent object files that implement the BFA driver stack.

## Important Build Targets

`obj-$(CONFIG_SCSI_BFA_FC) := bfa.o` tells kbuild to include the `bfa` driver object according to the `SCSI_BFA_FC` Kconfig setting. The `bfa-y` lists aggregate these objects into `bfa.o`: driver front-end files (`bfad.o`, `bfad_im.o`, `bfad_attr.o`, `bfad_debugfs.o`, `bfad_bsg.o`), IOC and hardware support (`bfa_ioc.o`, `bfa_ioc_cb.o`, `bfa_ioc_ct.o`, `bfa_hw_cb.o`, `bfa_hw_ct.o`), Fibre Channel services (`bfa_fcs.o`, `bfa_fcs_lport.o`, `bfa_fcs_rport.o`, `bfa_fcs_fcpim.o`, `bfa_fcbuild.o`), and lower-level port/FCP/core/service modules (`bfa_port.o`, `bfa_fcpim.o`, `bfa_core.o`, `bfa_svc.o`).

## Control Flow

There is no runtime control flow in this file. At build time, kbuild evaluates `CONFIG_SCSI_BFA_FC`, compiles the listed source files to objects, and links them into a single `bfa.o` module/built-in object according to the broader kernel configuration.

## State And Persistence Behavior

The file does not maintain runtime state or persistent data. Its build-state effect is deterministic: enabling the config includes all listed objects in the BFA driver; disabling it omits the composite object.

## Dependencies And Integration Points

The Makefile depends on Linux kbuild syntax and the existence of all listed `.c` files in the same directory. It integrates with the SCSI subsystem through the corresponding Kconfig option and with any module/built-in rules inherited from the surrounding kernel tree.

## Risks And Edge Cases

Missing or renamed object files will break the build. Adding a source file without updating `bfa-y` can silently omit code from the driver. Reordering generally should not matter for normal kernel object aggregation, but unresolved symbol dependencies or initcall/linker-section behavior should still be considered when making nontrivial build changes.

## Test Signals

The primary test is a kernel build with `CONFIG_SCSI_BFA_FC=y` and/or `m`, plus a disabled-config build to ensure the object is omitted. Build logs should show all listed BFA objects compiled and linked into `bfa.o` without missing-object or unresolved-symbol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/Makefile -->
