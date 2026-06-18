# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeMsg.c

## Research
`FLockRangeMsg.c` serializes outgoing byte-range lock requests. The payload contains client numeric ID, start offset, end offset, owner PID, lock type flags, entry info, aligned file handle ID, and aligned lock ack ID. The ops support sequence numbers and use dummy deserialization.

Control flow is fixed serialization. State is non-owned file/entry/ack data plus scalar range and lock metadata. Dependencies are `FLockRangeMsg.h`, `EntryInfo`, `NumNodeID`, and serialization helpers. Integration points are distributed POSIX byte-range locking. Risks include inclusive/exclusive range interpretation, start/end overflow or invalid ordering, non-owned lifetimes, ack ID matching, and retry semantics for lock operations. Test signals are range lock requests for shared/exclusive/unlock flags, server responses, and delayed lock grant acknowledgements.
