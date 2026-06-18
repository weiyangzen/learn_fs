# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_ct.c

## Purpose

`lpfc_ct.c` implements Common Transport (CT) support for the Emulex/Broadcom `lpfc` Fibre Channel driver. It builds and completes FC-GS directory-service, FDMI management-service, and application-service CT requests, and it handles unsolicited CT receive paths. The file is central to fabric name-server registration/discovery, FDMI HBA/port attribute registration, VMID application-id registration, and delayed-discovery timer handoff.

The code sits below discovery and NPIV/vport management and above the SLI IOCB/WQE transport layer. Its primary outputs are fabric-visible registrations and updates to in-memory driver state such as `vport->ct_flags`, discovery counters, node FC-4 type flags, FDMI masks, and VMID registration records.

## Important APIs, Types, and Functions

- `lpfc_ct_unsol_event(phba, pring, ctiocbq)` is the SLI ring unsolicited CT dispatcher. It validates BDE counts, handles buffer shortage statuses, routes management/MIB CT requests to local reject logic, delegates other unsolicited CT traffic to BSG, and returns/reposts receive buffers for HBQ and non-HBQ paths.
- `lpfc_ct_handle_unsol_abort(phba, dmabuf)` forwards CT sequence abort handling to the BSG CT layer.
- `lpfc_ct_free_iocb(phba, ctiocb)` releases the request payload, response DMA buffer chain, BPL buffer, and IOCBQ. CT completion handlers rely on this as the common cleanup path.
- `lpfc_ns_cmd(vport, cmdcode, retry, context)` builds and issues name-server CT commands. It supports `GID_FT`, `GID_PT`, `GFF_ID`, `GFT_ID`, `RFT_ID`, `RNN_ID`, `RSPN_ID`, `RSNN_NN`, `RSPNI_PNI`, `DA_ID`, and `RFF_ID`, selecting the corresponding completion callback.
- `lpfc_fdmi_cmd(vport, ndlp, cmdcode, new_mask)` builds FDMI CT commands and serializes HBA/port/SmartSAN/vendor attributes from mask-selected callback tables.
- `lpfc_fdmi_change_check(vport)` is called from heartbeat logic to detect host-name changes and mapped-port count changes, then re-registers affected name-server or FDMI attributes.
- `lpfc_vmid_cmd(vport, cmdcode, vmid)` builds CT application-service commands for VMID register, query, deregister, and deregister-all flows.
- `lpfc_find_vport_by_did(phba, did)` scans the HBA vport list under `port_list_lock` to avoid discovering local sibling vports unless peer-port login is configured.
- `lpfc_vport_symbolic_port_name()` and `lpfc_vport_symbolic_node_name()` format symbolic names used by name-server and FDMI attributes.
- `lpfc_decode_firmware_rev()` formats firmware revision strings from VPD for sysfs/FDMI consumers.
- `lpfc_delayed_disc_tmo()` and `lpfc_delayed_disc_timeout_handler()` bridge a timer event into the lpfc worker thread and restart SCR/name-server/PLOGI discovery.

Key data structures come from local driver headers: `struct lpfc_sli_ct_request`, `struct lpfc_iocbq`, `struct lpfc_dmabuf`, `struct lpfc_nodelist`, `struct lpfc_vport`, `struct lpfc_hba`, FDMI attribute structures in `lpfc_hw.h`, and SLI3/SLI4 IOCB/WQE helpers in `lpfc_sli*.h`.

## Control Flow

Outbound CT commands follow a common sequence:

1. A caller such as discovery, vport teardown, FDMI login completion, heartbeat, or VMID management calls `lpfc_ns_cmd()`, `lpfc_fdmi_cmd()`, or `lpfc_vmid_cmd()`.
2. The command builder allocates a request DMA buffer and a buffer-pointer-list DMA buffer with `lpfc_mbuf_alloc()`, fills a CT preamble, command-specific payload, and first BDE.
3. `lpfc_ct_cmd()` appends response buffers with `lpfc_alloc_ct_rsp()` and calls `lpfc_gen_req()`.
4. `lpfc_gen_req()` allocates an IOCBQ, saves request/response/BPL buffers on it, takes an `ndlp` reference, prepares the SLI GEN_REQUEST, and issues it on `LPFC_ELS_RING`.
5. The selected completion handler interprets transport status and CT accept/reject status, updates discovery/registration state, may retry or issue the next CT command, then calls `lpfc_ct_free_iocb()` and drops the `ndlp` reference.

Name-server discovery completions have specialized flows. `GID_FT` and `GID_PT` completions validate the link event tag, handle unloading and deferred RSCNs, retry transient failures, parse DID lists with `lpfc_ns_rsp()`, then start or resume discovery when `gidft_inp` and `num_disc_nodes` drain. `GFF_ID` filters initiator-only ports before setting up discovery nodes. `GFT_ID` updates an existing node's FCP/NVMe FC-4 type and either advances PRLI or logs out a node that still has no usable FC-4 type.

