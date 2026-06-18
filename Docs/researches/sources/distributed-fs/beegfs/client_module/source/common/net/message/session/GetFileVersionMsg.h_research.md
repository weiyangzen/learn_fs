# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionMsg.h

## Research
`GetFileVersionMsg.h` declares an outgoing metadata request to fetch a file version. It embeds `NetMessage`, stores a non-owned `EntryInfo` pointer, and initializes `NETMSGTYPE_GetFileVersion` with the shared ops.

Control flow is inline construction, with payload serialization in the `.c` file. State is non-owning and has no release hook. Dependencies are `NetMessage.h` and `EntryInfo.h`. Integration points are file-version/cache-coherency logic and metadata request handling. Risks are using an `EntryInfo` whose lifetime ends before serialization and no local validation of entry type. Test signals are metadata response version values and error propagation through `GetFileVersionRespMsg`.
