# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_disc.h

## Purpose
`lpfc_disc.h` defines LPFC discovery-layer data structures, node state constants, node flags, worker event types, and Fibre Channel/NVMe role metadata. It is the shared contract for representing remote NPorts, discovery state-machine inputs, delayed recovery work, target/initiator roles, registration state with SCSI/NVMe transports, and outstanding RRQ/XRI tracking.

## Important APIs, Types, And Constants
- Discovery limits: `FC_MAX_HOLD_RSCN`, `FC_MAX_NS_RSP`, `FC_MAXLOOP`, and `LPFC_DISC_FLOGI_TMO` bound RSCN deferral, NameServer response size, loop device count, and FLOGI timeout behavior.
- `enum lpfc_work_type` lists asynchronous work events such as online/offline transitions, warm start, kill, ELS retry, devloss, fast-path management events, HBA reset, and port recovery.
- `struct lpfc_work_evt` is the generic queued work item with list linkage, two opaque arguments, and event type.
- `struct lpfc_fast_path_event` wraps `lpfc_work_evt`, a vport pointer, and a union of SCSI/fabric/read-check event payloads for events raised from fast path code.
- `struct lpfc_node_rrqs` and `struct lpfc_node_rrq` support RRQ/XRI tracking. The bitmap form tracks active XRIs per node for SLI4; the list form records xritag, rxid, DID, vport, and stop time for individual RRQ handling.
- `struct lpfc_enc_info` records encryption status and CNSA level for a node session.
- `enum lpfc_fc4_xpt_flags` tracks whether the node is registered with LPFC, SCSI, and NVMe transport layers and whether NVMe unregister is waiting.
- `enum lpfc_nlp_save_flags` names conditions that keep a node alive across devloss/recovery, pending LOGO, or pending DA_ID.
- `struct lpfc_nodelist` is the central node object: list membership, service parameters, WWPN/WWNN, per-node spinlock, FC ID, last ELS command, role/type flags, FC4 capabilities, RPI/XRI/SID, retry and class info, NVMe NSLER/first-burst fields, encryption info, timers, owning HBA/vport, SCSI and NVMe transport rports, work events, kref, command depth, active RRQ bitmap, PRLI tracking, save flags, and NPIV wait queues.
- Node role/type masks include `NLP_FC_NODE`, `NLP_FABRIC`, `NLP_FCP_TARGET`, `NLP_FCP_INITIATOR`, `NLP_NVME_TARGET`, `NLP_NVME_INITIATOR`, and `NLP_NVME_DISCOVERY`.
- FC4 type masks include `NLP_FC4_NONE`, `NLP_FC4_FCP`, and `NLP_FC4_NVME`.
- `enum lpfc_nlp_flag` defines bit numbers for protocol and lifecycle flags such as sent PLOGI/PRLI/ADISC/LOGO, received PLOGI, unregister in progress, dropped initial ref, delay timer active, devloss in progress, deferred removal, target authentication required, FirstBurst support, and valid RPI.
- Node states `NLP_STE_*` define the discovery state machine from unused through PLOGI/ADISC/REG_LOGIN/PRLI/LOGO issue, unmapped, mapped, NPR, and freed.
- Node events `NLP_EVT_*` enumerate received ELS requests, ELS completions, REG_LOGIN completion, device removal, and device recovery.
- `lpfc_ndlp_check_qdepth(phba, ndlp)` checks node command depth against SLI4 maximum configured XRI.

## Control Flow And State Model
The comments describe the discovery state machine. Nodes can reside on PLOGI, ADISC, unmapped, mapped, and binding-related lists. Link up and RSCN processing move nodes from mapped/unmapped lists into ADISC or PLOGI processing lists, issue batches of ELS commands, and feed completions/events through the state machine. Successful Fibre Channel login moves nodes to the unmapped list; PRLI and binding assignment can move FCP targets to mapped. Link down sends recovery/removal events to nodes on active lists; devloss expiry ultimately removes nodes.

`struct lpfc_nodelist` is both a protocol state object and an integration object. It stores current and previous node state, transport registration flags, outstanding command accounting, timers, deferred work items, saved keepalive conditions, and references to transport remote-port objects. Fast-path and recovery code can queue `lpfc_work_evt` entries using the event enum, while discovery code uses `NLP_EVT_*` inputs to transition `nlp_state`.

## State And Persistence Behavior
All state is in-memory driver state associated with an HBA/vport and remote port discovery lifetime. `kref` controls object lifetime, `nlp_delayfunc` supports delayed ELS actions, and `save_flags` protects nodes from premature free under recovery-sensitive operations. `cmd_pending` and `cmd_qdepth` provide live I/O pressure state. The active RRQ bitmap and RRQ list fields track outstanding exchanges that require cleanup. No persistent storage is defined by this header.

## Dependencies And Integration Points
- Depends on kernel list, spinlock, timer, waitqueue, kref, atomic, bitmap, and bit definitions.
- Integrates with Fibre Channel service parameters (`struct serv_parm`), LPFC WWN types (`struct lpfc_name`), HBA/vport structures, SCSI transport `struct fc_rport`, and LPFC NVMe transport `struct lpfc_nvme_rport`.
- Used by debug and observability code such as `lpfc_debugfs_nodelist_data()` to render node state, role flags, transport flags, encryption state, command depth, and deferred DID.
- Defines events and states consumed by discovery, ELS, RSCN, devloss, NPIV, SCSI, and NVMe integration code across the LPFC driver.

## Risks And Edge Cases
- `nlp_flag` is an `unsigned long` bitset using enum bit positions; flag updates must use atomic bit operations or hold the proper node lock where required.
- Node lifetime is subtle because timers, queued work, SCSI rports, NVMe rports, devloss, LOGO, DA_ID, and discovery lists can all retain or refer to the same object.
- The discovery state machine comments are the primary local description of legal transitions; inconsistent transitions can leave nodes on wrong lists or registered with a transport after removal.
- `lpfc_ndlp_check_qdepth()` assumes SLI4 `max_cfg_param.max_xri` is valid for the HBA; callers in non-SLI4 paths need care.
- `LPFC_SLI4_MAX_XRI` fixes the node bitmap to 1024 XRIs, so adapters or firmware configurations exceeding that assumption would require structural changes.
- The union in `lpfc_fast_path_event` relies on forward-declared event payloads being complete before actual allocation/use in translation units that include this header.

## Test Signals
- Discovery tests should cover link up, RSCN, link down, devloss expiry, PLOGI/ADISC/PRLI/LOGO completions, and device recovery/removal events.
- Transport integration tests should verify SCSI/NVMe rport registration and unregister flags are consistent with `nlp_state`, `nlp_type`, and `fc4_xpt_flags`.
- Lifetime tests should stress delayed ELS timers, queued `els_retry_evt`, `dev_loss_evt`, `recovery_evt`, NPIV wait queues, and kref release ordering.
- Debugfs nodelist output is a useful manual signal because it exposes state names, DID/WWNs, RPI, type flags, encryption status, reference count, outstanding I/O, transport flags, and deferred DID.