FDMI discovery completion is a state chain. Physical ports normally progress `DHBA -> DPRT -> RHBA -> RPA`; vports progress `DPRT -> RPRT`, with `RPRT` deferred until the physical-port `RHBA` completes. FDMI CT rejects can downgrade from FDMI-2 or SmartSAN masks to older FDMI-1/FDMI-2 port masks and restart the relevant sequence. Successful physical-port `RPA` may optionally send an extra vendor MI `RPA` when firmware advertises MI support.

Unsolicited CT receive flow starts in `lpfc_ct_unsol_event()`. Management-service MIB requests are not implemented locally and are answered with an FS_RJT generated by `lpfc_ct_reject_event()`. Other unsolicited CT payloads are offered to `lpfc_bsg_ct_unsol_event()`. In all handled cases, receive buffers are logged, freed, and replenished according to HBQ or ring-posting mode.

VMID completion flow interprets application-service responses. `RAPP_IDENT` maps returned application IDs into the vport VMID hash table and marks the entry registered. `DAPP_IDENT` logs deregistration completion. `DALLAPP_ID` clears all non-free VMID slots, deletes hash nodes, and sets `FC_ALLOW_VMID`; if a deregister-all reject indicates the app ID is unavailable, it is accepted, while other failures may set `FC_DEREGISTER_ALL_APP_ID` for later retry.

## State and Persistence Behavior

All state is volatile kernel driver state; this file does not persist data to disk. The persistent effects are fabric-visible registrations in the name server, FDMI service, or application service.

Important state mutations include:

- `vport->ct_flags` records accepted name-server registrations such as `FC_CT_RFT_ID`, `FC_CT_RNN_ID`, `FC_CT_RSNN_NN`, `FC_CT_RSPN_ID`, `FC_CT_RSPNI_PNI`, and `FC_CT_RFF_ID`; `DA_ID` clears all CT flags.
- `vport->gidft_inp`, `vport->num_disc_nodes`, and `vport->fc_ns_retry` gate discovery progress, retry behavior, and RSCN cleanup.
- `struct lpfc_nodelist` entries get `nlp_fc4_type` bits for FCP/NVMe, state transitions such as `NLP_STE_NPR_NODE` or `NLP_STE_PRLI_ISSUE`, and recovery events for NVMET discovery.
- `vport->fdmi_hba_mask`, `vport->fdmi_port_mask`, and `vport->fdmi_num_disc` track which FDMI attributes are registered or need fallback/re-registration.
- `phba->hba_flag` uses `HBA_RHBA_CMPL` to release deferred vport `RPRT` commands; `phba->link_flag` uses `LS_CT_VEN_RPA` for the extra vendor MI FDMI transaction.
- `phba->os_host_name` is refreshed from `init_utsname()->nodename` and then propagated through name-server and FDMI re-registration.
- VMID state is protected by `vport->vmid_lock`; completion paths update `struct lpfc_vmid` flags, `un.app_id`, `vport->hash_table`, `vport->vmid_flag`, and load flags such as `FC_ALLOW_VMID` and `FC_DEREGISTER_ALL_APP_ID`.
- Delayed discovery uses `vport->work_port_events`, `WORKER_DELAYED_DISC_TMO`, and `FC_DISC_DELAYED` to transfer timer context into worker context.

Reference and memory ownership is explicit. Successful outbound commands transfer request/response/BPL ownership to the IOCBQ and its completion handler. `lpfc_gen_req()` increments the destination node reference; every completion path is expected to drop it after freeing the IOCB. Error paths free partially allocated DMA buffers before returning.

## Dependencies and Integration Points

This file depends heavily on the rest of the `lpfc` driver:

- SLI transport and DMA helpers: `lpfc_sli_get_iocbq()`, `lpfc_sli_release_iocbq()`, `lpfc_sli_issue_iocb()`, `lpfc_sli_prep_gen_req()`, `lpfc_sli_prep_xmit_seq64()`, BDE helpers, IOCB/WQE status accessors, and receive-buffer posting/freeing.
- Discovery and node management: `lpfc_findnode_did()`, `lpfc_setup_disc_node()`, `lpfc_disc_start()`, `lpfc_disc_state_machine()`, `lpfc_issue_els_prli()`, `lpfc_issue_els_logo()`, RSCN helpers, PLOGI/SCR/name-server discovery setup, and vport state changes.
- BSG CT integration: unsolicited non-MIB CT payloads and aborts are delegated to `lpfc_bsg_ct_unsol_event()` and `lpfc_bsg_ct_unsol_abort()`.
- NVMe/NVMET integration: RFF_ID handles NVMe initiator versus target feature bits and calls `lpfc_nvme_update_localport()` or `lpfc_nvmet_update_targetport()`.
- FDMI setup and login integration: FDMI nodes are created/logged in by ELS/discovery code, initial masks are set by `lpfc_setup_fdmi_mask()`, and `lpfc_mbx_cmpl_fdmi_reg_login()` starts FDMI command chains.
- Linux kernel services: DMA memory allocation, lists, spinlocks, rwlocks, timers, wait queues, UTS name strings, SCSI host identifiers, and byte-order helpers.

