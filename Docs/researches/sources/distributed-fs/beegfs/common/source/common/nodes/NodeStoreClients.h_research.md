# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreClients.h

## Purpose
Declares the client-node store specialization of `AbstractNodeStore`.

## Important APIs, Types, And Functions
The class declares add/update, delete, reference, enumeration, active check, size, and `syncNodes()`. It keeps `activeNodes`, `mutex`, `newNodeCond`, and a virtual `generateID()` hook.

## Control Flow
The API mirrors server stores but omits local-node and attached mapper/capacity-store behavior.

## State, Persistence, And Dependencies
All state is process-local. Dependencies are `Mutex`, `Condition`, `Node`, `StorageErrors`, and `AbstractNodeStore`.

## Integration Points
Used anywhere client nodes must be tracked separately from metadata/storage/management servers.

## Risks
Condition variable is broadcast on add but no wait API is exposed in this class. Subclasses must provide ID generation if zero-ID client registration is valid.

## Test Signals
Compile and subclass tests should verify virtual hooks and overrides match `AbstractNodeStore`.
