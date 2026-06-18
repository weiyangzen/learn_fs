# sources/control-plane/ceph-csi/internal/rbd/features/features_test.go

## Purpose
Smoke-tests librbd group snapshot capability detection in the current test environment.

## Important APIs, Types, And Functions
`TestSupportsGroupSnapGetInfo` calls `SupportsGroupSnapGetInfo`, fails if detection returns an unexpected error, and logs whether the symbol is supported.

## Control Flow
The test runs in parallel and does not assert a fixed support value, because installed librbd versions may differ across environments.

## State And Persistence
No persistent state is written. The test populates the package-level `sync.Once` cache in `features.go`, which can affect subsequent tests in the same process.

## Dependencies And Integration Points
Depends on cgo/native librbd availability and dynamic symbol detection. It verifies the detection path used by driver and identity capability advertisement.

## Risks And Test Signals
This catches broken dynamic loading but not incorrect capability wiring. Because it accepts both supported and unsupported states, it cannot detect accidental loss of support on environments that should provide the symbol.
