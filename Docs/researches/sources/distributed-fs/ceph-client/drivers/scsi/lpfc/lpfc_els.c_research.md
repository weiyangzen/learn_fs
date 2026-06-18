# Research: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_els.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005286`: lines 1-8376, `Docs/researches/chunks/subset-b-005286_research.md`
- `subset-b-005287`: lines 8377-12579, `Docs/researches/chunks/subset-b-005287_research.md`

## Chunk Research

### subset-b-005286: lines 1-8376

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

### subset-b-005287: lines 8377-12579

# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_els.c lines 8377-12579

## Scope

This chunk covers the latter ELS and discovery orchestration paths in the Emulex/Broadcom `lpfc` Fibre Channel driver. It begins at the tail of RSCN handling, where name-server queries are issued or the RSCN is flushed, and then covers unsolicited ELS request processing, point-to-point FLOGI handling, RLS/RTV/RPL/RRQ support, FARP/FAN/EDC/FPIN handling, ELS timeout and flush paths, vport name-server/FDMI discovery startup, FDISC and NPIV LOGO flows, fabric IOCB throttling, SLI4 ELS XRI-abort cleanup, ABTS recovery, and VMID QFPA/UVEM ELS commands.

The chunk depends on earlier code in `lpfc_els.c` for common ELS IOCB preparation/freeing, FLOGI/PLOGI/PRLI/LOGO/ADISC issue and completion logic, ELS response builders, RSCN parsing, EDC/RDF helpers, and RRQ bookkeeping. It also depends heavily on structures and constants in `lpfc.h`, `lpfc_sli.h`, `lpfc_disc.h`, and `lpfc_hw.h`, plus discovery state-machine code in `lpfc_hbadisc.c`, SLI queue and RRQ helpers in `lpfc_sli.c`, and VMID helpers in `lpfc_vmid.c`/`lpfc_ct.c`.

## Purpose

The visible code is the driver's ELS receive-side dispatcher and the tail of the fabric/vport discovery engine. Its responsibilities are:

- accept, reject, or route unsolicited ELS commands according to topology, vport discovery state, node state, and command type;
- handle point-to-point FLOGI negotiation, including loopback detection, local/remote DID assignment, deferred FLOGI ACC response, and fabric parameter capture;
- build ACC payloads for diagnostic or discovery ELS commands such as RNID, ECHO, RLS, RTV, RPL, RRQ, FARPR, and EDC;
- parse FPIN and EDC TLV descriptors, update congestion-management counters and shared congestion info, and selectively deliver FPIN descriptors to the FC transport;
- enforce ELS timeout behavior by aborting stale outstanding ELS IOCBs and flushing queued or in-flight ELS work during linkdown, vport teardown, mailbox timeout, or HBA teardown;
- start name-server SCR PLOGI and optional FDMI login after FLOGI/FDISC, register new VPIs, and recover from FDISC cases that require a fresh physical FLOGI;
- serialize fabric-bound ELS commands so switches see at most one outstanding fabric IOCB, while temporarily blocking on fabric busy/reject statuses;
- clean up SLI4 ELS SGL/XRI abort state, create RRQ recovery work, and trigger rport recovery when abort recovery requires a LOGO/relogin path;
- manage VMID priority-tagging allocation ranges and send QFPA/UVEM fabric ELS requests for VMID QoS and virtual-entity map registration.

## Important APIs, Types, and Functions

