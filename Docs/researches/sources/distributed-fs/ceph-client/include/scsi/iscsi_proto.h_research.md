# sources/distributed-fs/ceph-client/include/scsi/iscsi_proto.h

Purpose: Defines RFC 3720 iSCSI wire protocol constants, serial-number arithmetic, 24-bit length helpers, initiator tag helpers, and all fixed 48-byte PDU header structures.

Important APIs/types/functions: Structures cover generic headers, AHS headers, SCSI command/response, async events, NOP, task management, R2T, data out/in, text, login, logout, SNACK, and reject PDUs. Macros define opcodes, flags, status codes, login stages/status, logout reasons/responses, SNACK types, reject reasons, limits for text key/value pairs, default negotiated lengths, and iSCSI name length. Inline helpers implement RFC1982 serial comparisons and ITT build/extract.

Control flow and state: This is a protocol contract used by initiator and target code to parse and construct PDUs. Command sequencing relies on CmdSN/StatSN/DataSN serial arithmetic; login progresses through security negotiation, operational parameter negotiation, and full feature phase; data movement uses R2T/DataSN/offset fields and residual flags.

Dependencies and integration: Depends on Linux types and SCSI LUN/CDB definitions. Used by `iscsi_if.h`, libiscsi, iscsi_tcp, offload transports, and target implementations.

Risks and test signals: Risks include endian and 24-bit length mistakes, PDU struct size drift, incorrect serial arithmetic at wrap, invalid login stage transitions, and malformed AHS handling. Tests should include PDU size/layout assertions, encode/decode golden vectors, CmdSN/StatSN wrap tests, login negotiation, reject handling, and fuzzed PDU headers.
