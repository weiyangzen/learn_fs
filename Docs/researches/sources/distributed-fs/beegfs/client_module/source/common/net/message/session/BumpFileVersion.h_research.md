# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersion.h

## Research
`BumpFileVersion.h` declares the outgoing `BumpFileVersionMsg`. It defines feature flags for persistent file-version changes and optional file-event logging, embeds `NetMessage`, and stores non-owned `EntryInfo` and optional `FileEvent` pointers. The inline initializer sets `NETMSGTYPE_BumpFileVersion`, stores pointers, and sets feature flags according to `persistent` and event presence.

Control flow is construction and flag setup; serialization is in the `.c` file. State is non-owning and no release hook exists. Dependencies are `NetMessage.h`, `EntryInfo.h`, and `FileEvent.h`. Integration points are metadata operations that need to bump file version counters for cache invalidation and event logging. Risks are dangling pointers, forgetting the event flag when event data is present, and persistent version semantics under retries. Test signals are feature flags matching payload layout and server response values.
