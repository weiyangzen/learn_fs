# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_els.c lines 1-8376

Chunk id: `subset-b-005286`

## Scope

This chunk covers the first 8,376 lines of the Emulex/Broadcom `lpfc` Fibre Channel driver ELS implementation. It starts with ELS IOCB allocation and the fabric login path, then covers PLOGI/PRLI/ADISC/LOGO command issue and completion, ELS retry policy, ELS response generation, fabric diagnostic registration through SCR/RDF/EDC, RDP and LCB unsolicited diagnostic handling, and the beginning of RSCN handling. The line range ends inside `lpfc_els_handle_rscn()`, so later lines in the same source file complete that RSCN flow and cover additional unsolicited ELS handlers.

The code is not standalone. It is tied to the LPFC discovery state machine, mailbox layer, SLI-3/SLI-4 IOCB/WQE submission, node lifecycle management, SCSI/NVMe transport registration, FC fabric services, and hardware DMA buffer pools defined across the surrounding `lpfc` driver.

## Purpose

This chunk implements the active Extended Link Service control plane for LPFC ports. Its main jobs are:

- Build, issue, complete, retry, and free outbound ELS commands for fabric login, N_Port login, process login, address discovery, logout, SCR/RSCN, FARPR, RDF, EDC, and diagnostic responses.
- Drive discovery state transitions by converting ELS completions into node state-machine events such as `NLP_EVT_CMPL_PLOGI`, `NLP_EVT_CMPL_PRLI`, `NLP_EVT_CMPL_ADISC`, `NLP_EVT_CMPL_LOGO`, `NLP_EVT_DEVICE_RM`, and `NLP_EVT_DEVICE_RECOVERY`.
- Maintain fabric and vport state after FLOGI/FDISC, including assigned FCID, fabric service parameters, clean-address behavior, NPIV capability, VFI/VPI/RPI registration, fabric-controller registration, and FCF failover.
- Handle asynchronous or unsolicited ELS inputs that require ACC/RJT responses, such as RDF, EDC, RDP, LCB, RRQ, LOGO, ADISC, PRLI, RNID, ECHO, and RSCN.
- Negotiate congestion and link-diagnostic behavior with the fabric through EDC/RDF and report diagnostic data through RDP and LCB response paths.

## Important APIs, Types, and Functions

Core ELS allocation and cleanup:

- `lpfc_prep_els_iocb()` is the common allocator for ELS requests and responses. It allocates an IOCBQ, command DMA buffer, optional response DMA buffer, and BPL buffer; fills BDEs; delegates SLI-specific setup to `lpfc_sli_prep_els_req_rsp()`; records `vport`, retry count, command/response buffers, and driver timeout; and marks FIP FLOGI/FDISC/LOGO identifiers for fabric-controller traffic when needed.
- `lpfc_els_free_iocb()`, `lpfc_els_free_data()`, and `lpfc_els_free_bpl()` release the DMA buffers and IOCBQ. `LPFC_DELAY_MEM_FREE` moves buffers to `phba->elsbuf` for delayed free when firmware may still DMA into them.
- `lpfc_is_els_acc_rsp()` validates that a received response buffer begins with `ELS_LS_ACC`.
- `lpfc_els_chk_latt()` checks for SLI-3 link attention during discovery, marks `FC_ABORT_DISCOVERY`, and issues CLEAR_LA when needed.

Fabric login and VFI/VPI/RPI setup:

- `lpfc_initial_flogi()` and `lpfc_initial_fdisc()` find or allocate the `Fabric_DID` node and issue the first FLOGI or FDISC.
- `lpfc_issue_els_flogi()` builds the FLOGI payload from `vport->fc_sparam`, adjusts common service parameters, sets NPIV and priority-tagging fields, handles SLI-4 FCFI context setup, starts the discovery timer, marks `HBA_FLOGI_ISSUED`/`HBA_FLOGI_OUTSTANDING`, and sends the command through `lpfc_issue_fabric_iocb()`.
- `lpfc_cmpl_els_flogi()` is the top-level FLOGI completion. It handles link-attention aborts, FIP round-robin FCF failover, retry decisions, loop-open private-loop fallback, ACC parsing, VMID setup, and branch to fabric or point-to-point completion.
- `lpfc_cmpl_els_flogi_fabric()` updates `FC_FABRIC`, timing values, `fc_myDID`, fabric names, class support, max frame size, FDMI masks, NPIV flags, SLI-4 VFI behavior, RPI/VPI cleanup when fabric parameters changed, and then starts fabric registration or SLI-4 vport setup.
- `lpfc_cmpl_els_flogi_nport()` handles point-to-point topology, disables NPIV, chooses which side initiates PLOGI by comparing WWPNs, assigns `PT2PT_LocalID`/`PT2PT_RemoteID`, and either configures the link or starts discovery waiting for remote PLOGI.
- `lpfc_issue_fabric_reglogin()`, `lpfc_issue_reg_vfi()`, and `lpfc_issue_unreg_vfi()` issue mailbox commands that bind fabric service parameters to firmware objects for SLI-3/SLI-4 operation.
- `lpfc_check_clean_addr_bit()` detects fabric parameter or FCID changes and may set `FC_DISC_DELAYED` when the fabric response clears the clean-address bit.

Discovery ELS commands:

- `lpfc_issue_els_plogi()` builds PLOGI service parameters, advertises VMID support and firmware suppress-response support, defers if an UNREG_RPI is in progress, and submits on the ELS ring.
- `lpfc_cmpl_els_plogi()` validates the node, retries failures, invokes `lpfc_plogi_confirm_nport()` on success to reconcile WWPN/DID identity, records encryption status, detects VMID support, and drives the discovery state machine.
- `lpfc_plogi_confirm_nport()` is the identity-repair helper. When the WWPN returned by PLOGI belongs to another or new node, it unregisters RPIs, swaps or copies node state, flags, FC4 type, NVMe remote-port pointer, active RRQ bitmaps, and DIDs so the returned node accurately represents the logged-in N_Port.
- `lpfc_issue_els_prli()` sends one or two PRLIs depending on remote FC4 type. It supports FCP PRLI and NVMe PRLI, clears stale node protocol state before issuing, sets first-burst and NSLER bits where configured, tracks per-vport and per-node outstanding PRLI counters, and rejects strict NVMe FC4 on SLI-3.
- `lpfc_cmpl_els_prli()` decrements PRLI counters, retries eligible failures, differentiates expected PRLI rejection in dual FC4 probing from warning cases, and removes non-transport nodes when PRLI failure leaves no active protocol.
- `lpfc_issue_els_adisc()` and `lpfc_cmpl_els_adisc()` implement ADISC issue/completion, mark and clear `NLP_ADISC_SND`, run retry policy, and transition nodes after address validation.
- `lpfc_issue_els_logo()` and `lpfc_cmpl_els_logo()` issue logout, wake LOGO waiters, call the state machine for cleanup, start target recovery after LOGO when appropriate, or remove unregistered initiator/fabric nodes.
- `lpfc_more_plogi()`, `lpfc_more_adisc()`, `lpfc_els_disc_plogi()`, and `lpfc_els_disc_adisc()` throttle discovery by `vport->cfg_discovery_threads`, maintain `vport->num_disc_nodes`, set/clear `FC_NLP_MORE`, and keep discovery/RSCN timers alive.

Fabric service and diagnostics:

- `lpfc_issue_els_scr()` registers for state-change notifications with the fabric controller and, on SLI-4, first calls `lpfc_reg_fab_ctrl_node()` to register an RPI for the fabric-controller node.
- `lpfc_issue_els_rscn()` sends an outbound RSCN to the fabric controller or mapped point-to-point peer.
- `lpfc_issue_els_farpr()` builds a FARPR payload matching local and remote port/node names.
- `lpfc_issue_els_rdf()` registers for fabric performance-impact notification descriptors. It builds an RDF request for link integrity, delivery, peer congestion, and congestion FPIN tags.
- `lpfc_els_rcv_rdf()` accepts an incoming RDF and reissues local RDF registration.
- `lpfc_issue_els_edc()`, `lpfc_format_edc_cgn_desc()`, `lpfc_format_edc_lft_desc()`, `lpfc_cmpl_els_edc()`, and `lpfc_least_capable_settings()` exchange diagnostic capabilities. The driver advertises congestion and high-speed link-fault descriptors, parses fabric TLVs, chooses least-common congestion signaling/frequency behavior, and falls back to FPIN-only RDF when EDC is unavailable or invalid.
- `lpfc_link_is_lds_capable()` limits link diagnostic descriptor support to SLI-4 64G/128G links, including trunked links.