- `lpfc_els_rcv_flogi()` processes unsolicited FLOGI. It rejects loop-topology FLOGI, validates service parameters, detects external loopback by comparing WWPNs, selects point-to-point DID roles, updates `FC_PT2PT`/`FC_PT2PT_PLOGI` flags, stores `phba->fc_fabparam`, and either sends or defers a FLOGI ACC.
- `lpfc_els_rcv_rnid()`, `lpfc_els_rcv_echo()`, `lpfc_els_rcv_lirr()`, and `lpfc_els_rcv_rrq()` handle simple unsolicited commands: RNID accepts only format 0 or topology-discovery format, ECHO echoes payload data, LIRR is rejected, and RRQ is accepted and optionally clears SLI4 RRQ state.
- `lpfc_els_rsp_rls_acc()` is the mailbox completion that turns `MBX_READ_LNK_STAT` results into an RLS ACC payload with link error counters. `lpfc_els_rcv_rls()` gates RLS by node state, allocates the mailbox, saves OX/RX IDs, and rejects when resources or state are unsuitable.
- `lpfc_els_rcv_rtv()` builds an RTV ACC containing `fc_ratov`, `fc_edtov`, and ED_TOV resolution, using the received exchange identifiers in the response WQE/IOCB.
- `lpfc_issue_els_rrq()` and `lpfc_send_rrq()` send RRQ ELS requests for active SLI4 exchange recovery records represented by `struct lpfc_node_rrq`.
- `lpfc_els_rsp_rpl_acc()` and `lpfc_els_rcv_rpl()` implement Read Port List with this driver advertising only one local port entry.
- `lpfc_els_rcv_farp()` and `lpfc_els_rcv_farpr()` implement limited FARP/FARPR behavior, matching only WWPN/WWNN and optionally issuing PLOGI and FARPR.
- `lpfc_els_rcv_fan()` handles Fabric Address Notification for the physical port, either restarting fabric login when fabric names changed or restoring the prior DID and registering fabric/VFI state when the fabric is unchanged.
- `lpfc_els_rcv_edc()` parses EDC diagnostic descriptors, records congestion-signal and FPIN registration capabilities, applies least-capable congestion settings, sends an EDC ACC, and configures congestion signaling.
- `lpfc_els_timeout()` posts `WORKER_ELS_TMO`; `lpfc_els_timeout_handler()` scans ELS `txcmplq`, decrements driver timeouts, aborts timed-out IOCBs, and re-arms the ELS timer while completions remain.
- `lpfc_els_flush_cmd()` aborts fabric-list entries for a vport, aborts or cancels in-flight ELS/GEN requests, cancels eligible pending ELS `txq` IOCBs, and special-cases linkdown completions to avoid discovery retries. `lpfc_els_flush_all_cmd()` applies this to every vport under `port_list_lock`.
- `lpfc_send_els_failure_event()` and `lpfc_send_els_event()` publish vendor FC events for ELS LS_RJT/busy failures and incoming PLOGI/PRLO/ADISC/LOGO.
- `lpfc_els_rcv_fpin()`, with helpers `lpfc_els_rcv_fpin_li()`, `lpfc_els_rcv_fpin_del()`, `lpfc_els_rcv_fpin_peer_cgn()`, and `lpfc_els_rcv_fpin_cgn()`, parses FPIN TLVs, logs descriptor contents, updates congestion statistics, updates the CMF shared info area, and sends per-descriptor FPIN notifications to the FC transport only when appropriate.
- `lpfc_els_unsol_buffer()` is the central unsolicited ELS dispatcher. It finds or creates the `ndlp`, applies discovery/link/unload gates, increments receive counters, posts management events, drives `lpfc_disc_state_machine()` for login/logout/discovery commands, calls direct handlers for non-state-machine commands, and emits LS_RJT responses for unsupported or state-incompatible commands.
- `lpfc_els_unsol_event()` translates SLI IOCB/WCQE unsolicited receive events into driver DMA buffers, resolves NPIV vports from VPI on SLI3, replenishes receive buffers when needed, calls `lpfc_els_unsol_buffer()`, and releases input buffers afterward.
- `lpfc_do_scr_ns_plogi()`, `lpfc_start_fdmi()`, `lpfc_cmpl_reg_new_vport()`, and `lpfc_register_new_vport()` continue discovery after fabric login by registering the VPI, issuing NameServer PLOGI/SCR, and optionally logging into FDMI.
- `lpfc_retry_pport_discovery()`, `lpfc_fabric_login_reqd()`, `lpfc_cmpl_els_fdisc()`, and `lpfc_issue_els_fdisc()` implement NPIV FDISC issue/completion and fallback to physical FLOGI when the fabric rejects FDISC with login-required.
- `lpfc_cmpl_els_npiv_logo()` and `lpfc_issue_els_npiv_logo()` send vport LOGO and wake deletion waiters waiting for LOGO completion.
- `lpfc_fabric_block_timeout()`, `lpfc_resume_fabric_iocbs()`, `lpfc_unblock_fabric_iocbs()`, `lpfc_block_fabric_iocbs()`, `lpfc_cmpl_fabric_iocb()`, and `lpfc_issue_fabric_iocb()` provide the single-outstanding fabric IOCB scheduler and 100 ms busy/backoff block.
- `lpfc_fabric_abort_vport()`, `lpfc_fabric_abort_nport()`, and `lpfc_fabric_abort_hba()` remove queued fabric IOCBs and complete them with local reject/SLI aborted status.
- `lpfc_sli4_vport_delete_els_xri_aborted()` and `lpfc_sli4_els_xri_aborted()` clean SLI4 aborted ELS SGL state, drop retained `ndlp` references, free SGLs back to the ELS list, and set RRQ active state when a remote RRQ is needed.
- `lpfc_sli_abts_recover_port()` starts rport recovery after failed BLS abort by clearing FCP-2 device state, setting `NLP_ISSUE_LOGO`, and unregistering the RPI.
- VMID helpers `lpfc_init_cs_ctl_bitmap()`, `lpfc_vmid_set_cs_ctl_range()`, `lpfc_vmid_put_cs_ctl()`, and `lpfc_vmid_get_cs_ctl()` maintain the local CS_CTL allocation bitmap. `lpfc_issue_els_qfpa()`/`lpfc_cmpl_els_qfpa()` query fabric priority ranges and populate `vport->vmid_priority`. `lpfc_vmid_uvem()`/`lpfc_cmpl_els_uvem()` instantiate or de-instantiate VMID virtual-entity mappings and set VMID in-use/registered flags.

