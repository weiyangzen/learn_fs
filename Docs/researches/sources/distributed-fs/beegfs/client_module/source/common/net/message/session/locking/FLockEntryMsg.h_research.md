# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryMsg.h

## Research
`FLockEntryMsg.h` declares the outgoing whole-entry lock message. It embeds `NetMessage` and stores client numeric ID, non-owned file handle, non-owned `EntryInfo`, client-wide FD ID, owner PID, lock type flags, and non-owned lock ack ID. The inline session initializer sets lengths and scalar fields.

Control flow is construction plus serialization in the `.c` file. State is non-owning and not persisted in the message. Dependencies are `NetMessage.h` and `EntryInfo.h`. Integration points are distributed file locking and lock-grant acknowledgment handling. Risks are non-owned lifetime, ambiguous `clientFD` identity, incorrect lock flags, and empty/stale ack IDs. Test signals are entry lock request/response flows, delayed grant delivery, and sequence-number retry correctness.
