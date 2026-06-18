# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeRespMsg.h

## Research
`FLockRangeRespMsg.h` defines byte-range lock responses as a `SimpleIntMsg` wrapper with type `NETMSGTYPE_FLockRangeResp`. It is intended for incoming/deserialized responses and includes `StorageErrors.h` for status interpretation.

Control flow is inline initialization only. State is one integer payload. Dependencies are `SimpleIntMsg.h` and `StorageErrors.h`. Integration points are range-lock callers that decide whether to proceed, fail, or wait for a `LockGrantedMsgEx`. Risks are semantic ambiguity of the integer and no local validation of status domains. Test signals are range-lock response handling and correct behavior for immediate and delayed grants.