Key data types in this chunk include `struct lpfc_vport`, `struct lpfc_hba`, `struct lpfc_nodelist`, `struct lpfc_iocbq`, `union lpfc_wqe128`, `LPFC_MBOXQ_t`, `struct lpfc_dmabuf`, `struct serv_parm`, `struct ls_rjt`, `struct RRQ`, `struct RLS_RSP`, `struct RTV_RSP`, `RPL_RSP`, `struct fc_els_fpin`, `struct fc_tlv_desc`, `struct fc_diag_cg_sig_desc`, `struct fc_fn_*_desc`, `struct lpfc_sglq`, `struct lpfc_vmid`, `struct lpfc_vmid_context`, `struct priority_range_desc`, and `struct instantiated_ve_desc`.

## Control Flow

The first visible path finishes `lpfc_els_handle_rscn()`. If a valid name-server node is present, the driver issues GID_FT or GID_PT CT queries according to `cfg_ns_query` and keeps the RSCN pending while requests complete. If the NameServer login is suspect or absent, it creates or reuses the NameServer `ndlp`, sets it to `NLP_STE_PLOGI_ISSUE`, marks it fabric, issues PLOGI, and waits for PLOGI completion before continuing. If no query or login work remains, it flushes the pending RSCN.

Unsolicited receive handling enters through `lpfc_els_unsol_event()`. The routine extracts status, command type, BDE count, and receive buffers from the SLI event. It handles `IOSTAT_NEED_BUFFER` and receive-buffer-waiting local rejects by replenishing HBQ/ring buffers. On SLI3 NPIV, it resolves the target vport from the IOCB VPI. For HBQ-enabled paths it reuses the provided buffer pointers; otherwise it looks up ring-posted buffers by DMA address. It then calls `lpfc_els_unsol_buffer()` and frees any input buffers the handlers did not consume.

`lpfc_els_unsol_buffer()` is the main command router. It drops malformed events, failed completions, events arriving during link attention, vport unloading, device-loss nodes, or delayed discovery where the command is not PLOGI. It creates an NPR `ndlp` for unknown DIDs, sets fabric node type for fabric DIDs, takes an IOCB-held node reference, logs the command, and rejects most commands before fabric configuration is far enough along. The switch statement then either drives the discovery state machine for login/discovery commands or calls direct handlers for auxiliary commands. New temporary nodes are removed after commands that do not retain them. When rejection is needed, it builds LS_RJT from `rjt_err`/`rjt_exp`; in the repeated point-to-point FLOGI inconsistency case it also bounces the link through `lpfc_init_link()`.

