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
