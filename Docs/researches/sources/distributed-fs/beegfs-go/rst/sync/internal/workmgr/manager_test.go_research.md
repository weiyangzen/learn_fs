# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/manager_test.go

## Purpose
This file tests BeeSync work-manager persistence, scheduling, cancellation, BeeRemote reporting, and performance characteristics using temporary Badger databases and mock providers.

## Important APIs, Types, and Functions
`baseTestRequest` defines a reusable upload work request. Helper matchers compare protobuf job/request IDs and statuses in Testify mocks. `getTestManager` creates temp DB paths, logger, mock BeeRemote client, mock filesystem, starts the manager, and applies runtime config. `TestUpdateConfig`, `TestSubmitWorkRequest`, and `TestUpdateRequests` are functional tests. Benchmark functions measure manager submission and raw Badger store overhead.

## Control Flow
Tests set expectations on a mock RST client and BeeRemote mock provider, submit work requests, sleep for worker processing, and assert DB entry counts and active-work sizes. Cancellation tests deliberately constrain queue size and worker count to create active and inactive scenarios, then call `UpdateWork` and inspect returned work states and remaining DB mappings.

## State and Persistence Behavior
Each test uses separate temporary work journal and job store directories. Tests verify successful BeeRemote reporting cleans both stores, failed BeeRemote reporting retains entries and active work for retry, cancelling failed work removes entries, completed work cannot be cancelled, and inactive queued work can be cancelled with scheduler token cleanup.

## Dependencies and Integration Points
The file integrates `workmgr.Manager`, `beeremote.MockProvider`, `rst.MockClient`, mock filesystem, Badger options, scheduler behavior indirectly, Testify, protobuf cloning, and zaptest logging.

## Risks and Edge Cases
Tests rely on fixed sleep intervals for asynchronous worker processing. They use mock RSTs and mock Remote, so they do not cover real network failures, gRPC status-code retry classification, real object storage behavior, or restart recovery from pre-existing journals except through initialization code paths. Benchmark code includes manual Badger tuning experiments and is not a correctness gate.

## Test Signals
The tests confirm the work manager's main invariants: duplicate work is rejected, final successful reports clean persistent state, failed reports preserve retryable state, cancellation takes ownership of responses, completed work is not downgraded to cancelled, and multiple work requests for the same job can be indexed and removed independently.