Point-to-point FLOGI is a special receive-side flow. `lpfc_els_rcv_flogi()` clears prior loopback state, rejects loop-mode FLOGI, checks service parameters, compares local and remote port names, and either detects loopback, chooses local/remote point-to-point DIDs, or marks that this port should initiate PLOGI. It temporarily makes `fc_myDID` look like `Fabric_DID` so the FLOGI ACC is addressed correctly. If the local HBA has not yet issued its own FLOGI, it stores RX/OX IDs and an `ndlp` reference in `phba->defer_flogi_acc`; otherwise it immediately sends the ACC and restores the DID.

RLS and RTV both gate on the remote node being mapped or unmapped. RLS is asynchronous: `lpfc_els_rcv_rls()` issues `MBX_READ_LNK_STAT` and `lpfc_els_rsp_rls_acc()` later builds the response from mailbox counters. RTV is synchronous to the receive path: it allocates an ACC IOCB, fills timeout values from the HBA, copies exchange identifiers from the request, and issues the response. RPL similarly parses the requested maximum size, chooses a one-port response size when possible, and returns local DID/port name. RRQ receive accepts and clears local RRQ state, while RRQ transmit is used later for SLI4 aborted exchanges.

FPIN and EDC flows parse variable-length TLV payloads defensively. EDC resets congestion capability defaults, walks each diagnostic descriptor, handles link-fault and congestion-signal descriptors, then sends an EDC ACC and calls `lpfc_config_cgn_signal()`. FPIN validates the header and descriptor length, walks each TLV, logs link-integrity, delivery, peer-congestion, and congestion descriptors, updates per-tag congestion stats, and delivers accepted descriptors one at a time to `fc_host_fpin_rcv()`. Congestion descriptors can be consumed by the driver without upper-layer delivery when CMF is active and the FPIN type/severity maps to driver-managed alarm or warning counters.

ELS timeout and flush control is split between timer posting and worker execution. `lpfc_els_timeout()` only sets `WORKER_ELS_TMO` and wakes the worker. `lpfc_els_timeout_handler()` scans `txcmplq` under HBA/ring locks, skips management and abort/close work, honors per-IOCB `drvrTimeout`, determines the remote DID, builds an abort list, and then issues aborts outside the scan. It issues an HBA heartbeat timeout check and re-arms the timer if outstanding completions remain. `lpfc_els_flush_cmd()` uses similar queue scanning during teardown, but also aborts queued fabric IOCBs, cancels pending `txq` entries, rewrites linkdown completion handlers to `lpfc_cmpl_els_link_down()`, and cancels instead of aborting when SLI is inactive or mailbox timeout error is set.

Vport discovery after fabric login proceeds through VPI registration and NameServer login. `lpfc_register_new_vport()` issues `REG_VPI` with an `ndlp` callback reference. `lpfc_cmpl_reg_new_vport()` clears the needs-register flag, handles known registration failures by failing the vport or retrying INIT_VPI/unregister/re-FLOGI/FDISC paths, and on success marks `LPFC_VPI_REGISTERED`. Physical ports continue with fabric reglogin or FDISC startup plus NameServer PLOGI; virtual ports go directly to NameServer PLOGI. `lpfc_do_scr_ns_plogi()` respects delayed discovery by arming `delayed_disc_tmo`, creates a NameServer node if needed, issues PLOGI, and optionally starts FDMI login.

FDISC issue and completion are serialized through the fabric IOCB scheduler. `lpfc_issue_els_fdisc()` sets the vport to `LPFC_FDISC`, zeros `fc_myDID`, builds FDISC service parameters from the physical port with fabric-specific fields adjusted, records optional PNI auxiliary data, and sends via `lpfc_issue_fabric_iocb()`. `lpfc_cmpl_els_fdisc()` resets discovery timers for all queued fabric IOCBs, handles fabric login-required by forcing physical-port rediscovery, retries eligible failures, activates the vport on success, stores assigned DID and fabric names, checks the clean-address bit, unregisters RPIs/VPI when DID or fabric parameters require re-registration, and then issues INIT_VPI, REG_VPI, or NameServer PLOGI.

Fabric IOCB scheduling maintains a single outstanding fabric command with `phba->fabric_iocb_count`. `lpfc_issue_fabric_iocb()` immediately issues if the count is zero and fabric commands are not blocked; otherwise it queues the IOCB on `fabric_iocb_list`. Completion restores the original callback, invokes it, decrements the count, and resumes the next queued command unless a busy/reject status caused `lpfc_block_fabric_iocbs()` to set `FABRIC_COMANDS_BLOCKED` and arm the 100 ms unblock timer. `lpfc_resume_fabric_iocbs()` is the queued-command issuer and retries the next queued item if issuing one fails locally.

