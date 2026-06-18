# sources/control-plane/longhorn-engine/app/cmd/snapshot_test.go

## Purpose
Unit-tests argument validation for `revertSnapshot` to ensure invalid inputs return errors instead of panicking.

## Important APIs, Types, and Functions
- `TestRevertSnapshotWithNoArgs()`.
- `TestRevertSnapshotWithEmptyStringArg()`.
- Uses `flag.FlagSet` and `urfave/cli.NewContext` to call unexported command helper directly.

## Control Flow
The first test builds a CLI context with no args and asserts error text `snapshot name is required`. The second parses a single empty string argument and asserts `missing parameter for snapshot`.

## State and Persistence Behavior
No persistent state. It avoids controller client creation by failing before RPC setup.

## Dependencies and Integration Points
Depends on `testing`, Go `flag`, and urfave/cli. It protects the guard clause in `snapshot.go::revertSnapshot`.

## Risks and Edge Cases
The tests assert exact error strings, so message changes are breaking. They do not cover successful revert or controller-client failures.

## Test Signals
This file itself is the direct unit test signal for a known CLI panic/validation boundary.
