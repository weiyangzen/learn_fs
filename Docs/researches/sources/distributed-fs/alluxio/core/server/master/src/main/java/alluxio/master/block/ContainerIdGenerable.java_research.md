<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/ContainerIdGenerable.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/ContainerIdGenerable.java

## Purpose
Small interface for components that allocate unique block container IDs.

## Important APIs, Types, And Functions
- `getNewContainerId()` returns a unique container ID and may throw `UnavailableException`.

## Control Flow
The interface defines no implementation flow. `BlockMaster` extends it, and `BlockContainerIdGenerator` provides a simple atomic implementation.

## State And Persistence Behavior
Implementations decide how to store and persist the next ID. The exception declaration allows implementations backed by unavailable master state or journal context to fail allocation.

## Dependencies And Integration Points
Depends on Alluxio status `UnavailableException`. It is part of the block master API surface used by code that needs container IDs without depending on a concrete implementation.

## Risks And Edge Cases
Callers must handle unavailability and should not assume allocation is purely in-memory. Implementations must prevent reuse across restart and restore.

## Test Signals
Signals include uniqueness, unavailable-state propagation, and correct persisted-next-ID restore for implementations that journal container IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/ContainerIdGenerable.java -->
