# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStore.h

## Purpose
Provides a migration typedef from the old unified `NodeStore` name to `NodeStoreServers`.

## Important APIs, Types, And Functions
Only `typedef class NodeStoreServers NodeStore;` is exported.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
No state is owned. The header includes `NodeStoreServers.h`.

## Integration Points
Legacy code can include this file while the codebase transitions to explicit client/server stores.

## Risks
New code should avoid it because it hides the server-specific semantics of the aliased type.

## Test Signals
Build coverage of legacy includes is sufficient; no runtime tests are needed.
