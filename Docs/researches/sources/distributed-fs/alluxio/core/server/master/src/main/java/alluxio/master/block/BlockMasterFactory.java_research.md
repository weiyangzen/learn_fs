<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterFactory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterFactory.java

## Purpose
Factory for creating and registering the default `BlockMaster` implementation in the master registry.

## Important APIs, Types, And Functions
- Implements `MasterFactory<CoreMasterContext>`.
- `isEnabled()` always returns true.
- `getName()` returns `Constants.BLOCK_MASTER_NAME`.
- `create(MasterRegistry, CoreMasterContext)` obtains `MetricsMaster`, constructs `DefaultBlockMaster`, registers it as `BlockMaster`, and returns it.

## Control Flow
During `MasterUtils.createMasters`, the service loader invokes this factory. It relies on `MetricsMaster` already being available in the registry, then adds the block master interface mapping.

## State And Persistence Behavior
The factory itself is stateless. The created `DefaultBlockMaster` owns block metadata state and persistence through the provided context.

## Dependencies And Integration Points
Integrates with Alluxio service loading, `MasterRegistry`, `CoreMasterContext`, metrics master, constants, and the default block master implementation.

## Risks And Edge Cases
Parallel master factory creation means dependency ordering on `MetricsMaster` is important. If metrics master is absent, registry lookup will fail during creation.

## Test Signals
Signals include factory enabled/name values, successful registry insertion, correct dependency lookup, and `DefaultBlockMaster` construction with the supplied context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterFactory.java -->
