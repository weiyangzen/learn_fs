# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSNetworkProviderSupport.cpp

## Purpose
`AFSNetworkProviderSupport.cpp` maintains the redirector's provider enumeration list exposed to network-provider style queries. It inserts server/share/directory connection records and classifies them for Windows network resource enumeration.

## Important APIs, Control Flow, And State
`AFSAddConnectionEx` locks `ProviderListLock`, chooses the top-level provider list for server entries or the first server's child list for shares/directories, checks for duplicate `RemoteName` case-insensitively, strips a trailing slash in place, allocates an `AFSProviderConnectionCB` with inline remote-name storage, derives `ComponentName` by walking backward to the final path separator, calls `AFSInitializeConnectionInfo`, stores caller flags, and appends to either `ProviderEnumerationList` or the server's `EnumerationList`.

`AFSInitializeConnectionInfo` dissects the UNC-like name. Server-level entries are `RESOURCEDISPLAYTYPE_SERVER`, `RESOURCE_GLOBALNET`, and `RESOURCEUSAGE_CONTAINER` with comment `AFS Root`. Share-level entries are connectable disk shares, optionally attached if `LocalName` is set, with comment `AFS Share`. Deeper entries are connected directory resources with comment `AFS Directory`.

## Dependencies And Integration Points
The library receives `AFSAddConnectionEx` as a callback during `AFSInitializeLibrary`, so service/library discovery of cells/shares feeds this provider list. The data structure is stored in the RDR device extension and uses constants from `AFSDefines.h` mirroring Windows `NETRESOURCE` fields. It depends on `FsRtlDissectName`, pool wrappers, and the provider structures from shared headers.

## Risks And Test Signals
`AFSAddConnectionEx` mutates the caller's `RemoteName` buffer when removing a trailing slash, which is risky if the buffer is immutable or reused. Non-server insertions assume a single server at `ProviderEnumerationList`; multiple server support would need more precise parent selection. Comment buffers are allocated separately and are not freed here. Tests should cover duplicate insertions, trailing slash names, server before share ordering, share insertion without server, case-insensitive matching, component derivation, and cleanup by whatever tears down provider entries.
