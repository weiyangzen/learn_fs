# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterFactory.java

## Purpose
`MetaMasterFactory` is the master factory responsible for creating the Alluxio meta master. It is a small registry integration class that tells the master framework whether the meta master is enabled, names it, retrieves the already-registered `BlockMaster`, and constructs `DefaultMetaMaster`.

## Important APIs and Types
- Implements `MasterFactory<CoreMasterContext>`.
- `isEnabled()` always returns `true`, making the meta master a core master.
- `getName()` returns `Constants.META_MASTER_NAME`.
- `create(MasterRegistry, CoreMasterContext)` constructs `DefaultMetaMaster(registry.get(BlockMaster.class), context)` and registers it in the supplied `MasterRegistry`.

## Control Flow
The master bootstrap path discovers factories, calls `isEnabled`, then invokes `create`. This factory logs that it is creating the meta master, looks up the block master dependency from the registry, constructs the concrete default implementation, registers it, and returns it.

## State and Persistence
The factory is stateless. Persistence is entirely in the created `DefaultMetaMaster` and its journaled delegates.

## Dependencies and Integration Points
Depends on the master framework (`MasterFactory`, `MasterRegistry`, `CoreMasterContext`), `BlockMaster`, and constants. It is the bridge between service discovery/bootstrap and the meta master implementation.

## Risks and Edge Cases
The factory cannot disable the meta master, so configuration-based disablement is not supported here. Constructor or registry failures propagate during master startup. The factory assumes `BlockMaster` is already available in the registry.

## Test Signals
Tests can validate the factory name, enabled status, `BlockMaster` lookup, concrete type creation, and that the registry receives the created master.
