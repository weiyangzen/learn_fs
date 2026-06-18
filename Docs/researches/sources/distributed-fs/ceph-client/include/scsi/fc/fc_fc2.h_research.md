# sources/distributed-fs/ceph-client/include/scsi/fc/fc_fc2.h

Purpose: Defines FC-2 exchange and sequence status wire structures and status flags.

Important APIs/types/functions: `struct fc_ssb` models the packed Sequence Status Block with sequence ID, count range, status flags, error count, frame header CS_CTL/OX_ID, and RX_ID. `struct fc_esb` models the Exchange Status Block with exchange IDs, fabric IDs, exchange status, service params, and sequence status array. Macros define expected sizes and bit flags such as responder, active, abnormal, retransmission, timeout, and error policy.

Control flow and state: No runtime logic is present; these are packed protocol records consumed by FC exchange recovery and diagnostics.

Dependencies and integration: Used by libfc exchange manager, REC/SRR recovery, and FC-FS protocol code.

Risks and test signals: Risks include packed layout mismatches, endian conversion mistakes, and incorrect status-bit interpretation during recovery. Tests should assert `FC_SSB_SIZE`/`FC_ESB_SIZE`, parse known SSB/ESB samples, and exercise exchange recovery state decisions.