The tail of the chunk handles SLI4 abort cleanup and VMID ELS. Aborted ELS SGLs are moved from `lpfc_abts_els_sgl_list` back to the free ELS SGL list, associated `ndlp` references are dropped, and RRQ active state is set for nodes that need exchange cleanup. If the abort refers to an active XRI instead of an ABTS-list entry, the active SGL is marked `SGL_XRI_ABORTED`. VMID QFPA sends a fabric query, stores fabric priority descriptors, converts fabric low/high ranges plus even/odd local VE ID semantics into CS_CTL ranges, and marks QFPA complete. UVEM builds VEM-ID and instantiated/de-instantiated VE descriptors, returns CS_CTL IDs to the bitmap on de-instantiation, and on successful completion marks VMID support in use and instantiated VMIDs registered.

## State and Persistence

The chunk mutates volatile driver, firmware, and FC transport state rather than persistent on-disk data:

- `vport->fc_flag`, `load_flag`, `port_state`, `fc_myDID`, `fc_prevDID`, `rcv_flogi_cnt`, `vpi_state`, `fabric_portname`, and `fabric_nodename` track discovery progress, topology, DID assignment, delayed discovery, unloading, and VPI registration.
- `phba->link_flag`, `hba_flag`, `fc_topology`, `fc_fabparam`, `fabric_iocb_list`, `fabric_iocb_count`, `bit_flags`, `fabric_block_timer`, `fc_stat`, congestion settings, and `defer_flogi_acc` retain HBA-wide ELS, topology, scheduler, and congestion state.
- `struct lpfc_nodelist` references are deliberately retained across asynchronous IOCB and mailbox completions by `lpfc_nlp_get()` and released in completion, flush, deferred-FLOGI, or abort-cleanup paths. State transitions use `lpfc_nlp_set_state()` and `lpfc_disc_state_machine()`.
- Outstanding ELS IOCBs live in ELS ring `txq`/`txcmplq` and fabric queue lists. Timeout/flush code may abort in-flight IOCBs, cancel queued IOCBs with local reject, or switch completion callbacks for linkdown cleanup.
- Mailbox context fields `ctx_ndlp`, `ctx_u.ox_rx_id`, `vport`, and `mbox_cmpl` persist request context for asynchronous RLS and VPI registration completions.
- Congestion state is kept in HBA counters and flags such as `cgn_reg_signal`, `cgn_sig_freq`, `cgn_reg_fpin`, `cgn_fpin_frequency`, `cgn_sync_alarm_cnt`, `cgn_sync_warn_cnt`, `cgn_fabric_alarm_cnt`, and `cgn_fabric_warn_cnt`. When `phba->cgn_i` exists, FPIN congestion updates write the shared `struct lpfc_cgn_info` area and refresh its CRC.
- SLI4 aborted ELS exchange state is represented by SGL queue membership, `sglq_entry->state`, retained `sglq_entry->ndlp`, and active RRQ records.
- VMID priority-tagging state persists in `vport->vmid_priority_range`, `vport->vmid_priority.vmid_range`, `num_descriptors`, `qfpa_res`, `lpfc_vmid_host_uuid`, and VMID flags such as `LPFC_VMID_QOS_ENABLED`, `LPFC_VMID_QFPA_CMPL`, `LPFC_VMID_IN_USE`, `LPFC_VMID_REGISTERED`, and `LPFC_VMID_REQ_REGISTER`.

There is no filesystem or disk persistence in this chunk. Hardware-visible side effects include ELS IOCBs, mailbox commands, VPI/RPI unregisters, link initialization, congestion signal configuration, and VMID/Fabric service ELS payloads.

## Dependencies and Integration Points

Kernel and subsystem integration points include:

