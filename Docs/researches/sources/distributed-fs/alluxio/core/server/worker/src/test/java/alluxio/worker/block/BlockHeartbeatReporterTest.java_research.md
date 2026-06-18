# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockHeartbeatReporterTest.java

## Purpose
`BlockHeartbeatReporterTest` validates how `BlockHeartbeatReporter` accumulates, clears, and merges block heartbeat deltas for moves, removals, and lost storage.

## Important APIs, Types, and Functions
`generateReportEmpty()` checks empty output. `generateReportMove()` records moves to MEM/SSD/HDD and checks added blocks by location. `generateReportStateClear()` verifies reports clear state. `generateReportRemove()` checks removed block IDs. `generateReportMoveThenRemove()` ensures a moved-then-removed block is not reported as added. `generateAndRevert()` and `generateUpdateThenRevert()` validate `mergeBack()` after failed heartbeat submission with additional local updates.

## Control Flow, State, and Persistence
The reporter is in-memory. Generating a report clears pending deltas, and `mergeBack()` reintroduces a failed report while preserving newer changes.

## Dependencies and Integration Points
It depends on worker storage locations, configuration for register-to-all-masters, and block heartbeat report structures used by worker-master heartbeat RPCs.

## Risks and Test Signals
The test strongly covers delta coalescing and rollback semantics. Gaps include concurrency, large reports, interaction with `BlockMasterClient.heartbeat`, and storage-lost edge cases across duplicate paths.
