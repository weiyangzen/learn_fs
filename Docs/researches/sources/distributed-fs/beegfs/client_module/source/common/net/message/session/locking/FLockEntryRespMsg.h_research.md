# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryRespMsg.h

## Research
`FLockEntryRespMsg.h` defines whole-entry lock responses as a `SimpleIntMsg` wrapper with type `NETMSGTYPE_FLockEntryResp`. It is receive-oriented, and the integer value is expected to map to storage error/result codes.

Control flow is inline initialization; inherited simple-int ops handle payload. State is one integer result. Dependencies are `SimpleIntMsg.h` and `StorageErrors.h`. Integration points are entry-lock callers and lock wait logic. Risks are lack of typed result accessor and relying on higher layers to interpret wait/grant/error codes. Test signals are immediate lock responses and delayed-grant paths being distinguished correctly.
