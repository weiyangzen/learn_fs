# sources/distributed-fs/beegfs/meta/source/storage/Locking.h

## Purpose

`Locking.h` defines the data structures used by `FileInode` to implement append locks, whole-file flock locks, and byte-range locks. It encodes request identity, conflict semantics, waiter queue containers, range overlap logic, and ordering comparators for current lock sets.

## Important APIs and Types

`LockEntryNotifyType` identifies append versus flock notifications. `RangeOverlapType` classifies range relationships. `EntryLockDetails` identifies whole-file locks by client node ID and client FD, includes owner PID and ack ID, serializes all fields, exposes type predicates, converts lock type to unlock, compares handles, formats diagnostic strings, and orders map/set entries by FD then client ID.

`EntryLockQueuesContainer` bundles pointers to current exclusive lock, current shared locks, exclusive/shared waiter queues, duplicate waiter ack IDs, and notify type. `AppendLockQueuesContainer` specializes it for append locks with dummy shared queues.

`RangeLockDetails` identifies range locks by client node ID and owner PID, includes ack ID, type flags, inclusive start/end offsets, and exposes handle equality, mergeability, overlap classification, trimming, splitting, merging, string formatting, and two comparators. Shared range locks are ordered by owner/client/start; exclusive range locks are ordered by start under the invariant that exclusive locks do not overlap.

## Control Flow and State

These structures are mostly value types consumed by `FileInode` lock queues. Entry locks intentionally use FD-level identity so one process can block itself through different file descriptors. Range locks intentionally use process-level identity so a process does not block itself through different descriptors. Waiter duplicate suppression is done by lock ack ID sets.

## Persistence and Dependencies

All lock detail types have serializer functions and are serialized through `FileInode::LockState`. The header depends on common lock flag definitions, node IDs, and standard containers.

## Integration Points

`FileInode` owns sets/lists of these structures and calls conflict/unlock/try-next-waiter algorithms against them. `LockingNotifier` consumes notify lists generated from successful waiter promotion.

## Risks and Test Signals

Range arithmetic uses inclusive ends and `+1` in mergeability, so max-uint64 ranges can overflow if not guarded by callers. The exclusive comparator only orders by start and relies on no overlaps, making conflict checks critical. Tests should cover entry handle equality, range overlap classes, trim/split/merge boundaries, duplicate ack IDs, NOWAIT behavior, and serialization round trips.
