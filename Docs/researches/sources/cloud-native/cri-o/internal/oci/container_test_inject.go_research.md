# sources/cloud-native/cri-o/internal/oci/container_test_inject.go

## Purpose
Provides test-only hooks compiled with the `test` build tag for manipulating unexported OCI container/runtime internals.

## Important APIs and Integration
`Container.SetState` replaces internal state. `SetStateAndSpoofPid` fills PID/start-time data with PID 1 when missing, then replaces state. `RuntimeOCI` exposes a wrapper around `runtimeOCI`, and `NewRuntimeOCI` constructs it for tests with a supplied `Runtime` and handler.

## Risks and Test Signals
These helpers bypass production locking and validation, so they should remain build-tag restricted. They enable the container and runtime tests in this subset to exercise private stop/status behavior without starting full CRI-O.
