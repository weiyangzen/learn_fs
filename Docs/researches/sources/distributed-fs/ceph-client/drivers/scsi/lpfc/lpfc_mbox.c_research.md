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
