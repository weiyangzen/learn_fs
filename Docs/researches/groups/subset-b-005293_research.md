# subset-b-005293 Research

Grouped source research for LPFC Fibre Channel driver files under `sources/distributed-fs/ceph-client/drivers/scsi/lpfc/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_logmsg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_logmsg.h

## Purpose
`lpfc_logmsg.h` defines the LPFC driver's log-category bitmask and the logging macros used by the rest of the driver to route verbose, severity-driven, and trace-triggered messages through the kernel device logger. It is a small but central observability contract: other modules choose masks such as `LOG_MBOX`, `LOG_DISCOVERY`, `LOG_NVME`, or `LOG_TRACE_EVENT`, and these macros decide whether a message is emitted, buffered in the debug trace path, or accompanied by a debug dump.

## Important APIs, Types, and Constants
- `LOG_ELS`, `LOG_DISCOVERY`, `LOG_MBOX`, `LOG_INIT`, `LOG_LINK_EVENT`, `LOG_NODE`, `LOG_SLI`, `LOG_FCP_ERROR`, `LOG_LIBDFC`, `LOG_VPORT`, `LOG_FIP`, `LOG_SCSI_CMD`, `LOG_NVME`, `LOG_NVME_DISC`, `LOG_NVME_ABTS`, `LOG_NVME_IOERR`, `LOG_CGN_MGMT`, `LOG_ENCRYPTION`, and `LOG_TRACE_EVENT` are independent category bits used by `cfg_log_verbose`.
- `LOG_ALL_MSG` is the all-normal-categories mask, deliberately excluding the top trace-event bit.
- `lpfc_dmp_dbg(struct lpfc_hba *phba)` is declared as the debug-log dump hook used when a `LOG_TRACE_EVENT` message is emitted without verbose logging enabled.
- `lpfc_dbg_print(struct lpfc_hba *phba, const char *fmt, ...)` is the fallback buffered/debug trace path for messages not printed to the kernel log.
- `lpfc_vlog_msg()` and `lpfc_log_msg()` are older/simple macros that print when the selected mask is enabled or the severity is warning-or-higher by checking `level[1] <= '5'`.
- `lpfc_printf_vlog()` and `lpfc_printf_log()` are the richer macros used throughout the driver. They print when the mask is enabled or severity is error-or-higher by checking `level[1] <= '3'`; otherwise, when verbose logging is disabled, they call `lpfc_dbg_print()`.

## Control Flow and State
The macros are pure call-site helpers but depend on runtime state from `struct lpfc_hba` and `struct lpfc_vport`. Vport logs use `vport->cfg_log_verbose`; HBA logs prefer `phba->pport->cfg_log_verbose` when a physical port exists and fall back to `phba->cfg_log_verbose` during early initialization. When the category bit is enabled, the macros call `dev_printk()` against `phba->pcidev->dev` and prefix messages with board number and, for vport logging, VPI. If `LOG_TRACE_EVENT` is set and the message is printed because of severity rather than explicit verbosity, the macros first call `lpfc_dmp_dbg()` to dump driver debug state.

## State and Persistence Behavior
No persistent state is stored in this header. Runtime persistence is through the driver's configurable verbose masks and any debug buffers maintained behind `lpfc_dbg_print()`. The macros read flags but do not mutate driver state except for the trace dump side effect.

## Dependencies and Integration Points
The header assumes `struct lpfc_hba`, `struct lpfc_vport`, `pcidev`, `brd_no`, `pport`, `cfg_log_verbose`, and `vpi` are visible from including files. It integrates with Linux `dev_printk()` severity strings such as `KERN_ERR` and with the driver's debug dump/print implementations. The masks are referenced by mailbox setup, discovery state transitions, memory allocation failures, SCSI/NVMe paths, link handling, congestion management, and encryption paths.

## Risks and Edge Cases
- The severity filter indexes `level[1]`, so callers must pass normal `KERN_*` strings; unusual strings would break the severity test.
- Macro arguments reference `phba`, `vport`, and format arguments multiple times conceptually; callers should avoid side-effect expressions.
- `lpfc_printf_log()` dereferences `phba->pcidev`; very early or late teardown call sites must ensure the PCI device pointer remains valid.
- `LOG_TRACE_EVENT` can trigger heavy debug dumping from severe paths, which is useful for failures but risky in log storms.
- Messages below the print threshold may still be captured through `lpfc_dbg_print()` only when verbose logging is disabled; this distinction matters when comparing kernel logs with debug traces.

## Test Signals
Useful signals include boot/probe logs with the expected board and VPI prefixes, dynamic changes to `cfg_log_verbose` enabling category-specific output, severe messages printing even when category masks are disabled, trace-event failures invoking the debug dump hook, and no crashes during early initialization where `phba->pport` is not yet established.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_logmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_mbox.c

## Purpose
`lpfc_mbox.c` builds and manages mailbox commands for the Emulex/Broadcom LPFC Fibre Channel driver. Mailboxes are the control-plane transport to adapter firmware for link bring-up, configuration, NVRAM/VPD reads, service-parameter registration, VPI/VFI/FCFI/RPI lifecycle, HBQ/ring setup, SLI-4 configuration subcommands, SFP/RDP diagnostics, and mailbox queue bookkeeping.

## Important APIs, Types, and Functions
- Resource helpers: `lpfc_mbox_rsrc_prep()` allocates a single DMA `lpfc_dmabuf` and attaches it to `mbox->ctx_buf`; `lpfc_mbox_rsrc_cleanup()` frees that DMA buffer and returns the mailbox object to `phba->mbox_mem_pool`.
- Basic mailbox builders include `lpfc_down_link()`, `lpfc_dump_mem()`, `lpfc_dump_wakeup_param()`, `lpfc_read_nv()`, `lpfc_config_async()`, `lpfc_heart_beat()`, `lpfc_read_topology()`, `lpfc_clear_la()`, `lpfc_config_link()`, `lpfc_init_link()`, `lpfc_read_sparam()`, `lpfc_read_config()`, `lpfc_read_lnk_stat()`, `lpfc_read_rev()`, and `lpfc_kill_board()`.
- Login and virtual-port builders include `lpfc_reg_rpi()`, `lpfc_unreg_login()`, `lpfc_unreg_did()`, `lpfc_sli4_unreg_all_rpis()`, `lpfc_reg_vpi()`, `lpfc_unreg_vpi()`, `lpfc_init_vfi()`, `lpfc_reg_vfi()`, `lpfc_init_vpi()`, and `lpfc_unreg_vfi()`.
- Port/ring setup uses `lpfc_config_pcb_setup()`, `lpfc_config_port()`, `lpfc_config_ring()`, `lpfc_config_hbq()`, and HBQ profile helpers for profiles 2, 3, and 5.
- Queue APIs `lpfc_mbox_put()`, `lpfc_mbox_get()`, `__lpfc_mbox_cmpl_put()`, and `lpfc_mbox_cmpl_put()` maintain the pending and completion lists.
- Validation/timeouts are centralized in `lpfc_mbox_cmd_check()`, `lpfc_mbox_dev_check()`, and `lpfc_mbox_tmo_val()`.
- SLI-4 helpers include `lpfc_sli4_config()`, `lpfc_sli4_mbox_cmd_free()`, `lpfc_sli4_mbx_sge_set()`, `lpfc_sli4_mbx_sge_get()`, `lpfc_sli4_mbox_rsrc_extent()`, `lpfc_sli_config_mbox_subsys_get()`, and `lpfc_sli_config_mbox_opcode_get()`.
- FCoE/RDP mailbox helpers include `lpfc_sli4_mbx_read_fcf_rec()`, `lpfc_reg_fcfi()`, `lpfc_reg_fcfi_mrq()`, `lpfc_unreg_fcfi()`, `lpfc_sli4_dump_cfg_rg23()`, `lpfc_sli4_dump_page_a0()`, the RDP chained completion handlers, and `lpfc_resume_rpi()`.

## Control Flow and State
Most functions are command formatters: they zero `LPFC_MBOXQ_t`, fill either the SLI-3 `MAILBOX_t` view or the SLI-4 `lpfc_mqe` view, set the firmware command, populate BDE/SGE addresses with `putPaddrLow()` and `putPaddrHigh()`, and set `OWN_HOST` where applicable. Callers then issue the command through `lpfc_sli_issue_mbox()`.

SLI generation drives many branches. SLI-3 port configuration builds a PCB in host/SLIM memory, configures IOCB rings, HBQs, HGP/PGP pointers, NPIV capability, and MSI-X mapping. SLI-4 uses MQE bitfield helpers and preallocated physical IDs from `phba->vpi_ids`, `sli4_hba.vfi_ids`, and `sli4_hba.rpi_ids`. Non-embedded SLI-4 config commands allocate page-sized coherent DMA pages, write a config subheader into the first page, and describe pages in mailbox SGEs.

Mailbox list state is kept in `phba->sli.mboxq`, `phba->sli.mboxq_cmpl`, `phba->sli.mboxq_cnt`, and `phba->sli.mbox_active`. Pending commands are FIFO. Completion commands are put on a completion list, often from interrupt context, for worker-thread processing outside the interrupt handler.

Some flows are multi-step. The RDP/SFP diagnostic path issues page A0 dump, copies the result, reuses the same mailbox and DMA buffer for page A2, then issues `READ_LNK_STAT`; the final completion frees resources and invokes `rdp_context->cmpl()`. `lpfc_sli4_unreg_all_rpis()` builds a special overloaded UNREG_LOGIN command to unregister all RPIs under a VPI. `lpfc_reg_vfi()` sets update bits only for FC link type and derives BB credit recovery fields from fabric service parameters and SLI-4 BBSCN limits.

## State and Persistence Behavior
The file does not persist data outside memory or firmware, but it is responsible for moving important in-memory state into firmware-visible command payloads. It reads and encodes link timers (`fc_edtov`, `fc_ratov`, `fc_arbtov`, `fc_altov`, `fc_crtov`), topology, port IDs, WWNs, FCF records, VPI/VFI/RPI/FCFI mappings, queue IDs, HBQ descriptors, and feature flags. DMA buffers attached through `ctx_buf` and SLI-4 `sge_array` must survive until firmware completion. Queue state persists until commands are completed, canceled, or freed during teardown.

## Dependencies and Integration Points
This file depends on Linux PCI/DMA facilities, SCSI and FC transport headers, driver hardware definitions (`lpfc_hw*.h`), SLI ring/queue definitions, discovery structures, logging, compatibility helpers, and mailbox command constants. It is called by initialization, link event handling, discovery state machine code, FCoE FCF selection, VPI/VFI management, RDP diagnostics, NVMe target setup, and SLI interrupt/completion paths. Its cleanup functions are used by `lpfc_mem.c` to free queued and active mailbox commands during driver teardown.

## Risks and Edge Cases
- Mailbox resource ownership is split across `ctx_buf`, `ctx_u`, mempool ownership, and optional SLI-4 `sge_array`; mismatched cleanup paths can leak coherent DMA memory or double-free mailbox objects.
- `lpfc_sli4_config()` may allocate fewer pages than requested and returns the allocated length; callers must compare it with their required length before using command payloads.
- Command timeout selection for SLI-4 config depends on correctly extracting subsystem/opcode from embedded or non-embedded headers.
- Some functions require caller-side locking discipline. `lpfc_mbox_rsrc_cleanup()` has a locked/unlocked mode, and the mailbox queue functions themselves do not take locks.
- SLI-3 PCB/HGP setup depends on BAR values and SLIM offsets; incorrect BAR handling can make firmware poll the wrong memory.
- RDP chained completions reuse the same mailbox object; any completion that fails to preserve or clear `ctx_buf` correctly can corrupt final cleanup.
- Registration commands require physical versus logical RPI/VPI interpretation to match SLI generation; passing the wrong ID can unregister or resume the wrong firmware object.

## Test Signals
Validation should exercise probe/link bring-up through `CONFIG_PORT`, `CONFIG_RING`, `CONFIG_HBQ`, `INIT_LINK`, `CONFIG_LINK`, `READ_SPARAM`, VPI/VFI registration, and FCFI registration. Fault injection should cover DMA allocation failures in `lpfc_mbox_rsrc_prep()` and non-embedded SLI-4 page allocation, mailbox issue returning `MBX_NOT_FINISHED`, PCI channel offline checks, HBA error-state rejection, RPI full failures, and RDP page A0/A2/link-stat failure paths. Runtime signals include mailbox queue counts returning to zero on teardown, no leaked coherent DMA pages, expected extended timeouts for flash/object/profile commands, and correct FCF/RQ routing under NVMe target MRQ modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_mem.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_mem.c

## Purpose
`lpfc_mem.c` owns the LPFC driver's memory-pool lifecycle and the allocation/free paths for control buffers, mailbox objects, node objects, receive buffers, NVMe target buffers, HBQ/RQ buffers, and teardown cleanup. It bridges Linux DMA pools/mempools with adapter-specific buffer formats used by SLI-3 HBQs and SLI-4 receive queues.

## Important APIs, Types, and Functions
- Pool sizing constants define safety and mempool depths: `LPFC_MBUF_POOL_SIZE`, `LPFC_MEM_POOL_SIZE`, `LPFC_DEVICE_DATA_POOL_SIZE`, `LPFC_RRQ_POOL_SIZE`, and `LPFC_MBX_POOL_SIZE`.
- `lpfc_mem_alloc()` creates the common `lpfc_mbuf_pool`, a preallocated DMA safety pool, mailbox and nodelist mempools, SLI-4 RRQ/header/data pools, SLI-3 HBQ pool, and optional ExpressLane device-data pool.
- `lpfc_mem_alloc_active_rrq_pool_s4()` creates a kmalloc-backed mempool sized to the SLI-4 maximum XRI bitmap.
- `lpfc_nvmet_mem_alloc()` creates the larger NVMe target data receive buffer pool.
- `lpfc_mem_free()` tears down pools created by `lpfc_mem_alloc()` and drains device-data list entries.
- `lpfc_mem_free_all()` additionally frees queued/completed/active mailbox commands, SCSI DMA pools, congestion information DMA memory, RX monitor ring, and IOCB lookup arrays.
- `lpfc_mbuf_alloc()`, `__lpfc_mbuf_free()`, and `lpfc_mbuf_free()` provide DMA buffer allocation with a priority fallback safety pool protected by `phba->hbalock`.
- `lpfc_nvmet_buf_alloc()` and `lpfc_nvmet_buf_free()` allocate/free generic NVMe target DMA buffers from `lpfc_sg_dma_buf_pool`.
- `lpfc_els_hbq_alloc()`/`lpfc_els_hbq_free()` handle SLI-3 HBQ buffers.
- `lpfc_sli4_rb_alloc()`/`lpfc_sli4_rb_free()` allocate paired SLI-4 header and data receive buffers.
- `lpfc_sli4_nvmet_alloc()`/`lpfc_sli4_nvmet_free()` allocate paired SLI-4 header plus larger NVMe target data buffers.
- `lpfc_in_buf_free()` returns unsolicited input buffers through the right SLI-3 HBQ or generic mbuf path.
- `lpfc_rq_buf_free()` reposts an SLI-4 RQ buffer pair to hardware queues or frees it through the RQB free callback if repost fails.

## Control Flow and State
Allocation is staged. `lpfc_mem_alloc()` starts with the common BPL-sized DMA pool and pre-fills `phba->lpfc_mbuf_safety_pool` with 64 coherent buffers. It then creates mailbox and node mempools. SLI-4 adapters receive RRQ, header receive, and data receive pools; older SLI adapters receive an HBQ pool. Optional ExpressLane support creates a device-data mempool. Every failure label unwinds only the pools already created and resets relevant pointers.

Teardown is two-layered. `lpfc_mem_free_all()` first drains live mailbox queues and the active mailbox, choosing `lpfc_sli4_mbox_cmd_free()` for SLI-4 config mailboxes and `lpfc_mbox_rsrc_cleanup()` for ordinary mailbox commands. It clears `LPFC_SLI_MBOX_ACTIVE` under `hbalock`, then delegates to `lpfc_mem_free()` for normal pools and finally destroys broader SCSI/control allocations. `lpfc_mem_free()` calls `lpfc_sli_hbqbuf_free_all()` before destroying receive pools and drains `phba->luns` before destroying the optional device-data pool.

Receive-buffer free paths are reuse-oriented. SLI-3 HBQ buffers are either returned to HBQ firmware accounting or freed through the configured HBQ free callback depending on the tag. SLI-4 RQ buffers are removed from the software list, converted into HRQE/DRQE physical addresses, reposted with `lpfc_sli4_rq_put()`, then re-linked and counted on success; failure logs details and calls the RQB free callback.

## State and Persistence Behavior
All state is in kernel memory and DMA-coherent buffers owned by `struct lpfc_hba`. Persistent fields include DMA pool pointers, mempool pointers, safety-pool element arrays/counts, active RRQ bitmap size, RQ/HBQ buffer lists, LUN device-data list, queued mailbox lists, active mailbox pointer, congestion info buffer, RX monitor pointer, and IOCB lookup table. No on-disk persistence occurs, but DMA buffers remain firmware-visible until returned, reposted, or freed.

## Dependencies and Integration Points
The file uses Linux `dma_pool_create/alloc/free/destroy`, coherent DMA APIs, mempool APIs, spinlocks, list primitives, and PCI device DMA context. Driver-local integration includes mailbox cleanup from `lpfc_mbox.c`, SLI/HBQ/RQ queue helpers, NVMe target support, SCSI buffer pools, congestion-management data, RX monitoring, and nodelist allocation. Discovery, ELS, unsolicited receive, NVMe target, and SCSI paths all rely on these pools being initialized before use.

## Risks and Edge Cases
- `lpfc_mem_alloc()` has a long unwind chain; any added pool must be inserted at the right failure label or teardown will leak or destroy uninitialized pointers.
- `lpfc_mbuf_alloc()` uses `GFP_KERNEL` and takes `hbalock` only around the safety pool, so callers must respect the documented no-lock/no-interrupt context for allocation.
- `__lpfc_mbuf_free()` must only be called with `hbalock` held; using it from unlocked contexts corrupts safety-pool counters.
- `lpfc_mem_free_sli_mbox()` must detect SLI-4 config mailboxes correctly; freeing a non-embedded SLI-4 config mailbox as a generic mailbox would leak SGE DMA pages.
- `lpfc_in_buf_free()` returns early if HBQs are no longer in use, leaving ownership with teardown assumptions; ordering around `hbq_in_use` matters.
- `lpfc_rq_buf_free()` assumes the `lpfc_dmabuf` is the header buffer embedded in `struct rqb_dmabuf`; passing a data buffer or generic mbuf would compute the wrong container.
- Destroying DMA pools while firmware still owns posted buffers would be unsafe; callers must stop queues and drain receive paths first.

## Test Signals
Useful tests include forced allocation failure at each pool creation stage, teardown after partial initialization, mailbox queue drain with ordinary and SLI-4 config commands, priority mbuf fallback exhaustion/refill, SLI-3 HBQ free while `hbq_in_use` changes, SLI-4 RQ repost success and failure, NVMe target receive buffer allocation/free, and leak checks after probe/remove or PCI error recovery. Runtime counters to watch include safety-pool `current_count`, RQB `buffer_count`, empty mailbox queues after teardown, and absence of DMA API debug warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nl.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nl.h

## Purpose
`lpfc_nl.h` defines the LPFC driver's Fibre Channel transport event masks and payload layouts for one-way driver-to-application notifications. It is the shared event ABI used by driver event producers and userspace/libdfc-style consumers through the FC transport/netlink event path.

## Important APIs, Types, and Constants
- Registration bits include `FC_REG_LINK_EVENT`, `FC_REG_RSCN_EVENT`, `FC_REG_CT_EVENT`, `FC_REG_DUMP_EVENT`, `FC_REG_TEMPERATURE_EVENT`, `FC_REG_VPORTRSCN_EVENT`, `FC_REG_ELS_EVENT`, `FC_REG_FABRIC_EVENT`, `FC_REG_SCSI_EVENT`, `FC_REG_BOARD_EVENT`, and `FC_REG_ADAPTER_EVENT`.
- `FC_REG_EVENT_MASK` is the union of supported registration categories.
- Temperature event codes are `LPFC_CRIT_TEMP`, `LPFC_THRESHOLD_TEMP`, and `LPFC_NORMAL_TEMP`.
- `struct lpfc_rscn_event_header` describes RSCN payloads with flexible `rscn_payload[]` data.
- `struct lpfc_els_event_header`, `struct lpfc_lsrjt_event`, and `struct lpfc_logo_event` describe ELS notifications and special LS_RJT/LOGO payloads.
- `struct lpfc_fabric_event_header` and `struct lpfc_fcprdchkerr_event` describe fabric busy/port busy/FCP read-check errors.
- `struct lpfc_scsi_event_header`, `struct lpfc_scsi_varqueuedepth_event`, and `struct lpfc_scsi_check_condition_event` describe SCSI queue, reset, queue-depth, and check-condition notifications.
- `struct lpfc_board_event_header`, `struct lpfc_adapter_event_header`, and `struct temp_event` cover board, adapter arrival, and temperature events.

## Control Flow and State
The header does not implement event delivery. Producers allocate or fill the defined structures with `event_type` first, followed by subcategory and type-specific fields, then pass the payload to the FC transport notification mechanism. Consumers can parse the first words generically and dispatch by category/subcategory. Registration masks filter which event categories an application receives.

## State and Persistence Behavior
No state is stored in this header. Event state is transient and carried in payload structs. The ABI expectation is persistent: field order, integer widths, and category constants must remain compatible with userspace tools.

## Dependencies and Integration Points
The header relies on fixed-width integer types and driver FC naming conventions. It is included by mailbox/discovery/SCSI/link modules that build event payloads. It integrates with RSCN handling, ELS receipt/reject paths, fabric notifications, SCSI error and queue-depth reporting, board interrupt reporting, adapter arrival notifications, dump events, and temperature monitoring.

## Risks and Edge Cases
- This is a binary payload ABI; changing struct layout, field order, or integer size would break consumers.
- There are duplicate definitions for the temperature codes in the file; they currently match, but future edits must keep them synchronized or remove the duplication carefully.
- Flexible RSCN payload length must be validated by event senders and receivers to avoid truncation or overread.
- WWPN/WWNN fields are raw 8-byte arrays; endianness/formatting must be handled consistently by producers and consumers.
- The broad `FC_REG_EVENT_MASK` must be updated when new event categories are added or userspace cannot subscribe to them through the aggregate mask.

## Test Signals
ABI tests should verify struct sizes/offsets expected by consumers, category mask filtering, RSCN payload-length handling, ELS subcategory dispatch for PLOGI/PRLO/ADISC/LS_RJT/LOGO, fabric and SCSI special-case payload content, temperature event codes, and compatibility with existing userspace event decoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nportdisc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nportdisc.c

## Purpose
`lpfc_nportdisc.c` implements the LPFC N_Port discovery state machine. It handles received and completed ELS operations such as PLOGI, PRLI, ADISC/PDISC, LOGO, and PRLO; performs service-parameter validation; coordinates RPI registration/unregistration; maps Fibre Channel and NVMe roles; drives recovery/removal transitions; and funnels all node events through a state/event action table.

## Important APIs, Types, and Functions
- Validation helpers: `lpfc_check_unload_and_clr_rscn()`, `lpfc_check_adisc()`, `lpfc_check_sparm()`, and `lpfc_check_elscmpl_iocb()`.
- Cleanup/recovery helpers: `lpfc_els_abort()`, `lpfc_release_rpi()`, `lpfc_disc_set_adisc()`, and illegal-transition handlers.
- PLOGI flow: `lpfc_rcv_plogi()`, `lpfc_defer_plogi_acc()`, `lpfc_cmpl_plogi_plogi_issue()`, and state-specific receive/completion wrappers.
- ADISC/PDISC flow: `lpfc_rcv_padisc()`, `lpfc_mbx_cmpl_resume_rpi()`, `lpfc_cmpl_adisc_adisc_issue()`, and ADISC/NPR wrappers.
- LOGO/PRLO flow: `lpfc_rcv_logo()` plus state-specific LOGO/PRLO handlers.
- PRLI flow: `lpfc_rcv_prli_support_check()`, `lpfc_rcv_prli()`, `lpfc_cmpl_prli_prli_issue()`, and target/initiator role updates.
- `lpfc_disc_action[]` is the state/event dispatch matrix indexed by `NLP_STE_*` state and `NLP_EVT_*` event.
- `lpfc_disc_state_machine()` is the public entry point that logs/traces the event, takes a temporary node reference, invokes the table action, logs the result, and releases the reference.

## Control Flow and State
Discovery is table-driven. Each event is dispatched by `lpfc_disc_state_machine()` through `lpfc_disc_action[(state * NLP_EVT_MAX_EVENT) + evt]`. The covered node states are unused, PLOGI issue, ADISC issue, REG_LOGIN issue, PRLI issue, LOGO issue, unmapped, mapped, and NPR. Events cover received ELS requests, ELS completions, registration completion, device removal, and device recovery.

The normal initiator login path is: issue or receive PLOGI, validate remote service parameters, register the RPI through a mailbox, transition to `NLP_STE_REG_LOGIN_ISSUE`, complete registration, determine FC4 capabilities, issue PRLI, complete PRLI, then transition to `NLP_STE_MAPPED_NODE` for targets or `NLP_STE_UNMAPPED_NODE` for initiator-only/fabric nodes. ADISC recovery can avoid full PLOGI when `NLP_RPI_REGISTERED`, `cfg_use_adisc`, RSCN mode, and FCP-2 target conditions allow it.

Received PLOGI is conservative. The code rejects zero WWPN/WWNN, bounds remote receive sizes to local service parameters, updates node WWNs/classes/max frame size, handles point-to-point timer negotiation, optionally issues SLI-3 `CONFIG_LINK` or SLI-4 `REG_VFI`, unregisters stale SLI-4 RPI state, allocates a REG_RPI mailbox, and defers the PLOGI ACC until after registration completes. PLOGI collision in `PLOGI_ISSUE` compares port names; the lower local port name accepts the remote PLOGI, while the other side rejects with command-in-progress.

PRLI processing distinguishes FCP and NVMe. It updates `nlp_type`, `nlp_fc4_type`, `nlp_fcp_info`, `nlp_nvme_info`, first-burst flags, NVMe discovery capability, and FC transport rport roles. Solicited PRLI completion waits until all outstanding FC4 PRLIs complete before moving to mapped/unmapped state. NPIV restricted-login ports reject or LOGO initiator-only functions as appropriate.

LOGO and device recovery paths move nodes toward `NLP_STE_NPR_NODE`, unregister transport/backend state, abort outstanding ELS IOCBs, start one-second rediscovery timers when needed, and treat fabric LOGO specially by tearing down/retrying vport discovery. Device removal usually drops the node unless it is still on a discovery list, in which case `NLP_NODEV_REMOVE` defers final cleanup.

## State and Persistence Behavior
Persistent runtime state is held in `struct lpfc_nodelist`, `struct lpfc_vport`, and `struct lpfc_hba`. Important node fields include `nlp_state`, `nlp_prev_state`, `nlp_flag`, `nlp_type`, `nlp_fc4_type`, `nlp_fcp_info`, `nlp_nvme_info`, `nlp_rpi`, `nlp_DID`, `nlp_nodename`, `nlp_portname`, `nlp_maxframe`, `fc4_prli_sent`, retry timers, and krefs. Vport state includes FC flags such as `FC_PT2PT`, `FC_FABRIC`, `FC_RSCN_MODE`, `FC_UNLOADING`, discovery counters, port state, local service parameters, and configured FC4 support. HBA state contributes SLI revision, link timers, fabric parameters, topology, NVMe target support, and mailbox/ELS rings.

No disk persistence occurs. The state machine mutates in-memory node state and firmware state through mailbox commands (`REG_LOGIN`, `UNREG_LOGIN`, `RESUME_RPI`, `REG_VFI`, `CONFIG_LINK`) and ELS exchanges. Timers persist pending rediscovery intent until callback execution or cancellation.

## Dependencies and Integration Points
The file depends on Linux timers, spinlocks, krefs, SCSI FC transport roles, FC ELS frame formats, and driver-local ELS, SLI, mailbox, vport, NVMe, debugfs, and logging APIs. It integrates with nameserver queries (`GFT_ID`), transport rport role changes, NVMe localport updates and target invalidation, fabric/vport discovery, mailbox completions from `lpfc_mbox.c`, buffer ownership from ELS IOCBs, and SLI abort logic.

## Risks and Edge Cases
- The action table must stay aligned with `NLP_STE_MAX_STATE` and `NLP_EVT_MAX_EVENT`; adding states/events without updating the table creates wrong dispatch.
- `lpfc_check_elscmpl_iocb()` can return `NULL` when command buffers were cleared for abort; completion handlers must not blindly dereference returned payloads.
- PLOGI ACC is intentionally deferred until REG_RPI completes. Changing this ordering can allow the remote port to send I/O before firmware has usable RPI state.
- Node references are passed through mailbox and resume-RPI completions; every `lpfc_nlp_get()` must pair with a put on all failure paths.
- RSCN handling avoids disrupting active RSCN discovery unless unloading; recovery code that ignores this can lose discovery progress.
- LOGO storms and delayed rediscovery timers are throttled with `NLP_LOGO_ACC`, `NLP_DELAY_TMO`, and one-second timers; incorrect flag clearing can cause repeated PLOGI/LOGO loops.
- NVMe target and initiator mode have different PRLI support rules; accepting the wrong PRLI can expose unsupported roles or create illegal transitions.
- Device removal while on discovery lists uses deferred flags instead of immediate free; callers must later honor `NLP_NODEV_REMOVE`.

## Test Signals
High-value tests include PLOGI with invalid WWPN/WWNN, oversized service parameters, PLOGI collision tie-breaking, point-to-point timer negotiation, SLI-4 RPI resume before ADISC/PLOGI ACC, REG_LOGIN success/failure including `MBXERR_RPI_FULL`, PRLI FCP and NVMe role combinations, NPIV restricted-login rejection, LOGO from fabric DID versus ordinary target, PRLO on mapped targets, RSCN/device-recovery transitions from mapped/unmapped/NPR states, node kref leak checks, and debugfs discovery traces showing expected DSM in/out state pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nportdisc.c -->