Retry and delayed work:

- `lpfc_els_retry()` centralizes retry decisions for FLOGI, FDISC, PLOGI, PRLI/NVMe PRLI, ADISC, and LOGO. It interprets IOCB/WQE status, LS_RJT reason/explanation fields, FCF discovery state, topology, local unload state, and command type to choose no retry, immediate retry, delayed retry, link reset, or special state updates.
- `lpfc_els_retry_delay()` is the node timer callback. It holds a node reference, posts `LPFC_EVT_ELS_RETRY` to `phba->work_list`, and wakes the worker.
- `lpfc_els_retry_delay_handler()` consumes delayed retry work, clears `NLP_DELAY_TMO`, reads `nlp_last_elscmd`, restores retry count, and reissues the matching ELS command.
- `lpfc_cancel_retry_delay_tmo()` cancels delayed retry state and, if a discovery node was pending, advances the remaining ADISC/PLOGI discovery flow.
- `lpfc_link_reset()` issues `INIT_LINK`, enabling link-attention interrupts first on older SLI revisions.

ELS response builders and completions:

- `lpfc_els_rsp_acc()` builds generic ACC, FLOGI/PLOGI ACC with service parameters, PRLO ACC, or RDF ACC and optionally carries a mailbox command that `lpfc_cmpl_els_rsp()` will issue after successful response transmission.
- `lpfc_els_rsp_reject()` builds LS_RJT with caller-supplied reason/explanation.
- `lpfc_issue_els_edc_rsp()`, `lpfc_els_rsp_adisc_acc()`, `lpfc_els_rsp_prli_acc()`, `lpfc_els_rsp_rnid_acc()`, and `lpfc_els_rsp_echo_acc()` build specific ACC payloads for incoming EDC, ADISC, PRLI, RNID, and ECHO.
- `lpfc_cmpl_els_rsp()` handles response completion, optional post-ACC REG_LOGIN mailbox issue, PLOGI collision flags, encryption reporting after accepting a PLOGI, SLI-4 NPIV node dropping, and deferred point-to-point FLOGI ACC reference cleanup.
- `lpfc_cmpl_els_logo_acc()` finalizes LOGO ACC handling, unregistering RPI for NPR nodes and restarting PLOGI after PRLO.
- `lpfc_mbx_cmpl_dflt_rpi()` completes temporary/default RPI cleanup and drops the node.
- `lpfc_els_clear_rrq()` parses a received RRQ payload and clears the matching active RRQ entry; `lpfc_cmpl_els_rrq()` completes outbound RRQ and clears the active exchange tracking.

RDP, LCB, and RSCN handling:

- RDP helper functions format link-service, SFP, link-error, buffer-to-buffer credit, optical element diagnostic, optical product data, FEC, speed, and port-name descriptors.
- `lpfc_els_rcv_rdp()` validates incoming RDP support and payload, allocates an `lpfc_rdp_context`, stores RX/OX IDs and an ndlp reference, then starts mailbox reads through `lpfc_get_rdp_info()`.
- `lpfc_get_rdp_info()` starts asynchronous SFP page A0 read; `lpfc_get_sfp_info_wait()` is the synchronous variant that reads SFP page A0 and A2 into the RDP context.
- `lpfc_els_rdp_cmpl()` builds an RDP ACC from mailbox-collected SFP and link statistics or emits LS_RJT on failure.
- `lpfc_els_rcv_lcb()`, `lpfc_sli4_set_beacon()`, and `lpfc_els_lcb_rsp()` validate link cable beacon requests, issue SLI-4 SET_BEACON_CONFIG mailbox commands, and respond with LCB ACC/RJT.
- `lpfc_els_flush_rscn()` frees held RSCN payload buffers and clears RSCN flags.
- `lpfc_rscn_payload_check()` matches a DID against held RSCN payloads by port, area, domain, or fabric scope.
- `lpfc_rscn_recovery_check()` moves affected nodes through `NLP_EVT_DEVICE_RECOVERY`, except unloading ports, unused nodes, in-flight discovery states, and NVMe target mode.
- `lpfc_send_rscn_event()` posts vendor RSCN events to management applications.
- `lpfc_els_rcv_rscn()` accepts and processes unsolicited RSCN. It posts SCSI transport events, handles point-to-point rescan, ignores self-vport-only NPIV RSCNs, coalesces or defers payloads while discovery is active, starts discovery timeout, sends ACC, triggers recovery checks, and enters `lpfc_els_handle_rscn()`.
- `lpfc_els_handle_rscn()` begins the name-server comparison path. This chunk only includes its setup and first `NameServer_DID` branch; subsequent lines complete the function.

