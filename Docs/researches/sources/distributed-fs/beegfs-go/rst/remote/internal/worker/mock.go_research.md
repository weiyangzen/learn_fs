# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/mock.go

## Purpose
This file implements a Testify-backed worker node used by tests in other packages to simulate BeeSync worker behavior without running gRPC services.

## Important APIs, Types, and Functions
`MockNode` embeds `baseNode` and `mock.Mock`, satisfying both `Worker` and `grpcClientHandler`. `newMockNode` installs configured expectations. `connect`, `disconnect`, `SubmitWork`, and `UpdateWork` delegate to Testify calls. `heartbeat` returns a ready response without requiring expectations.

## Control Flow
Factory setup loops through `MockExpectation` entries and registers `On(...).Return(...)` calls. `SubmitWork` and `UpdateWork` reject offline nodes, call the configured mock method, report errors through `rpcErr`, and otherwise echo back work metadata with a fresh copy of the configured status.

## State and Persistence Behavior
No persistent state is used. The mock relies on `baseNode` state transitions and RPC wait-group tracking like real workers. It intentionally copies returned status objects to prevent tests from sharing mutable status pointers across requests.

## Dependencies and Integration Points
The mock depends on Testify mock and protobuf `flex`. It is used by job-manager tests and workermgr tests through `worker.Config{Type: worker.Mock}`.

## Risks and Edge Cases
`UpdateWork` cannot set `Path` in its returned `flex.Work` because the update request lacks a path; comments flag this as a possible source of future test issues. Expectations must include every method invoked by the test except heartbeat. Mock behavior may hide real gRPC status-code handling and reconnect behavior.

## Test Signals
The file is indirectly exercised by many tests in `remote/internal/job`. There are no direct tests of expectation setup, offline rejection, or error notification behavior.
