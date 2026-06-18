# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileMsg.h

## Research
`FSyncLocalFileMsg.h` declares the outgoing fsync-local-file storage message. It defines flags for no-sync, session checking, buddy-mirror group target IDs, and secondary selection. The struct embeds `NetMessage`, stores `NumNodeID clientNumID`, non-owned file handle ID pointer/length, and target ID. The inline session initializer fills these fields with `NETMSGTYPE_FSyncLocalFile`.

Control flow is construction plus serialization in the `.c` file. State is non-owning for the file handle and fixed-size otherwise. Dependencies are `NetMessage.h`. Integration points are storage session synchronization and mirrored target flush handling. Risks are flag/target mismatch, using stale file handles, and no local validation of target ID. Test signals are correct payload layout and server responses for normal, no-sync, session-check, and buddy-mirror cases.
