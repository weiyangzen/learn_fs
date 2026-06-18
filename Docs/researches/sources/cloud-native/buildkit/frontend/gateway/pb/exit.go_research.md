# sources/cloud-native/buildkit/frontend/gateway/pb/exit.go

## Purpose

This file defines the typed gateway exec exit error used to carry container process exit status over gRPC error details and local APIs.

## Important APIs, Types, And Functions

- `UnknownExitStatus` is the sentinel exit status `255` for cases where a process never starts or exit status cannot be obtained.
- Package `init` registers `ExitMessage` with `typeurl` for typed error conversion.
- `ExitError` stores `ExitCode` and wrapped `Err`.
- `(*ExitError).ToProto`, `Error`, and `Unwrap` implement typed gRPC error and normal Go error behavior.
- `(*ExitMessage).WrapError` reconstructs an `ExitError` from protobuf error details.

## Control Flow

When a process exits nonzero, gateway server/client code wraps status information in `ExitMessage`/`ExitError`. `Error` delegates to the wrapped error message when present, otherwise formats the exit code. `WrapError` is called by typed error conversion to attach the code to a received error.

## State And Persistence Behavior

Only global type registration is performed. Exit errors are transient process results.

## Dependencies And Integration Points

It integrates with `containerd/typeurl` and BuildKit `grpcerrors.TypedErrorProto`. `gateway.go` emits exit messages from `ExecProcess`, and `grpcclient/client.go` converts received nonzero exit messages into `pb.ExitError`.

## Risks And Edge Cases

`UnknownExitStatus` is intentionally aligned with containerd behavior without importing containerd. If a real process exits 255, callers must distinguish context from wrapped error details. If `Err` is nil, the error text is a plain exit-code message.

## Test Signals

No direct tests are in this subset. Useful coverage would assert typed registration round trips, wrapping/unwrapping behavior, and nonzero process exit conversion in gateway exec.
