<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/nodes/MetaNodeOpStats.h -->
# sources/distributed-fs/beegfs/meta/source/nodes/MetaNodeOpStats.h

## Purpose
Defines metadata operation accounting by client IP and user ID for metadata-server filesystem operations.

## Important APIs, Types, and Functions
`MetaNodeOpStats` derives from `NodeOpStats` and exposes `updateNodeOp(const IPAddress&, MetaOpCounterTypes, unsigned)`. It takes a read lock, looks up counters by 128-bit client IP and user ID, upgrades to a write lock when either key is absent, inserts `MetaOpCounter` instances as needed, then increments both counters.

## Control Flow, State, and Persistence
State lives in inherited `clientCounterMap` and `userCounterMap`; no disk persistence happens here. The function intentionally allows a race between read unlock and write lock because duplicate insertion is a no-op via map insert semantics. Counters are updated while the lock is held.

## Dependencies and Integration Points
Depends on `NodeOpStats`, `MetaOpCounter`, `SafeRWLock`, `Node`, `IPAddress`, and `MetaOpCounterTypes`. Called by message handlers such as unlink, listdir, find-owner, lookup-intent, and rename.

## Risks and Test Signals
The read-to-write upgrade path uses iterators found before unlocking; after reacquiring the write lock, stale end/non-end checks can be risky if the maps changed. Tests should stress concurrent first-use updates for the same and different IP/user pairs, IPv6 address conversion, and correct increments for both client and user counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/nodes/MetaNodeOpStats.h -->