## Control Flow

Most outbound commands follow a common pattern. The issuer finds or receives an `lpfc_nodelist`, calls `lpfc_prep_els_iocb()`, fills the command payload, assigns a command-specific completion callback, takes an ndlp reference with `lpfc_nlp_get()`, and submits through `lpfc_sli_issue_iocb()` or the fabric-gated `lpfc_issue_fabric_iocb()`. The completion callback extracts SLI-neutral status through `get_job_ulpstatus()`, `get_job_word4()`, and related helpers, checks link attention, asks `lpfc_els_retry()` if failure is retryable, and either reissues/delays the command or drives the discovery state machine and frees the IOCB.

FLOGI is the root discovery path. `lpfc_initial_flogi()` creates the fabric node and moves the vport to `LPFC_FLOGI`. Completion either retries, falls back to private loop discovery after loop-open failure, runs fabric setup for F_Port responses, or runs point-to-point setup for N_Port responses. Fabric setup updates vport and HBA fabric parameters, handles FCID/fabric-name changes by unregistering stale RPI/VPI state, registers VFI or fabric login, and starts FDISC/SCR/name-server discovery when VFI/VPI state is ready. Point-to-point setup chooses whether local or remote initiates PLOGI and configures link state accordingly.

After FLOGI/FDISC, discovery advances through PLOGI, PRLI, and optionally ADISC. The code maintains `NLP_NPR_2B_DISC`, `NLP_NPR_ADISC`, `FC_NDISC_ACTIVE`, `FC_NLP_MORE`, `num_disc_nodes`, and per-command sent flags to avoid issuing too many ELS commands at once and to resume when completions arrive. Successful PLOGI may swap node identity before the state machine sees the completion; successful PRLI marks FC4 protocol availability; failed commands can remove nodes when they are not registered with SCSI or NVMe transports.

RSCN processing is an overlay on discovery. Incoming RSCNs are acknowledged quickly, payloads are stored in `fc_rscn_id_list`, and affected nodes are moved to recovery unless they are already in a login/logout transition. If discovery is already active, RSCNs are coalesced into the last held buffer when possible or converted to full rediscovery through `FC_RSCN_DISCOVERY`. `lpfc_end_rscn()` later either handles queued RSCNs or clears `FC_RSCN_MODE`.

Diagnostics follow two paths. EDC/RDF are fabric-registration flows initiated by the local port or by incoming RDF, and completions update congestion-management state. RDP/LCB are unsolicited diagnostic requests from a remote port or fabric controller; they may need mailbox operations before the ELS response can be sent, so context structures hold ndlp references and exchange IDs across asynchronous mailbox completion.

## State and Persistence Behavior

This chunk is dominated by live kernel and firmware state rather than file-backed persistence.

Long-lived vport and HBA state includes `fc_flag`, `load_flag`, `port_state`, `fc_myDID`, `fc_prevDID`, `fabric_portname`, `fabric_nodename`, `fc_sparam`, `fc_fabparam`, `fc_ratov`, `fc_edtov`, `fc_rscn_id_list`, `fc_rscn_id_cnt`, `fc_rscn_flush`, `num_disc_nodes`, `fc_ns_retry`, VMID fields, FDMI masks, FCF discovery flags, and congestion-management fields such as `cgn_reg_signal`, `cgn_reg_fpin`, `cgn_sig_freq`, `cgn_fpin_frequency`, and link-diagnostic thresholds.

Per-node state includes `nlp_state`, `nlp_prev_state`, `nlp_flag`, `save_flags`, `nlp_DID`, WWPN/WWNN, RPI, FC4 type, transport registration flags, PRLI counters, delayed retry timer state (`nlp_delayfunc`, `nlp_last_elscmd`, `nlp_retry`, `els_retry_evt`), active RRQ bitmaps, encryption info, VMID support, and optional SCSI/NVMe remote-port pointers.

