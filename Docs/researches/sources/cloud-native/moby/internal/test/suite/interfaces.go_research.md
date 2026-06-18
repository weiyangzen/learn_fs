# sources/cloud-native/moby/internal/test/suite/interfaces.go

## Purpose
Defines lifecycle interfaces for Moby's lightweight internal test suite runner.

## Important APIs, Types, And Functions
- `SetupAllSuite` requires `SetUpSuite(context.Context, *testing.T)`.
- `SetupTestSuite` requires `SetUpTest(context.Context, *testing.T)`.
- `TearDownAllSuite` requires `TearDownSuite(context.Context, *testing.T)`.
- `TearDownTestSuite` requires `TearDownTest(context.Context, *testing.T)`.
- `TimeoutTestSuite` declares `OnTimeout()`.

## Control Flow
This file only defines interfaces; `suite.go` performs discovery and invocation.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses `context` and `testing`. Suite implementations can opt into lifecycle hooks by implementing these exact signatures.

## Risks And Edge Cases
Signature mismatches are detected in `suite.go` and panic with explicit messages. `TimeoutTestSuite` is defined but not invoked by the runner in the neighboring implementation.

## Test Signals
Behavior is covered indirectly by suite runner usage; no direct tests are in this file.
