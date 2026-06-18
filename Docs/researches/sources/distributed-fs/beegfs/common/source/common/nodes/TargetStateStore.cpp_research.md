# sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateStore.cpp

## Purpose
Implements a thread-safe map of target IDs to reachability/consistency state and coordinated atomic synchronization with mirror buddy groups.

## Important APIs, Types, And Functions
Implements `addIfNotExists()`, `removeTarget()`, `syncStatesAndGroups()`, `syncStatesFromLists()`, `getStatesAndGroups()`, `getStatesAsLists()`, `getStatesAsListsUnlocked()`, and string conversion helpers.

## Control Flow
Bulk sync builds a temporary `TargetStateInfoMap`, then swaps it under write lock. `syncStatesAndGroups()` also locks the buddy-group mapper write lock and swaps group mappings under the same critical section, updating the local group ID if a group contains the local node. Reads of states plus groups take both locks in read mode to avoid observing split-brain transitions.

## State, Persistence, And Dependencies
State is `statesMap` protected by `RWLock` and the `NodeType` used for logs. Persistence is external via serialized lists/messages. Dependencies include `MirrorBuddyGroupMapper`, `ZipIterator`, and `TargetStateInfo`.

## Integration Points
`TargetMapper` creates/removes entries. Management state sync and mirror buddy group messages use the atomic group/state APIs. Node stores may attach a state store for cleanup.

## Risks
All callers must use the combined state/group APIs when mirror groups are involved; otherwise observers can see inconsistent failover state. `syncStatesFromLists()` zips lists and silently stops at shortest input if list lengths differ. Lock ordering with buddy groups must stay consistent.

## Test Signals
Cover add-if-not-exists idempotence, list sync with mismatched lengths, atomic state/group swap, local group detection, read consistency under concurrent sync, and string conversion of invalid enums.