IOCB and mailbox state is transient but asynchronous. ELS IOCBs own DMA buffers until completion; delayed-free paths keep buffers on `phba->elsbuf` across a heartbeat. Mailboxes may carry `ctx_ndlp`, `ctx_buf`, `ctx_u.rdp`, or `ctx_u.lcb` and must clean references on success and failure. Response IOCBs may carry an `LPFC_MBOXQ_t` that is only issued after ACC completion, which makes ACC completion part of the login state machine.

Hardware-visible persistence is limited to link and firmware object state: VFI/VPI/RPI registration, CLEAR_LA, INIT_LINK, SET_BEACON_CONFIG, and congestion signal configuration. RSCN payloads are held in DMA buffers in memory until processed or flushed. The code posts RSCN vendor events to the FC transport/netlink path but does not persist them itself.

## Dependencies and Integration Points

- LPFC SLI submission and completion APIs: `lpfc_sli_get_iocbq()`, `lpfc_sli_release_iocbq()`, `lpfc_sli_issue_iocb()`, `lpfc_issue_fabric_iocb()`, `lpfc_sli_prep_els_req_rsp()`, WQE/IOCB field helpers, and abort support.
- LPFC mailbox APIs: `lpfc_sli_issue_mbox()`, `lpfc_sli_issue_mbox_wait()`, `lpfc_config_link()`, `lpfc_reg_rpi()`, `lpfc_reg_vfi()`, `lpfc_unreg_vfi()`, `lpfc_init_link()`, `lpfc_sli4_config()`, SFP memory dump helpers, and mailbox resource cleanup.
- Discovery/node state machine: `lpfc_disc_state_machine()`, `lpfc_nlp_init()`, `lpfc_enqueue_node()`, `lpfc_nlp_get()`, `lpfc_nlp_put()`, `lpfc_nlp_set_state()`, `lpfc_unreg_rpi()`, `lpfc_nlp_unreg_node()`, `lpfc_drop_node()`, `lpfc_disc_start()`, `lpfc_do_scr_ns_plogi()`, and CT/name-server code reached after this chunk.
- SCSI and NVMe transport integration: `SCSI_XPT_REGD`, `NVME_XPT_REGD`, `lpfc_nvme_rescan_port()`, remote-port encryption attributes, and device-loss behavior.
- Fibre Channel protocol definitions from `<uapi/scsi/fc/fc_fs.h>` and `<uapi/scsi/fc/fc_els.h>` plus LPFC-specific structures for PRLI, ADISC, RRQ, RDF, EDC, RDP, LCB, VMID, and FDMI.
- Linux kernel infrastructure: DMA buffer allocation, mempools, timers, work lists, spin locks, `fc_host_post_event()`, `fc_host_post_vendor_event()`, endian conversion helpers, `list_for_each_entry_safe()`, and debugfs discovery tracing.

## Risks and Edge Cases

- Node lifetime is delicate. Many paths take an ndlp reference for IOCB or mailbox completion, then also drop initial references when nodes are not transport registered. Incorrect additions around retry, deferred FLOGI ACC, PLOGI identity swaps, or mailbox failure can leak nodes or prematurely free them.
- `lpfc_plogi_confirm_nport()` swaps substantial node identity and state under two node locks. Changes to node flags, NVMe remote-port ownership, active RRQ bitmaps, or transport registration need careful review against this swap path.
- FLOGI fabric-parameter changes trigger broad cleanup: pending mailbox cleanup, RPI unregister, VPI unregister/init, VFI registration, FDMI mask reset, and possible delayed discovery. Missing one cleanup path can leave firmware RPIs bound to stale FCIDs.
- Retry policy intentionally contains unbounded or long retries: FLOGI can retry forever outside loopback, NameServer PLOGI can continue indefinitely for some errors, no-resource retries can run up to 250 attempts, FDISC retries scale to devloss timeout, and PLOGI/PRLI busy cases retry up to 48 times. This is useful for fabric convergence but can mask persistent faults.
- Delayed retry uses timers, work-list entries, and node references. `lpfc_cancel_retry_delay_tmo()` must stay synchronized with discovery counters or `num_disc_nodes` and `FC_NLP_MORE` can become inconsistent.
- Several response paths issue a mailbox only after an ACC completes. Failure to transmit the ACC, link attention during response completion, or mailbox issue failure must free mailbox resources and clear node flags correctly.
- RSCN coalescing mutates held payload buffers and steals `cmdiocb->cmd_dmabuf` by setting it to NULL. Any future cleanup change must preserve this ownership transfer or it will double-free or leak RSCN buffers.
- `fc_rscn_flush` is used as a simple exclusion token around RSCN payload arrays. It is protected only around acquisition/release with `host_lock`, while payload walking happens after the token is set. Callers must not bypass the token.
- RDP and LCB contexts hold ndlp references across mailbox completions. Error paths that allocate context, take references, then fail mailbox issue are easy places for reference imbalance.
- EDC TLV parsing depends on fabric-provided descriptor lengths. The code validates truncation and exact expected sizes before casting; new descriptor support should keep the same defensive parsing style.
- Some protocol fields are SLI-revision sensitive. SLI-4 uses WQE context/RCVOXID fields and SLI-3 uses IOCB `ulpContext`/`ox_id`; every new response path must set both correctly.
- VMID, encryption, NVMe first-burst, NSLER, and suppress-response features are negotiated opportunistically through service parameters or PRLI fields. Regressions may only appear with specific switch/target capabilities.
- This range ends before `lpfc_els_handle_rscn()` completes, so any final conclusions about name-server query fallback and RSCN completion must be reconciled with the next chunk.

