# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileMsg.c

## Research
`FSyncLocalFileMsg.c` implements outgoing serialization for storage-server fsync requests. The payload contains client numeric ID, aligned file handle ID string, and target ID. The ops use dummy deserialization and default processing.

Control flow is fixed wire-order serialization. State is set by `FSyncLocalFileMsg_initFromSession`: non-owned file handle string plus scalar client/target IDs. Dependencies are `FSyncLocalFileMsg.h`, `NumNodeID`, and serialization helpers. Integration points are close/fsync/session code paths that ask storage targets to flush a local chunk file. Header feature flags in the `.h` support no-sync, session-check, and buddy-mirror target semantics. Risks include target ID meaning target versus buddy group based on flags, file handle lifetime, and absent sequence-number support here compared with open/close/lock messages. Test signals are fsync request serialization, response value via `FSyncLocalFileRespMsg`, and correct flag handling in callers.
