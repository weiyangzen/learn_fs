# sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/mock.go

## Purpose
This file provides a Testify-backed BeeRemote provider for BeeSync tests.

## Important APIs, Types, and Functions
`MockProvider` embeds `mock.Mock` and satisfies `Provider`. `init` and `disconnect` are no-ops. `updateWork` and `submitJob` call Testify expectations and return a configured error.

## Control Flow
Tests configure expectations on the mock provider after `beeremote.Client` selects it for address `mock:0`. Each provider method retrieves the first return argument and validates that non-nil values are errors.

## State and Persistence Behavior
No state is persisted. Test expectation state lives in the embedded Testify mock.

## Dependencies and Integration Points
The mock provider is selected by `Client.UpdateConfig` and is heavily used by `sync/internal/workmgr/manager_test.go` to assert final work results sent to BeeRemote.

## Risks and Edge Cases
The mock panics if a non-error return value is configured, which is useful for tests but not production behavior. It does not model gRPC status codes unless tests explicitly return status errors.

## Test Signals
The work-manager tests exercise `updateWork` expectations for completed, failed, and retrying work results. `submitJob` is not exercised in this subset.
