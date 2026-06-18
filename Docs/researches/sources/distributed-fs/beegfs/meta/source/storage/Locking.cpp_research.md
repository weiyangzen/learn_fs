# sources/distributed-fs/beegfs/meta/source/storage/Locking.cpp

## Purpose

`Locking.cpp` implements equality and randomized test initialization for file lock detail structures declared in `Locking.h`. The actual lock algorithms live in `FileInode`; this file provides value semantics and test support for serialized lock state.

## Important APIs and Functions

`EntryLockDetails::operator==` compares client node ID, client file descriptor, owner PID, lock ack ID, and lock type flags. `RangeLockDetails::operator==` compares client node ID, owner PID, lock ack ID, lock type flags, and inclusive start/end range. `initRandomForSerializationTests` for both structures fills fields with random IDs, flags, ranges, and alphanumeric ack IDs.

## Control Flow and State

The implementation is straight-line. Random initialization uses `Random` and `StringTk::genRandomAlphaNumericString`. It does not validate that generated range start is less than or equal to end, because serialization tests only need nonconstant field coverage.

## Persistence and Dependencies

The file depends on serialization headers, `Random`, `StringTk`, and `Locking.h`. It has no persistence of its own, but these structures are serialized as part of file inode lock state.

## Integration Points

`FileInode::LockState` serializes `EntryLockDetails` and `RangeLockDetails` collections. Unit tests use random initialization to validate serialization/deserialization paths.

## Risks and Test Signals

Equality must stay aligned with serialized fields. If new fields are added to lock detail structs, both serialization and equality/test initialization need updates. Tests should assert round-trip equality for entry and range locks and include edge ranges and empty ack IDs in addition to random values.