Externally visible prototypes are declared in `lpfc_crtn.h`. Call sites include SLI unsolicited ring setup in `lpfc_sli.c`, name-server and FDMI discovery in `lpfc_hbadisc.c`, vport teardown in `lpfc_vport.c`, VMID registration logic in `lpfc_vmid.c`, firmware/symbolic-name reporting in `lpfc_init.c` and `lpfc_attr.c`, and heartbeat FDMI refresh in `lpfc_init.c`.

## Risks and Edge Cases

- The command builders use low-level DMA buffers, manual BDE construction, and many goto-based cleanup paths. Regressions can cause leaks, double frees, stale node references, or DMA payload corruption.
- CT response parsing assumes the data placed by hardware is consistent with command-specific layouts. Incorrect response sizes, endian conversions, or CT reject handling could misclassify ports or corrupt discovery progress.
- `gidft_inp` and `num_disc_nodes` are coordination counters spread across discovery and CT completion paths. Missed decrements or duplicate retries can stall discovery or prematurely call `lpfc_disc_start()`.
- Event-tag checks intentionally ignore stale responses after link changes. Any new completion path must preserve this behavior to avoid applying old fabric data to a new link epoch.
- FDMI downgrade logic is switch-behavior sensitive. Reject handling that changes `fdmi_hba_mask` or `fdmi_port_mask` can reduce reported capabilities and must not loop forever across `DHBA`, `DPRT`, `RHBA`, `RPA`, and `RPRT`.
- FDMI attribute packing is bounded by `LPFC_BPL_SIZE - LPFC_CT_PREAMBLE`; adding attributes must preserve the mask-to-function-table ordering and buffer-size checks.
- Unsolicited CT buffer handling differs for SLI3 non-HBQ, HBQ, and SLI4 WCQE paths. Bugs here can leak receive buffers or fail to repost buffers during buffer pressure.
- VMID completion includes a notable ownership hazard: the `DALLAPP_ID` branch calls `lpfc_ct_free_iocb()` early and the common `free_res` label can also free the same IOCBQ. Changes around that branch need careful audit against current control flow and actual completion sequencing.
- VMID `DALLAPP_ID` uses `read_lock()` while zeroing VMID slots, which is unusual for mutation and should be treated cautiously if lock semantics are revisited.
- String formatting functions feed fabric-visible attributes. Truncation is mostly bounded with `scnprintf`, `strlcat`, and `strscpy`, but firmware revision formatting still uses `sprintf()` into caller-provided buffers sized by convention.

## Test Signals

Useful validation signals for this file are mostly integration and fault-injection oriented:

- Build coverage for the `lpfc` driver with SLI3/SLI4, NVMe, NVMET, NPIV, FDMI, SmartSAN, and VMID configuration combinations.
- Discovery tests where `lpfc_ns_cmd()` issues `GID_FT`/`GID_PT`, receives accept, no-entry reject, transient local reject, stale event tag, and lost-link statuses; expected signals are correct `gidft_inp` drain, RSCN flush behavior, vport state, and node FC-4 type assignment.
- Name-server registration tests for `RFT_ID`, `RNN_ID`, `RSPN_ID`, `RSNN_NN`, `RSPNI_PNI`, `RFF_ID`, and `DA_ID`; expected signals are `vport->ct_flags` transitions and correct FCP/NVMe feature bits.
- FDMI fabric-compatibility tests that force FS_RJT on FDMI-2/SmartSAN attributes and confirm fallback to FDMI-1 or FDMI-2 port masks without retry loops.
- Heartbeat tests for host-name change and mapped-node-count change, checking that `lpfc_fdmi_change_check()` reissues only the required name-server/FDMI commands.
- Unsolicited CT tests through BSG and MIB reject paths, including no-buffer and receive-buffer-waiting statuses, to confirm buffer replenishment and no leaks.
- VMID tests for register, deregister, deregister-all, app-id-not-available reject, and transport error paths; expected signals are VMID hash-table updates, flags, load flags, and absence of memory/reference leaks.
- Runtime observability comes from `lpfc_printf_vlog()`/`lpfc_printf_log()` messages, discovery tracepoints via `lpfc_debugfs_disc_trc()`, SCSI host symbolic-name exports, FDMI/name-server fabric records, and driver counters such as `phba->fc_stat.NoRcvBuf`.
