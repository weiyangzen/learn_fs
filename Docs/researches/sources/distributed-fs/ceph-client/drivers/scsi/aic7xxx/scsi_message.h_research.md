# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/scsi_message.h

Purpose: public-domain SCSI parallel interface message constant header used by aic7xxx/aic79xx negotiation and message-in/message-out handling.

Important APIs/types/functions: defines one-byte messages such as save/restore data pointer, disconnect, reject, and noop; two-byte tagged queue and wide-residue messages; identify-message helpers `MSG_IDENTIFY()`, `MSG_ISIDENTIFY()`, and `MSG_IDENTIFY_LUNMASK`; and extended message lengths/option bits for SDTR, WDTR, and PPR negotiation.

Control flow: no executable code. Macros encode and decode message bytes in protocol state machines.

State and persistence: no mutable state; constants reflect SCSI bus protocol values.

Dependencies and integration: consumed by low-level aic SCSI message negotiation code and sequencer interaction paths.

Risks and test signals: incorrect constants directly break SCSI negotiation. `MSG_IDENTIFY(lun, disc)` assumes the caller masks or bounds LUN values appropriately. Protocol tests should cover identify messages, tagged queue messages, sync/wide/PPR negotiation combinations, message reject fallback, and legacy devices that do not support optional features.
