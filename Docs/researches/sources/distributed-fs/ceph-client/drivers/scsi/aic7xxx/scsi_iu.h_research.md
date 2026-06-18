# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/scsi_iu.h

Purpose: defines SCSI information-unit status header layout and constants for packetized SCSI status, sense data, packet-failure codes, and task-management flags.

Important APIs/types/functions: `struct scsi_status_iu_header` models a status IU with flags, status, sense length, packet-failure length, and variable packet-failure data. `SIU_PKTFAIL_CODE()` uses `scsi_4btoul()` to decode packet failure codes. `SIU_SENSE_OFFSET()` calculates sense-data offset depending on `SIU_RSPVALID`. Constants define packet-failure reasons and task-management function bits.

Control flow: no functions beyond macros. Consumers inspect IU flags, compute offsets, and branch on task-management or packet-failure values.

State and persistence: no state; this is a wire-format contract.

Dependencies and integration: depends on `u_int8_t` and `scsi_4btoul()` from the aic support headers. Used by packetized SCSI handling in aic7xxx/aic79xx code.

Risks and test signals: variable-length IU parsing is bounds-sensitive; callers must ensure buffers contain the advertised packet-failure and sense lengths before using the offsets. Tests should include status IUs with response data absent/present, malformed lengths, packet-failure codes, and task-management responses.
