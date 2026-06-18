# sources/cloud-native/nydus-snapshotter/version/version.go

## Purpose
This Go package centralizes build identity values for nydus-snapshotter. It exposes package-level variables for semantic version, VCS revision, Go runtime version, and build timestamp.

## Important APIs, Types, and Functions
- `Version`, `Revision`, and `BuildTimestamp` default to `"unknown"` and are intended to be overridden at link time with `-ldflags -X`.
- `GoVersion` is initialized from `runtime.Version()` at program startup.
- There are no functions or custom types.

## Control Flow
Package initialization assigns the variable values. Downstream binaries import the package and include these variables in version output or diagnostics.

## State and Persistence
State is process-global and immutable by convention, though exported variables can be modified by other Go code. No persistence occurs.

## Dependencies and Integration Points
The only code dependency is Go's `runtime` package. Build scripts and release pipelines integrate by injecting the true values during linking.

## Risks and Edge Cases
If build flags are omitted, release binaries report `"unknown"` version, revision, and timestamp. Because the values are variables rather than constants, accidental mutation is possible in tests or runtime code.

## Test Signals
No tests are present in this file. Validation is typically through CLI `version` output in built artifacts and release jobs that assert ldflags were applied.
