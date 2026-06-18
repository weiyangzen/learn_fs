# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionMsg.c

## Research
`GetFileVersionMsg.c` implements outgoing serialization for querying a file version. The payload is just serialized `EntryInfo`; deserialization is dummy because the client sends this request and expects `GetFileVersionRespMsg`.

Control flow is one serializer call through `EntryInfo_serialize`. State is a non-owned `EntryInfo` pointer in the message. Dependencies are `GetFileVersionMsg.h` and storage entry serialization. Integration points are cache invalidation/version checking code that asks metadata for the current file version. Risks are dangling entry info, no sequence-number support, and relying on server-side result/version pairing. Test signals are serialized entry info matching target file and response version updating caller state.
