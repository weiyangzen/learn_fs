# sources/cloud-native/moby/daemon/errors.go

## Purpose
Centralizes daemon error types and container-start exit-code mapping so API routers and clients receive correct conflict/not-found/invalid/unknown classifications and CLI-compatible exit statuses.

## Important APIs, Types, And Functions
- `containerNotRunningError`, `objNotFoundError`, `nameConflictError`, `invalidIdentifier`, `incompatibleDeviceRequest`, `duplicateMountPointError`, `containerFileNotFound`, and `startInvalidConfigError` implement errdefs marker interfaces.
- `errNotRunning`, `containerNotFound`, `errContainerIsRestarting`, `errExecNotFound`, and `errExecPaused` build common errors.
- `setExitCodeFromError` maps containerd start errors to 126, 127, or 128 and wraps them as invalid config or unknown errors.
- `isInvalidCommand` recognizes common executable-not-found messages.

## Control Flow
Marker methods such as `Conflict`, `NotFound`, and `InvalidParameter` drive errdefs classification. Start error mapping extracts the gRPC status message, checks for permission denied, directory execution, not-a-directory bind issues, command-not-found signatures, and otherwise returns an unknown error after setting a generic exit code.

## State And Persistence
No persistent state. `setExitCodeFromError` mutates container exit code through the provided callback.

## Dependencies And Integration Points
Integrates with `errdefs`, `pkg/errors`, gRPC status conversion, syscall error strings, device request errors, exec/container lifecycle code, and CLI expectations for exit codes.

## Risks And Edge Cases
String matching against runtime/containerd error messages is brittle but necessary for compatibility. The EISDIR path appends permission-denied text to preserve existing CLI behavior. Unknown runtime errors become exit code 128 and errdefs unknown.

## Test Signals
`errors_test.go` verifies `errNotRunning` classification through `isNotRunning`. Broader start-error mapping requires start-path tests.
