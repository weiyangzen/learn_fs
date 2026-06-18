# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendMsg.c

## Research
`FLockAppendMsg.c` implements outgoing serialization for append-lock requests. The payload contains client numeric ID, client-wide file descriptor ID, owner PID, lock type flags, serialized `EntryInfo`, aligned file handle ID, and aligned lock ack ID. Deserialization is dummy.

Control flow is fixed field order. State is non-owned `EntryInfo`, file handle, and lock ack ID, plus scalar lock identity fields. Dependencies are `FLockAppendMsg.h`, `EntryInfo`, `NumNodeID`, and serialization helpers. Integration points are global append-lock code paths that coordinate append serialization across clients/storage. Risks include non-owned pointer lifetime, owner PID being informative only and shared across fork, lockAckID correctness for asynchronous lock grants, and lack of sequence-number support unlike entry/range locks. Test signals are server lock response handling, lock grant ack wakeups, and correct serialization of aligned strings.
