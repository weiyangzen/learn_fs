# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeMsg.h

## Research
`FLockRangeMsg.h` declares the outgoing byte-range lock message. It stores client numeric ID, non-owned file handle, non-owned `EntryInfo`, owner PID, lock type flags, `uint64_t start` and `end`, and non-owned lock ack ID. The inline initializer computes string lengths and records all range/lock fields.

Control flow is construction plus serialization in the `.c` file. State is non-owning for pointers, fixed-size for range and lock fields. Dependencies are `NetMessage.h` and `EntryInfo.h`. Integration points are fcntl range-lock handling and asynchronous lock-grant tracking. Risks are invalid ranges, mismatch with Linux `file_lock` semantics, string lifetime, and wrong ack ID association. Test signals are byte-range lock/unlock operations across clients and delayed grant wakeups.