- FC transport: `fc_host_post_vendor_event()`, `fc_get_event_number()`, `fc_host_fpin_rcv()`, FC vport states such as `FC_VPORT_ACTIVE`/`FC_VPORT_FAILED`, and FC FPIN/EDC TLV structures.
- Kernel timers and workers: `mod_timer()`, `jiffies`, `secs_to_jiffies()`, `msecs_to_jiffies()`, timer callbacks for ELS and fabric blocks, `work_port_events`, and `lpfc_worker_wake_up()`.
- Locking and reference primitives: HBA locks, ring locks, SGL list locks, host locks, node locks, VMID rwlocks, atomics, bit operations, and krefs.
- Memory and DMA-buffer helpers: mempools for mailboxes, ELS DMA buffers, HBQ/ring-post receive buffers, and `kzalloc_objs()`/`kmalloc_obj()` allocations for event and VMID structures.
- Byte-order and bitfield helpers: `cpu_to_be32()`, `be32_to_cpu()`, `cpu_to_le16()`, `cpu_to_le32()`, `be64_to_cpu()`, and `bf_get()`/`bf_set()` for WQE, RRQ, RTV, and VMID descriptor fields.
- SLI queue and IOCB APIs: `lpfc_sli_issue_iocb()`, `lpfc_sli_issue_mbox()`, `lpfc_sli_issue_abort_iotag()`, `lpfc_sli_cancel_iocbs()`, `lpfc_phba_elsring()`, `get_job_*()` accessors, WQE request tags, and SLI3/SLI4 command constants.
- Discovery and node management: `lpfc_findnode_did()`, `lpfc_nlp_init()`, `lpfc_nlp_get()`/`lpfc_nlp_put()`, `lpfc_nlp_set_state()`, `lpfc_disc_state_machine()`, `lpfc_check_nlp_post_devloss()`, `lpfc_unreg_rpi()`, `lpfc_cleanup_pending_mbox()`, `lpfc_sli4_unreg_all_rpis()`, `lpfc_mbx_unreg_vpi()`, `lpfc_issue_init_vfi()`, `lpfc_issue_reg_vfi()`, `lpfc_issue_init_vpi()`, and `lpfc_start_fdiscs()`.
- Fabric and CT integration: NameServer GID_FT/GID_PT, SCR PLOGI, FDMI PLOGI, RDF acceptance only from `Fabric_Cntl_DID`, fabric login registration, and fabric IOCB serialization.
- Congestion/CMF integration: EDC capability negotiation, `lpfc_least_capable_settings()`, `lpfc_config_cgn_signal()`, `lpfc_cgn_update_stat()`, and `lpfc_cgn_calc_crc32()`.
- VMID integration: VMID allocation initialized in `lpfc_init.c`, exported attributes in `lpfc_attr.c`, CT VMID registration in `lpfc_ct.c`, IO tagging in SCSI/NVMe paths, and `lpfc_is_vmid_enabled()`/`lpfc_reinit_vmid()`.

## Risks and Edge Cases

