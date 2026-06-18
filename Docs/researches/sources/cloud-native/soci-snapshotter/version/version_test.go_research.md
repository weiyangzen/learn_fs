# sources/cloud-native/soci-snapshotter/version/version_test.go

## Purpose
`version_test.go` enforces that the `Version` variable is populated during test/build execution.

## Important APIs, Types, and Functions
`TestVersion` fails if `Version == Unset`.

## Control Flow, State, and Persistence
The test reads package global state only. It has no IO or persistence.

## Dependencies and Integration Points
It depends on Go `testing` and on build tooling injecting version metadata. It is therefore a signal for Makefile or CI linker flag wiring.

## Risks and Test Signals
The test can fail in plain `go test` invocations that do not set `-ldflags`. It does not validate `Revision`.
