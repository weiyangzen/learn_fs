# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryMsg.c

## Research
`FLockEntryMsg.c` serializes outgoing whole-entry lock requests. Payload order is client numeric ID, client-wide FD identity, owner PID, lock type flags, entry info, aligned file handle ID, and aligned lock ack ID. The ops mark the message as supporting sequence numbers and use dummy deserialization.

Control flow is fixed field serialization. State is non-owned entry/file/ack strings and scalar lock metadata. Dependencies are `FLockEntryMsg.h`, `EntryInfo`, `NumNodeID`, and serialization. Integration points are global flock/fcntl entry-lock paths where retries and sequence numbers help avoid duplicate or reordered operations. Risks include retry semantics, stale non-owned pointers, lock type flag correctness, and asynchronous grant ack ID coordination. Test signals are lock acquisition/release request serialization, delayed lock grants, and sequence-number behavior under retry.