- `lpfc_els_rcv_flogi()` calls `lpfc_check_sparm()` but ignores its return value. If that helper can report invalid service parameters without side effects, the local comment promising LS_RJT on validation failure is not reflected in this implementation.
- Deferred FLOGI ACC handling stores RX/OX IDs and an `ndlp` reference in HBA-wide state. Any missed cleanup path can leak the node reference or send an ACC against stale point-to-point state; related cleanup exists outside this chunk.
- The point-to-point FLOGI loopback path differs by SLI revision: pre-SLI4 reinitializes the link and returns failure, while SLI4 marks `LS_EXTERNAL_LOOPBACK` and aborts FLOGI. Tests need both paths because discovery side effects are very different.
- Many ACC builders manually copy received RX/OX IDs into SLI3 IOCB or SLI4 WQE fields. A mismatch between request and response exchange fields would produce silent FC protocol failures.
- RLS mailbox completion frees the mailbox and drops the mailbox-held node reference before preparing/sending the ACC. Its reference ordering is subtle: the function later takes an IOCB completion reference and may call `lpfc_nlp_put(ndlp)` again on issue failure.
- `lpfc_els_unsol_buffer()` can replace `ndlp` after `lpfc_plogi_confirm_nport()`. Any assumptions about `newnode` after PLOGI confirmation require care because the current `ndlp` may no longer be the one initially created.
- New temporary nodes are removed in many but not all command cases. Deferred FLOGI deliberately retains the node, while other direct handlers often call device remove after responding. Adding new cases needs explicit new-node ownership decisions.
- The unsolicited dispatcher rejects most commands before `LPFC_FABRIC_CFG_LINK`, but permits point-to-point PLOGI under `FC_PT2PT`. Changes to discovery states or flags can easily cause valid P2P bring-up to be rejected as logical busy.
- FPIN delivery rewrites the received FPIN buffer to deliver each descriptor individually. The length arithmetic and in-place descriptor copy are fragile, especially for multi-descriptor payloads and unknown descriptor lengths.
- FPIN/EDC TLV loops depend on `FC_TLV_DESC_SZ_FROM_LENGTH(tlv)` being sane before advancing. The code checks truncation in several places, but malformed zero-length or inconsistent descriptors deserve fuzz-style coverage.
- Congestion FPIN handling suppresses upper-layer delivery when CMF consumes warning/alarm events. This is intentional, but it means tests should validate both driver-managed and transport-delivered paths.
- `lpfc_els_timeout_handler()` records `els_command` outside the later abort-list loop, so timeout log messages for multiple aborted IOCBs may not identify each IOCB's original ELS command precisely.
- `lpfc_els_flush_cmd()` has different behavior depending on SLI active state, mailbox timeout error, link state, and LIBDFC flag. It is a high-risk cleanup path for double completion, missed aborts, or leaked IOCBs if queue ownership changes.
- `lpfc_els_flush_all_cmd()` iterates vports under `port_list_lock` while `lpfc_els_flush_cmd()` performs substantial work and takes other locks. Lock ordering should be reviewed before changing this path.
- VPI registration completion handles many mailbox status codes and can reuse the same mailbox for INIT_VPI. Reference transfer to the new mailbox callback is easy to break if new cases are added.
- `lpfc_cmpl_els_fdisc()` walks all queued fabric IOCBs to reset discovery timers without taking a visible lock in this snippet. The surrounding completion context may serialize fabric access, but this list access is worth checking if fabric scheduling is modified.
- The comment on `lpfc_issue_fabric_iocb()` explicitly notes that a newly issued IOCB can jump ahead of already queued fabric IOCBs because readiness does not require an empty queue.
- Fabric IOCB completion calls the original completion before decrementing `fabric_iocb_count`. If the original callback indirectly depends on fabric scheduling state, this ordering matters.
- `lpfc_sli4_vport_delete_els_xri_aborted()` stores `ndlp = sglq_entry->ndlp`, clears the SGL node pointer, and then uses `ndlp->nlp_DID` in the unload/Fabric_DID check. The branch is guarded by the earlier non-NULL test, but future edits must preserve that invariant.
- `lpfc_sli4_els_xri_aborted()` frees SGL state and then uses `sglq_entry->sli4_lxritag` to set RRQ active. The entry is back on the free list at that point, so concurrency around SGL reuse must remain protected by existing worker/lock ordering.
- `lpfc_sli_abts_recover_port()` only recovers mapped nodes. Aborts against unmapped or NPR nodes are logged and ignored, so upper layers must tolerate no rport recovery in those states.
- VMID QFPA completion copies `len + 8` bytes from the response into `vport->qfpa_res` without a visible bound against the allocated `FCELSSIZE`-derived buffer or `MAX_PRIORITY_DESC`. Fabric responses with excessive descriptor lengths would be risky if not bounded by ELS receive size elsewhere.
- VMID CS_CTL bitmap helpers have edge cases: `lpfc_vmid_set_cs_ctl_range()` allows `max == LPFC_VMID_MAX_PRIORITY_RANGE`, which would attempt to set a bit at the nominal size limit; `lpfc_vmid_get_cs_ctl()` returns `0` both for "no bit available" and for allocated bit 0.
- Several VMID descriptor fields assign constants with `be32_to_cpu()` rather than `cpu_to_be32()`. This may match how the constants are defined, but byte-order assumptions should be verified before changing descriptor definitions.
- `lpfc_cmpl_els_uvem()` sets `ndlp = NULL` when the node is not unmapped and then calls `lpfc_nlp_put(ndlp)`. This depends on `lpfc_nlp_put()` being NULL-safe or the path avoiding invalid states; it is a sharp edge for maintenance.

## Test and Validation Signals

Good validation for this chunk should include protocol, teardown, and fault-injection coverage:

