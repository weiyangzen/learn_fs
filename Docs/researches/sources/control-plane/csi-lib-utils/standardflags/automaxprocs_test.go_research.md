# sources/control-plane/csi-lib-utils/standardflags/automaxprocs_test.go

## Purpose

This test file verifies parsing and state transitions for the shared `-automaxprocs` flag.

## Important Behavior

`TestAutomaxprocsArgument` ensures the flag is registered, then calls `flag.Set("automaxprocs", value)` for `true`, `false`, empty string, and invalid text, expecting only the invalid text to error. `TestEnableDisableAutomaxprocs` ensures the flag exists, disables it if already enabled, calls `EnableAutomaxprocs`, checks enabled state, then disables via `handleAutomaxprocs("false")` and checks state again.

## State, Dependencies, and Integration

The tests mutate Go's global default `flag.CommandLine` and the package-level `undoAutomaxprocs` state. They depend on the real `maxprocs.Set` behavior but do not assert exact `GOMAXPROCS` values.

## Risks and Test Signals

Global flag state means these tests can interact with other tests in the same process if run with conflicting flag registrations. They check error paths and enabled-state plumbing, but not logger output or container quota detection. Passing `go test ./standardflags` is the signal.
