# sources/control-plane/mayastor/test/grpc/test_rebuild.js

## Purpose
Mocha/Chai tests for rebuild task behavior on a legacy Mayastor nexus. The suite verifies running, stopping, pausing, resuming rebuilds and child online/offline operations using a one-child nexus plus a second aio child added as rebuild target.

## Important APIs, Types, And Functions
The file defines `createGrpcClient`, `checkState`, `checkNumRebuilds`, `checkRebuildState`, retry helpers, and `checkRebuildStats`. It drives `AddChildNexus`, `StartRebuild`, `StopRebuild`, `PauseRebuild`, `ResumeRebuild`, `ChildOperation`, `GetRebuildState`, `GetRebuildStats`, and `ListNexus`.

## Control Flow
Setup creates two 100 MiB aio files, starts Mayastor, creates a nexus with the source child, then each nested `describe` block adds the target child, performs the rebuild action under test, and asserts nexus, child, rebuild-count, and stats state. Teardown removes the target child and eventually destroys the nexus and files.

## State And Persistence
State is transient Mayastor in-memory nexus/rebuild state plus two `/tmp` backing files. Rebuild progress and counters are queried over gRPC and not persisted by the test itself.

## Dependencies And Integration Points
Uses `grpc-promise` over `mayastor.proto`, `sleep-promise` for polling, `test_common` for process startup and NBD permission management, and aio bdev URIs. It covers the legacy gRPC rebuild API that v1 compatibility tests also exercise.

## Risks
The teardown block includes a suspicious stray brace/comma in the source, and the tests are timing-sensitive because rebuild state transitions are polled with short retry windows. Some assertions compare numeric counts to string literals, which depends on proto loader conversion behavior.

## Test Signals
Successful runs indicate that rebuild state transitions, task counters, child degradation, and stats fields remain observable and compatible through the legacy API.
