# sources/control-plane/ceph-csi/internal/health-checker/manager_test.go

## Purpose
`manager_test.go` verifies basic manager semantics for missing, shared, and non-shared stat checkers.

## Important APIs, Types, And Functions
`TestManager` exercises normal `StartChecker`, `IsHealthy`, and `StopChecker`. `TestSharedChecker` verifies `StartSharedChecker` stores a checker under volume ID only and ignores path during lookup. `TestTwoNonSharedChecker` verifies two different paths for the same volume are independent.

## Control Flow And Test Behavior
Tests use temporary directories and the same fake volume ID. They start `StatCheckerType` checkers only, query health immediately, and stop the checkers at the end. `require.ErrorContains` asserts missing non-shared path lookup reports no checker.

## Dependencies And Integration Points
The tests depend on `testify/require` and package-private manager behavior. They indirectly instantiate stat checkers, so they depend on the host filesystem allowing `os.Stat` on temporary directories.

## Risks And Edge Cases
The assertions contain repeated checks against the earlier `err` variable instead of the newly returned `msg` in some places, which weakens failure detection. No race detector behavior is asserted, and there is no cleanup defer if a fatal assertion happens after a checker has been started.

## Test Signals
The tests document intended keying semantics: shared checkers shadow path-specific lookup, and non-shared checkers are isolated by path. Coverage gaps include file checkers, duplicate keys, invalid checker types, combined type bitmasks, and concurrent usage.
