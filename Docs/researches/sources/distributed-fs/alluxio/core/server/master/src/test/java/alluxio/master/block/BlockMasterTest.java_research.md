# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterTest.java

Purpose: broad unit test suite for `BlockMaster` worker registration, worker state transitions, block metadata, heartbeats, decommissioning, metrics dependencies, and container id reservation.

Important APIs/types/functions: setup creates a `DefaultBlockMaster` with `MetricsMaster`, `MasterRegistry`, `ManualClock`, and no-op journal context; helper stream registration functions generate `RegisterWorkerPRequest` chunks and send them to `BlockMasterWorkerServiceHandler`; tests cover build version, capacity accounting, lost/decommissioned workers, register/stream-register upgrade scenarios, block removal, heartbeat deltas, lost storage, unknown workers, executor shutdown, `getBlockInfo`, and concurrent `getNewContainerId`.

Control flow: most tests register workers through direct or streaming APIs, mutate clock or worker state, invoke heartbeats/commits/removals, then assert worker reports, command types, block locations, and counts. Decommission upgrade tests ensure a worker can be decommissioned with `canRegisterAgain`, continue sending cleanup heartbeats/commits, then re-register with a newer build version. Removal upgrade tests verify stale blocks are scheduled for freeing after re-registration.

State and persistence: exercises in-memory block master worker/block maps plus journal-reserved container ids under a no-op journal system. Manual heartbeat scheduling drives lost worker detection. The executor service is owned by the master and shutdown is asserted.

Dependencies/integration: integrates `DefaultBlockMaster`, `MetricsMasterFactory`, `MasterTestUtils`, `HeartbeatScheduler`, worker protobuf commands, register streaming, and block metadata wire types.

Risks: tests rely on constants for medium/tier strings and manual heartbeat contexts. Concurrent container id test asserts reservation bounds rather than exact journal entry count. The suite is large enough that shared setup global configuration can affect later tests if not reset by rules.

Test signals: protects build version propagation, live/lost/decommissioned counts, auto-deletion of lost workers, re-registration after loss or decommission, block location visibility for decommissioned workers, worker heartbeat add/remove/lost-storage effects, orphaned block cleanup commands, unknown-worker register command, executor termination, block info shape, and thread-safe container id reservation.
