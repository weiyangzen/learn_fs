# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendRespMsg.h

## Research
`FLockAppendRespMsg.h` defines append-lock responses as a receive-only `SimpleIntMsg` wrapper using `NETMSGTYPE_FLockAppendResp`. The integer represents a storage/metadata result code, with `StorageErrors.h` included for the expected status domain.

Control flow is inline initialization only; deserialization is inherited from `SimpleIntMsg`. State is one integer payload. Dependencies are `SimpleIntMsg.h` and `StorageErrors.h`. Integration points are append-lock request callers that decide whether the lock was granted immediately, denied, or will arrive asynchronously. Risks are no typed accessor/conversion in this header and semantic mismatch if status values change. Test signals are lock response parsing and correct waiting behavior for delayed grants.