- Exercise unsolicited PLOGI, FLOGI, LOGO, PRLO, ADISC, PDISC, PRLI/NVMEPRLI, RSCN, RDP, LCB, RDF, RNID, ECHO, RLS, RTV, RPL, RRQ, FARP, FARPR, FAN, FPIN, EDC, and unsupported command paths. Confirm counters in `phba->fc_stat`, debug traces, ACC/LS_RJT responses, and state-machine events match expectations.
- Test point-to-point FLOGI with local WWPN greater than remote, less than remote, equal to remote on SLI3, and equal to remote on SLI4. Verify DID assignment, `FC_PT2PT`/`FC_PT2PT_PLOGI`, loopback flags, deferred ACC, and link reinitialization/abort behavior.
- Validate receive gating by injecting unsolicited ELS during link attention, vport unload, delayed discovery, node device-loss, early fabric state, and point-to-point discovery. Expected results are drop, logical-busy reject, or P2P exception handling according to command type.
- Fault-inject allocation and issue failures in RLS mailbox allocation/issue, RTV/RPL ACC IOCB allocation, RRQ issue, VPI registration, FDISC issue, NPIV LOGO issue, QFPA issue, and UVEM issue. Check node references and IOCBs are released exactly once.
- Exercise RLS mailbox completion with success and mailbox status failure. Verify link counters are big-endian in the ACC and mailbox/node references are released.
- Send valid and malformed FPIN/EDC payloads: short headers, descriptor lengths smaller than headers, truncated descriptors, unknown descriptors, multi-descriptor FPINs, congestion alarm/warning/clear/lost-credit/stall/oversubscription types, and peer-congestion WWPN lists larger than the logging cap.
- Confirm FPIN congestion side effects: CMF-off events are delivered upward, CMF-on warning/alarm events update sync/fabric counters and shared congestion info CRC, and driver-consumed descriptors are not delivered through `fc_host_fpin_rcv()`.
- Run ELS timeout tests with in-flight ELS_REQUEST, XMIT_ELS_RSP, GEN_REQUEST, FDISC, FARP/FARPR, LIBDFC, abort, and close commands. Confirm only eligible IOCBs are aborted and the timer re-arms while completions remain.
- Test `lpfc_els_flush_cmd()` during normal linkdown, vport delete, mailbox-timeout recovery, inactive SLI, and active LIBDFC management traffic. Validate abort versus cancel behavior and completion status `IOSTAT_LOCAL_REJECT/IOERR_SLI_ABORTED`.
- Verify vport discovery after successful FDISC, FDISC retryable failure, fabric login-required reject, changed DID/fabric parameters, SLI4 MAC-update re-registration, INIT_VPI-needed flow, and NameServer allocation failure.
- Exercise VPI registration mailbox statuses `0x11`, `0x9603`, `0x9602`, `0x20`, `MBX_NOT_FINISHED`, and success on physical and virtual ports. Check FC vport state, discovery timers, RPI/VPI unregisters, and VMID reinitialization.
- Stress fabric IOCB serialization with multiple queued FLOGI/FDISC/fabric commands, fabric busy, NPort busy, temporary unavailable reject, LS_RJT logical-busy/unable-to-perform, unblock timer expiry, issue failures in `lpfc_resume_fabric_iocbs()`, and abort by vport/nport/HBA.
- Validate SLI4 ELS XRI abort cleanup for ABTS-list entries with and without `ndlp`, active-XRI entries, unknown XRIs, vport unloading of Fabric_DID SGLs, and pending `txq` wakeup.
- Trigger ABTS rport recovery for mapped and unmapped nodes. Confirm mapped nodes clear FCP-2, set `NLP_ISSUE_LOGO`, unregister RPI, and later relogin; unmapped nodes should only log no recovery needed.
- Test VMID QFPA success, LS_RJT, transport error, missing response buffer, allocation failure, out-of-range descriptor ranges, even-only/odd-only/even-odd local VE ID mapping, and QoS-enabled descriptors. Check `vmid_priority_range` bitmap and `LPFC_VMID_QFPA_CMPL`.
- Test UVEM instantiate and de-instantiate success and failure. Confirm host UUID initialization, CS_CTL return on de-instantiate, `LPFC_VMID_IN_USE`, `LPFC_VMID_REGISTERED`, and `LPFC_VMID_REQ_REGISTER` transitions under `vmid_lock`.
