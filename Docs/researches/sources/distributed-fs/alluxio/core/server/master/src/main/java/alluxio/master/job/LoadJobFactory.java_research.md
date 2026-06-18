# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/LoadJobFactory.java

## Purpose
`LoadJobFactory` creates new `LoadJob` instances from client `LoadJobRequest`s. It translates gRPC load options and authenticated user context into the scheduler job model.

## Important APIs, types, and functions
The constructor stores `LoadJobRequest` and `FileSystemMaster`. `create()` extracts path, optional bandwidth, partial-listing flag, verify flag, authenticated user name, creates a filtered `FileIterable`, generates a UUID job id, and returns a `LoadJob`.

## Control flow
The factory reads request options, interprets `has*` flags, captures user via `AuthenticatedClientUser.getOrNull()`, and delegates iteration to `FileIterable`.

## State and persistence behavior
The factory is short-lived and stateless after creation. The generated job id and options become the job state that `LoadJob` journals later.

## Dependencies and integration points
It depends on `LoadJobRequest`, `LoadJobPOptions`, `FileSystemMaster`, `AuthenticatedClientUser`, `User`, UUID generation, and the scheduler factory contract. It is selected by `JobFactoryProducer`.

## Risks
If no authenticated user is set, the job runs with an empty user optional; downstream access/listing behavior must handle that. The user is fetched twice, which is usually harmless but assumes the thread-local does not change. Invalid bandwidth values are rejected by the `LoadJob` constructor rather than here.

## Test signals
Tests should cover optional bandwidth, partial listing, verify flag, user present/absent, UUID uniqueness expectation, filter wiring, and invalid request option propagation.
