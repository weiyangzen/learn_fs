# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileRespMsg.h

## Research
`FSyncLocalFileRespMsg.h` defines fsync-local-file responses as `SimpleInt64Msg` with type `NETMSGTYPE_FSyncLocalFileResp`. `FSyncLocalFileRespMsg_getValue` exposes the 64-bit response value, which can represent a result/status domain chosen by the storage protocol.

Control flow is inline init and accessor only. State is one int64 payload. Dependencies are `SimpleInt64Msg.h`. Integration points are fsync request paths that need storage-server completion status. Risks include ambiguous signed 64-bit semantics and no typed conversion to `FhgfsOpsErr` in this wrapper. Test signals are response parsing for successful and failed storage fsync operations.
