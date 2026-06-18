# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendMsg.h

## Research
`FLockAppendMsg.h` declares the outgoing append-lock request. It embeds `NetMessage` and stores client ID, non-owned file handle, non-owned entry info, client-wide FD identity, owner PID, lock type flags, and non-owned lock ack ID. The inline session initializer fills all fields and computes string lengths.

Control flow is construction and later serialization. State is non-owning for pointers, fixed-size for lock metadata. Dependencies are `NetMessage.h` and `EntryInfo.h`. Integration points are append locking and asynchronous lock-grant acknowledgement machinery. Risks are stale file handle/entry info, wrong lock type flags, empty ack IDs preventing waiters from waking, and no local validation of range/append semantics. Test signals are append lock request/response behavior and `LockGrantedMsgEx` matching the lockAckID.