## Test and Validation Signals

- Build-test with SLI-3 and SLI-4 code enabled. Pay attention to WQE/IOCB field access, endian conversions, and structures from FC ELS headers.
- Use fault injection for `lpfc_prep_els_iocb()` allocation stages, `lpfc_nlp_get()` failures, and mailbox allocation/issue failures. Expected signals are clean IOCB/DMA/mailbox frees and balanced ndlp references.
- Exercise FLOGI success to fabric, FLOGI success to point-to-point N_Port, FLOGI loop-open failure/private-loop fallback, FIP FCF failover, and FLOGI retry exhaustion/lost-link cases. Watch `FC_FABRIC`, `FC_PT2PT`, `FC_PUBLIC_LOOP`, `HBA_FLOGI_OUTSTANDING`, VFI/VPI flags, and node refcounts.
- Test fabric parameter changes where FCID, fabric WWPN/WWNN, or clean-address bit changes. Expected behavior is delayed discovery when configured, RPI/VPI cleanup, FDMI mask reset, and correct rediscovery.
- Run discovery with many remote ports to verify `cfg_discovery_threads`, `num_disc_nodes`, `FC_NLP_MORE`, `FC_NDISC_ACTIVE`, and discovery timeout behavior across PLOGI and ADISC phases.
- Exercise mixed FCP/NVMe remote ports. Verify dual PRLI issue on SLI-4, NVMe rejection handling in point-to-point mode, first-burst fields, NSLER bits, and transport registration outcomes.
- Inject LS_RJT, local reject, no-resource, sequence-timeout, invalid-RPI, fabric busy, and remote busy statuses for FLOGI/PLOGI/PRLI/ADISC/FDISC. Expected signals are retry delay values, retry caps, `elsXmitRetry`, `elsDelayRetry`, and `elsRetryExceeded`.
- Send LOGO/PRLO collision and recovery scenarios. Confirm LOGO waiters wake, target nodes restart discovery when appropriate, and non-transport nodes are removed.
- Validate ELS ACC/RJT responses for PLOGI, PRLI, ADISC, RNID, ECHO, RDF, EDC, and LOGO with both SLI-3 and SLI-4 exchange ID handling.
- Exercise EDC/RDF with fabrics that support congestion signals, FPIN only, malformed TLVs, and no EDC. Expected signals include `lpfc_config_cgn_signal()` calls, `cgn_reg_signal`/`cgn_reg_fpin` changes, and RDF fallback.
- Send RDP and LCB requests on supported and unsupported links. Expected behavior is ACC with populated descriptors/beacon response on valid SLI-4 FC links and LS_RJT on FCoE, old SLI, bad descriptor, unsupported subcommand, or mailbox failure.
- Exercise RSCN reception during idle, during active discovery, in point-to-point mode, during NPIV self-vport-only notifications, and while the RSCN list is being flushed. Watch payload buffer ownership, `FC_RSCN_MODE`, `FC_RSCN_DEFERRED`, `FC_RSCN_DISCOVERY`, vendor events, and node recovery transitions.
