# sources/distributed-fs/beegfs/common/source/common/storage/StorageTargetInfo.h

## Purpose
Defines a serializable snapshot of a storage target's path, space, inode counts, and consistency state.

## Important APIs, Types, And Functions
Constructors, `statStoragePath()`, getters, comparison/equality operators, serialization, and `StorageTargetInfoList` typedefs are exported. List serialization is marked as not having embedded item lengths.

## Control Flow
Serialization writes target ID, aligned path string, disk space totals/free, inode totals/free, and consistency state as `uint8_t`.

## State, Persistence, And Dependencies
State is target ID, path, disk/inode counters, and `TargetConsistencyState`. Depends on `Node`, `TargetStateInfo`, `StorageErrors`, and serialization.

## Integration Points
Used by storage target reporting, capacity pool updates, management tools, and stat-storage-path messages.

## Risks
`getPathStr()` returns by value, not reference. Ordering compares only target ID, while equality compares all fields.

## Test Signals
Serialization golden data, equality/order differences, consistency state width, and stat RPC integration.
